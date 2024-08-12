################################################################################
# From decisions/decision_op_dep_itself_per_field.py
# Check if a decision can depend on one each of its own operand
################################################################################
import pandas as pd
import math
import numpy as np
import sys
import os
sys.path.append("../../src_ift_utils")
from gconsts import *
from util import *
from IFT_template import *
from csv_utils import *

def get_dep(div_dec_nodes_raw, all_div_dec_nodes, rs1=None):
    # 
    assert(rs1 is not None)
    for k_, v_ in div_dec_nodes_raw.items():
        for tmp in v_:
            cnt = 0
            for t_ in v_:
                if t_ == tmp:
                    cnt += 1
            assert(cnt == 1)
        if len(v_) > 1:
            if rs1:
                all_div_dec_nodes[k_].iso_rs1dep = True 
            else:
                all_div_dec_nodes[k_].iso_rs2dep = True 
        if len(v_) == 1:
            if rs1:
                all_div_dec_nodes[k_].rs1_iso_taint_only_one = True
            else:
                all_div_dec_nodes[k_].rs2_iso_taint_only_one = True
        # differing non-isomorphic set
        noniso_update = []
        for aset in v_:
            aset_t = sorted([transform(pl) for pl in aset])
            if not aset_t in noniso_update:
                noniso_update.append(aset_t)
        #print("noniso_update ", noniso_update, v_)
        if len(noniso_update) > 1:
            if rs1:
                all_div_dec_nodes[k_].noniso_rs1dep = True
                #print("noniso_rs1_dep")
            else:
                all_div_dec_nodes[k_].noniso_rs2dep = True

    for k_, v_ in all_div_dec_nodes.items():
        assert(not (v_.rs1_iso_taint_only_one and v_.iso_rs1dep))
        if not rs1:
            assert(not (v_.rs2_iso_taint_only_one and v_.iso_rs2dep))
    return all_div_dec_nodes

arr = []

OPFIELD="../../src/opfields.txt"
instn_to_field = {}
with open(OPFIELD, "r") as f:
    for line in f:
        line = line[:-1]
        instn = line.split("|")[0]
        arr = line.split("|")[1]
        v = []
        if arr != "": #len(line.split("|")) > 1:
            v = line.split("|")[1].split(",")
        instn_to_field[instn] = v
instn = None

def gen(instn):

    ffname = "../xSummarize/follower_set_v2.txt"

    if not os.path.exists(ffname):
        assert(0)

    iii = ""
    with open("../idef.sv", "r") as idef:
        for line in idef:
            iii += line
    
    ##################################################################################
    ## Each file should be a decision only
    # IUV itself
    # both op 
    tar_dir = "bothfield" #
    print('->', instn_to_field[instn])
    if len(instn_to_field[instn]) < 2:
        return

    rs1_dir = "rs1/out"
    rs2_dir = "rs2/out"
    prep_dir("rs1/out")
    prep_dir("rs2/out")
    
    i_itself_obj = I_ITSELF(instn, tar_dir)
    csv_list = i_itself_obj.check_results()

    cnt = 0
    togen = []
    unique_pl = set()
    decision_map = {} # unique pl after ddn
    for tup in csv_list:
        csvff, itm, ddn, afset = tup
        if not ddn in decision_map:
            decision_map[ddn] = set()

        for pl in afset:
            if pl != "":
                decision_map[ddn].add(pl)
        df = pd.read_csv(csvff, dtype=mydtypes)
        res, bnd, time = df_query(df, "DEP_bothrs_") #%s" % itm)
        #stat_inst.add(res, bnd, time)  
        if res == "covered":
            cnt += 1
            togen.append((itm, ddn, afset))
            for pl in afset:
                unique_pl.add(pl)
    #print(cnt, len(csv_list))
    # ufsm checks...
    ufsm_cover = "{I}_IFT_3/itself/ufsm/opdep.txt".format(I=instn)
    ufsm_arr_valid = False
    def in_ufsm_arr(pl):
        if not ufsm_arr_valid:
            return -1
        for itm in ufsm_map:
            if itm[0] in pl:
                return itm[1]
                #return True
        #return False
    per_field_task = []
    per_field_done = []
    for itm in togen:
        cnt, ddn, afset = itm
        print(afset)
        src_f = "{t}/out/{cnt}.sv".format(t=tar_dir, cnt=cnt)
        # unless afset have at least one ufsm that can be tainted by both rs
        # then we need to check individually
        #req = False
        depg = set()
        if afset[0] == "" or len(afset) == 0:
            for pl in decision_map[ddn]:
                depg.add(in_ufsm_arr(pl))
        else:
            for pl in afset:
                depg.add(in_ufsm_arr(pl))
        if -1 in depg or 3 in depg or (1 in depg and 2 in depg):
            tar_f = "{t}/{cnt}.sv".format(t=rs1_dir, cnt=cnt)
            os.system("sed 's/BORTHRS/RS1/g' %s > %s" % (src_f, tar_f))

            tar_f = "{t}/{cnt}.sv".format(t=rs2_dir, cnt=cnt)
            os.system("sed 's/BORTHRS/RS2/g' %s > %s" % (src_f, tar_f))
            per_field_task.append(cnt)
        else:
            per_field_done.append((cnt, depg))
    with open("./per_field_task.txt".format(t=tar_dir), "w") as f:
        for itm in per_field_task:
            f.write("%s\n" % itm)
    with open("./per_field_done.txt".format(t=tar_dir), "w") as f:
        for itm in per_field_done:
            f.write("%s,%s\n" % (itm[0], ",".join([str(r) for r in list(itm[1])])))

