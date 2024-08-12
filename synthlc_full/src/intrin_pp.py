import os
from gconsts import *
from util import *
from IFT_template import *
from csv_util import *
# just entire group first
def intrin_pp(
    i_p_instns,
    field_i_p,
    BATCH_INSTNDIR,
    i_p_id,
    i0_constraint,
    decision_src, 
    div_node_all_uniq_pl_iso, 
    cnt_follower_sets,
    group_items_transmitter
    ):
    res_map = {}
    # from (i_p, rs1/rs2) to cnt of decisions that are tainted 
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

        org_dir = "group_{I}_IFT/itself".format(I=i_p_id)
        tar_dir = "group_{I}_IFT/itself_per".format(I=i_p_id)
        prep_dir(tar_dir + "/out")
        TFIELD="bothrs_"
        DEFINEOPTAINT="`define BORTHRS"
        if field_i_p == "rs1":
            TFIELD="rs1_"
            DEFINEOPTAINT="`define RS1"

        # decision idx
        csvf ="{tdir}/{ID}_g.csv".format(tdir=org_dir, ID=cnt)

        if not os.path.exists(csvf):
            assert(0)
        df = pd.read_csv(csvf, dtype=mydtypes)

        res, bnd, time = df_query(df, "DEP_%s" % (TFIELD + str(cnt)))
        if res == "covered":
            for i_p in i_p_instns:
                i0_constraint = get_i_constraint_indep(i_p, "i0")
                csvf ="{tdir}/{ID}_{i_p}.csv".format(tdir=org_dir, ID=cnt, i_p=i_p)
                df = pd.read_csv(csvf, dtype=mydtypes)
                res, bnd, time = df_query(df, "DEP_%s" % (TFIELD + str(cnt)))
                if res == "covered" and TFIELD == "rs1_":
                    res_map[(i_p, "rs1")] = res_map.get((i_p, "rs1"), 0) + 1
                    # from (i_p, rs1/rs2) to cnt of decisions that are tainted 
                    continue

                skip = False
                if i_p in ["SW", "SB", "SD", "SH"]:
                    skip = True
                    if len(afset) == 0:
                        rs1, rs2 = skip_ufsm_based([i_p], uniq_pl_in_all_pl_set)
                    else:
                        rs1, rs2 = skip_ufsm_based([i_p], afset)
                    assert (rs1 == False and rs2 == True) 
                if res == "covered" and skip:
                    res_map[(i_p, "rs1")] = res_map.get((i_p, "rs1"), 0) + 1
                    continue

                if res == "covered" and TFIELD=="bothrs_": 
                    for tag, deft in zip(["rs1", "rs2"], ["`define RS1", "`define RS2"]):
                        csvf="{tdir}/{ID}_{i_p}_{tag}.csv".format(tdir=tar_dir, ID=cnt, i_p=i_p, tag=tag)
                        df = pd.read_csv(csvf, dtype=mydtypes)
                        res, bnd, time = df_query(df, "DEP_%s" % (TFIELD + str(cnt)))
                        if res == "covered":
                            res_map[(i_p, tag)] = res_map.get((i_p, tag), 0) + 1
    rs1_res = []                        
    rs2_res = []                        
    for k, v in res_map.items():
        if k[1] == "rs1" and v >= 2:
            rs1_res.append(k[0])
        if k[1] == "rs2" and v >= 2:
            rs2_res.append(k[0])
    #print("-->  ", rs1_res)
    #print("-->  ", rs2_res)
    rs1_ret = True
    rs2_ret = True
    for i_p in i_p_instns:
        rs1_ret = rs1_ret and i_p in rs1_res
        rs2_ret = rs2_ret and i_p in rs2_res
    return (rs1_ret, rs2_ret)
