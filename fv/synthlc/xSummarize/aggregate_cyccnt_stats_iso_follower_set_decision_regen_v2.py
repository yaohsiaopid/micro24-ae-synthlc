import re
import networkx as nx
from itertools import chain, combinations
import textwrap
import pandas as pd
import numpy as np
import os
import itertools
import pandas as pd
import sys
from MYGRAPH import *
sys.path.append("../../src")
from util import *
from HB_template import *
from DOT_template import *
from solver import *
HEADERFILE="../header.sv"
h_ = ""
with open(HEADERFILE, "r") as f:
    for line in f:
        h_ += line
isomorphic_sets = [
set(["lsq_enq_0_s1", "lsq_enq_1_s1"]), 
set(["scb_0_s12", "scb_1_s12", "scb_2_s12", "scb_3_s12"]), 
set(["scb_0_s13", "scb_1_s13", "scb_2_s13", "scb_3_s13"]),
set(["scb_0_s14", "scb_1_s14", "scb_2_s14", "scb_3_s14"]), 
set(["scb_0_s8", "scb_1_s8", "scb_2_s8", "scb_3_s8"]),
set(["stb_com_0_s1", "stb_com_1_s1"]),
set(["stb_spec_0_s1", "stb_spec_1_s1"]),
########## finals ######
set(["lsq_enq_0_s1___final", "lsq_enq_1_s1___final"]), 
set(["scb_0_s12___final", "scb_1_s12___final", "scb_2_s12___final", "scb_3_s12___final"]), 
set(["scb_0_s13___final", "scb_1_s13___final", "scb_2_s13___final", "scb_3_s13___final"]),
set(["scb_0_s14___final", "scb_1_s14___final", "scb_2_s14___final", "scb_3_s14___final"]), 
set(["scb_0_s8___final", "scb_1_s8___final", "scb_2_s8___final", "scb_3_s8___final"]),
set(["stb_com_0_s1___final", "stb_com_1_s1___final"]),
set(["stb_spec_0_s1___final", "stb_spec_1_s1___final"]),
]
pl_to_iso_set = {}
# check if one is in cv_perflocs then every other should be
#iterables = []
for idx, aset in enumerate(isomorphic_sets):
    sync = None 
    for itm in aset:
        pl_to_iso_set[itm] = idx
        #if sync is None:
        #    sync = (itm in cv_perflocs)
        #else:
        #    assert(sync == (itm in cv_perflocs))

def transform(itm):
    return itm
    if itm in pl_to_iso_set:
        iso = "iso_%d" % pl_to_iso_set[itm]
        return iso
    else:
        return itm
def transformset(aset):
    return aset
    ret = []
    for itm in aset:
        if itm in pl_to_iso_set:
            iso = "iso_%d" % pl_to_iso_set[itm]
            if not iso in ret:
                ret.append(iso)
            else:
                assert(0)
        else:
            ret.append(itm)
    return set(ret)

class GenComb:
    def __init__(self, arr):
        self.arr = arr
        self.res = []
        self.acc = []
        self.solver = SolverFor('QF_LIRA')
        self.variables = {}
    def gen(self):
        self.get_all_combination(0)
    def get_all_combination(self, idx):
        if idx == len(self.arr):
            self.res.append(self.acc[::])
            return
        # e weight 
        #for t in range(0, self.arr[idx]):
        #    self.acc.append(t)
        #    self.get_all_combination(idx+1)
        #    self.acc.pop()
        for t in range(0, len(self.arr[idx])):
            self.acc.append(self.arr[t])
            a, b = self.arr[t][0]
            if not a in self.variables:
                self.variables[a] = Int('%' % a)
            if not b in self.variables:
                self.variables[b] = Int('%' % b)
            self.solver.push()

            if self.arr[t][1] == '>':
                self.solver += (self.variables[a] < self.variables[b])
            if self.arr[t][1] == '<':
                self.solver += (self.variables[a] > self.variables[b])
            if self.arr[t][1] == '=':
                self.solver += (self.variables[a] == self.variables[b])

            r = self.solver.check()
            if r == sat:
                self.get_all_combination(idx+1)

            self.acc.pop()
            self.solver.pop()


# For cycle count per IUV or per PL set
is_interference_case = "III" in os.getcwd()

cv_perflocs = get_array("../xCoverAPerflocDiv/cover_individual.txt")
edge = get_array("../../xGenPerfLocDfgDiv/dfg_e.txt")
#edge = get_array("../../xGenPerfLocDfgDiv_versions/xGenPerfLocDfgDiv_v2_11/dfg_e.txt")

pl_signals = {}
with open("../../../xDUVPLs/perfloc_signals.txt", "r") as f:
    for line in f:
        pl, sigs = line[:-1].split(" : ")
        pl_signals[pl] = sigs.split(",")
iid_map = {}
for k, v in pl_signals.items():
    iid_map[k] = v[0]
#print("TODO: for pair of nodes after transitive reduction we shoudl check if \
#its possible to have two happen concurrently if not we should see if per PL set \
#is always one way or the other")

list_rows = [
    "id_stage_s1",
    "issue_s1",
    "issue_s2",
    "issue_s8",
    "issue_s16",
    "issue_s32",
    "lsq_enq_0_s1",
    "lsq_enq_1_s1",
    "serdiv_unit_divide_s1",
    "serdiv_unit_divide_s2",
    "stb_spec_0_s1",
    "stb_spec_1_s1",
    "load_unit_s1",
    "store_unit_s1",
    "store_unit_s3",
    "load_unit_buff_s1",
    "csr_buffer_s1",
    "mult_s1",
    "load_unit_op_s1",
    "load_unit_op_s2",
    "load_unit_op_s3",
    "scb_0_s12",
    "scb_0_s13",
    "scb_0_s14",
    "scb_0_s8",
    "scb_1_s12",
    "scb_1_s13",
    "scb_1_s14",
    "scb_1_s8",
    "scb_2_s12",
    "scb_2_s13",
    "scb_2_s14",
    "scb_2_s8",
    "scb_3_s12",
    "scb_3_s13",
    "scb_3_s14",
    "scb_3_s8",
    "stb_com_0_s1",
    "stb_com_1_s1",
    "mem_req_s1",
]

