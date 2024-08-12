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
class GenComb:
    def __init__(self, arr):
        self.arr = arr
        self.res = []
        self.acc = []
    def gen(self):
        self.get_all_combination(0)
    def get_all_combination(self, idx):
        if idx == len(self.arr):
            self.res.append(self.acc[::])
            return
        # e weight 
        results = []
        for t in range(0, self.arr[idx]):
            self.acc.append(t)
            self.get_all_combination(idx+1)
            self.acc.pop()
# For cycle count per IUV or per PL set
is_interference_case = "III" in os.getcwd()

cv_perflocs = get_array("../xCoverAPerflocDiv/cover_individual.txt")
edge = get_array("../../xGenPerfLocDfgDiv/dfg_e.txt")

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
    "load_unit_op_s1",
    "load_unit_op_s2",
    "load_unit_op_s3",
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
#print("leaving_hb_proven_res_pairs:", leaving_hb_proven_res_pairs)
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

def gen():

    if not os.path.isdir("out_complete_2"):
        os.mkdir("out_complete_2")

    if not os.path.isdir("out_complete_2_setcover"):
        os.mkdir("out_complete_2_setcover")

    FINAL=True
    cnt_todo_cover_final = 0

    for set_idx, aSet in enumerate(reachable_sets):

        cover_hb = []
        cover_concur = []

        undet_hb = []
        undet_concur = []

        print("===== SET idx: %d ====" % set_idx)

        result_edges = {}
        with open("../xCollectReEval/%d_edge_todo_per_set.txt" % set_idx, "r") as f:
            df = None
            for line in f:
                #f.write("%s,%s:%s\n" % (k[0], k[1], ",".join(v)))
                pair = (line.split(":")[0]).split(",")
                seqs = (line[:-1].split(":")[1]).split(",")
                print(pair, seqs)
                if df is None:
                    df = pd.read_csv("../xCollectReEval/com_%d.csv" % set_idx, dtype=mydtypes)
                    assert(df is not None)

                for hbtype in seqs:
                    prop = None
                    if hbtype == ">":
                        prop = "CS_{e0}_hb_{e1}".format(e0=pair[0], e1=pair[1])
                        res, bnd, time = df_query(df, prop)
                        if res == "covered":
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
                            cover_concur.append([pair[0], pair[1]])
                            if ((pair[0], pair[1]) in result_edges):
                                result_edges[(pair[0], pair[1])].append("=")
                            else:
                                result_edges[(pair[0], pair[1])] = ["="]
                        elif res == "undetermined":
                            undet_concur.append([pair[0], pair[1]])
        print("hb ", cover_hb)
        print("concur ", cover_concur)
        print("undeter_hb ", undet_hb)
        print("undeter_concur ", undet_concur)
        var_cnt = 1
        sets_edges = []
        for k, v in result_edges.items():
            var_cnt *= len(v)
            sets_edges.append([(k, v_i) for v_i in v])
            print(k, v)

        print("var cnt ", var_cnt)
        comb_edges = list(itertools.product(*sets_edges))
        print(len(comb_edges))
        print(comb_edges)

        with open("%d_combination.txt" % set_idx, "w") as f:
            for itm in comb_edges:
                for e in itm:
                    f.write("%s,%s,%s," % (e[0][0], e[0][1], e[1]))
                f.write("\n") 

        for combidx, cv_edge_comb in enumerate(comb_edges):
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
                    

            # concurrent tagged through same color 
            color_cnt=4
            node_colors = {}
            for itm in enter_concurrent_pairs:
                a, b = itm 
                if a in aSet and b in aSet:
                    c = None
                    if itm[0] in node_colors:
                        c = node_colors[itm[0]]
                    elif itm[1] in node_colors:
                        c = node_colors[itm[1]]

                    if c is None:
                        c = color_cnt
                        color_cnt += 1
                    
                    node_colors[a] = c
                    node_colors[b] = c


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
                
                    #for e in DG.out_edges(itm):
                    #    if iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
                    #        implied_edges_same_iid.append((itm + "___final", e[1]))
                    #    
                    #DG.add_edge(itm, itm + "___final") 

            for itm in aSet:
                if cyc_cnt_gt1_per_set.get(set_idx) is None:
                    continue
                if itm in cyc_cnt_gt1_per_set[set_idx]:
                    for e in DG.out_edges(itm):
                        if iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
                            implied_edges_same_iid.append((itm + "___final", e[1]))
                        
                    DG.add_edge(itm, itm + "___final") 
            
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
                    DG.add_edge(e_prime[0], e[1])

                in_edges = DG.in_edges(e[1])
                for e_prime in in_edges:
                    assert(e_prime[1] == e[1])
                    DG.add_edge(e_prime[0], e[0])

                out_edges = DG.out_edges(e[0])
                for e_prime in out_edges:
                    assert(e_prime[0] == e[0])
                    DG.add_edge(e[1], e_prime[1])

                out_edges = DG.out_edges(e[1])
                for e_prime in out_edges:
                    assert(e_prime[0] == e[1])
                    DG.add_edge(e[0], e_prime[1])
            if len(list(nx.simple_cycles(DG))) > 0:
                print("Issue %d, combidx %d cyclic" % (set_idx, combidx))
                continue
            TR = nx.transitive_reduction(DG) #, reflexive=False)
            TC = nx.transitive_closure(DG, reflexive=False)
            reduce_e = list(TR.edges)

            ################################################################################ 
            # setup solver 
            ################################################################################ 
            slv = MySolver(TR, edge_weight, implied_edges_same_iid, iid_map_tmp,
                    edge_weight_single, enter_concurrent_pairs + concur_in_comb +
                    aws_concur_leaving_pairs, whb_edge)
            slv.add_constraints()

            ################################################################################ 
            # Get all edges that is not proven 
            ################################################################################ 
            pairs_final = {}
            for idx, eorg in enumerate(edge):
                if not (eorg[0] in aSet and eorg[1] in aSet):
                    continue
                if (iid_map[eorg[0]] == iid_map[eorg[1]]):
                    continue
                e_primes = [] 
                if eorg[0] + "___final" in TC.nodes() and eorg[1] in aSet:
                    e_primes.append([eorg[0] + "___final", eorg[1]])
                if eorg[0] in aSet and eorg[1] + "___final" in TC.nodes():
                    e_primes.append([eorg[0], eorg[1] + "___final"])
                if (eorg[1] + "___final" in TC.nodes()) and (eorg[0] + "___final" in TC.nodes()):
                    e_primes.append([eorg[0] + "___final" , eorg[1] + "___final"])
                if len(e_primes) == 0:
                    continue
                for e in e_primes:
                    if tuple(e) in TC.edges() or (e[1], e[0]) in TC.edges():
                        continue
                    if e in edge_weight_single or (e[1], e[0]) in edge_weight_single:
                        continue
                    if e in enter_concurrent_pairs or [e[1], e[0]] in enter_concurrent_pairs: 
                        continue
                    if slv.check_imp_hb(e):
                        print("set idx %d %d imp hb %s %s" % (set_idx, combidx, e[0], e[1]))
                        continue

                    can_be_hb = slv.check_hb_possibility(e)
                    if not can_be_hb:
                        print("set idx %d %d imp can't be hb %s %s" % (set_idx, combidx, e[0], e[1]))
                        continue
                    # if no hb relation between enter nodes we skip...
                    #enter_nodes = [e[0].split("___final")[0], e[1].split("___final")[0]]
                    #if slv.check_hb_possibility(enter_nodes) and slv.check_hb_possibility([enter_nodes[1],enter_nodes[0]]):
                    #    print("???!!! no fixed order in enter node?", e[1], e[0])
                    #    continue

                    
                    if e[0] < e[1]:
                        if (e[0], e[1]) in pairs_final:
                            # e[0] HB e[1]
                            pairs_final[(e[0], e[1])].append(">")
                        else:
                            pairs_final[(e[0], e[1])] = [">", "="]
                    else:
                        if (e[1], e[0]) in pairs_final:
                            pairs_final[(e[1], e[0])].append("<")
                        else:
                            pairs_final[(e[1], e[0])] = ["<", "="]
                            
            cnt_setidx = 0
            for k, v in pairs_final.items():
                print("(%s, %s): %s" % (k[0], k[1], ",".join(v)))
                cnt_todo_cover_final += len(v)
                cnt_setidx += len(v)


            
            print("Issue %d, combidx %d" % (set_idx, combidx))
            print(cnt_setidx)
            
            #pairs_todo_pruned = {}
            #for k, v in pairs_todo.items():
            #    pairs_todo_pruned[k] = v
            #    print("(%s, %s): %s" % (k[0], k[1], ",".join(v)))
            #    cnt_todo_cover_final += len(v)
            #print("========================================")

            with open("%d_%d_final_edge_todo_per_set.txt" % (set_idx, combidx), "w") as f:
                for k, v in pairs_final.items():
                    f.write("%s,%s:%s\n" % (k[0], k[1], ",".join(v)))

            if cnt_setidx == 0:
                if len(cv_edge_comb) > 0:
                    with open("out_complete_2_setcover/com_%d_%d.sv" % (set_idx, combidx), "w") as f:
                        f.write(h_)
                        s = ""
                        for pl in cv_perflocs:
                            if not pl in aSet:
                                f.write(no_s1_t.format(s1=pl))
                            else:
                                f.write(hpn_reg_t2.format(s1=pl))
                                s += "{s1}_hpn && ".format(s1=pl)
                        s += "1'b1 "
                        f.write("wire set_r = %s;\n" % s)
                        for e in cv_edge_comb:
                            t_ = e[1]
                            p = e[0]
                            assert(not("___final" in p[0] or "___final" in p[1]))

                            if t_ == '>':
                                f.write(A_enter_hb_enter.format(e0=p[0], e1=p[1]))
                            if t_ == '<':
                                f.write(A_enter_hb_enter.format(e0=p[1], e1=p[0]))
                            if t_ == '=':
                                f.write(A_enter_concur_enter.format(e0=p[0], e1=p[1]))
                        f.write("C_SETR: cover property (@(posedge clk_i) set_r);\n")
            else:
                os.system("cp ./prove_from.tcl out_complete_2/com_%d_%d.tcl" % (set_idx, combidx))
                with open("out_complete_2/com_%d_%d.sv" % (set_idx, combidx), "w") as f:
                    f.write(h_)
                    s = ""
                    for pl in cv_perflocs:
                        if not pl in aSet:
                            f.write(no_s1_t.format(s1=pl))
                        else:
                            f.write(hpn_reg_t2.format(s1=pl))
                            s += "{s1}_hpn && ".format(s1=pl)
                    s += "1'b1 "
                    f.write("wire set_r = %s;\n" % s)

                    for e in cv_edge_comb:
                        t_ = e[1]
                        p = e[0]
                        assert(not("___final" in p[0] or "___final" in p[1]))

                        if t_ == '>':
                            f.write(A_enter_hb_enter.format(e0=p[0], e1=p[1]))
                        if t_ == '<':
                            f.write(A_enter_hb_enter.format(e0=p[1], e1=p[0]))
                        if t_ == '=':
                            f.write(A_enter_concur_enter.format(e0=p[0], e1=p[1]))

                    for k, v in pairs_final.items():
                        for tt in v:
                            if ">" == tt:
                                if '___final' in k[0] and '___final' in k[1]:
                                    f.write(C_final_hb_final.format(e0nm=k[0], e1nm=k[1], e0=k[0][:-8], e1=k[1][:-8]))
                                elif '___final' in k[0] and (not '___final' in k[1]):
                                    f.write(C_final_hb_enter.format(e0nm=k[0], e1nm=k[1], e0=k[0][:-8], e1=k[1]))
                                elif (not '___final' in k[0]) and '___final' in k[1]:
                                    f.write(C_enter_hb_final.format(e0nm=k[0], e1nm=k[1], e0=k[0], e1=k[1][:-8]))
                                else:
                                    assert(0)

                            elif "<" == tt:
                                if '___final' in k[1] and '___final' in k[0]:
                                    f.write(C_final_hb_final.format(e0nm=k[1], e1nm=k[0], e0=k[1][:-8], e1=k[0][:-8]))
                                elif '___final' in k[1] and (not '___final' in k[0]):
                                    f.write(C_final_hb_enter.format(e0nm=k[1], e1nm=k[0], e0=k[1][:-8], e1=k[0]))
                                elif (not '___final' in k[1]) and '___final' in k[0]:
                                    f.write(C_enter_hb_final.format(e0nm=k[1], e1nm=k[0], e0=k[1], e1=k[0][:-8]))
                                else:
                                    assert(0)
                            else:
                                if '___final' in k[0] and '___final' in k[1]:
                                    f.write(C_final_concur_final.format(e0nm=k[0], e1nm=k[1], e0=k[0][:-8], e1=k[1][:-8]))
                                elif '___final' in k[0] and (not '___final' in k[1]):                                      
                                    f.write(C_final_concur_enter.format(e0nm=k[0], e1nm=k[1], e0=k[0][:-8], e1=k[1]))
                                elif (not '___final' in k[0]) and '___final' in k[1]:                                      
                                    f.write(C_enter_concur_final.format(e0nm=k[0], e1nm=k[1], e0=k[0], e1=k[1][:-8]))
                                else:
                                    assert(0)

        
    #print("cnt todo:", cnt_todo_cover)
    print("cnt_todo_cover_final", cnt_todo_cover_final)

if len(sys.argv) < 2:
    print("gen/pp/stats")
    exit(0)

opt = sys.argv[1]
if opt == "gen":
    gen()
elif opt == "pp":
    pp()
elif opt == "stats":
    stats()
        
