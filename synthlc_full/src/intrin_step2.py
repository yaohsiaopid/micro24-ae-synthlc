import os
from gconsts import *
from util import *
from IFT_template import *
from csv_util import *
# just entire group first
def intrin_step2_proc(
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
        TFIELD="bothrs_"
        DEFINEOPTAINT="`define BORTHRS"
        if field_i_p == "rs1":
            TFIELD="rs1_"
            DEFINEOPTAINT="`define RS1"

        # decision idx
        #outfilename="{tdir}/out/{ID}_g.sv".format(tdir=tar_dir, ID=cnt)
        #orgf ="{tdir}/out/{ID}_g.sv".format(tdir=tar_dir, ID=cnt)
        csvf ="{tdir}/{ID}_g.csv".format(tdir=tar_dir, ID=cnt)

        if not os.path.exists(csvf):
            assert(0)
        df = pd.read_csv(csvf, dtype=mydtypes)

        res, bnd, time = df_query(df, "DEP_%s" % (TFIELD + str(cnt)))
        if res == "covered":
            for i_p in i_p_instns:
                i0_constraint = get_i_constraint_indep(i_p, "i0")
                outfilename="{tdir}/out/{ID}_{i_p}.sv".format(tdir=tar_dir, ID=cnt, i_p=i_p)
        
                outstring = itself_template_prop 
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
