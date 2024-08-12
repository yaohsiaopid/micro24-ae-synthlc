import re
import networkx as nx
from itertools import chain, combinations
import pandas as pd
import numpy as np
import os
import pandas as pd
import sys
sys.path.append("../../src")
from util import *
from HB_template import *
HEADERFILE="../header.sv"
h_ = ""
with open(HEADERFILE, "r") as f:
    for line in f:
        h_ += line

cv_perflocs = get_array("../xCoverAPerflocDiv/cover_individual.txt")
edge = get_array("../../xGenPerfLocDfgDiv/dfg_e.txt")

pl_signals = {}
with open("../../../xDUVPLs/perfloc_signals.txt", "r") as f:
    for line in f:
        pl, sigs = line[:-1].split(" : ")
        pl_signals[pl] = sigs.split(",")
iid_map = {}
for k, v in pl_signals.items():
    #print(k, v[0])
    iid_map[k] = v[0]
#print(pl_signals)
################################################################################
## Before update on PERFLOC EXCLUSIVENESS
################################################################################
#node_implications = get_array("../xPairwiseDepDiv/implication_pl.txt")
#node_implication_iid = {}
#for itm in node_implications:
#    # u implies v
#    u, v = itm 
#    if set(pl_signals[v]).issubset(set(pl_signals[u])):
#        #node_implication_iid.append(itm)
#        # not v mean either (enter u or not v)
#        node_implication_iid[v] = node_implication_iid.get(v, []) + [u]
#
################################################################################
## performing locations of same iid are exclusive of each other 
################################################################################
#node_implications = get_array("../xPairwiseDepDiv/implication_pl.txt")
node_implications = []
node_implication_iid = {}
################################################################################

#print("node implication iid: ", node_implication_iid)
enter_concurrent_pairs = get_array("../xHBPerfG_dfg_v3_div/aws_concurrent.txt")
whb_edge = get_array("../xHBPerfG_dfg_v3_div/whb_proven.txt")
hb_edge = get_array("../xHBPerfG_dfg_v3_div/hb_proven.txt")
reachable_sets = get_array("../xPerfLocSubsetDiv/reachable_set.txt", arr_as_ele = True)
TC_per_set = []
for itm in reachable_sets:
    DG = nx.DiGraph()
    for hb_e in hb_edge:
        if hb_e[0] in itm and hb_e[1] in itm:
            DG.add_edge(hb_e[0], hb_e[1])

    tmp_TC = nx.transitive_closure(DG, reflexive=False)
    TC_per_set.append(tmp_TC)

aggDG = nx.DiGraph(hb_edge)
aggTC = nx.transitive_closure(aggDG, reflexive=False)    

