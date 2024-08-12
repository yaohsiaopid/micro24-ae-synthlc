################################################################################
# For dynamic cases older and younger 
################################################################################
  
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib
import pandas as pd
import math
import numpy as np
import sys

import os
sys.path.append("../../src_ift_utils")
from gconsts import *
from util import *
from IFT_template import *

arr = []
BATCH_INSTNDIR="../../src/opcodes_batch"
group_items = []
# ISA subset
#group_map_ff = "%s/group_map.txt" % BATCH_INSTNDIR)
group_map_ff = "%s/group_map_subset.txt" % BATCH_INSTNDIR
try:
    with open(group_map_ff, "r") as f:
        for line in f:
            arr = line[:-1].split("|")
            assert(len(arr) == 3)
            group_items.append(arr)
    print("group items:", group_items)
except FileNotFoundError:
    sys.exit(0)
batch_transponder = []
batch_transponder_group_id = []
if os.path.exists(BATCH_INSTNDIR + "/batch_transponder_2.txt"):
    with open(BATCH_INSTNDIR + "/batch_transponder_2.txt", "r") as f:
        for line in f:
            arr = line[:-1].split("|")
            batch_transponder.append(arr)
            #batch_transponder.append(int(line[:-1]))
            batch_transponder_group_id.append(arr[0])


def gen():
    # current instruction is transponder

    # decisions in the group are the same
    i0_constraint = ""
    with open("../idef.sv", "r") as idef:
        for line in idef:
            i0_constraint += line

    dec_map_pp_f = "../xDecisionsIntrinsic/dec_map_pp.txt"
    div_node_decision_iso, div_node_all_uniq_pl_iso = get_decision_dic_pp_file(dec_map_pp_f)

    print(" div map ", div_node_decision_iso)
    print(" div node all uniq pl ", div_node_all_uniq_pl_iso)

    # for each group of transmitters (will iterate over them if they indeed can taint)
    for agroup in group_items:
        group_id, field, t_instns = agroup
        if field == "" :
            continue
        tar_dir = "bothfield" # those candidate transmitter with two operands
        TFIELD="bothrs_"
        DEFINEOPTAINT="`define BORTHRS"
        if field == "rs1":
            tar_dir = "rs1"
            TFIELD="rs1_"
            DEFINEOPTAINT="`define RS1"
        
        i1_constraint = ""
        with open("%s/group_subset_%s.sv" % (BATCH_INSTNDIR, group_id), "r") as idef: 
            for line in idef:
                i1_constraint += (line.replace("i0", "i1"))

        prep_dir("{tardir}/out".format(tardir=tar_dir))

        ### Each file should be a decision only
        #decision_log = open("{tdir}/dec_g_maps.txt".format(tdir=tar_dir), "w")
        decision_log = open("./dec_g_maps.txt", "w")
        cnt = 0
        for decision_node, follower_sets in div_node_decision_iso.items():
            if len(follower_sets) == 1:
                continue
            uniq_pl_in_all_pl_set = sorted(div_node_all_uniq_pl_iso[decision_node])
            for afset in follower_sets:
                #if len(afset) == 0:
                #    # 17 and 7
                #    print("%d|%s|%s" % (cnt, decision_node, ",".join(afset)),
                #            file=decision_log)
                #    cnt += 1
                #    continue
                afset = sorted(afset)
                followerset = "("
                if not decision_node in afset:
                    followerset += "!{node} && ".format(node=transform_disjunc(decision_node))
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
                        #t0 += (transform_iso_t0(eachN) + " ,") # + "_t0 ,")
                        t0 += (transform_iso_t0_neg(eachN, decision_node) + " ,")
                    t0 += "1'b0}"

                else:
                    t0 = "|{"
                    for eachN in afset:
                        t0 += (transform_iso_t0(eachN) + " ,") # + "_t0 ,")
                    t0 += "1'b0}"
                print("%d|%s|%s" % (cnt, decision_node, ",".join(afset)),
                        file=decision_log)
                outstring = dynamic_template 
                rep_pairs = [ 
                    ("OP_TAINT", DEFINEOPTAINT), 
                    ("INSTN_CONSTRAINT", i0_constraint), #iii),
                    ("I1_CONSTRAINT", i1_constraint),
                    ("DECNODE", transform_disjunc(decision_node)), #decision_node), 
                    ("FOLLOWERSET", followerset),
                    ("FIELD",  TFIELD + str(cnt)),
                    ("TT0", t0),
                    ]
                for tt in rep_pairs:
                    outstring = outstring.replace(tt[0], tt[1])
                with open("{tdir}/out/{groupid}_{ID}.sv".format(tdir=tar_dir,
                    groupid=group_id, ID=cnt),
                        "w") as outf:
                    outf.write(outstring)

                outstring = yngr_template_header
                for tt in rep_pairs:
                    outstring = outstring.replace(tt[0], tt[1])
                with open("{tdir}/out/{groupid}_{ID}_yngr.sv".format(tdir=tar_dir,
                    groupid=group_id, ID=cnt),
                        "w") as outf:
                    outf.write(outstring)

                cnt += 1
        decision_log.close()

opt = sys.argv[1]
#if sys.argv[2] == "":
#    print("pass instn name")
#    sys.exit(0)
if opt == "gen":
    gen()
elif opt == "pp":
    pp()
        
