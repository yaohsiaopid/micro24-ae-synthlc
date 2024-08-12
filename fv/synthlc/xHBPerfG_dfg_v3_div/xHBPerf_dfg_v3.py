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

HEADERFILE='../header.sv'
h_ = ""
with open(HEADERFILE, "r") as f:
    for line in f:
        h_ += line

cv_perflocs = get_array("../xCoverAPerflocDiv/cover_individual.txt")
edge = get_array("../../xGenPerfLocDfgDiv/dfg_e.txt")
reachable_sets = get_array("../xPerfLocSubsetDiv/reachable_set.txt", arr_as_ele = True)

print("edges: ", len(edge))

def gen():
    reachable_nodes = get_array("../xCoverAPerflocDiv/cover_individual.txt")

    if not os.path.isdir("out"):
        print("creating dir out")
        os.mkdir("out")

    for idx, e in enumerate(edge):
        in_aset = False
        for aSet in reachable_sets:
            if e[0] in aSet and e[1] in aSet:
                in_aset = True
        #if in_aset:
        # unfortunately previous bug and to avoid re-evaluate stuffs
        if in_aset: #and e in yosys_edge: 
            with open ("out/HB_%d.sv" % idx, "w") as f:
                f.write(h_)
                f.write(hpn_reg_t.format(s1 = e[0], s2 = e[1], cnt = idx))
                f.write(ENTER_A_HP_ENTER_B_t.format(s1 = e[0], s2 = e[1], cnt = idx))

def gen_s2():
    reachable_nodes = get_array("../xCoverAPerflocDiv/cover_individual.txt")
    print(reachable_nodes )

    whb = []
    shb = []
    undetermined = []
    for idx, e in enumerate(edge):
        in_aset = False
        for aSet in reachable_sets:
            if e[0] in aSet and e[1] in aSet:
                in_aset = True
        if not in_aset:
            continue
        #if not e in yosys_edge:
        #    continue
        #if not (e[0] in reachable_nodes and e[1] in reachable_nodes):
        #    continue

        TMPLT=GLBTOPMOD + ".HB_%d"
        r_, tpt_ = get_result("HB_%d.csv" % idx, TMPLT % idx) #"ariane.HB_%d" % idx)
        print(idx, r_)
        if r_ == "cex":
            print("CHECK FOR WHB for ", e)
            with open ("out/WHB_%d.sv" % idx, "w") as f:
                f.write("`define WHB\n")
                f.write(h_)
                f.write(hpn_reg_t.format(s1 = e[0], s2 = e[1], cnt = idx))
                f.write(ENTER_A_HP_ENTER_B_t.format(s1 = e[0], s2 = e[1], cnt = idx))
            whb.append(e)
        elif r_ == "undetermined":
            print("undetermined?", e[0], e[1])
    with open("whb_todo.txt", "w") as f:
        for e in whb:
            f.write(",".join(e) + "\n")

def pp():
    reachable_nodes = get_array("../xCoverAPerflocDiv/cover_individual.txt")
    whb = get_array("whb_todo.txt")
    hb_ = []
    whb_ = []
    aws_same = []
    undetermined_hb = []
    undetermined_whb = []
    undetermined_concur = []
    per_pl_set = []
    for idx, itm in enumerate(edge):
        if not (itm[0] in reachable_nodes and itm[1] in reachable_nodes):
            continue
        in_aset = False
        for aSet in reachable_sets:
            if itm[0] in aSet and itm[1] in aSet:
                in_aset = True
        if not in_aset:
            continue
        #if not itm in yosys_edge:
        #    continue
        TMPLT=GLBTOPMOD + ".HB_%d"
        r_, t_ = get_result("HB_%d.csv" % idx, TMPLT % idx) #"ariane.HB_%d" % idx)
        if r_ == "ERR":
            print("FAIL HB_%d" % idx)
        if r_ == "cex":
            TMPLT=GLBTOPMOD + ".WHB_%d"
            r2, t2 = get_result("WHB_%d.csv" % idx, TMPLT % idx) #"ariane.WHB_%d" % idx)
            TMPLT=GLBTOPMOD + ".WHB_CONCUR_%d"
            r2_samecyc, t2_samecyc = get_result(
                    "WHB_%d.csv" % idx, TMPLT % idx) #"ariane.WHB_CONCUR_%d" % idx)
            if r2 == "ERR":
                print("FAIL WHB_%d" % idx)
                os.system('grep "WHB_.*proven" %s ' % ("WHB_%d.csv" % idx))
            if r2_samecyc == "ERR":
                print("FAIL WHB_%d" % idx)
                os.system('grep "WHB_.*proven" %s ' % ("WHB_%d.csv" % idx))

            if r2 == "proven":
                whb_.append(itm)
            elif r2 == "undetermined":
                print("WHB_%d %s %s undetermined" % (idx, itm[0], itm[1]))
                undetermined_whb.append(itm)
            if r2 != 'proven':
                per_pl_set.append(itm)

            if r2_samecyc == "proven":
                aws_same.append(itm)
            elif r2_samecyc == "undetermined":
                print("WHB_CONCUR_%d %s %s undetermined" % (idx, itm[0], itm[1]))

                undetermined_concur.append(itm)


        elif r_ == "proven":
            hb_.append(itm)
        elif r_ == "undetermined":
            undetermined_hb.append(itm)
            print("undetermined HB: ", itm)
    #with open("hb_undetermined.txt", "w") as f:
    #    for e in undetermined:
    #        f.write(",".join(e) + "\n")

    with open("hb_proven.txt", "w") as f:
        for e in hb_:
            f.write(",".join(e) + "\n")
    at_the_same_time = []
    for e in whb_:
        if [e[1], e[0]] in whb_:
            at_the_same_time.append(e)
    for e in aws_same:
        if not e in at_the_same_time:
            at_the_same_time.append(e)
    with open("aws_concurrent.txt", "w") as f:
        for itm in at_the_same_time:
            f.write(",".join(itm) + "\n")
        
    with open("whb_proven.txt", "w") as f:
        for e in whb_:
            if not e in at_the_same_time:
                f.write(",".join(e) + "\n")
    with open("undetermined.txt", "w") as f:
        f.write("* undetermined hb\n")
        for itm in undetermined_hb:
            f.write(",".join(itm) + "\n")
        f.write("* undetermined whb\n")
        for itm in undetermined_whb:
            f.write(",".join(itm) + "\n")
        f.write("* undetermined concur\n")
        for itm in undetermined_concur:
            f.write(",".join(itm) + "\n")
    for itm in per_pl_set:
        rev = [itm[1], itm[0]]
        if rev in at_the_same_time or itm in at_the_same_time:
            continue
        if rev in hb_:
            continue
        if rev in whb_:
            print("? ", itm)
            continue
        # a -- dfg --> b but it doesn't constitue any happens-before relation
        # from a to b 
        #print("No particular relation", itm) 