#print("edges: ", len(edge))
properties = ""
def gen():
    if not os.path.isdir("out"):
        os.mkdir("out")
    #over1cyc_over_all_pl, perset_pl_cyc = \
    #    get_cyc_list_from_fname("../xPerfLocCycleCount/cycle_count.txt")
    max_cycle_per_pl = get_array("../xPerfLocCycleCount/max_cycle_per_pl.txt")
    over1cyc_over_all_pl = set()
    for itm in max_cycle_per_pl:
        if int(itm[1]) > 1:
            over1cyc_over_all_pl.add(itm[0])
    cnt = 0

    consider_edge = []
    # only check when those nodes can stick over 1 cycle we don't yet assume fixed set here


    over1cyc_pl = over1cyc_over_all_pl
    for idx, e in enumerate(edge):

        in_aset = False
        for aSet in reachable_sets:
            if e[0] in aSet and e[1] in aSet:
                in_aset = True
        if not in_aset:
            continue

        outf = None
        fnm = "out/HB_LEAVING_%d.sv" % cnt
        if not (e[0] in cv_perflocs and e[1] in cv_perflocs):
            continue
        if not ((e[0] in over1cyc_pl)  or (e[1] in over1cyc_pl)):
            continue
        if ((e[0], e[1]) in node_implications) and ((e[1], e[0]) in node_implications):
            print("IFF on %s %s" % (e[0], e[1]))
            continue
        if iid_map[e[0]] == iid_map[e[1]]:
            #print("same iid, leaving order is same as enter order: %s %s" % (e[0], e[1]))
            continue


        # not_s1
        not_s1 = "(!%s)" % e[0]
        if e[0] in node_implication_iid:
            s_tmp = ""
            for itm in node_implication_iid[e[0]]:
                s_tmp = itm + " || " 
            s_tmp += " 0"
            not_s1 = "(" + s_tmp + ")" + " || " + not_s1

        # not_s2
        not_s2 = "(!%s)" % e[1]
        if e[1] in node_implication_iid:
            s_tmp = ""
            for itm in node_implication_iid[e[1]]:
                s_tmp = itm + " || " 
            s_tmp += " 0"
            not_s2 = "(" + s_tmp + ")" + " || " + not_s2

        def mod_f(outf, s):
            if outf is None:
                #if not e in yosys_edge:
                #    fnm = fnm + ".txt" 
                outf = open(fnm, "w") #"out/HB_LEAVING_%d.sv" % cnt, "w")
                outf.write(h_)
                outf.write(hpn_reg_t.format(s1=e[0], s2=e[1]))
                if e[1] in over1cyc_pl:
                    outf.write(assume_s2_over_2cyc.format(s2=e[1]))
                #outf.write(assume_path_sv(cv_perflocs, aSet))
            outf.write(s)
            return outf

        if e[0] in over1cyc_pl:
            # check leaving e[0] happens-before entering e[1]

            # either all PL set having the edge should transitively implied e[1]
            # hb e[0] otherwise we need to check
            e_in_tc_edge = True
            for tmpTC in TC_per_set:
                if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                    e_in_tc_edge = e_in_tc_edge and ((e[1], e[0]) in tmpTC.edges())

            #if (e[1], e[0]) in TC.edges() or  \
            #   ((e[1], e[0]) in enter_concurrent_pairs):

            if (e[1], e[0]) in aggTC.edges() and not e_in_tc_edge:
                print("PROBLEM ????", e[1], e[0])

            if ((e[1], e[0]) in enter_concurrent_pairs):
                print("enter %s already happens-before entering %s " %  \
                (e[1], e[0]))
            elif e_in_tc_edge:
                print("enter %s already happens-before entering %s all tc edges" %  \
                (e[1], e[0]))
            else: 

                outf = mod_f(outf, HB_leaving_s1_hb_s2.format(
                        not_s1 = not_s1, s1 = e[0], s2 = e[1])) 

        if e[1] in over1cyc_pl:
            # checking enter e[0] happens-before leaving e[1]
            # if enter e[0] always happen before e[1] then we don't need to
            # do so since it's already implied that e[0] happens-before
            # leaving e[1]
            #if (not ((e[0], e[1]) in TC.edges())) and \
            #   (not ((e[0], e[1])) in enter_concurrent_pairs):

            e_in_tc_edge = True
            for tmpTC in TC_per_set:
                if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                    e_in_tc_edge = e_in_tc_edge and ((e[0], e[1]) in tmpTC.edges())

            if (e[0], e[1]) in aggTC.edges() and not e_in_tc_edge:
                print("PROBLEM ????", e[0], e[1])

            if ((e[0], e[1]) in enter_concurrent_pairs):
                print("enter %s already happens-before entering %s " %  \
                (e[0], e[1]))
            elif e_in_tc_edge:
                print("enter %s already happens-before entering %s all tc edges" %  \
                (e[0], e[1]))
            else: 
                outf = mod_f(outf, HB_s1_hb_leaving_s2.format(
                    s1=e[0], s2=e[1], not_s2=not_s2))
                
        if e[0] in over1cyc_pl and e[1] in over1cyc_pl:
            # checking leaving e[0] happens-before leaving e[0]
            outf = mod_f(outf, HB_leaving_s1_hb_leaving_s2.format(
                    s1=e[0], s2=e[1], not_s1=not_s1, not_s2=not_s2))

        if outf is not None:
            #if e in yosys_edge:
            consider_edge.append((e[0], e[1], cnt))
            outf.close()
            cnt += 1
    with open("check_e.txt", "w") as f:
        for itm in consider_edge:
            f.write("%s,%s,%d\n" % itm)


