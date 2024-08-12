################################################################################
# Collect result for dynamic cases evaluated first using groups and those
# covered group to per instruction combination
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

import re
import os
sys.path.append("../../src_ift_utils")
from gconsts import *
from util import *
from IFT_template import *
from csv_utils import *

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
    #print("group items:", group_items)
except FileNotFoundError:
    sys.exit(0)

def gen():
    # current instruction is transponder

    # decisions in the group are the same

    dec_map_pp_f = "../xDecisionsIntrinsic/dec_map_pp.txt"
    div_node_decision_iso, div_node_all_uniq_pl_iso = get_decision_dic_pp_file(dec_map_pp_f)

    # for each group of transmitters (will iterate over them if they indeed can taint), collect
    # bothfield results, and instantiate per field check
    #
    todo = {}
    for agroup in group_items:

        group_id, field, t_instns = agroup
        if field == "":
            continue

        tar_dir = "bothfield" # those candidate transmitter with two operands
        TFIELD="bothrs_"
        DEFINEOPTAINT="`define BORTHRS"
        if field == "rs1":
            tar_dir = "rs1"
            TFIELD="rs1_"
            DEFINEOPTAINT="`define RS1"

        # candidate transmitter : instruction in group_id /t_instns

        ### Each file should be a decision only
        dec_log_f = "dec_g_maps.txt"
        if not os.path.exists(dec_log_f):
            print("FAIL %s not found" % dec_log_f)
            continue
        decision_log = open(dec_log_f, "r")
        tmp_decision_map = {}
        for line in decision_log:
            line = line[:-1]
            cnt, decision_node, afset = line.split("|")
            if afset == "":
                afset = []
            else:
                afset = afset.split(",")
            if not decision_node in tmp_decision_map:
                tmp_decision_map[decision_node] = []
            tmp_decision_map[decision_node].append((cnt, afset))
        for k, v in tmp_decision_map.items():
            if len(v) == 1:
                continue
            decision_node = k
            for tup in v:
                cnt, afset = tup
                csvf = "{tdir}/{groupid}_{cnt}.csv".format(tdir=tar_dir, cnt=cnt, groupid=group_id)
                if not os.path.exists(csvf):
                    print("FAIL %s not found" % csvf)
                    return 
            
                df = pd.read_csv(csvf, dtype=mydtypes)
                res, bnd, time = df_query(df, "DEP_I_%s" % (TFIELD + cnt))
                if res == "covered":
                    k=(cnt, TFIELD)
                    if not TFIELD == "bothrs_":
                        continue
                    #if not k in todo:
                    #    todo[k] = []
                    #else:
                    #    assert(todo[k][0][1] == decision_node and todo[k][0][2] == afset)
                    #todo[k].append((group_id, decision_node, afset))
                    #print("covered! ", k, group_id, decision_node, afset)
                    #inst_t = group_map_ff[group_id]
                    #for i_t in inst_t:
                    orgf = "bothfield/out/{groupid}_{cnt}.sv".format(groupid=group_id, cnt = cnt)
                    h_ = ""
                    with open(orgf, "r") as f:
                        for ll in f:
                            h_ += ll

                    prep_dir("bothfield_perfield/out")

                    rs1_f = "./bothfield_perfield/out/{groupid}_{cnt}_1.sv".format(cnt = cnt, groupid = group_id)
                    with open(rs1_f, "w") as rs1_f_hdlr:
                        rs1_f_hdlr.write(h_.replace("BORTHRS", "RS1"))

                    rs2_f = "./bothfield_perfield/out/{groupid}_{cnt}_2.sv".format(cnt = cnt, groupid = group_id )
                    with open(rs2_f, "w") as rs2_f_hdlr:
                        rs2_f_hdlr.write(h_.replace("BORTHRS", "RS2"))


