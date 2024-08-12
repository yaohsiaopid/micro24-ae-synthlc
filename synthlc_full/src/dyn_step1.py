import os
from gconsts import *
from util import *
from IFT_template import *
def dyn_step1_proc(
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

                outfilename="{tdir}/out/{groupid}_{ID}.sv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
                #if os.path.exists(outfilename):
                #    continue

                i1_constraint = ""
                with open("%s/group_%s.sv" % (BATCH_INSTNDIR, group_id), "r") as idef: 
                    for line in idef:
                        i1_constraint += (line.replace("i0", "i1"))

                prep_dir("{tardir}/out".format(tardir=tar_dir))

                outstring = dynamic_template 
                rep_pairs = [ 
                    ("OP_TAINT", DEFINEOPTAINT), 
                    ("INSTN_CONSTRAINT", i0_constraint), #iii),
                    ("I1_CONSTRAINT", i1_constraint),
                    ("DECNODE", transform_disjunc(decision_src)), #decision_src), 
                    ("FOLLOWERSET", followerset),
                    ("FIELD",  TFIELD + str(cnt)),
                    ("TT0", t0),
                    ]
                for tt in rep_pairs:
                    outstring = outstring.replace(tt[0], tt[1])
                outfilename="{tdir}/out/{groupid}_{ID}.sv".format(tdir=tar_dir, groupid=group_id, ID=cnt)
                #if os.path.exists(outfilename):
                #    continue
                with open(outfilename, "w") as outf:
                    outf.write(outstring)
    cmd = "python3 host_batch_run_template_v2.py group_{groupid}_IFT/dyn/bothfield group_{groupid}_IFT/dyn/bothfield/out group_{groupid}_IFT/dyn/rs1 group_{groupid}_IFT/dyn/rs1/out".format(groupid=i_p_id)
    return cmd