def gen_s2():
    #over1cyc_over_all_pl, perset_pl_cyc = \
    #    get_cyc_list_from_fname("../xPerfLocCycleCount/cycle_count.txt")
    max_cycle_per_pl = get_array("../xPerfLocCycleCount/max_cycle_per_pl.txt")
    over1cyc_over_all_pl = set()
    for itm in max_cycle_per_pl:
        if int(itm[1]) > 1:
            over1cyc_over_all_pl.add(itm[0])

    over1cyc_pl = over1cyc_over_all_pl

    consider_edge = {}
    with open("check_e.txt", "r") as f:
        for line in f:
            itm = line[:-1].split(",")
            #assert(len(itm) == 4)
            assert(len(itm) == 3)
            consider_edge[(itm[0], itm[1])] = int(itm[2]) #(int(itm[2]), int(itm[3]))

    whb_edge_todo = []
    cnt = 0
    for e, v in consider_edge.items():
        csv_ = pd.read_csv("HB_LEAVING_%d.csv" % v)
        csv_noprecon = csv_[~csv_['Name'].str.contains("precondition")]
        csv_percond = csv_[csv_['Name'].str.contains("precondition")]
        fnm = "out/WHB_LEAVING_%d.sv" % v

        outf = None

        # not_s1
        not_s1 = "(!%s)" % e[0]
        if e[0] in node_implication_iid:
            s_tmp = ""
            for itm in node_implication_iid[e[0]]:
                s_tmp = itm + " || " 
            s_tmp += " 0"
            not_s1 = "(" + s_tmp + ")" + " || " + not_s1

        # not_s2
        not_s2 = "(!%s)" % e[1]
        if e[1] in node_implication_iid:
            s_tmp = ""
            for itm in node_implication_iid[e[1]]:
                s_tmp = itm + " || " 
            s_tmp += " 0"
            not_s2 = "(" + s_tmp + ")" + " || " + not_s2

        def mod_f(outf, s):
            if outf is None:
                outf = open(fnm, "w") #"out/HB_LEAVING_%d.sv" % cnt, "w")
                outf.write(h_)
                outf.write(hpn_reg_t.format(s1=e[0], s2=e[1]))
                outf.write("`define WHB\n")
                #outf.write(assume_path_sv(cv_perflocs, aSet))
            outf.write(s)
            return outf

        e_in_tc_edge = True
        for tmpTC in TC_per_set:
            if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                e_in_tc_edge = e_in_tc_edge and ((e[1], e[0]) in tmpTC.edges())

        if (e[1], e[0]) in aggTC.edges() and not e_in_tc_edge:
            print("PROBLEM ????", e[1], e[0])


        if e[0] in over1cyc_pl and not (
                e_in_tc_edge or 
               ((e[1], e[0]) in enter_concurrent_pairs)
              #  (e[1], e[0]) in TC.edges() or 
              # ((e[1], e[0]) in enter_concurrent_pairs)
            ):
            # check leaving e[0] happens-before entering e[1]
            #HB_leaving_s1_hb_s2
            prop = "HB_LEAVING_{s1}_{s2}".format(s1=e[0], s2=e[1])
            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            res = res['Result']
            if res.values[0] == "cex":
                print("PROP whb: ", prop)
                # not_s1
                not_s1 = "(!%s)" % e[0]
                if e[0] in node_implication_iid:
                    s_tmp = ""
                    for itm in node_implication_iid[e[0]]:
                        s_tmp = itm + " || " 
                    s_tmp += " 0"
                    not_s1 = "(" + s_tmp + ")" + " || " + not_s1

                outf = mod_f(outf, HB_leaving_s1_hb_s2.format(
                        not_s1 = not_s1, s1 = e[0], s2 = e[1]))
            elif res.values[0] == "undetermined":
                print("UNDETERMINED ", prop) 
                
        e_in_tc_edge = True
        for tmpTC in TC_per_set:
            if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                e_in_tc_edge = e_in_tc_edge and ((e[0], e[1]) in tmpTC.edges())

        if (e[0], e[1]) in aggTC.edges() and not e_in_tc_edge:
            print("PROBLEM ????", e[0], e[1])

        # checking e[0] enters happens-before leaving e[1]
        #not ((e[0], e[1]) in TC.edges())) and \
        if e[1] in over1cyc_pl and \
           (not e_in_tc_edge) and \
           (not ((e[0], e[1])) in enter_concurrent_pairs):

            prop = "HB_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            res = res['Result']
            if res.values[0] == "cex":
                outf = mod_f(outf, HB_s1_hb_leaving_s2.format(
                    s1=e[0], s2=e[1], not_s2=not_s2))
            elif res.values[0] == "undetermined":
                print("UNDETERMINED ", prop) 

        if e[0] in over1cyc_pl and e[1] in over1cyc_pl:
            # checking leaving e[0] happens-before leaving e[0]
            prop = "HB_LEAVING_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            res = res['Result']
            if res.values[0] == "cex":
                outf = mod_f(outf, HB_leaving_s1_hb_leaving_s2.format(
                    not_s1=not_s1, not_s2=not_s2,s1=e[0], s2=e[1]))

        if outf is not None:
            whb_edge_todo.append((e[0], e[1], v))
    with open("whb_check_e.txt", "w") as f:
        for itm in whb_edge_todo:
            f.write("%s,%s,%d\n" % itm)

