import os
import pandas as pd
from gconsts import *
from csv_util import *
from util import *
from IFT_template import *
import itertools

    
def dyn_step2_proc(
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
        for agroup in group_items_transmitter:
            todo_group = []
            # group_id is the id of the candidate transmitters
            group_id, field, t_instns = agroup
            t_instns = t_instns.split(",")
            if field == "" :
                continue
            todo_group = [group_id]
            for group_id in todo_group: 
                tar_dir = "group_{I}_IFT/dyn/bothfield".format(I=i_p_id)
                TFIELD="bothrs_"
                DEFINEOPTAINT="`define BORTHRS"
                if field == "rs1":
                    tar_dir = "group_{I}_IFT/dyn/rs1".format(I=i_p_id)
                    TFIELD="rs1_"
                    DEFINEOPTAINT="`define RS1"

                csvf ="{tdir}/{groupid}_{ID}.csv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
                if not os.path.exists(csvf):
                    assert(0)
                    continue

                #print("-> csv ", group_id, TFIELD, cnt)
                df = pd.read_csv(csvf, dtype=mydtypes)
                res, bnd, time = df_query(df, "DEP_I_%s" % (TFIELD + cnt))
                if res == "covered":
                    # group , but per field


                    # intra-group instn pair 
                    #print("-> covered", group_id, TFIELD, cnt)
                    outf ="{tdir}/out/{groupid}_{ID}_intragp.sv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
                    svfile = open(outf, "w") 
                    outstring = dynamic_template_header
                    rep_pairs = [ 
                        ("OP_TAINT", DEFINEOPTAINT), 
                        ("DECNODE", transform_disjunc(decision_src))
                        ]
                    for tt in rep_pairs:
                        outstring = outstring.replace(tt[0], tt[1])
                    svfile.write(outstring)

                    # iterate in every combination of transmitter and transponder in the group 
                    all_pairs = list(itertools.product(i_p_instns, t_instns))
                    #print(all_pairs)
                    for p in all_pairs:
                        i_p, i_t = p
                        i0_constraint = get_i_constraint(i_p, "i0")
                        i1_constraint = get_i_constraint(i_t, "i1")

                        rep_pairs = [ 
                            ("INSTN_CONSTRAINT", i0_constraint), 
                            ("I1_CONSTRAINT", i1_constraint),
                            ("FIELD",  (i_p + "_" + i_t)), 
                            ("DECNODE", transform_disjunc(decision_src)), #decision_src), 
                            ("FOLLOWERSET", followerset),
                            ("TT0", t0),
                        ]
                        outstring = decision_template    
                        for tt in rep_pairs:
                            outstring = outstring.replace(tt[0], tt[1])
                        svfile.write(outstring)
                    svfile.close()

    cmd = "python3 host_batch_run_template_v2.py --seq group_{groupid}_IFT/dyn/bothfield group_{groupid}_IFT/dyn/bothfield/out group_{groupid}_IFT/dyn/rs1 group_{groupid}_IFT/dyn/rs1/out".format(groupid=i_p_id)
    return cmd