def pp(cur_inst):
    # current instruction is transponder

    # decisions in the group are the same

    dec_map_pp_f = "../xDecisionsIntrinsic/dec_map_pp.txt"
    div_node_decision_iso, div_node_all_uniq_pl_iso = get_decision_dic_pp_file(dec_map_pp_f)

    # for each group of transmitters (will iterate over them if they indeed can taint), collect
    # bothfield results, and instantiate per field check

    # decision source -> input operands (I1, op1), (I2, op2) ... 
    dyn_result = {} 
    for agroup in group_items:

        group_id, field, t_instns = agroup
        if field == "":
            continue

        tar_dir = "bothfield" # those candidate transmitter with two operands
        TFIELD="bothrs_"
        DEFINEOPTAINT="`define BORTHRS"
        if field == "rs1":
            tar_dir = "rs1"
            TFIELD="rs1_"
            DEFINEOPTAINT="`define RS1"

        # candidate transmitter : instruction in group_id /t_instns

        ### Each file should be a decision only
        dec_log_f = "dec_g_maps.txt"
        if not os.path.exists(dec_log_f):
            print("FAIL %s not found" % dec_log_f)
            continue
        decision_log = open(dec_log_f, "r")
        tmp_decision_map = {}
        for line in decision_log:
            line = line[:-1]
            cnt, decision_node, afset = line.split("|")
            if afset == "":
                afset = []
            else:
                afset = afset.split(",")
            if not decision_node in tmp_decision_map:
                tmp_decision_map[decision_node] = []
            tmp_decision_map[decision_node].append((cnt, afset))
            if not decision_node in dyn_result:
                dyn_result[decision_node] = []
                # list of (transmitter_group_id, decision_cnt, operands: rs1, rs2, rs1rs2)
        #print("-> tmp dieciosn_map", tmp_decision_map)

        for k, v in tmp_decision_map.items():
            if len(v) == 1:
                continue
            decision_node = k
            for tup in v:
                cnt, afset = tup
                csvf = "{tdir}/{groupid}_{cnt}.csv".format(tdir=tar_dir, cnt=cnt, groupid=group_id)
                if not os.path.exists(csvf):
                    print("FAIL %s not found" % csvf)
                    return 
            
                df = pd.read_csv(csvf, dtype=mydtypes)
                res, bnd, time = df_query(df, "DEP_I_%s" % (TFIELD + cnt))
                if res == "covered":
                    k=(cnt, TFIELD)
                    if not TFIELD == "bothrs_":
                        dyn_result[decision_node].append((group_id, cnt, "rs1"))
                        continue
                    #if not k in todo:
                    #    todo[k] = []
                    #else:
                    #    assert(todo[k][0][1] == decision_node and todo[k][0][2] == afset)
                    #todo[k].append((group_id, decision_node, afset))
                    #print("covered! ", k, group_id, decision_node, afset)
                    #inst_t = group_map_ff[group_id]
                    #for i_t in inst_t:

                    result = ""
                    rs1_f = "./bothfield_perfield/{groupid}_{cnt}_1.csv".format(cnt = cnt, groupid = group_id)
                    df = pd.read_csv(rs1_f, dtype=mydtypes)
                    res, bnd, time = df_query(df, "DEP_I_%s" % (TFIELD + cnt))
                    if res == "covered":
                        result += "rs1"

                    rs2_f = "./bothfield_perfield/{groupid}_{cnt}_2.csv".format(cnt = cnt, groupid = group_id )
                    df = pd.read_csv(rs2_f, dtype=mydtypes)
                    res, bnd, time = df_query(df, "DEP_I_%s" % (TFIELD + cnt))
                    if res == "covered":
                        result += "rs2"

                    dyn_result[decision_node].append((group_id, cnt, result))
    decision_log = open(dec_log_f, "r")
    tmp_decision_map = {}
    for line in decision_log:
        line = line[:-1]
        cnt, decision_node, afset = line.split("|")
        if afset == "":
            afset = []
        else:
            afset = afset.split(",")
        if not decision_node in tmp_decision_map:
            tmp_decision_map[decision_node] = []
        tmp_decision_map[decision_node].append((cnt, afset))

    transform_map = {}
    for k, v in tmp_decision_map.items():
        # k: decision source
        # v: decision id and the follower set
        transform_map[k] = [len(v)]
    intrinsic_map = {}
    with open("../xDecisionsIntrinsic/intrinsic_result.txt", "r") as f:
        for line in f:
            arr = line[:-1].split(",")
            dec_src = arr[1]
            rs1_dep = arr[4]
            rs2_dep = arr[5]
            intrinsic_map[transform(dec_src)] = rs1_dep + rs2_dep
    N=22
    print(" ", end="")            
    print(N * " ", end="")            
    for agroup in group_items:
        print("{:<8}".format(agroup[2]), end="")
    print()
    print(N * " ", end="")            
    for agroup in group_items:
        print((" N ") + ("  D  "), end = "")
    print()
    print("operand rs1/2".rjust(N, " "), end="")            
    for agroup in group_items:
        print((" 1 2") + (" 1 2"), end = "")
    print()
    
    for decision_src, decisions in tmp_decision_map.items():
        print(decision_src.ljust(N, " "), end="")
        print(" ", end="")            
        column = ""
        # for each group of transmitters
        for agroup in group_items:
            group_id, field, t_instns = agroup
            if field == "":
                continue

            # Intrinsic , rs1, rs2
            tmpres = ["0", "0"]
            if cur_inst in t_instns:
                # N op1
                if decision_src in intrinsic_map:
                    tmpres[0] = intrinsic_map[decision_src][0] 
                    tmpres[1] = intrinsic_map[decision_src][1] 
            column += " ".join(tmpres) + " "

            # consider the i_T as Dynamic 
            tmpres = ["0", "0"]
            # (group_id, cnt, result)
            arr = dyn_result[decision_node]
            rs1, rs2 = 0, 0
            for itm in arr:
                tid, cnt, rr = itm
                if tid == group_id and "rs1" in rr:
                    rs1+=1
                if tid == group_id and "rs2" in rr:
                    rs2+=1
            if rs1 >= 2:
                tmpres[0] = "1"
            if rs2 >= 2:
                tmpres[1] = "1"
            column += " ".join(tmpres) + " "

        print(column)
    #for k, v in dyn_result.items():
    #    print(k)
    #    print(" ==> ", v)                     
opt = sys.argv[1]
if opt == "gen":
    gen() 
elif opt == "pp":
    assert(sys.argv[2] != "")
    pp(sys.argv[2])
        