def pp():
    #over1cyc_over_all_pl, perset_pl_cyc = \
    #    get_cyc_list_from_fname("../xPerfLocCycleCount/cycle_count.txt")
    max_cycle_per_pl = get_array("../xPerfLocCycleCount/max_cycle_per_pl.txt")
    over1cyc_over_all_pl = set()
    for itm in max_cycle_per_pl:
        if int(itm[1]) > 1:
            over1cyc_over_all_pl.add(itm[0])
    over1cyc_pl = over1cyc_over_all_pl

    consider_edge = {}
    with open("check_e.txt", "r") as f:
        for line in f:
            itm = line[:-1].split(",")
            assert(len(itm) == 3)
            consider_edge[(itm[0], itm[1])] = int(itm[2])

    agg_res = []

    hb_proven_res = []
    whb_leaving_res = []
    aws_concur_res = []

    for e, v in consider_edge.items():
        fnm = "HB_LEAVING_%d.csv" % v
        assert(os.path.exists(fnm))
        csv_ = pd.read_csv(fnm)
        csv_noprecon = csv_[~csv_['Name'].str.contains("precondition")]
        csv_percond = csv_[csv_['Name'].str.contains("precondition")]
        outf = None
        e_in_tc_edge = True
        for tmpTC in TC_per_set:
            if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                e_in_tc_edge = e_in_tc_edge and ((e[1], e[0]) in tmpTC.edges())
        if e[0] in over1cyc_pl and not (
                e_in_tc_edge or 
        #        (e[1], e[0]) in TC.edges() or 
               ((e[1], e[0]) in enter_concurrent_pairs)
            ):
            # check leaving e[0] happens-before entering e[1]
            #HB_leaving_s1_hb_s2
            prop = "HB_LEAVING_{s1}_{s2}".format(s1=e[0], s2=e[1])
            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            res = res['Result']

            res_precond = csv_percond[csv_percond['Name'].str.contains(prop)]
            res_precond = res_precond['Result']

            agg_res.append((prop, res.values[0], res_precond.values[0]))

            if res.values[0] == "cex":
                prop = "WHB_LEAVING_{s1}_hb_{s2}".format(s1=e[0], s2=e[1])
                csv_whb_org = pd.read_csv("WHB_LEAVING_%d.csv" % v)
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                assert(len(res_lis) == 2)
                agg_res.append((prop, res_lis[0], res_lis[1]))
                if res_lis[0] == "proven" and res_lis[1] == "covered":
                    whb_leaving_res.append((1, e[0], 0, e[1])) # 1 as final , 0 as enter

                prop = "WHB_CONCUR_LEAVING_{s1}_hb_{s2}".format(s1=e[0], s2=e[1])
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                agg_res.append((prop, res_lis[0], res_lis[1]))
                if res_lis[0] == "proven" and res_lis[1] == "covered":
                    aws_concur_res.append((1, e[0], 0, e[1])) # 1 as final , 0 as enter


            elif res.values[0] == "undetermined":
                print("UNDETERMINED ", prop) 
            elif res.values[0] == "proven" and res_precond.values[0] == "covered":
                hb_proven_res.append((1, e[0], 0, e[1])) # 1 as final , 0 as enter
                

        e_in_tc_edge = True
        for tmpTC in TC_per_set:
            if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                e_in_tc_edge = e_in_tc_edge and ((e[0], e[1]) in tmpTC.edges())


       #(not ((e[0], e[1]) in TC.edges())) and \
        if e[1] in over1cyc_pl and \
           (not e_in_tc_edge) and \
           (not ((e[0], e[1])) in enter_concurrent_pairs):
            # checking e[0] enters happens-before leaving e[1]
            prop = "HB_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])

            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            res = res['Result']

            res_precond = csv_percond[csv_percond['Name'].str.contains(prop)]
            res_precond = res_precond['Result']

            agg_res.append((prop, res.values[0], res_precond.values[0]))

            if res.values[0] == "cex":
                prop = "WHB_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb_org = pd.read_csv("WHB_LEAVING_%d.csv" % v)
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                assert(len(res_lis) == 2)
                agg_res.append((prop, res_lis[0], res_lis[1]))
                if res_lis[0] == "proven" and res_lis[1] == "covered":
                    whb_leaving_res.append((0, e[0], 1, e[1])) # 1 as final , 0 as enter

                prop = "WHB_CONCUR_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                print(fnm, prop, res_lis)
                agg_res.append((prop, res_lis[0], res_lis[1]))
                if res_lis[0] == "proven" and res_lis[1] == "covered":
                    aws_concur_res.append((0, e[0], 1, e[1])) # 1 as final , 0 as enter
            
            elif res.values[0] == "undetermined":
                print("UNDETERMINED ", prop) 
            elif res.values[0] == "proven" and res_precond.values[0] == "covered":
                hb_proven_res.append((0, e[0], 1, e[1])) # 1 as final , 0 as enter

        if e[0] in over1cyc_pl and e[1] in over1cyc_pl:
            # checking leaving e[0] happens-before leaving e[0]
            prop = "HB_LEAVING_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            res = res['Result']

            res_precond = csv_percond[csv_percond['Name'].str.contains(prop)]
            res_precond = res_precond['Result']

            agg_res.append((prop, res.values[0], res_precond.values[0]))

            if res.values[0] == "cex":
                prop = "WHB_LEAVING_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb_org = pd.read_csv("WHB_LEAVING_%d.csv" % v)
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                assert(len(res_lis) == 2)
                agg_res.append((prop, res_lis[0], res_lis[1]))
                if res_lis[0] == "proven" and res_lis[1] == "covered":
                    whb_leaving_res.append((1, e[0], 1, e[1])) # 1 as final , 0 as enter

                prop = "WHB_CONCUR_LEAVING_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                if res_lis[0] == "proven" and res_lis[1] == "covered":
                    aws_concur_res.append((1, e[0], 1, e[1])) # 1 as final , 0 as enter
                agg_res.append((prop, res_lis[0], res_lis[1]))

            elif res.values[0] == "undetermined":
                print("UNDETERMINED ", prop) 
            elif res.values[0] == "proven" and res_precond.values[0] == "covered":
                hb_proven_res.append((1, e[0], 1, e[1])) # 1 as final , 0 as enter

    with open("leaving_hb.txt", "w") as f:
        #f.write("prop_name,result,precondition_result\n")
        for itm in agg_res:
            f.write(",".join(itm) + "\n")
    with open("leaving_hb_proven.txt", "w") as f:
        #f.write("final,e[0],final,e[1]\n")
        for itm in hb_proven_res:
            f.write("%d,%s,%d,%s\n" % itm)
        
    with open("leaving_concur_proven.txt", "w") as f:
        #f.write("final,e[0],final,e[1]\n")
        for itm in aws_concur_res:
            f.write("%d,%s,%d,%s\n" % itm)

    with open("leaving_whb_proven.txt", "w") as f:
        #f.write("final,e[0],final,e[1]\n")
        for itm in whb_leaving_res:
            tmp_itm = (itm[2], itm[3], itm[0], itm[1])
            if not (itm in aws_concur_res or tmp_itm in aws_concur_res):
                #print(tmp_itm)
                f.write("%d,%s,%d,%s\n" % itm)

