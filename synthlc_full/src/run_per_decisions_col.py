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
from intrin_step1 import *
from intrin_step2 import *
from intrin_step3 import *
from intrin_pp import *
from dyn_step1 import *
from dyn_step2 import *
from dyn_step3 import *
from post_proc_all import *
from plot import *
NDECISION=2
TEST = False

for itm in sys.argv[1:]:
    if itm == "--test":
        TEST= True
    if itm == "--all":
        NDECISION=1000
# * `batch_transponder_2.txt`: group_<idx>.sv include instructions tagged in the
#   file, each group batch instructions with same set of decisions
# * `group_map.txt`: batch instructions into group of candidate transmitters.
#   This is primarily for optimization purpose. 
# ADD, BEQ, DIV/REM, LW, SW
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
#todolist = ["9"]
todolist = [] #"11"]
i_mapping = {"ADD": "3", "BEQ": "9", "DIV": "11", "Load": "18", "Store": "7"}
nm = None
for itm in sys.argv[1:]:
    if "--g" in itm:
        todolist=[itm.split("=")[1]]
    if "--i" in itm:
        instn=itm.split("=")[1]
        if (instn in i_mapping):
            todolist = [i_mapping[instn]]
            nm = instn
        else:
            sys.exit(0)
    if "--num" in itm:
        cnt=int(itm.split("=")[1])
        NDECISION=cnt


#print(todolist)
#sys.exit(0)

result_map = {} # (i_p_id, decision_src) to  ret_arr
for batch_itm in batch_transponder:
    i_p_id , field, t_instns = batch_itm 
    if nm is None:
        nm = t_instns[0]
    if todolist is not None and not i_p_id in todolist:
        continue
    t_instns = t_instns.split(",")
    print(40*"-=")
    print("* transponder group: ", t_instns)
    
    # decisions in the group are the same
    instn= t_instns[0]


    i0_constraint = ""
    with open("%s/group_%s.sv" % (BATCH_INSTNDIR, i_p_id), "r") as idef: 
        for line in idef:
            i0_constraint += line 

    dec_map_pp_f = "./decisions_per_group/group_{i_p_id}_IFT_2_iso_map.txt".format(i_p_id = i_p_id)
    #if dec_map_pp_f is not None: 
    #    div_node_decision_iso, div_node_all_uniq_pl_iso = get_decision_dic_pp_file(dec_map_pp_f)
    #print(dec_map_pp_f)
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
    #print(div_node_decision_iso)
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
    print("* decision source lists:", decision_src_ordered_list)
    doing = 0
    tmp_cntr = 0
    for dnd_idx, decision_src in enumerate(decision_src_ordered_list):
        cnt_follower_sets = div_node_decision_iso[decision_src] 

        if (tmp_cntr >= NDECISION):
            tmp_cntr += 1
            continue
        else:
            tmp_cntr += 1

        print(40*"-=")
        print("* decision source: ", decision_src)
        print(" working ...")

        #if not TEST and decision_src in decision_src_done:
        #    continue
        #if doing:
        #    break
        #doing = 1
        if (i_p_id, decision_src) in result_map:
            ret_arr = result_map[(i_p_id, decision_src)]
            ret_arr[0] -= 1
            plot_table(ret_arr, i_p_id, nm)# t_instns[0])
            continue 

        # intrinsic, entire group 
        cmd = intrin_step1_proc(field, BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, 
            div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)
        print(cmd)
        if (not TEST) and (not decision_src in decision_src_done):
            subprocess.call(cmd, shell=True) 

        # intrinsic per instruction in the group for covered
        cmd = intrin_step2_proc(t_instns, field, BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, 
            div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)
        print(cmd)
        if (not TEST) and (not decision_src in decision_src_done):
            subprocess.call(cmd, shell=True) 

        # intrinsic per instruction that are covered and has two field, we then iterate per field
        cmd = intrin_step3_proc(t_instns, field, BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, 
            div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)
        print(cmd)
        if (not TEST) and (not decision_src in decision_src_done):
            subprocess.call(cmd, shell=True) 

        intrin_res = intrin_pp(t_instns, field, BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, 
            div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)

        print("===> ", intrin_res, decision_src, t_instns)

        # dynamic step 1: bothfield, rs1 for each group of candidate transmiter 
        cmd = dyn_step1_proc( BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, 
            div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)
        print(cmd)
        if (not TEST) and (not decision_src in decision_src_done):
            subprocess.call(cmd, shell=True) 
        
        # dyanmic step 2: per instn (ip, it) pair in the group for covered cases
        #cmd = dyn_step2_proc 
        cmd = dyn_step2_proc(t_instns, BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, 
            div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)
        print(cmd)
        if (not TEST) and (not decision_src in decision_src_done):
            subprocess.call(cmd, shell=True) 


        # dynamic step 3: per field
        cmd = dyn_step3_proc(t_instns, BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)
        print(cmd)

        if (not TEST) and (not decision_src in decision_src_done):
            subprocess.call(cmd, shell=True) 

        #with open("%s/done.txt" % group_folder, "a") as logf:
        #    logf.write(decision_src + "\n")

        ## produe the column
        ret_arr = post_proc_all(intrin_res, field, t_instns, BATCH_INSTNDIR, i_p_id, i0_constraint, decision_src, 
            div_node_all_uniq_pl_iso, cnt_follower_sets, group_items_transmitter)
        result_map[(i_p_id, decision_src)] = ret_arr
        plot_table(ret_arr, i_p_id, nm) #t_instns[0])
            

