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
def MYGRAPHING(
    dotfilenm,
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
    WEIGHTED=False, 
    edge_weight_result=None,
    edge_weight_single_in=[]
    ):

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

    edge_weight_single = edge_weight_single_in
    for e in implied_edges_same_iid:
        DG.add_edge(*e)

    for itm in leaving_hb_proven_res_pairs:
        if itm[0] in DG.nodes() and itm[1] in DG.nodes():
            DG.add_edge(itm[0], itm[1])


    #for itm in whb_edge:
    #    pass
    for itm in whb_finals + whb_edge:
        if not(itm[0] in DG.nodes() and itm[1] in DG.nodes()):
            continue
        if not slv.check_imp_concur(itm):
            DG.add_edge(itm[0], itm[1])
            print("ADD EDGE TEST1", itm[0], itm[1])

        
        #if [itm[0], itm[1]] in concur_in_comb or  \
        #    [itm[1], itm[0]] in concur_in_comb or \
        #    (itm[0], itm[1]) in concur_in_comb or \
        #    (itm[1], itm[0]) in concur_in_comb:
        #        continue
    # concurrent tagged through same color 

    color_cnt=4
    node_colors = {}

   

    for e in enter_concurrent_pairs + aws_concur_leaving_pairs + concur_in_comb:
        a, b = e
        if not (a in DG.nodes() and b in DG.nodes()):
            continue

        c = None
        if a in node_colors:
            c = node_colors[a]
        elif b in node_colors:
            c = node_colors[b]

        if c is None:
            c = color_cnt
            color_cnt += 1
        
        node_colors[a] = c
        node_colors[b] = c

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


    g = dot_header 
    g += label_s

    for itm in list(DG.nodes):
        if itm in node_colors:
            g += uhb_node_color.format(color=color_names[node_colors[itm]], 
                                        nm=itm, loc=node_rows[itm])
        else:
            g += uhb_node.format(nm=itm, loc=node_rows[itm])
    for e in TR.edges():
        if not WEIGHTED:
            if e in edge_weight:
                cyc_e = edge_weight[e]
                cyc_e_s = "{" + ",".join([str(r) for r in cyc_e]) + "}(OVERAPPROX)"
                g += uhb_edge_label.format(color=color_names[2], u=e[0], v=e[1], 
                        e_s=textwrap.fill(cyc_e_s, 20))
            else:
                g += uhb_edge.format(color="black", u=e[0], v=e[1])
        else:
            if e in edge_weight:
                cyc_e = [] #edge_weight[e]
                var_e, covered_set = edge_weight_result

                for itm in covered_set:
                    idx = var_e.index((e[0], e[1]))
                    cyc_e.append(itm[idx])
                print("CCCC ", e, cyc_e)
                cyc_e_s = "{" + ",".join([str(r) for r in cyc_e]) + "}"
                g += uhb_edge_label.format(color="darkgreen", u=e[0], v=e[1], 
                        e_s=textwrap.fill(cyc_e_s, 20))
            elif e in edge_weight_single:
                g += uhb_edge_label.format(color="black", u=e[0], v=e[1], e_s="1_")
            else:
                g += uhb_edge_label.format(color="black", u=e[0], v=e[1], e_s="")
            # real weighted        


    g += "}"
    ################################################################################ 

    png_file = dotfilenm.split(".")[0] + ".png"
    with open(dotfilenm, "w") as f:
        f.write(g)
    os.system("dot -Tpng %s -o %s" % (dotfilenm, png_file))