def stats():
    comps = []
    incomps = []

    for f in os.listdir("."):
        if f.endswith(".csv"):
            df = pd.read_csv(f, dtype=mydtypes)
            subdf = df[~df['Name'].str.contains("precondition")]
            subdf = subdf[subdf['Name'].str.contains("HB")]
            for idx, tar_row in subdf.iterrows():
                #precond = \
                #    df[df['Name'].str.contains(tar_row['Name']+":precondition1")]
                #assert(len(precond) == 1)
                #res = precond['Result'].values[0]
                #bnd = precond['Bound'].values[0]
                #sr = re.search("([0-9]+)", bnd)
                #if sr is not None:
                #    bnd = int(sr.group(1))
                #else:
                #    bnd = None
                #time = float(precond['Time'].values[0][:-2])
                #if res in ["covered", "unreachable", "cex", "proven"]:
                #    comps.append(time)
                #else:
                #    incomps.append((time, bnd))

                res = tar_row['Result']
                bnd = tar_row['Bound']
                sr = re.search("([0-9]+)", bnd)
                if sr is not None:
                    bnd = int(sr.group(1))
                else:
                    bnd = None
                time = float(tar_row['Time'][:-2])
                if res.values[0] in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(time)
                else:
                    incomps.append((time, bnd))

    with open("stats.txt", "w") as f:
        f.write("%d,%f\n" % (len(comps), sum(comps)))
        for itm in comps:
            f.write("%f," % itm)
        f.write("\n")
        t = sum([r[0] for r in incomps])
        f.write("%d,%f\n" % (len(incomps), t))
        for itm in incomps:
            f.write("%f," % itm[0])
        f.write("\n")
        for itm in incomps:
            f.write("%d," % itm[1])
        f.write("\n")


