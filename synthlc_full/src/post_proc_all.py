import os
import pandas as pd
from gconsts import *
from csv_util import *
from util import *
from IFT_template import *
import itertools

def post_proc_all(
    intrin_res,
    field,
    i_p_instns,
    BATCH_INSTNDIR,
    i_p_id,
    i0_constraint,
    decision_src, 
    div_node_all_uniq_pl_iso, 
    cnt_follower_sets,
    group_items_transmitter
    ):
    ret_arr = []
    ret_arr.append(len(cnt_follower_sets))
    uniq_pl_in_all_pl_set = sorted(div_node_all_uniq_pl_iso[decision_src])

    # groups in the table in the order: Branch, DIV, JALR, Load, REM, Store
    table_order = [str(itm) for itm in [9, 11, 10, 4, 11, 7]]
    table_in = [str(itm) for itm in [9, 11, 10, 4, 11, 7]]

    for agroup in group_items_transmitter:
        group_id, field, t_instns = agroup
        if not group_id in table_order:
            table_order.append(group_id)
    #print(table_order)
    #return
    # iterate over group of transmitters
    for group_id in table_order:
        for agroup in group_items_transmitter:
            gid, field, t_instns = agroup
            if gid == group_id:
                break

        t_instns = t_instns.split(",")

        ######## intrinsic ########
        intrinsic_result = [0, 0] # rs1, rs2
        #print('-.->', i_p_id, i_p_instns, t_instns)
        if i_p_id == group_id or sorted(i_p_instns) == sorted(t_instns):
            #print("!!!")
            for idx, itm in enumerate(intrin_res):
                intrinsic_result[idx] = int(itm)
            
        ######## dynamic: this group_id as transmitter ########
        dynamic_result = [0, 0] # rs1, rs2 
        #print("==> ", group_id, t_instns)
        if field == "" :
            continue
        res_map = {} # (i_p, i_t, rs1/rs2) to cnt of decisions that are tainted 
        for pairafset in cnt_follower_sets:
            cnt, afset = pairafset

            tar_dir = "group_{I}_IFT/dyn/bothfield".format(I=i_p_id)
            TFIELD="bothrs_"
            if field == "rs1":
                tar_dir = "group_{I}_IFT/dyn/rs1".format(I=i_p_id)
                TFIELD="rs1_"

            rs1_f, rs2_f = None, None
            if TFIELD == "bothrs_": 
                # File shared by the group
                rs1_f = "{tdir}/out_perfield/{cnt}_{field}_rs1.sv".format(tdir=tar_dir, cnt = cnt, field=field)
                rs2_f = "{tdir}/out_perfield/{cnt}_{field}_rs2.sv".format(tdir=tar_dir, cnt = cnt, field=field)
            # Group wide check
            csvf ="{tdir}/{groupid}_{ID}.csv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
            df = pd.read_csv(csvf, dtype=mydtypes)
            res, bnd, time = df_query(df, "DEP_I_%s" % (TFIELD + cnt))
            if res == "covered":
                csvf ="{tdir}/{groupid}_{ID}_intragp.csv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
                #print("==> ", csvf)
                df = pd.read_csv(csvf, dtype=mydtypes)
                all_pairs = list(itertools.product(i_p_instns, t_instns))
                csv_rs1_f = "{tdir}/{cnt}_{field}_rs1.csv".format(tdir=tar_dir, cnt = cnt, field=field)
                if os.path.exists(csv_rs1_f):
                    df1 = pd.read_csv(csv_rs1_f, dtype=mydtypes)

                csv_rs2_f = "{tdir}/{cnt}_{field}_rs2.csv".format(tdir=tar_dir, cnt = cnt, field=field)
                if os.path.exists(csv_rs2_f):
                    df2 = pd.read_csv(csv_rs2_f, dtype=mydtypes)

                for p in all_pairs:
                    i_p, i_t = p
                    prop_name = "DEP_I_%s" % (i_p + "_" + i_t) 
                    res, bnd, time = df_query(df, prop_name)
                    if res == "covered" and TFIELD == "rs1_":
                        res_map[(i_p, i_t, "rs1")] = res_map.get((i_p, i_t, "rs1"), 0) + 1
                    elif res == "covered" and TFIELD == "bothrs_":
                        # if skip then just reigster rs1
                        skip = False
                        if i_t in ["SW", "SB", "SD", "SH"]:
                            skip = True
                            if len(afset) == 0:
                                rs1, rs2 = skip_ufsm_based([i_t], uniq_pl_in_all_pl_set)
                            else:
                                rs1, rs2 = skip_ufsm_based([i_t], afset)
                            assert (rs1 == False and rs2 == True) 
                        if skip:
                            res_map[(i_p, i_t, "rs1")] = res_map.get((i_p, i_t, "rs1"), 0) + 1
                            continue
                        # check per operands
                        res, bnd, time = df_query(df1, prop_name)
                        if res == "covered":
                            res_map[(i_p, i_t, "rs1")] = res_map.get((i_p, i_t, "rs1"), 0) + 1
                        res, bnd, time = df_query(df2, prop_name)
                        if res == "covered":
                            res_map[(i_p, i_t, "rs2")] = res_map.get((i_p, i_t, "rs2"), 0) + 1
                            
        #print(80*"-")
        #print(t_instns, len(cnt_follower_sets))

        rs1 = None
        rs2 = None
        all_pairs = list(itertools.product(i_p_instns, t_instns))
        for p in all_pairs:
            i_p, i_t = p
            if rs1 is None:
                rs1 = ((i_p, i_t, "rs1") in res_map and res_map[(i_p, i_t, "rs1")] >= 2)
                rs2 = ((i_p, i_t, "rs2") in res_map and res_map[(i_p, i_t, "rs2")] >= 2)
            else:
                t1 = ((i_p, i_t, "rs1") in res_map and res_map[(i_p, i_t, "rs1")] >= 2)
                if not (t1 == rs1):
                    #print("!!! WARN", i_p, i_t, "rs1")
                    rs1 = rs1 or t1
                t2 = ((i_p, i_t, "rs2") in res_map and res_map[(i_p, i_t, "rs2")] >= 2)
                if not (t2 == rs2):
                    #print("!!! WARN", i_p, i_t, "rs2")
                    rs2 = rs2 or t2
        if group_id in table_in:
            #print(t_instns, intrinsic_result[0], intrinsic_result[1], rs1, rs2)
            ret_arr += [intrinsic_result[0], intrinsic_result[1], int(rs1), int(rs2)]
        #for k, v in res_map.items():
            #print(" ==> ", k, v)
    print(ret_arr)        
    return ret_arr
            



    ## groups not in the table
    #for agroup in group_items_transmitter:
    #    group_id, field, t_instns = agroup
    #    if group_id in table_order:
    #        continue
    #    # Checks all are not "covered"

    #    if i_p_id == group_id:
    #        assert(intrin_res[0] == False and intrin_res[1] == False)


