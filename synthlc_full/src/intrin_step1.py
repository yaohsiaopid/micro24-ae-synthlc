import os
from gconsts import *
from util import *
from IFT_template import *
# just entire group first
def intrin_step1_proc(
    field_i_p,
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

        tar_dir = "group_{I}_IFT/itself".format(I=i_p_id)
        prep_dir("{tardir}/out".format(tardir=tar_dir))
        TFIELD="bothrs_"
        DEFINEOPTAINT="`define BORTHRS"
        if field_i_p == "rs1":
            TFIELD="rs1_"
            DEFINEOPTAINT="`define RS1"

        # decision idx
        outfilename="{tdir}/out/{ID}_g.sv".format(tdir=tar_dir, ID=cnt)
        outstring = itself_template_prop #itself_template
        rep_pairs = [ 
            ("OP_TAINT", DEFINEOPTAINT), 
            #("OP_TAINT", "`define RS1"), 
            ("INSTN_CONSTRAINT", i0_constraint),
            # ("DECNODE", decision_src), 
            ("DECNODE", transform_disjunc(decision_src)),
            ("FOLLOWERSET", followerset),
            ("FIELD",  TFIELD + str(cnt)),
            ("TT0", t0),
            ]
        for tt in rep_pairs:
            outstring = outstring.replace(tt[0], tt[1])
        with open(outfilename, "w") as f:
            f.write(outstring)

    cmd = "python3 host_batch_run_template_v2.py group_{groupid}_IFT/itself group_{groupid}_IFT/itself/out".format(groupid=i_p_id)
    return cmd