def stats2():
    comps = []
    incomps = []
    #over1cyc_over_all_pl, perset_pl_cyc = \
    #    get_cyc_list_from_fname("../xPerfLocCycleCount/cycle_count.txt")
    max_cycle_per_pl = get_array("../xPerfLocCycleCount/max_cycle_per_pl.txt")
    over1cyc_over_all_pl = set()
    for itm in max_cycle_per_pl:
        if int(itm[1]) > 1:
            over1cyc_over_all_pl.add(itm[0])
    over1cyc_pl = over1cyc_over_all_pl

    consider_edge = {}
    with open("check_e.txt", "r") as f:
        for line in f:
            itm = line[:-1].split(",")
            assert(len(itm) == 3)
            consider_edge[(itm[0], itm[1])] = int(itm[2])


    hb_proven_res = []
    whb_leaving_res = []
    aws_concur_res = []

    for e, v in consider_edge.items():
        fnm = "HB_LEAVING_%d.csv" % v
        assert(os.path.exists(fnm))
        csv_ = pd.read_csv(fnm)
        csv_noprecon = csv_[~csv_['Name'].str.contains("precondition")]
        csv_percond = csv_[csv_['Name'].str.contains("precondition")]
        outf = None
        e_in_tc_edge = True
        for tmpTC in TC_per_set:
            if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                e_in_tc_edge = e_in_tc_edge and ((e[1], e[0]) in tmpTC.edges())
        if e[0] in over1cyc_pl and not (
                e_in_tc_edge or 
        #        (e[1], e[0]) in TC.edges() or 
               ((e[1], e[0]) in enter_concurrent_pairs)
            ):
            # check leaving e[0] happens-before entering e[1]
            #HB_leaving_s1_hb_s2
            prop = "HB_LEAVING_{s1}_{s2}".format(s1=e[0], s2=e[1])
            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            time = float(res['Time'].values[0][:-2])
            res = res['Result']
            if res.values[0] in ["covered", "unreachable", "cex", "proven"]:
                comps.append(time)
            else:
                incomps.append((time, -1))

            if res.values[0] == "cex":
                prop = "WHB_LEAVING_{s1}_hb_{s2}".format(s1=e[0], s2=e[1])
                csv_whb_org = pd.read_csv("WHB_LEAVING_%d.csv" % v)
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                time_list = [float(t[:-2]) for t in csv_whb['Time'].values]
                if res_lis[0] in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(time_list[0])
                else:
                    incomps.append((time_list[0], -1))

                prop = "WHB_CONCUR_LEAVING_{s1}_hb_{s2}".format(s1=e[0], s2=e[1])
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                time_list = [float(t[:-2]) for t in csv_whb['Time'].values]
                if res_lis[0] in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(time_list[0])
                else:
                    incomps.append((time_list[0], -1))
                

        e_in_tc_edge = True
        for tmpTC in TC_per_set:
            if e[1] in tmpTC.nodes() and e[0] in tmpTC.nodes():
                e_in_tc_edge = e_in_tc_edge and ((e[0], e[1]) in tmpTC.edges())


       #(not ((e[0], e[1]) in TC.edges())) and \
        if e[1] in over1cyc_pl and \
           (not e_in_tc_edge) and \
           (not ((e[0], e[1])) in enter_concurrent_pairs):
            # checking e[0] enters happens-before leaving e[1]
            prop = "HB_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])

            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            time = float(res['Time'].values[0][:-2])
            res = res['Result']

            if res.values[0] in ["covered", "unreachable", "cex", "proven"]:
                comps.append(time)
            else:
                incomps.append((time, -1))

            res_precond = csv_percond[csv_percond['Name'].str.contains(prop)]
            res_precond = res_precond['Result']


            if res.values[0] == "cex":
                prop = "WHB_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb_org = pd.read_csv("WHB_LEAVING_%d.csv" % v)
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                time_list = [float(t[:-2]) for t in csv_whb['Time'].values]
                if res_lis[0] in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(time_list[0])
                else:
                    incomps.append((time_list[0], -1))

                prop = "WHB_CONCUR_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                time_list = [float(t[:-2]) for t in csv_whb['Time'].values]
                if res_lis[0] in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(time_list[0])
                else:
                    incomps.append((time_list[0], -1))
            

        if e[0] in over1cyc_pl and e[1] in over1cyc_pl:
            # checking leaving e[0] happens-before leaving e[0]
            prop = "HB_LEAVING_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
            res = csv_noprecon[csv_noprecon['Name'].str.contains(prop)]
            time = float(res['Time'].values[0][:-2])
            res = res['Result']

            if res.values[0] in ["covered", "unreachable", "cex", "proven"]:
                comps.append(time)
            else:
                incomps.append((time, -1))

            res_precond = csv_percond[csv_percond['Name'].str.contains(prop)]
            res_precond = res_precond['Result']


            if res.values[0] == "cex":
                prop = "WHB_LEAVING_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb_org = pd.read_csv("WHB_LEAVING_%d.csv" % v)
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                time_list = [float(t[:-2]) for t in csv_whb['Time'].values]
                if res_lis[0] in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(time_list[0])
                else:
                    incomps.append((time_list[0], -1))

                prop = "WHB_CONCUR_LEAVING_{s1}_LEAVING_{s2}".format(s1=e[0], s2=e[1])
                csv_whb = csv_whb_org[csv_whb_org['Name'].str.contains(prop)]
                res_lis = csv_whb['Result'].values
                if res_lis[0] in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(time_list[0])
                else:
                    incomps.append((time_list[0], -1))

    with open("stats.txt", "w") as f:
        f.write("%d,%f\n" % (len(comps), sum(comps)))
        for itm in comps:
            f.write("%f," % itm)
        f.write("\n")
        t = sum([r[0] for r in incomps])
        f.write("%d,%f\n" % (len(incomps), t))
        for itm in incomps:
            f.write("%f," % itm[0])
        f.write("\n")
        for itm in incomps:
            f.write("%d," % itm[1])
        f.write("\n")
if len(sys.argv) != 2:
    print("gen/gen_s2/pp")
    exit(0)

opt = sys.argv[1]
if opt == "gen":
    gen()
elif opt == "gen_s2":
    gen_s2()
elif opt == "pp":
    pp()
elif opt == "stats":
    stats2()
