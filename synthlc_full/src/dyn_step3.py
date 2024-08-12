import os
import pandas as pd
from gconsts import *
from csv_util import *
from util import *
from IFT_template import *
import itertools
    
def dyn_step3_proc(
    i_p_instns,
    BATCH_INSTNDIR,
    i_p_id,
    i0_constraint,
    decision_src, 
    div_node_all_uniq_pl_iso, 
    cnt_follower_sets,
    group_items_transmitter
    ):
    uniq_pl_in_all_pl_set = sorted(div_node_all_uniq_pl_iso[decision_src])
    # iter over each decision for thie decision_src
    for pairafset in cnt_follower_sets:
        cnt, afset = pairafset
        afset = sorted(afset)
        followerset = "("
        if not decision_src in afset:
            followerset += "!{node} && ".format(node=transform_disjunc(decision_src))
        for eachN in uniq_pl_in_all_pl_set:
            if eachN == "":
                continue
            followerset += "{ina}{node} && ".format(
                    node = transform_disjunc(eachN),
                    ina = ("" if (eachN in afset) else "!")
            )
     
        followerset += " 1'b1)"
        if len(afset) == 0:
            t0 = "|{"
            for eachN in uniq_pl_in_all_pl_set:
                if eachN == "":
                    continue
                t0 += (transform_iso_t0_neg(eachN, decision_src) + " ,")
            t0 += "1'b0}"

        else:
            t0 = "|{"
            for eachN in afset:
                t0 += (transform_iso_t0(eachN) + " ,") # + "_t0 ,")
            t0 += "1'b0}"

        # for this given decision_src, afset
        # iterate over group of transmitters
        rs1_f_hdlr = None
        rs2_f_hdlr = None
        for agroup in group_items_transmitter:
            #todo_group = []
            # group_id is the id of the candidate transmitters
            group_id, field, t_instns = agroup
            t_instns = t_instns.split(",")
            if field == "" :
                continue
            #todo_group = [group_id]

            #for group_id in todo_group: 
            tar_dir = "group_{I}_IFT/dyn/bothfield".format(I=i_p_id)
            TFIELD="bothrs_"
            DEFINEOPTAINT="`define BORTHRS"
            if field == "rs1":
                tar_dir = "group_{I}_IFT/dyn/rs1".format(I=i_p_id)
                TFIELD="rs1_"
                DEFINEOPTAINT="`define RS1"

            if TFIELD == "bothrs_": 
                prep_dir(tar_dir + "/out_perfield")
                # File shared by the group
                rs1_f = "{tdir}/out_perfield/{cnt}_{field}_rs1.sv".format(tdir=tar_dir, cnt = cnt, field=field)
                rs2_f = "{tdir}/out_perfield/{cnt}_{field}_rs2.sv".format(tdir=tar_dir, cnt = cnt, field=field)


            csvf ="{tdir}/{groupid}_{ID}.csv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
            if not os.path.exists(csvf):
                assert(0)
                continue

            #print("-> csv ", group_id, TFIELD, cnt)
            df = pd.read_csv(csvf, dtype=mydtypes)
            res, bnd, time = df_query(df, "DEP_I_%s" % (TFIELD + cnt))
            if res == "covered":
                # group , but per field
                # > Do for SW ufsm

                # intra-group instn pair 
                #print("-> covered", group_id, TFIELD, cnt, field)
                orgf ="{tdir}/out/{groupid}_{ID}_intragp.sv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
                header,  prop_start = "", False
                cur_prop = None
                props_meta = {}
                with open(orgf, "r") as f:
                    for line in f:
                        if "cover property" in line:
                            prop_start = True
                        if not prop_start:
                            header += line
                        else:
                            if "cover" in line:
                                if cur_prop is not None:
                                    props_meta[cur_prop] = acc
                                    #print('->', cur_prop)
                                    acc = ""
                                cur_prop = line.split(":")[0]
                                acc = line
                            else:
                                acc += line
                ###
                if cur_prop is not None:
                    props_meta[cur_prop] = acc


                csvf ="{tdir}/{groupid}_{ID}_intragp.csv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
                df = pd.read_csv(csvf, dtype=mydtypes)


                # iterate in every combination of transmitter and transponder in the group 
                all_pairs = list(itertools.product(i_p_instns, t_instns))
                #print(all_pairs)
                for p in all_pairs:
                    i_p, i_t = p

                    prop_name = "DEP_I_%s" % (i_p + "_" + i_t) 
                    res, bnd, time = df_query(df, prop_name)
                    if res == "covered":
                        # TODO: collecting resulst for rs1?

                        #print("-->", i_p, i_t, field)
                        if TFIELD == "bothrs_": 
                            # generate new files if needed
                            
                            
                            skip = False
                            if i_t in ["SW", "SB", "SD", "SH"]:
                                skip = True
                                if len(afset) == 0:
                                    rs1, rs2 = skip_ufsm_based([i_t], uniq_pl_in_all_pl_set)
                                else:
                                    rs1, rs2 = skip_ufsm_based([i_t], afset)
                                assert (rs1 == False and rs2 == True) 
                            if not skip:                             
                                if rs1_f_hdlr is None:
                                    rs1_f_hdlr = open(rs1_f, "w")
                                    rs1_f_hdlr.write(header.replace("BORTHRS", "RS1"))
                                if rs2_f_hdlr is None:
                                    rs2_f_hdlr = open(rs2_f, "w")
                                    rs2_f_hdlr.write(header.replace("BORTHRS", "RS2"))
                                rs1_f_hdlr.write(props_meta[prop_name] + "\n")
                                rs2_f_hdlr.write(props_meta[prop_name] + "\n")
        if rs2_f_hdlr is not None:
            rs2_f_hdlr.close()
            rs1_f_hdlr.close()
    cmd = "python3 host_batch_run_template_v2.py --seq group_{groupid}_IFT/dyn/bothfield group_{groupid}_IFT/dyn/bothfield/out_perfield".format(groupid=i_p_id)
    return cmd