enter_concurrent_pairs = get_array("../xHBPerfG_dfg_v3_div/aws_concurrent.txt", exit_on_fail=False)
# print(type(enter_concurrent_pairs[0]))
whb_edge = get_array("../xHBPerfG_dfg_v3_div/whb_proven.txt", exit_on_fail=False)
hb_edge = get_array("../xHBPerfG_dfg_v3_div/hb_proven.txt", exit_on_fail=False)
print("HB edge:", hb_edge)
reachable_sets = get_array("../xPerfLocSubsetDiv/reachable_set.txt", arr_as_ele = True)

#if os.path.exists("../xPerfLocCycleCount_v2/max_cycle_per_pl.txt"):
#    max_cyc_per_pl_raw = get_array("../xPerfLocCycleCount_v2/max_cycle_per_pl.txt")
#    print("perfloc cycle v2")
#else:
max_cyc_per_pl_raw = get_array("../xPerfLocCycleCount/max_cycle_per_pl.txt")
#print("TBD")
    #if os.path.exists("../xPerfLocCycleCount/max_cycle_per_pl_covered.txt"):
    #    max_cyc_per_pl_raw = get_array("../xPerfLocCycleCount/max_cycle_per_pl_covered.txt")
    #    print("pl_covered.txt")
    #else:
    #    max_cyc_per_pl_raw = get_array("../xPerfLocCycleCount/max_cycle_per_pl.txt")
    #    print("pl.txt")

max_cyc_per_pl = {}
for itm in max_cyc_per_pl_raw:
    max_cyc_per_pl[itm[0]] = int(itm[1])
#if os.path.exists("../xPerfLocCycleCount_v2/max_cycle_per_pl.txt"):
#    cyc_cnt_gt1_per_set_raw = get_array("../xPerfLocCycleCount_v2/cycle_count_gt1_perset.txt")
#else:
cyc_cnt_gt1_per_set_raw = get_array("../xPerfLocCycleCount/cycle_count_gt1_perset.txt")

cyc_cnt_gt1_per_set = {}
for itm in cyc_cnt_gt1_per_set_raw:
    set_idx, pl, gt1 = itm
    set_idx = int(set_idx)
    if gt1 == "1":
        if cyc_cnt_gt1_per_set.get(set_idx) is None:
            cyc_cnt_gt1_per_set[set_idx] = []
        cyc_cnt_gt1_per_set[set_idx].append(pl)
#print(cyc_cnt_gt1_per_set)


leaving_hb_proven_res = get_array("../xHBPerfG_leaving/leaving_hb_proven.txt", exit_on_fail=False)
leaving_hb_proven_res_pairs = []
for itm in leaving_hb_proven_res:
    u = itm[1]
    if itm[0] == "1":
        u += "___final"
    v = itm[3]
    if itm[2] == "1":
        v += "___final"
    leaving_hb_proven_res_pairs.append((u, v))
print("leaving_hb_proven_res_pairs:", leaving_hb_proven_res_pairs)
aws_concur_leaving = get_array("../xHBPerfG_leaving/leaving_concur_proven.txt", exit_on_fail=False)
aws_concur_leaving_pairs = []
for itm in aws_concur_leaving:
    u = itm[1]
    if itm[0] == "1":
        u += "___final"
    v = itm[3]
    if itm[2] == "1":
        v += "___final"
    aws_concur_leaving_pairs.append((u, v))
whb_leaving_res = get_array("../xHBPerfG_leaving/leaving_whb_proven.txt", exit_on_fail=False)

undetermined_dfe = get_array("../xHBPerfG_dfg_v3_div/undetermined.txt") 
undetermined_whb = []
undetermined_hb = []
undetermined_concur = []
cnt = 0
for itm in undetermined_dfe:
    if "*" in itm:
        cnt += 1
        continue
    if cnt == 1:
        undetermined_hb.append((itm[0], itm[1]))
    if cnt == 2:
        undetermined_whb.append((itm[0], itm[1]))
    if cnt == 3:
        undetermined_concur.append((itm[0], itm[1]))
hb_cex_e = get_array("../xHBPerfG_dfg_v3_div/whb_todo.txt") 



intra_single_cyc = {}


node_rows = {}
label_s = ""
row = 0
for _, v in enumerate(list_rows):
    node_rows[v] = row
    label_s += label.format(nm=v,loc=row)
    row += 1
    if v in max_cyc_per_pl and max_cyc_per_pl[v] > 1:
    #if v in over1cyc_pl:
        label_s += label.format(nm = v + "___final", loc=row)
        node_rows[v + "___final"] = row
        row += 1

path_cnt = 0

#skip=[]
#with open("skip.log", "r") as f:
#    for line in f:
#        skip.append(int(line[:-1]))

feasible_cnt_total_per_pl_set = []
cover_cnt_total_per_pl_set = []
feasible_cnt_total_per_pl_set_final = []
cover_cnt_total_per_pl_set_final = []