def pp(instn):
    ffname = "../xSummarize/follower_set_v2.txt"
    outf = open("./intrinsic_result.txt", "w")
    if not os.path.exists(ffname):
        assert(0)

    ##################################################################################
    ## Each file should be a decision only
    # IUV itself
    # both op 
    tar_dir = "bothfield" #
    twofield=True
    TFIELD="bothrs"
    print('->', instn_to_field[instn])
    if len(instn_to_field[instn]) == 1:
        tar_dir = "rs1"
        TFIELD="rs1"
        twofield=False
    elif len(instn_to_field[instn]) == 0:
        twofield=False
        div_node_decision, div_node_all_uniq_pl = get_decision_dic(ffname)
        for decision_node, follower_sets in div_node_decision.items():
            if len(follower_sets) == 1:
                continue
            print("<=E=>{I},{n},-1,-1,-1,-1,-1,-1".format(I=instn, n=decision_node))
            print("<=E=>{I},{n},-1,-1,-1,-1,-1,-1".format(I=instn, n=decision_node), file=outf)
        return


    rs1_dir = "rs1/out"
    rs2_dir = "rs2/out"
    
    i_itself_obj = I_ITSELF(instn, tar_dir)
    csv_list_w_dec = i_itself_obj.check_results()

    todo_per_field = []
    all_div_dec_nodes = {}
    all_div_dec_nodes_cnt = {}

    # divergent decision node with at least one tainted result 
    div_dec_nodes_raw = {}
    for tup in csv_list_w_dec:
        csvff, itm, decn, fset = tup
        if not decn in all_div_dec_nodes:
            all_div_dec_nodes[decn] = DivDecNode()
            all_div_dec_nodes[decn].rs1false()
        df = pd.read_csv(csvff, dtype=mydtypes)
        res, bnd, time = df_query(df, "DEP_%s_%s" % (TFIELD, itm))

        if res == "covered":
            print("COVER", csvff, itm, decn, fset)
            if not decn in div_dec_nodes_raw:
                div_dec_nodes_raw[decn] = []        
            div_dec_nodes_raw[decn].append(fset)

        if res == "covered" and twofield:
            todo_per_field.append(tup)
        res, bnd, time = df_query(df, "DECSANITY")
        if res != "covered":
            print("decision not covered ", decn, fset)
        else:
            #if not decn in all_div_dec_nodes_cnt:
            #    all_div_dec_nodes_cnt[decn] = 0
            #all_div_dec_nodes_cnt[decn] += 1
            all_div_dec_nodes[decn].addcnt(fset)
    
    if not twofield:
        # all decisions that is tainted
        all_div_dec_nodes = get_dep(div_dec_nodes_raw, 
            all_div_dec_nodes,
            rs1=True)
    else:
        print("-->")
        per_field_done = {}
        perfieldfile = "./per_field_done.txt".format(t=tar_dir)
        if os.path.exists(perfieldfile):
            with open(perfieldfile, "r") as f:
                for line in f:
                    tmparr = line[:-1].split(",")
                    # cnt -> opdep possibility
                    per_field_done[tmparr[0]] = tmparr[1:]

        rs1_dir = "./rs1"
        rs2_dir = "./rs2"
        #"{I}_IFT/itself/rs2".format(I=instn)

        rs1_raw = {}
        rs2_raw = {}
        perfieldtodo = False
        for n in all_div_dec_nodes.keys():
            all_div_dec_nodes[n].rs2false()

        # all decisions tainted udner BOTHRS checks
        for todo_p in todo_per_field:
            csvff, itm, decn, fset = todo_p
            todoarr = [True, True]
            if itm in per_field_done:
                print("HERE DEBUG", instn)
                v = per_field_done[itm]
                if len(v) == 1:
                    if v[0] == "2":
                        # rs1 dependent only
                        todoarr = [False, False]
                        if not decn in rs1_raw:
                            rs1_raw[decn] = []
                        rs1_raw[decn].append(fset)
                    elif v[1] == "1":
                        # rs2 dependent only
                        todoarr = [False, False]
                        if not decn in rs2_raw:
                            rs2_raw[decn] = []
                        rs2_raw[decn].append(fset)
                    # othrwise we need to see both
            if todoarr[0]: #(rs12_exist[0] and itm in rs12_task[0]) or (not rs12_exist[0]):
                tar_f = "{t}/{cnt}.csv".format(t=rs1_dir, cnt=itm)
                if os.path.exists(tar_f):
                    df = pd.read_csv(tar_f, dtype=mydtypes)
                    res, bnd, time = df_query(df, "DEP_bothrs_%s" % itm)
                    #stat_inst.add(res, bnd, time)  
                    if res == "covered":
                        if not decn in rs1_raw:
                            rs1_raw[decn] = []
                        rs1_raw[decn].append(fset)
                else:
                    print("FAIL CANNOT FIND %s" % tar_f)
                    assert(os.path.exists("{t}/out/{cnt}.sv".format(t=rs1_dir, cnt=itm)))
                    perfieldtodo = True

            if todoarr[1]: #(rs12_exist[1] and itm in rs12_task[1]) or (not rs12_exist[1]):
                tar_f = "{t}/{cnt}.csv".format(t=rs2_dir, cnt=itm)
                if os.path.exists(tar_f):
                    df = pd.read_csv(tar_f, dtype=mydtypes)
                    res, bnd, time = df_query(df, "DEP_bothrs_%s" % itm)
                    #stat_inst.add(res, bnd, time)  
                    if res == "covered":
                        if not decn in rs2_raw:
                            rs2_raw[decn] = []
                        rs2_raw[decn].append(fset)
                else:
                    print("CANNOT FIND %s" % tar_f)
                    assert(os.path.exists("{t}/out/{cnt}.sv".format(t=rs2_dir, cnt=itm)))

                    perfieldtodo = True
          
        all_div_dec_nodes = get_dep(rs1_raw, 
            all_div_dec_nodes,
            rs1=True)
        all_div_dec_nodes = get_dep(rs2_raw, 
            all_div_dec_nodes,
            rs1=False)
    for k, v in all_div_dec_nodes.items():
        if all_div_dec_nodes[k].cnt < 2:
            print("[DEBUG] ", instn, k) #all_div_dec_nodes_cnt[k])
            continue
        print("<=E=>{I},{n},{res}".format(I=instn, n=k, res=v.str()))
        print("<=E=>{I},{n},{res}".format(I=instn, n=k, res=v.str()), file=outf)
    with open("./dec_map_pp.txt", "w") as f:
        for k, v in all_div_dec_nodes.items():
            if v.cnt < 2:
                continue
            for afset in sorted(v.follower_sets):
                f.write("%s|%s\n" % (k, ",".join(sorted(afset))))
    outf.close()
opt = sys.argv[1]
if sys.argv[2] == "":
    print("pass instn name")
    sys.exit(0)
if opt == "gen":
    gen(sys.argv[2])
elif opt == "pp":
    pp(sys.argv[2])
        