def stats():
    reachable_nodes = get_array("../xCoverAPerflocDiv/cover_individual.txt")
    whb = get_array("whb_todo.txt")
    det_time_point = []
    det_res = []
    hb_ = []
    whb_ = []
    undetermined = []
    #sum_ = 0

    comps = []
    incomps = []
    for idx, itm in enumerate(edge):
        if not itm in whb:
            continue
        if not (itm[0] in reachable_nodes and itm[1] in reachable_nodes):
            continue
        in_aset = False
        for aSet in reachable_sets:
            if itm[0] in aSet and itm[1] in aSet:
                in_aset = True
        if not in_aset:
            continue
        #if not itm in yosys_edge:
        #    continue
        df = pd.read_csv("HB_%d.csv" % idx, dtype=mydtypes)
        res, bnd, time = df_query(df, "HB_%d" % idx)
        if res in ["covered", "unreachable", "cex", "proven"]:
            comps.append(time)
        else:
            incomps.append((time, bnd))

        if res == "cex":

            TMPLT=GLBTOPMOD + ".WHB_%d"
            r2, t2 = get_result("WHB_%d.csv" % idx, TMPLT % idx) #"ariane.WHB_%d" % idx)
            TMPLT=GLBTOPMOD + ".WHB_CONCUR_%d"
            r2_samecyc, t2_samecyc = get_result(
                    "WHB_%d.csv" % idx, TMPLT % idx) #"ariane.WHB_CONCUR_%d" % idx)

            df = pd.read_csv("WHB_%d.csv" % idx, dtype=mydtypes)
            if r2 == "ERR":
                r=df[df['Name'].str.contains("WHB_") & ~(df['Name'].str.contains("precondition"))]
                r=r[~r['Name'].str.contains("CONCUR")]
                print("FAIL WHB_%d.csv" % idx, r['Name'].values[0])
                if len(r) == 1:
                    res=r['Result'].values[0]
                    t = float(r['Time'].values[0][:-2])
                    if res in ["covered", "unreachable", "cex", "proven"]:
                        comps.append(t)
                    else:
                        incomps.append((t, -1))
                else:
                    assert(0)
            else:
                if r2 in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(t2) 
                else:
                    incomps.append((time,-1))
            if r2_samecyc == "ERR":
                r=df[df['Name'].str.contains("WHB_") & ~(df['Name'].str.contains("precondition"))]
                r=r[r['Name'].str.contains("CONCUR")]
                print("FAIL WHB_CONCUR_%d.csv" % idx, r['Name'].values[0])
                if len(r) == 1:
                    res=r['Result'].values[0]
                    t = float(r['Time'].values[0][:-2])
                    if res in ["covered", "unreachable", "cex", "proven"]:
                        comps.append(t)
                    else:
                        incomps.append((t, -1))
                else:
                    assert(0)
            else:
                if r2_samecyc in ["covered", "unreachable", "cex", "proven"]:
                    comps.append(t2_samecyc) 
                else:
                    incomps.append((t2_samecyc,-1))

        #if os.path.exists("WHB_%d.csv" % idx):
        #    #sum_ += get_time_total("WHB_%d.csv" % idx) # "ariane.WHB_%d" % idx)
        #    df = pd.read_csv("WHB_%d.csv" % idx, dtype=mydtypes)
        #    res, bnd, time = df_query(df, "WHB_%d" % idx)
        #    if res in ["covered", "unreachable", "cex", "proven"]:
        #        comps.append(time)
        #    else:
        #        incomps.append((time, bnd))
        #    res, bnd, time = df_query(df, "WHB_CONCUR_%d" % idx)
        #    if res in ["covered", "unreachable", "cex", "proven"]:
        #        comps.append(time)
        #    else:
        #        incomps.append((time, bnd))

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
    stats()
        