all_exe_paths_covered = []
all_exe_paths_covered_sets = []
def gen():

    reachablePL_follower = {}
    for pl in cv_perflocs:
        #reachablePL_follower[transform(pl)] = []
        reachablePL_follower[pl] = []
        #reachablePL_follower[pl + "___final"] = []

    cnt_todo_cover_final = 0

    for set_idx, aSet in enumerate(reachable_sets):
        #if set_idx != 59:
        #    continue
        #if not set_idx in skip:
        #    continue

        cover_hb = []
        cover_concur = []

        undet_hb = []
        undet_concur = []

        print("===== SET idx: %d ====" % set_idx)

        result_edges = {}
        total_edges_possible = {}
        #with open("./%d_edge_todo_per_set.txt" % set_idx, "r") as f:
        with open("../xCollectReEval/%d_edge_todo_per_set.txt" % set_idx, "r") as f:
            df = None
            for line in f:
                #f.write("%s,%s:%s\n" % (k[0], k[1], ",".join(v)))
                pair = (line.split(":")[0]).split(",")
                seqs = (line[:-1].split(":")[1]).split(",")
                #print(pair, seqs)
                if df is None:
                    df = pd.read_csv("../xCollectReEval/com_%d.csv" % set_idx, dtype=mydtypes)
                    assert(df is not None)

                hascover = False
                for hbtype in seqs:
                    prop = None
                    res = None
                    if hbtype == ">":
                        prop = "CS_{e0}_hb_{e1}".format(e0=pair[0], e1=pair[1])
                        if prop == "CS_load_unit_op_s2_hb_scb_3_s8" or prop == "CS_load_unit_op_s2_hb_scb_2_s8":
                            res = "undetermined"
                        else:
                            res, bnd, time = df_query(df, prop)
                        #res, bnd, time = df_query(df, prop)
                        if res == "covered":
                            hascover=True
                            cover_hb.append([pair[0], pair[1]])
                            if ((pair[0], pair[1]) in result_edges):
                                result_edges[(pair[0], pair[1])].append(">")
                            else:
                                result_edges[(pair[0], pair[1])] = [">"]
                        elif res == "undetermined":
                            undet_hb.append([pair[0], pair[1]])
                    if hbtype == "<":
                        prop = "CS_{e0}_hb_{e1}".format(e0=pair[1], e1=pair[0])
                        res, bnd, time = df_query(df, prop)
                        if res == "covered":
                            hascover=True
                            cover_hb.append([pair[1], pair[0]])
                            if ((pair[0], pair[1]) in result_edges):
                                result_edges[(pair[0], pair[1])].append("<")
                            else:
                                result_edges[(pair[0], pair[1])] = ["<"]
                        elif res == "undetermined":
                            undet_hb.append([pair[0], pair[1]])
                    if hbtype == "=":
                        prop = "CS_{e0}_concur_{e1}".format(e0=pair[1], e1=pair[0])
                        res, bnd, time = df_query(df, prop)
                        if res == "covered":
                            hascover=True
                            cover_concur.append([pair[0], pair[1]])
                            if ((pair[0], pair[1]) in result_edges):
                                result_edges[(pair[0], pair[1])].append("=")
                            else:
                                result_edges[(pair[0], pair[1])] = ["="]
                        elif res == "undetermined":
                            undet_concur.append([pair[0], pair[1]])
                    if not (res == "unreachable"):
                        if (pair[0], pair[1]) in total_edges_possible:
                            total_edges_possible[(pair[0], pair[1])].append(hbtype)
                        else:
                            total_edges_possible[(pair[0], pair[1])] = [hbtype]
                    else:
                        hascover = True
               
                if not hascover:
                    print("not cover!! need additional order", pair, total_edges_possible[(pair[0], pair[1])])
                    total_edges_possible[(pair[0], pair[1])] = [">", "=", "<"]

        #print("hb ", cover_hb)
        #print("concur ", cover_concur)
        #print("undeter_hb ", undet_hb)
        #print("undeter_concur ", undet_concur)
        var_cnt = 1
        sets_edges = []
        for k, v in result_edges.items():
            var_cnt *= len(v)
            sets_edges.append([(k, v_i) for v_i in v])
            #print(k, v)

        #var_cnt_total = 1
        #sets_edges_total = []
        #for k, v in total_edges_possible.items():
        #    assert(len(v) == len(set(v)))
        #    var_cnt_total *= len(v)
        #    sets_edges_total.append([(k, v_i) for v_i in v])
        ####################################
        # BUILD GRAPH
        ####################################
        DG = nx.DiGraph()

        for e in hb_edge:
            if e[0] in aSet and e[1] in aSet:
                DG.add_edge(e[0], e[1])
        implied_edges_same_iid = []
        edge_weight = {}
        iid_map_tmp = iid_map
        for itm in aSet:
            DG.add_node(itm)

            # if perset_pl_cyc.get(set_idx) is None:
            if cyc_cnt_gt1_per_set.get(set_idx) is None:
                continue

            ## at least one greater than 1 
            #cyc_cnt = [int(r) > 1 for r in cyc]
            #if sum(cyc_cnt) >= 1:
            if itm in cyc_cnt_gt1_per_set[set_idx]:
                edge_weight[(itm, itm+"___final")] = \
                    [t for t in range(0, max_cyc_per_pl[itm])] #max #[int(r)-1 for r in cyc]
                iid_map_tmp[itm+"___final"] = iid_map_tmp[itm]
        whb_finals = [] 
        for itm in aSet:
            if cyc_cnt_gt1_per_set.get(set_idx) is None:
                continue
            if itm in cyc_cnt_gt1_per_set[set_idx]:
                for e in DG.out_edges(itm):
                    if iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
                        implied_edges_same_iid.append((itm + "___final", e[1]))
                    
                whb_finals.append((itm, itm + "___final")) ##DG.add_edge(itm, itm + "___final") 
                DG.add_node(itm + "___final")

        edge_weight_single = []
        for e in implied_edges_same_iid:
            DG.add_edge(*e)

        for itm in leaving_hb_proven_res_pairs:
            if itm[0] in DG.nodes() and itm[1] in DG.nodes():
                DG.add_edge(itm[0], itm[1])

        #for itm in aws_concur_leaving_pairs:
        #    if itm[0] in DG.nodes() and itm[1] in DG.nodes():

        for e in enter_concurrent_pairs + aws_concur_leaving_pairs:
            a, b = e
            if not (a in DG.nodes() and b in DG.nodes()):
                continue

            in_edges = DG.in_edges(e[0])
            for e_prime in in_edges:
                assert(e_prime[1] == e[0])
                #if e_prime[0] != e[1]:
                if True:
                    DG.add_edge(e_prime[0], e[1])

            in_edges = DG.in_edges(e[1])
            for e_prime in in_edges:
                assert(e_prime[1] == e[1])
                #if e_prime[0] != e[0]:
                if True:
                    DG.add_edge(e_prime[0], e[0])

            out_edges = DG.out_edges(e[0])
            for e_prime in out_edges:
                assert(e_prime[0] == e[0])
                #if e[1] != e_prime[1]:
                if True:
                    DG.add_edge(e[1], e_prime[1])

            out_edges = DG.out_edges(e[1])
            for e_prime in out_edges:
                assert(e_prime[0] == e[1])
                #if e[0] != e_prime[1]:
                if True:
                    DG.add_edge(e[0], e_prime[1])

        TR = nx.transitive_reduction(DG) #, reflexive=False)

        ################################################################################ 
        # setup solver 
        ################################################################################ 
        slv = MySolver(TR, edge_weight, implied_edges_same_iid, iid_map_tmp,
                edge_weight_single, enter_concurrent_pairs +
                aws_concur_leaving_pairs, whb_edge, whb_finals)
        res = slv.add_constraints()
        if res == False:
            print("Issue %d cyclic" % (set_idx))
            continue


        comb_edges = list(itertools.product(*sets_edges))
        #print(comb_edges)
        #continue

        cover_hb = []
        cover_concur = []
        undet_hb = []
        undet_concur = []

        for combidx, cv_edge_comb in enumerate(comb_edges):
            result_edges_final = {}
            total_edges_possible_final = {}

            undetermined_comb_entering = False

            cnt_todo = 0
            #if not os.path.exists("./%d_%d_final_edge_todo_per_set.txt" % (set_idx, combidx)):
            if not os.path.exists("../xCollectReEvalLeaveOrder/%d_%d_final_edge_todo_per_set.txt" % (set_idx, combidx)):
                print("set %d combidx %d cyclic" % (set_idx, combidx))
                continue

            #with open("./%d_%d_final_edge_todo_per_set.txt" % (set_idx, combidx), "r") as f:
            with open("../xCollectReEvalLeaveOrder/%d_%d_final_edge_todo_per_set.txt" % (set_idx, combidx), "r") as f:
                for line in f:
                    cnt_todo += 1
            if cnt_todo == 0:
                print("!! setidx %d %d has fix set of order on final nodes" % (set_idx, combidx))
                #print(cv_edge_comb)
                #print("TODO: res on set_r")
                doplot=False
                if len(cv_edge_comb) > 0:
                    #df = pd.read_csv("./out_trial2_2_setcover_results/com_%d_%d.csv" % (set_idx, combidx), dtype=mydtypes)
                    df = pd.read_csv("../xCollectReEvalLeaveOrder/com_%d_%d.csv" % (set_idx, combidx), dtype=mydtypes)
                    res, bnd, time = df_query(df, "C_SETR")
                    if res == "covered":
                        # plot 
                        doplot=True

                    if res == "undetermined":
                        print("!! setidx %d %d has fix set of order on final nodes but not covered!!!!" % (set_idx, combidx))

                else:
                    doplot=True

                if not doplot:
                    continue

                plset_iso = transformset(list(TR.nodes()))
                if not plset_iso in all_exe_paths_covered:
                    all_exe_paths_covered.append(plset_iso) #] = set()
                    all_exe_paths_covered_sets.append([])
                edges_iso = []
                for itm in TR.edges():
                    edges_iso.append((transform(itm[0]),transform(itm[1])))
                concur_iso = []
                #for itm in concur_in_comb:
                concur_in_comb = []
                for e in cv_edge_comb:
                    t_ = e[1]
                    p = e[0]
                    if t_ == '>':
                        DG.add_edge(p[0], p[1])
                    if t_ == '<':
                        DG.add_edge(p[1], p[0])
                    if t_ == '=':
                        concur_in_comb.append([p[0],p[1]])
                for itm in enter_concurrent_pairs + concur_in_comb + aws_concur_leaving_pairs:
                    if itm[0] in TR.nodes() and itm[1] in TR.nodes():
                        ttuple = tuple(sorted([transform(itm[0]),transform(itm[1])]))
                        if not ttuple in concur_iso:
                            concur_iso.append(ttuple)
                    
                tidx=all_exe_paths_covered.index(plset_iso)
                edges_iso = sorted(edges_iso)
                concur_iso = sorted(concur_iso)

                exists = False
                for tmpitm in all_exe_paths_covered_sets[tidx]:
                    if edges_iso == tmpitm[0] and concur_iso == tmpitm[1]:
                        exists=True
                new_iso_path = False
                if not exists: #not (edges_iso, concur_iso) in all_exe_paths_covered_sets[tidx]:
                    all_exe_paths_covered_sets[tidx].append((edges_iso, concur_iso))
                    new_iso_path = True
                else:
                    print("in here already")
                if new_iso_path:
                    if not os.path.isdir("nonisograph"):
                        os.mkdir("nonisograph")

                    ####################################
                    # BUILD GRAPH
                    ####################################
                    DG = nx.DiGraph()

                    for e in hb_edge:
                        if e[0] in aSet and e[1] in aSet:
                            DG.add_edge(e[0], e[1])
                    implied_edges_same_iid = []
                    edge_weight = {}
                    iid_map_tmp = iid_map
                    for itm in aSet:
                        DG.add_node(itm)

                        # if perset_pl_cyc.get(set_idx) is None:
                        if cyc_cnt_gt1_per_set.get(set_idx) is None:
                            continue

                        ## at least one greater than 1 
                        #cyc_cnt = [int(r) > 1 for r in cyc]
                        #if sum(cyc_cnt) >= 1:
                        if itm in cyc_cnt_gt1_per_set[set_idx]:
                            edge_weight[(itm, itm+"___final")] = \
                                [t for t in range(0, max_cyc_per_pl[itm])] #max #[int(r)-1 for r in cyc]
                            iid_map_tmp[itm+"___final"] = iid_map_tmp[itm]
                    whb_finals = [] 
                    for itm in aSet:
                        if cyc_cnt_gt1_per_set.get(set_idx) is None:
                            continue
                        if itm in cyc_cnt_gt1_per_set[set_idx]:
                            for e in DG.out_edges(itm):
                                if iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
                                    implied_edges_same_iid.append((itm + "___final", e[1]))
                                
                            whb_finals.append((itm, itm + "___final")) ##DG.add_edge(itm, itm + "___final") 
                            DG.add_node(itm + "___final")

                    concur_in_comb = []
                    for e in cv_edge_comb:
                        t_ = e[1]
                        p = e[0]
                        if t_ == '>':
                            DG.add_edge(p[0], p[1])
                        if t_ == '<':
                            DG.add_edge(p[1], p[0])
                        if t_ == '=':
                            concur_in_comb.append([p[0],p[1]])
                    edge_weight_single = []
                    for e in implied_edges_same_iid:
                        DG.add_edge(*e)

                    for itm in leaving_hb_proven_res_pairs:
                        if itm[0] in DG.nodes() and itm[1] in DG.nodes():
                            DG.add_edge(itm[0], itm[1])

                    #for itm in aws_concur_leaving_pairs:
                    #    if itm[0] in DG.nodes() and itm[1] in DG.nodes():

                    for e in enter_concurrent_pairs + aws_concur_leaving_pairs + concur_in_comb:
                        a, b = e
                        if not (a in DG.nodes() and b in DG.nodes()):
                            continue

                        in_edges = DG.in_edges(e[0])
                        for e_prime in in_edges:
                            assert(e_prime[1] == e[0])
                            #if e_prime[0] != e[1]:
                            if True:
                                DG.add_edge(e_prime[0], e[1])

                        in_edges = DG.in_edges(e[1])
                        for e_prime in in_edges:
                            assert(e_prime[1] == e[1])
                            #if e_prime[0] != e[0]:
                            if True:
                                DG.add_edge(e_prime[0], e[0])

                        out_edges = DG.out_edges(e[0])
                        for e_prime in out_edges:
                            assert(e_prime[0] == e[0])
                            #if e[1] != e_prime[1]:
                            if True:
                                DG.add_edge(e[1], e_prime[1])

                        out_edges = DG.out_edges(e[1])
                        for e_prime in out_edges:
                            assert(e_prime[0] == e[1])
                            #if e[0] != e_prime[1]:
                            if True:
                                DG.add_edge(e[0], e_prime[1])

                    TR = nx.transitive_reduction(DG) #, reflexive=False)

                    ################################################################################ 
                    # setup solver 
                    ################################################################################ 
                    slv = MySolver(TR, edge_weight, implied_edges_same_iid, iid_map_tmp,
                            edge_weight_single, enter_concurrent_pairs + concur_in_comb + 
                            aws_concur_leaving_pairs, whb_edge, whb_finals)
                    res = slv.add_constraints()

                    ################################################################################ 
                    # Follower set
                    tmpfollower = {}
                    print("followerset gen", TR.edges())
                    for n in TR.nodes():
                        if n in TR.nodes() and (n + "___final") in TR.nodes():
                            TR.add_edge(n, n+"___final")
                    TR = nx.transitive_reduction(TR)
                    for tmp_n_raw in TR.nodes():
                        #if tmp_n_raw.endswith("___final"):
                        #    tmp_n = transform(tmp_n_raw.split("___")[0])
                        #else:
                        #    tmp_n = transform(tmp_n_raw)
                        #if tmp_n.endswith("___final"):
                        #    tmpfollower[tmp_n.split("___")[0]] = set()
                        #else:
                        tmp_n = tmp_n_raw
                        tmpfollower[tmp_n] = set()
                        for succ_raw in TR.successors(tmp_n_raw):
                            succ = transform(succ_raw)
                            if tmp_n.endswith("___final"):
                                #tmpfollower[tmp_n.split("___")[0]].add(succ)
                                tmpfollower[tmp_n].add(succ)
                            else:
                                tmpfollower[tmp_n].add(succ)

                    #for e_raw in whb_finals: #edge_weight:
                    #    e = (transform(e_raw[0]), transform(e_raw[1]))
                    #    if e_raw[0].endswith("___final"):
                    #        #e[0] = transform(e_raw[0].split("___")[0])
                    #        e[0] = e_raw[0]#.split("___")[0])
                    #    #e = (transform(e_raw[0]), transform(e_raw[1]))
                    #    print("whb_final: ", e_raw)
                    #    tmpfollower[e[0]].add(e[1])

                    for k, v in tmpfollower.items():
                        #if len(v) == 0:
                        #    continue
                        if not k in reachablePL_follower:
                            reachablePL_follower[k] = []
                        if not v in reachablePL_follower[k]:
                            reachablePL_follower[k].append(v)

                    ################################################################################ 

                     
                    MYGRAPHING(
                            "nonisograph/com_%d_%d.dot" % (set_idx, combidx),
                            hb_edge,
                            aSet, 
                            cyc_cnt_gt1_per_set,
                            leaving_hb_proven_res_pairs,
                            enter_concurrent_pairs, 
                            aws_concur_leaving_pairs,
                            max_cyc_per_pl,
                            iid_map,
                            set_idx,
                            cv_edge_comb, 
                            whb_edge,
                            slv,
                            WEIGHTED=False)

                ### TODO
                #plset_iso = transform(list(TR.nodes()))
                #if not plset_iso in all_exe_paths_covered:
                #    all_exe_paths_covered[plset_iso] = set()

                #all_exe_paths_covered[plset_iso].add(set_of_edges/concur)
                #res, bnd, time = df_query(df, "set_r", exact_name=True)
                # check
                continue
            print("set idx %d combidx %d" % (set_idx, combidx))
            #with open("./%d_%d_final_edge_todo_per_set.txt" % (set_idx, combidx), "r") as f:
            with open("../xCollectReEvalLeaveOrder/%d_%d_final_edge_todo_per_set.txt" % (set_idx, combidx), "r") as f:
                df = None
                for line in f:
                    pair = (line.split(":")[0]).split(",")
                    seqs = (line[:-1].split(":")[1]).split(",")
                    if df is None:
                        #if os.path.exists("./trial2_todo/com_%d_%d.csv" % (set_idx, combidx)):
                        #    df = pd.read_csv("./trial2_todo/com_%d_%d.csv" % (set_idx, combidx), dtype=mydtypes)
                        #else:
                        #    df = pd.read_csv("./com_%d_%d.csv" % (set_idx, combidx), dtype=mydtypes)
                        ##df = pd.read_csv("./trial2_todo/com_%d_%d.csv" % (set_idx, combidx), dtype=mydtypes)
                        df = pd.read_csv("../xCollectReEvalLeaveOrder/com_%d_%d.csv" % (set_idx, combidx), dtype=mydtypes)
                        assert(df is not None)
                    
                    hascover = False
                    for hbtype in seqs:
                        prop = None
                        if hbtype == ">":
                            prop = "CS_{e0}_hb_{e1}".format(e0=pair[0], e1=pair[1])
                            res, bnd, time = df_query(df, prop)
                            if res == "covered":
                                hascover = True
                                cover_hb.append([pair[0], pair[1]])
                                if ((pair[0], pair[1]) in result_edges_final):
                                    result_edges_final[(pair[0], pair[1])].append(">")
                                else:
                                    result_edges_final[(pair[0], pair[1])] = [">"]
                            elif res == "undetermined":
                                undet_hb.append([pair[0], pair[1]])
                        if hbtype == "<":
                            prop = "CS_{e0}_hb_{e1}".format(e0=pair[1], e1=pair[0])
                            res, bnd, time = df_query(df, prop)
                            if res == "covered":
                                hascover = True
                                cover_hb.append([pair[1], pair[0]])
                                if ((pair[0], pair[1]) in result_edges_final):
                                    result_edges_final[(pair[0], pair[1])].append("<")
                                else:
                                    result_edges_final[(pair[0], pair[1])] = ["<"]
                            elif res == "undetermined":
                                undet_hb.append([pair[0], pair[1]])
                        if hbtype == "=":
                            prop = "CS_{e0}_concur_{e1}".format(e0=pair[0], e1=pair[1])
                            res, bnd, time = df_query(df, prop)
                            if res == "covered":
                                hascover = True
                                cover_concur.append([pair[0], pair[1]])
                                if ((pair[0], pair[1]) in result_edges_final):
                                    result_edges_final[(pair[0], pair[1])].append("=")
                                else:
                                    result_edges_final[(pair[0], pair[1])] = ["="]
                            elif res == "undetermined":
                                undet_concur.append([pair[0], pair[1]])
                        if not (res == "unreachable"):
                            if (pair[0], pair[1]) in total_edges_possible_final:
                                total_edges_possible_final[(pair[0], pair[1])].append(hbtype)
                            else:
                                total_edges_possible_final[(pair[0], pair[1])] = [hbtype]
                    if not hascover:
                        print("not final cover!! need additional order", pair, total_edges_possible_final[(pair[0], pair[1])])
                        total_edges_possible_final[(pair[0], pair[1])] = [">", "=", "<"]
                res, bnd, time = df_query(df, "set_r", exact_name=True)
                print("set_r is covered? ", res)
                     

            var_cnt_final = 1
            sets_edges_final = []
            for k, v in result_edges_final.items():
                assert(len(v) == len(set(v)))
                var_cnt_final *= len(v)
                sets_edges_final.append([(k, v_i) for v_i in v])
                #print(k, v)

            if not res == "covered":
                print("set/comb idx %d %d is not covered? " % (set_idx, combidx))
                continue

            def check_combs():
                var_cnt_total = 1
                sets_edges_total = []
                for k, v in total_edges_possible_final.items():
                    assert(len(v) == len(set(v)))
                    var_cnt_total *= len(v)
                    sets_edges_total.append([(k, v_i) for v_i in v])

                ####################################
                # BUILD GRAPH
                ####################################
                DG = nx.DiGraph()

                for e in hb_edge:
                    if e[0] in aSet and e[1] in aSet:
                        DG.add_edge(e[0], e[1])
                concur_in_comb = []
                for e in cv_edge_comb:
                    t_ = e[1]
                    p = e[0]
                    if t_ == '>':
                        DG.add_edge(p[0], p[1])
                    if t_ == '<':
                        DG.add_edge(p[1], p[0])
                    if t_ == '=':
                        concur_in_comb.append([p[0],p[1]])
                implied_edges_same_iid = []
                edge_weight = {}
                iid_map_tmp = iid_map
                for itm in aSet:
                    DG.add_node(itm)

                    # if perset_pl_cyc.get(set_idx) is None:
                    if cyc_cnt_gt1_per_set.get(set_idx) is None:
                        continue

                    ## at least one greater than 1 
                    #cyc_cnt = [int(r) > 1 for r in cyc]
                    #if sum(cyc_cnt) >= 1:
                    if itm in cyc_cnt_gt1_per_set[set_idx]:
                        edge_weight[(itm, itm+"___final")] = \
                            [t for t in range(0, max_cyc_per_pl[itm])] #max #[int(r)-1 for r in cyc]
                        iid_map_tmp[itm+"___final"] = iid_map_tmp[itm]
                whb_finals = [] 
                for itm in aSet:
                    if cyc_cnt_gt1_per_set.get(set_idx) is None:
                        continue
                    if itm in cyc_cnt_gt1_per_set[set_idx]:
                        for e in DG.out_edges(itm):
                            if iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
                                implied_edges_same_iid.append((itm + "___final", e[1]))
                            
                        whb_finals.append((itm, itm + "___final")) ##DG.add_edge(itm, itm + "___final") 
                        DG.add_node(itm + "___final")

                edge_weight_single = []
                for e in implied_edges_same_iid:
                    DG.add_edge(*e)

                for itm in leaving_hb_proven_res_pairs:
                    if itm[0] in DG.nodes() and itm[1] in DG.nodes():
                        DG.add_edge(itm[0], itm[1])

                #for itm in aws_concur_leaving_pairs:
                #    if itm[0] in DG.nodes() and itm[1] in DG.nodes():

                for e in enter_concurrent_pairs + aws_concur_leaving_pairs + concur_in_comb:
                    a, b = e
                    if not (a in DG.nodes() and b in DG.nodes()):
                        continue

                    in_edges = DG.in_edges(e[0])
                    for e_prime in in_edges:
                        assert(e_prime[1] == e[0])
                        #if e_prime[0] != e[1]:
                        if True:
                            DG.add_edge(e_prime[0], e[1])

                    in_edges = DG.in_edges(e[1])
                    for e_prime in in_edges:
                        assert(e_prime[1] == e[1])
                        #if e_prime[0] != e[0]:
                        if True:
                            DG.add_edge(e_prime[0], e[0])

                    out_edges = DG.out_edges(e[0])
                    for e_prime in out_edges:
                        assert(e_prime[0] == e[0])
                        #if e[1] != e_prime[1]:
                        if True:
                            DG.add_edge(e[1], e_prime[1])

                    out_edges = DG.out_edges(e[1])
                    for e_prime in out_edges:
                        assert(e_prime[0] == e[1])
                        #if e[0] != e_prime[1]:
                        if True:
                            DG.add_edge(e[0], e_prime[1])

                TR = nx.transitive_reduction(DG) #, reflexive=False)

                ################################################################################ 
                # setup solver 
                ################################################################################ 
                slv = MySolver(TR, edge_weight, implied_edges_same_iid, iid_map_tmp,
                        edge_weight_single, enter_concurrent_pairs + concur_in_comb +
                        aws_concur_leaving_pairs, whb_edge, whb_finals)
                res = slv.add_constraints()
                if res == False:
                    print("Issue %d %d cyclic (sat)" % (set_idx, combidx))


                #slv.gen(sets_edges_total)
                

                print("%d %d combidx var cnt %d" % (set_idx, combidx, var_cnt_final))
                #print("var total", var_cnt_total)
                #print(sets_edges_total)
                print("final feasible cnt", len(slv.res))
                feasible_cnt_total_per_pl_set_final.append(len(slv.res))
                cover_cnt_total_per_pl_set_final.append(var_cnt_final)

            #check_combs()

            #continue
            comb_edges_final = list(itertools.product(*sets_edges_final))
            print(len(comb_edges_final))
            noncyc=0
            for combidx_final, cv_edge_comb_final in enumerate(comb_edges_final):
                print("particular orders", len(cv_edge_comb_final), len(cv_edge_comb))
                #print("particular orders", cv_edge_comb_final, cv_edge_comb)
                DG = nx.DiGraph()

                for e in hb_edge:
                    if e[0] in aSet and e[1] in aSet:
                        DG.add_edge(e[0], e[1])
                concur_in_comb = []
                for e in cv_edge_comb:
                    t_ = e[1]
                    p = e[0]
                    if t_ == '>':
                        DG.add_edge(p[0], p[1])
                    if t_ == '<':
                        DG.add_edge(p[1], p[0])
                    if t_ == '=':
                        concur_in_comb.append([p[0],p[1]])
                for e in cv_edge_comb_final:
                    t_ = e[1]
                    p = e[0]
                    if t_ == '>':
                        DG.add_edge(p[0], p[1])
                    if t_ == '<':
                        DG.add_edge(p[1], p[0])
                    if t_ == '=':
                        concur_in_comb.append([p[0],p[1]])
                        
                print("concur_in_comb", concur_in_comb) 
                # concurrent tagged through same color 
                color_cnt=4
                node_colors = {}

                # same iid leave order same as enter order
                implied_edges_same_iid = []

                edge_weight = {}
                iid_map_tmp = iid_map
                for itm in aSet:
                    DG.add_node(itm)

                    # if perset_pl_cyc.get(set_idx) is None:
                    if cyc_cnt_gt1_per_set.get(set_idx) is None:
                        continue

                    ## at least one greater than 1 
                    #cyc_cnt = [int(r) > 1 for r in cyc]
                    #if sum(cyc_cnt) >= 1:
                    if itm in cyc_cnt_gt1_per_set[set_idx]:
                        edge_weight[(itm, itm+"___final")] = \
                            [t for t in range(0, max_cyc_per_pl[itm])] #max #[int(r)-1 for r in cyc]
                        iid_map_tmp[itm+"___final"] = iid_map_tmp[itm]
                whb_finals = []
                for itm in aSet:
                    if cyc_cnt_gt1_per_set.get(set_idx) is None:
                        continue
                    if itm in cyc_cnt_gt1_per_set[set_idx]:
                        for e in DG.out_edges(itm):
                            if iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
                                implied_edges_same_iid.append((itm + "___final", e[1]))

                        whb_finals.append((itm, itm+"___final"))
                        DG.add_node(itm+"___final")
                        #DG.add_edge(itm, itm + "___final") 
        
                
                # node_colors always concurrent -> constraint on the edge weight 
                for itm in aws_concur_leaving_pairs:
                    if itm[0] in DG.nodes() and itm[1] in DG.nodes():
                        c = None
                        if itm[0] in node_colors:
                            c = node_colors[itm[0]]
                        elif itm[1] in node_colors:
                            c = node_colors[itm[1]]

                        if c is None:
                            c = color_cnt
                            color_cnt += 1
                        node_colors[itm[0]] = c
                        node_colors[itm[1]] = c



                # heuristic
                edge_weight_single = []
                #if intra_single_cyc.get(set_idx) is not None:
                #    for e in intra_single_cyc[set_idx]:
                #        # only use for source not longer than 1 cycle: (otherwise if its
                #        # staying longer than 1 cycle it will implies many more things  more correlation..)
                #        if not e[0] + "___final" in iid_map_tmp:
                #            print("heuristic", set_idx, e)
                #            edge_weight_single.append(e)
                #            DG.add_edge(e[0], e[1])
                #else:
                #    print("intra_single_cyc don't have key ", set_idx)



                #print(hb_edge)
                for e in implied_edges_same_iid:
                    DG.add_edge(*e)

                for itm in leaving_hb_proven_res_pairs:
                    if itm[0] in DG.nodes() and itm[1] in DG.nodes():
                        DG.add_edge(itm[0], itm[1])

                #for itm in aws_concur_leaving_pairs:
                #    if itm[0] in DG.nodes() and itm[1] in DG.nodes():

                for e in enter_concurrent_pairs + aws_concur_leaving_pairs + concur_in_comb:
                    a, b = e
                    if not (a in DG.nodes() and b in DG.nodes()):
                        continue

                    in_edges = DG.in_edges(e[0])
                    for e_prime in in_edges:
                        assert(e_prime[1] == e[0])
                        #if e_prime[0] != e[1]:
                        if True:
                            DG.add_edge(e_prime[0], e[1])

                    in_edges = DG.in_edges(e[1])
                    for e_prime in in_edges:
                        assert(e_prime[1] == e[1])
                        #if e_prime[0] != e[0]:
                        if True:
                            DG.add_edge(e_prime[0], e[0])

                    out_edges = DG.out_edges(e[0])
                    for e_prime in out_edges:
                        assert(e_prime[0] == e[0])
                        #if e[1] != e_prime[1]:
                        if True:
                            DG.add_edge(e[1], e_prime[1])

                    out_edges = DG.out_edges(e[1])
                    for e_prime in out_edges:
                        assert(e_prime[0] == e[1])
                        #if e[0] != e_prime[1]:
                        if True:

                            DG.add_edge(e[0], e_prime[1])

                if len(list(nx.simple_cycles(DG))) > 0:
                    print("Issue %d, combidx %d %d cyclic" % (set_idx, combidx, combidx_final))
                    #print(list(nx.simple_cycles(DG)))
                    #assert(0)
                    continue

                TR = nx.transitive_reduction(DG) #, reflexive=False)
                TC = nx.transitive_closure(DG, reflexive=False)
                reduce_e = list(TR.edges)

                ################################################################################ 
                # setup solver 
                ################################################################################ 
                slv = MySolver(TR, edge_weight, implied_edges_same_iid, iid_map_tmp,
                        edge_weight_single, enter_concurrent_pairs + concur_in_comb +
                        aws_concur_leaving_pairs, whb_edge, whb_finals)
                slv.add_constraints(debug=(set_idx == 64))
                res = slv.add_constraints()
                if res == False:
                    print(list(TR.edges()))
                    print("Issue %d, combidx %d %d cyclic (sat) " % (set_idx, combidx, combidx_final))
                    continue

                print(list(TR.nodes()))
                print(list(TR.edges()))
                print("FINAL EXE PATH set idx %d %d %d" % (set_idx, combidx, combidx_final))
                
                ## TODO 
                
                plset_iso = transformset(list(TR.nodes()))
                if not plset_iso in all_exe_paths_covered:
                    all_exe_paths_covered.append(plset_iso) #] = set()
                    all_exe_paths_covered_sets.append([])
                edges_iso = []
                for itm in TR.edges():
                    edges_iso.append((transform(itm[0]),transform(itm[1])))
                concur_iso = []
                #for itm in concur_in_comb:
                for itm in enter_concurrent_pairs + concur_in_comb + aws_concur_leaving_pairs:
                    if itm[0] in TR.nodes() and itm[1] in TR.nodes():
                        ttuple = tuple(sorted([transform(itm[0]),transform(itm[1])]))
                        if not ttuple in concur_iso:
                            concur_iso.append(ttuple)
                    
                tidx=all_exe_paths_covered.index(plset_iso)
                edges_iso = sorted(edges_iso)
                concur_iso = sorted(concur_iso)

                exists = False
                for tmpitm in all_exe_paths_covered_sets[tidx]:
                    if edges_iso == tmpitm[0] and concur_iso == tmpitm[1]:
                        exists=True
                new_iso_path = False
                if not exists: #not (edges_iso, concur_iso) in all_exe_paths_covered_sets[tidx]:
                    all_exe_paths_covered_sets[tidx].append((edges_iso, concur_iso))
                    new_iso_path = True
                else:
                    print("in here already")
                if new_iso_path:
                    ################################################################################ 
                    # Follower set
                    tmpfollower = {}

                    print("followerset gen", TR.edges())
                    for n in TR.nodes():
                        if n in TR.nodes() and (n + "___final") in TR.nodes():
                            TR.add_edge(n, n+"___final")
                    TR = nx.transitive_reduction(TR)

                    for tmp_n_raw in TR.nodes():
                        tmp_n = tmp_n_raw
                        #if tmp_n_raw.endswith("___final"):
                        #    tmp_n = transform(tmp_n_raw.split("___")[0])
                        #else:
                        #    tmp_n = transform(tmp_n_raw)
                        #if tmp_n.endswith("___final"):
                        #    tmpfollower[tmp_n.split("___")[0]] = set()
                        #else:

                        tmpfollower[tmp_n] = set()
                        for succ_raw in TR.successors(tmp_n_raw):
                            succ = transform(succ_raw)
                            if tmp_n.endswith("___final"):
                                #tmpfollower[tmp_n.split("___")[0]].add(succ)
                                tmpfollower[tmp_n].add(succ)
                            else:
                                tmpfollower[tmp_n].add(succ)

                    #for e_raw in whb_finals: #edge_weight:
                    #    e = (transform(e_raw[0]), transform(e_raw[1]))
                    #    if e_raw[0].endswith("___final"):
                    #        #e[0] = transform(e_raw[0].split("___")[0])
                    #        e[0] = e_raw[0] #transform(e_raw[0].split("___")[0])
                    #    #e = (transform(e_raw[0]), transform(e_raw[1]))
                    #    print("whb final 2: ", e_raw)
                    #    tmpfollower[e[0]].add(e[1])

                    for k, v in tmpfollower.items():
                        if not k in reachablePL_follower:
                            reachablePL_follower[k] = []
                        if not v in reachablePL_follower[k]:
                            reachablePL_follower[k].append(v)

                    ################################################################################ 

                    if not os.path.isdir("nonisograph"):
                        os.mkdir("nonisograph")
                    MYGRAPHING(
                            "nonisograph/com_%d_%d_%d.dot" % (set_idx, combidx, combidx_final),
                            hb_edge,
                            aSet, 
                            cyc_cnt_gt1_per_set,
                            leaving_hb_proven_res_pairs,
                            enter_concurrent_pairs, 
                            aws_concur_leaving_pairs,
                            max_cyc_per_pl,
                            iid_map,
                            set_idx,
                            cv_edge_comb + cv_edge_comb_final,
                            whb_edge,
                            slv,
                            WEIGHTED=False)
                #all_exe_paths_covered[plset_iso].add(set_of_edges/concur)



    print("EXECNT", len(all_exe_paths_covered))
    total_cnt = 0
    squash = 0
    for idx, itm in enumerate(all_exe_paths_covered_sets):
        #print(len(itm))
        print(itm)
        total_cnt += len(itm)
        #if not "iso_2" in all_exe_paths_covered[idx]:
        if "NI" in os.getcwd() or ("iso_2" in all_exe_paths_covered[idx] or "iso_3" in all_exe_paths_covered[idx]):
            print("NEW PATH" , all_exe_paths_covered[idx])
            for comb_idx, titm in enumerate(itm):
                f = open("all_path_%d_%d.txt" % (idx, comb_idx), "w")
                for t in titm[0]:
                    #print(t)
                    f.write("%s,%s\n" % (t[0], t[1]))
                f.write("----------\n")
                for t in titm[1]:
                    f.write("%s,%s\n" % (t[0], t[1]))
                f.close()
        tmpitm=all_exe_paths_covered[idx]
        if not ("iso_2" in tmpitm): #all_exe_paths_covered[idx]):
            if not ("iso_3" in tmpitm):
                squash += len(itm)
    print("TOTAL CNT COVERED", total_cnt)
    print("TOTAL CNT COVERED SQUASH", squash)

    #print("cnt todo:", cnt_todo_cover)
    #print("cnt_todo_cover_final", cnt_todo_cover_final)
    #print(len(feasible_cnt_total_per_pl_set))
    #print(len(cover_cnt_total_per_pl_set))
    #print(len(feasible_cnt_total_per_pl_set_final))
    #print(len(cover_cnt_total_per_pl_set_final))

    #print(*feasible_cnt_total_per_pl_set)
    #print(*cover_cnt_total_per_pl_set)
    #print(*feasible_cnt_total_per_pl_set_final)
    #print(*cover_cnt_total_per_pl_set_final)

    with open("follower_set_v2.txt", "w") as f:
        for k, v in reachablePL_follower.items():
            #if len(v) == 0:
            #    continue
            f.write("%s:%d\n" % (k, len(v)))
            for tmpl in v:
                f.write("%s\n" % ",".join(list(tmpl)))

    print("==================== successor ==========")
    for k, v in reachablePL_follower.items():
        print(k, ":", "(", len(v), ")", v)
    print("=========================================")

print("JJ")
if len(sys.argv) < 2:
    print("gen/pp/stats")
    exit(0)

opt = sys.argv[1]
if opt == "gen":
    gen()
elif opt == "gen_s2":
    gen_s2()
elif opt == "pp":
    pp()
elif opt == "stats":
    stats()
        
