import re
import networkx as nx
from itertools import chain, combinations
import textwrap
import pandas as pd
import numpy as np
import os
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
    cnt_todo_cover = 0
    for set_idx, aSet in enumerate(reachable_sets):
        print("===== SET idx: %d ====" % set_idx)
        DG = nx.DiGraph()

        for e in hb_edge:
            if e[0] in aSet and e[1] in aSet:
                DG.add_edge(e[0], e[1])


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
            
                # since its same ufsm, if entering e[0] happens-before entering
                # e[1], leaving e[0] should also happens-before entering e[1]
                for e in DG.out_edges(itm):
                    if iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
                        implied_edges_same_iid.append((itm + "___final", e[1]))
                    
                DG.add_edge(itm, itm + "___final") 
        



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

        for e in enter_concurrent_pairs + aws_concur_leaving_pairs:
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

        TR = nx.transitive_reduction(DG) #, reflexive=False)
        TC = nx.transitive_closure(DG, reflexive=False)
        reduce_e = list(TR.edges)

        ################################################################################ 
        # setup solver 
        ################################################################################ 
        slv = MySolver(TR, edge_weight, implied_edges_same_iid, iid_map_tmp,
                edge_weight_single, enter_concurrent_pairs +
                aws_concur_leaving_pairs, whb_edge)
        slv.add_constraints()

        ################################################################################ 
        # Get all edges that is not proven 
        ################################################################################ 
        pairs_todo = {}
        for idx, e in enumerate(edge):
            if not (e[0] in aSet and e[1] in aSet):
                continue

            # e[0] enter v.s e[1] enter
            if tuple(e) in TC.edges() or (e[1], e[0]) in TC.edges():
                continue
            #if e in edge_weight_single or (e[1], e[0]) in edge_weight_single:
            #    continue
            if e in enter_concurrent_pairs or [e[1], e[0]] in enter_concurrent_pairs: 
                continue
            if slv.check_imp_hb(e):
                print("set idx %d imp hb %s %s" % (set_idx, e[0], e[1]))
                continue

            can_be_hb = slv.check_hb_possibility(e)
            if not can_be_hb:
                print("set idx %d imp can't be hb %s %s" % (set_idx, e[0], e[1]))
                continue
            
            if e[0] < e[1]:
                if (e[0], e[1]) in pairs_todo:
                    # e[0] HB e[1]
                    pairs_todo[(e[0], e[1])].append(">")
                else:
                    pairs_todo[(e[0], e[1])] = [">", "="]
            else:
                if (e[1], e[0]) in pairs_todo:
                    pairs_todo[(e[1], e[0])].append("<")
                else:
                    pairs_todo[(e[1], e[0])] = ["<", "="]
               
            #print("%d Issue: %s %s" % (set_idx, e[0], e[1]))

        print("Issue %d" % set_idx)
        pairs_todo_pruned = {}
        cnt_setidx = 0
        for k, v in pairs_todo.items():
            #if k in undetermined_hb:
            #    if "<" in v:
            #        v.remove("<")
            #    if "=" in v:
            #        v.remove("=")
            #if (k[1], k[0]) in undetermined_hb:
            #    if ">" in v:
            #        v.remove(">")
            #    if "=" in v:
            #        v.remove("=")
            #if k in undetermined_concur or (k[1], k[0]) in undetermined_concur:
            #    if ">" in v:
            #        v.remove(">")
            #    if "<" in v:
            #        v.remove("<")
            #
            #if k in undetermined_whb:
            #    if "<" in v:
            #        v.remove("<")
            #if (k[1], k[0]) in undetermined_whb:
            #    if ">" in v:
            #        v.remove(">")

            pairs_todo_pruned[k] = v
            print("(%s, %s): %s" % (k[0], k[1], ",".join(v)))
            cnt_todo_cover += len(v)
            cnt_setidx += len(v)
        print("========================================")
        with open("%d_edge_todo_per_set.txt" % set_idx, "w") as f:
            for k, v in pairs_todo.items():  
                f.write("%s,%s:%s\n" % (k[0], k[1], ",".join(v)))  

        if not os.path.isdir("out_complete"):
            os.mkdir("out_complete")
        
        if cnt_setidx != 0:
            os.system("cp ./prove_from.tcl out_complete/com_%d.tcl" % set_idx)
            with open("out_complete/com_%d.sv" % set_idx, "w") as f:
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
                for k, v in pairs_todo_pruned.items():
                    for tt in v:
                        if ">" == tt:
                            f.write(C_hb_prop.format(e0=k[0], e1=k[1]))
                        elif "<" == tt:
                            f.write(C_hb_prop.format(e0=k[1], e1=k[0]))
                        else:
                            f.write(C_concur_prop.format(e0=k[1], e1=k[0]))









        ################################################################################# 
        ## For those nodes that can be greater than 1 cyclers generate all
        ## combination they potentially will cover
        ################################################################################# 
        #var_cnt = 0
        #var_values = []
        #var_e = []
        #possible_cnt = 1
        #for e in reduce_e:
        #    if e in edge_weight:
        #        var_cnt += 1
        #        var_values.append(len(edge_weight[e]))
        #        possible_cnt = possible_cnt * len(edge_weight[e])
        #        assert(not e in var_e)
        #        var_e.append(e)
        #print('var values', var_values)
        #print('var e', var_e)

        #for whbitm in undetermined_whb:
        #    if whbitm[0] in TR.nodes() and whbitm[1] in TR.nodes():
        #        aws_at_same_time = False
        #        aws_hb = False
        #        slv.push()
        #        slv.add_at_same_time(whbitm)
        #        if slv.test_unsat():
        #            # always at same time
        #            aws_at_same_time = True
        #        slv.pop()
        #        slv.push()
        #        slv.add_hb(whbitm)
        #        if slv.test_unsat():
        #            # always at same time
        #            aws_hb = True
        #        slv.pop()

        #        if aws_at_same_time:
        #            continue
        #        elif aws_hb:
        #            continue
        #        else:
        #            print("set idx %d UNDET WHB itm %s %s" % (set_idx, whbitm[0], whbitm[1]))

        #if not nx.is_weakly_connected(TR):
        #    print("set idx %d is not connected " % set_idx)
        #    for whbitm in undetermined_hb:
        #        necessary=False
        #        tmpTR = TR.copy()
        #        tmpTR.add_edge(*whbitm)
        #        if nx.is_weakly_connected(tmpTR):
        #            necessary=True
        #        if necessary:
        #            print("set idx %d UNDET HB need itm %s %s" % (set_idx, whbitm[0], whbitm[1]))
        #    for whbitm in undetermined_whb:
        #        necessary=False
        #        tmpTR = TR.copy()
        #        tmpTR.add_edge(*whbitm)
        #        if nx.is_weakly_connected(tmpTR):
        #            necessary=True
        #        if necessary:
        #            print("set idx %d UNDET WHB need itm %s %s" % (set_idx, whbitm[0], whbitm[1]))

        #    for whbitm in undetermined_concur:
        #        necessary=False
        #        tmpTR = TR.copy()
        #        in_edges = tmpTR.in_edges(whbitm[0])
        #        for e_prime in in_edges:
        #            tmpTR.add_edge(e_prime[0], whbitm[1])

        #        in_edges = tmpTR.in_edgese(whbitm[1])
        #        for e_prime in in_edges:
        #            tmpTR.add_edge(e_prime[0], whbitm[0])

        #        if nx.is_weakly_connected(tmpTR):
        #            necessary=True
        #        if necessary:
        #            print("set idx %d UNDET concur need itm %s %s" % (set_idx, whbitm[0], whbitm[1]))



        #if is_interference_case:
        #    # Each node just reference from max_per_pl and enumerate on IUV case
        #    # timing differentiability should not be effected?!
        #    with open("%d_cycle_count_todo.txt" % set_idx, "w") as f:       
        #        for e in var_e:
        #            f.write("%s,%s," % (e[0], e[1]))
        #else:
        #    print("ENUMERATE all combintaions :/ ? ")

        #    comb_obj = GenComb(var_values)
        #    comb_obj.gen()

        #    if var_cnt > 1: #<= 1:
        #        print("var cnt greater than 1!")
        #    # Explore all possible cycle count set..
        #    todo_possible_set = []
        #    remove_cnt = 0
        #    for a_comb in comb_obj.res:
        #        # list of e_weight
        #        slv.push()
        #        for e, cyc in zip(var_e, a_comb):
        #            slv.add_e_cyc(e, cyc)
        #        if slv.test_added_es():
        #            todo_possible_set.append(a_comb)
        #        else:   
        #            remove_cnt += 1
        #        slv.pop()
        #    with open("%d_cycle_count_remove_cnt.txt" % set_idx, "w") as f:
        #        f.write("%s\n" % remove_cnt)
        #    with open("%d_cycle_count_todo.txt" % set_idx, "w") as f:       
        #        for e in var_e:
        #            f.write("%s,%s," % (e[0], e[1]))
        #        if len(todo_possible_set) > 0:
        #            f.write("\n")
        #        for itm in todo_possible_set:
        #            for cyc in itm:
        #                f.write("%d," % cyc)
        #            f.write("\n")
        #            path_cnt += 1
        #    if len(todo_possible_set) == 0:
        #        path_cnt = 1

         
        #if possible_cnt > 200:
        #    print("!!! skip combination enumerate and test %d" % possible_cnt)
        #    with open("%d_cycle_count_remove_cnt.txt" % set_idx, "w") as f:
        #        f.write("0\n")
        #    with open("%d_cycle_count_todo.txt" % set_idx, "w") as f:       
        #        for e in var_e:
        #            f.write("(%s,%s)," % (e[0], e[1]))
        #        f.write("\n")
        #        for itm in var_values:
        #            f.write("%d\n" % itm)

        #    path_cnt += possible_cnt
        #else:
        #    print("ENUMERATE all combintaions :/ ? ")

        #    comb_obj = GenComb(var_values)
        #    comb_obj.gen()
        #    #print("list_cyc_comb ", comb_obj.res)

        #    if var_cnt > 1: #<= 1:
        #        print("var cnt greater than 1!")
        #    # Explore all possible cycle count set..
        #    todo_possible_set = []
        #    remove_cnt = 0
        #    for a_comb in comb_obj.res:
        #        # list of e_weight
        #        slv.push()
        #        for e, cyc in zip(var_e, a_comb):
        #            slv.add_e_cyc(e, cyc)
        #        if slv.test_added_es():
        #            todo_possible_set.append(a_comb)
        #        else:   
        #            remove_cnt += 1
        #        slv.pop()
        #    with open("%d_cycle_count_remove_cnt.txt" % set_idx, "w") as f:
        #        f.write("%s\n" % remove_cnt)
        #    with open("%d_cycle_count_todo.txt" % set_idx, "w") as f:       
        #        for e in var_e:
        #            f.write("(%s,%s)," % (e[0], e[1]))
        #        f.write("\n")
        #        for itm in todo_possible_set:
        #            for cyc in itm:
        #                f.write("%d," % cyc)
        #            f.write("\n")
        #            path_cnt += 1
        #    if len(todo_possible_set) == 0:
        #        path_cnt = 1

        ################################################################################# 
        ## Get list of edge having no weight (if solver prove 1 cycle then no need
        ## to assert, otherwise assert 1cyc)
        ################################################################################# 
        #edge_weight_todo = []
        #edge_weight_export = []
        #edge_weight_mustbe1cyc = []
        #for e in reduce_e: #list(TR.edges):
        #    if (e in edge_weight) or \
        #       (e in implied_edges_same_iid) or \
        #       (iid_map_tmp[e[0]] == iid_map_tmp[e[1]]) or \
        #       (e in edge_weight_single):
        #        continue 
        #    edge_weight_todo.append((e[0], e[1]))

        #for itm in edge_weight_todo:
        #    if slv.test_e_1cyc(itm):
        #        print("(%s,%s) is 1 cyc!" % itm)
        #        edge_weight_mustbe1cyc.append(itm)
        #    else:
        #        edge_weight_export.append(itm)

        #with open("%d_1cyc_edge_weight_todo.txt" % set_idx, "w") as f:
        #    for itm in edge_weight_export: #edge_weight_todo:
        #        f.write("%s,%s\n" % itm)
        #with open("%d_edge_weight_mustbe1cyc.txt" % set_idx, "w") as f:
        #    for itm in edge_weight_mustbe1cyc:
        #        f.write("%s,%s\n" % itm)

        ################################################################################ 
        # build the graph
        ################################################################################ 

        #g = dot_header 
        #g += label_s

        #for itm in list(DG.nodes):
        #    if itm in node_colors:
        #        g += uhb_node_color.format(color=color_names[node_colors[itm]], 
        #                                    nm=itm, loc=node_rows[itm])
        #    else:
        #        g += uhb_node.format(nm=itm, loc=node_rows[itm])

        #for e in reduce_e: #list(TR.edges):
        #    if e in edge_weight:
        #        cyc_e = edge_weight[e]
        #        cyc_e_s = "{" + ",".join([str(r) for r in cyc_e]) + "}(TODO!!)"
        #        g += uhb_edge_label.format(color=color_names[2], u=e[0], v=e[1], 
        #                e_s=textwrap.fill(cyc_e_s, 20))
        #    # same iid only one state and since we assume no re-entering the
        #    # transition edge must be one cycle
        #    elif e in implied_edges_same_iid:
        #        g += uhb_edge_label.format(color=color_names[1], u=e[0], v=e[1],
        #                e_s="1")
        #    elif iid_map_tmp[e[0]] == iid_map_tmp[e[1]]:
        #        g += uhb_edge_label.format(color=color_names[1], u=e[0], v=e[1],
        #                 e_s="1_")
        #    else:
        #        c_ = color_names[0]
        #        if e in leaving_hb_proven_res_pairs:
        #            c_ = color_names[3]
        #        e_s = None
        #        if e in edge_weight_single:
        #            g += uhb_edge_label.format(color=c_, u=e[0], v=e[1], e_s="1_heuristic")
        #        else:
        #            if e in edge_weight_mustbe1cyc:
        #                g += uhb_edge_label.format(color=color_names[4], u=e[0], v=e[1], e_s="1_slv")
        #            else:
        #                c_ = "red"
        #                g += uhb_edge.format(color=c_, u=e[0], v=e[1])
        #                print("NO EDGE WEIGHT", e)

        ##print(hb_edge)
        #g += "}"
        ################################################################################# 

        #dot_file = "hb_%d.dot" % set_idx
        #pdf_file = "hb_%d.png" % set_idx
        #with open("hb_%d.dot" % set_idx , "w") as f:
        #    f.write(g)
        #os.system("dot -Tpng %s -o %s" % (dot_file, pdf_file))


        #trans_closure = nx.transitive_closure(DG)
        #for idx, e in enumerate(edge):
        #    if not (e[0] in aSet and e[1] in aSet):
        #        continue

        #    # consider e in aSet that is not yet handled...
        #    if e in trans_closure.edges() or (e[1], e[0]) in trans_closure.edges():
        #        continue
        #    if e in edge_weight_single or (e[1], e[0]) in edge_weight_single:
        #        continue
        #    if e in enter_concurrent_pairs or (e[1], e[0]) in enter_concurrent_pairs: 
        #        continue

        #    print("%d Issue: %s %s" % (set_idx, e[0], e[1]))

    print("cnt todo:", cnt_todo_cover)
    ##os.system("dot -Tpdf legend.dot -o legend.pdf")
    #with open("potential_path_cnt.txt", "w") as f:
    #    print("PATH COUNT: %d" % path_cnt, file=f)

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
        
