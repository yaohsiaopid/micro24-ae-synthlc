sys.exit(1)
################################################################################
# For dynamic cases with groups
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
import subprocess

import os
from gconsts import *
from util import *
from IFT_template import *

# * `batch_transponder_2.txt`: group_<idx>.sv include instructions tagged in the
#   file, each group batch instructions with same set of decisions
# * `group_map.txt`: batch instructions into group of candidate transmitters.
#   This is primarily for optimization purpose. 

# group_id as input 3, 9, 11, 18, 7

BATCH_INSTNDIR="./opcodes_batch"
group_items_transmitter  = []
if not os.path.exists("%s/group_map.txt" % BATCH_INSTNDIR):
    sys.exit("error: can't find group_map.txt")
with open("%s/group_map.txt" % BATCH_INSTNDIR, "r") as f:
    for line in f:
        arr = line[:-1].split("|")
        assert(len(arr) == 3)
        group_items_transmitter.append(arr)

batch_transponder = []
batch_transponder_group_id = []

if os.path.exists(BATCH_INSTNDIR + "/batch_transponder_2.txt"):
    with open(BATCH_INSTNDIR + "/batch_transponder_2.txt", "r") as f:
        for line in f:
            arr = line[:-1].split("|")
            batch_transponder.append(arr)
            batch_transponder_group_id.append(arr[0])
# map of transponder instruction to set of candidate transmitters
#if len(sys.argv) < 2:
#    sys.exit(0)
#todolist = [sys.argv[2]]
#todolist = ["3"] #, "9", "11", "18", "7"]
todolist = [str(i) for i in range(19)]
todolist = ["3"]

for batch_itm in batch_transponder:
    i_p_id , field, t_instns = batch_itm 
    if todolist is not None and not i_p_id in todolist:
        continue
    t_instns = t_instns.split(",")
    print(t_instns)
    
    # decisions in the group are the same
    instn= t_instns[0]


    i0_constraint = ""
    with open("%s/group_%s.sv" % (BATCH_INSTNDIR, i_p_id), "r") as idef: 
        for line in idef:
            i0_constraint += line 

    dec_map_pp_f = "./decisions_per_group/group_{i_p_id}_IFT_2_iso_map.txt".format(i_p_id = i_p_id)
    #if dec_map_pp_f is not None: 
    #    div_node_decision_iso, div_node_all_uniq_pl_iso = get_decision_dic_pp_file(dec_map_pp_f)
    print(dec_map_pp_f)
    decision_log = open(dec_map_pp_f, "r")
    div_node_decision_iso = {} #tmp_decision_map = {}
    div_node_all_uniq_pl_iso = {}
    div_node_all_uniq_pl_iso_r = {}
    for line in decision_log:
        line = line[:-1]
        cnt, decision_src, afset = line.split("|")
        if afset == "":
            afset = []
        else:
            afset = afset.split(",")
        if not decision_src in div_node_decision_iso:
            div_node_decision_iso[decision_src] = []
            div_node_all_uniq_pl_iso_r[decision_src] = set()
        div_node_decision_iso[decision_src].append((cnt, afset))
        for itm in afset:
            div_node_all_uniq_pl_iso_r[decision_src].add(itm)
    for k, v in div_node_all_uniq_pl_iso_r.items():
        div_node_all_uniq_pl_iso[k] = sorted(v)
    print(div_node_decision_iso)
    #print(" ===> working on ", instn, file = outlog)
    #print(" div map ", div_node_decision_iso)
    #print(" div node all uniq pl ", div_node_all_uniq_pl_iso)

    #print("working on ", i_p_id, t_instns)
    #continue
    group_folder = "group_{I}_IFT".format(I=i_p_id)
    decision_src_done = []
    try: 
        done_decisions_ff = open("%s/done.txt" % group_folder, "r")
        for line in done_decisions_ff:
            decision_src_done.append(line[:-1])
    except Exception as e:
        decision_src_done = []

    decision_src_ordered_list = []
    with open("%s/batch_transponder_src_list.txt" % BATCH_INSTNDIR, "r") as f:
        for line in f:
            tmparr = line[:-1].split("|")
            group_id_t, dec_src_lists = tmparr[0], tmparr[1]
            if group_id_t == i_p_id:
                decision_src_ordered_list = [itm for itm in dec_src_lists.split(";") if itm != ""]
                break
                
    # Each file should be a decision only
    # transponder's decisions
    #for decision_src, cnt_follower_sets in div_node_decision_iso.items():
    print("--->", decision_src_ordered_list)
    doing = 0
    for dnd_idx, decision_src in enumerate(decision_src_ordered_list):
        cnt_follower_sets = div_node_decision_iso[decision_src] 
        if decision_src in decision_src_done:
            continue
        if doing:
            break
        doing = 1
        print(decision_src, "working!")

        if len(cnt_follower_sets) == 1:
            assert(0)
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
                    #t0 += (transform_iso_t0(eachN) + " ,") # + "_t0 ,")
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
                    if os.path.exists(outfilename):
                        continue

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
                    if os.path.exists(outfilename):
                        continue
                    with open(outfilename, "w") as outf:
                        outf.write(outstring)
        cmd = "python3 host_batch_run_template_v2.py group_{groupid}_IFT/dyn/bothfield group_{groupid}_IFT/dyn/bothfield/out group_{groupid}_IFT/dyn/rs1 group_{groupid}_IFT/dyn/rs1/out".format(groupid=i_p_id)
        #log_f = open("run_group_{groupid}.log".format(groupid=i_p_id), "a")
        subprocess.call(cmd, shell=True) #, stdout=log_f)
        #log_f.close()

        # itself

        # Next: per field
        # Intra group
        # younger 
        # 
