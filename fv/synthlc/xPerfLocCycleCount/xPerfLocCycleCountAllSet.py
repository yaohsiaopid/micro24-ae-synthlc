# 1. for all reachable nodes run max cycle **in no specific sets**
# 2. for nodes with greater than 1 max cycle specialize? 

import networkx as nx
import re
from itertools import chain, combinations
import pandas as pd
import numpy as np
import os
import pandas as pd
import sys
sys.path.append("../../src")
from util import *
from HB_template import *


cv_perflocs = get_array("../xCoverAPerflocDiv/cover_individual.txt")
reachable_sets = get_array("../xPerfLocSubsetDiv/reachable_set.txt", arr_as_ele = True)
#interference = False
#cwd = os.getcwd()
#if "III" in cwd:
#    print("interference case")
#    interference = True

interference = True
HEADERFILE="../header.sv"
h_ = ""
with open(HEADERFILE, "r") as f:
    for line in f:
        h_ += line

def gen():
    if not os.path.isdir("out"):
        print("creating dir out")
        os.mkdir("out")

    t_ = ''
    with open("template.tcl", "r") as f:
        for line in f:
            t_ += line.replace("CLK", GLBCLK)

    for itm in cv_perflocs:
        with open("out/cycle_count_%s.tcl" % (itm), "w") as f:
            fnm = os.getcwd() + "/max_cycle_count_%s.csv" % (itm)
            f.write(t_ % (itm, fnm))
        with open("out/cycle_count_%s.sv" % (itm), "w") as f:
            f.write(h_)

def proc(fnm, itm):
    if not os.path.exists(fnm):
        return None
    csv_ = pd.read_csv(fnm)

    nm_raw = csv_[csv_['Name'].str.contains('consec_%s' % itm)]['Name'].values
    nm_raw = [int(re.search(r"consec_%s_([0-9]+)" % itm, nm).group(1)) for nm in nm_raw]

    res_raw = csv_[csv_['Name'].str.contains('consec_%s' % itm)]['Result'].values
    res_raw = list(zip(nm_raw, res_raw))

    res = sorted(res_raw, key = lambda i: i[0], reverse=True)
    res_inc = sorted(res_raw, key = lambda i: i[0], reverse=False)

    cyc = None
    cyc_res = None

    for rr in res:
        if rr[1] == 'covered' or rr[1] == 'undetermined':
            cyc = rr[0]
            cyc_res = rr[1]
            break

    max_cyc_covered = None
    for rr in res:
        if rr[1] == 'covered':
            max_cyc_covered = rr[0]
            break
    assert(max_cyc_covered is not None)

    # prerequisite for cyc to be max cycle is other smaller number
    # should not be unreachable
    min_unreach_cyc = None
    min_covered_cyc_under_unreach = None
    
    for rr in res_inc:
        if rr[1] == 'unreachable' and rr[0] < cyc:
            min_unreach_cyc = rr[0]
            break
        if rr[1] == 'covered':
            min_covered_cyc_under_unreach = rr[0]
    if min_unreach_cyc is not None:
        print(itm, cyc, "cyc change to ", min_covered_cyc_under_unreach,
                "from original result", cyc, cyc_res)
        cyc = min_covered_cyc_under_unreach

    return (cyc, max_cyc_covered)

def gen_s2():
    if not os.path.isdir("out2"):
        print("creating dir out2")
        os.mkdir("out2")


    max_cyc_perloc = []
    max_cyc_perloc_covered = []

    for itm in cv_perflocs:
        fnm = os.getcwd() + "/max_cycle_count_%s.csv" % (itm)
        cyc, max_cyc_covered = proc(fnm, itm)
        max_cyc_perloc_covered.append((itm, max_cyc_covered))
        if cyc is not None:
            max_cyc_perloc.append((itm, cyc))
            if cyc <= 1:
                continue

            # for each reachable set try see if the performing location can be
            # longer than one cycle 
            for set_idx, aSet in enumerate(reachable_sets):
                if not itm in aSet:
                    continue
            
                #if interference:
                #    continue
                with open("out2/over1cyc_%d_%s.sv" % (set_idx, itm), "w") as f:
                    f.write(h_)
                    s = ""
                    for pl in cv_perflocs:
                        if not pl in aSet:
                            f.write(no_s1_t.format(s1=pl))
                        else:
                            f.write(hpn_reg_t2.format(s1=pl))
                            s += "{s1}_hpn && ".format(s1=pl)
                    s += "1 "
                    f.write(assume_path.format(s=s)) 
                    f.write(CS_prop_gt.format(itm=itm, cnt=2, s=s))

    with open("max_cycle_per_pl.txt", "w") as f:
        for itm in max_cyc_perloc:
            f.write("%s,%d\n" % itm)

    with open("max_cycle_per_pl_covered.txt", "w") as f:
        for itm in max_cyc_perloc_covered:
            f.write("%s,%d\n" % itm)

def pp():
    max_cyc_perloc = get_array("max_cycle_per_pl.txt")
    pl_cyc = {}
    for itm in max_cyc_perloc:
        pl_cyc[itm[0]] = int(itm[1])
    result = [] # (itm,cyc_that_covered,...)
    undetermined_result = []
    # itm, cyc, res
    for itm in cv_perflocs:
        if pl_cyc[itm] == 1:
            continue

        for set_idx, aSet in enumerate(reachable_sets):
            if not itm in aSet:
                continue

            #if interference:
            #    result.append((set_idx, itm, 1))
            #    continue


            fnm = os.getcwd() + "/over1cyc_%d_%s.csv" % (set_idx, itm)
            #print(fnm)
            check_file(fnm)
            df = pd.read_csv(fnm, dtype=mydtypes)
            res, bnd, time = df_query(df, "CS_gt_%s_%d" % (itm, 2))
            #print(res)
            if res == "unreachable":
                result.append((set_idx, itm, 0))  
                # can reach only 1 cycle even thooug other set has this nodes
                # over 1 cycle
            else:
                result.append((set_idx, itm, 1))

    with open("cycle_count_gt1_perset.txt", "w") as f:
        for itm in result:
            f.write("%d,%s,%d\n" % itm)

def stats():
    max_cyc_perloc = get_array("max_cycle_per_pl.txt")
    pl_cyc = {}
    for itm in max_cyc_perloc:
        pl_cyc[itm[0]] = int(itm[1])

    comps = []
    incomps = []
    for itm in cv_perflocs:
        fnm = os.getcwd() + "/max_cycle_count_%s.csv" % (itm)
        df = pd.read_csv(fnm, dtype=mydtypes)
        df = df[df['Name'].str.contains('consec_%s' % itm)]
        for r_, time in zip(list(df['Result'].values), list(df['Time'].values)):
            t_ = float(time[:-2])
            if r_ in ["covered", "unreachable", "cex", "proven"]:
                comps.append(t_)
            else:
                incomps.append((t_, -1))

        #if pl_cyc[itm] != 1:
        #    for set_idx, aSet in enumerate(reachable_sets):
        #        if not itm in aSet:
        #            continue
        #        #fnm = os.getcwd() + "/over1cyc_%d_%s.csv" % (set_idx, itm)
        #        #df = pd.read_csv(fnm, dtype=mydtypes)
        #        #res, bnd, time = df_query(df, "CS_gt_%s_%d" % (itm, 2))
        #        #if res in ["covered", "unreachable", "cex", "proven"]:
        #        #    comps.append(time)
        #        #else:
        #        #    incomps.append((time, bnd))


        #fnm = os.getcwd() + "/max_cycle_count_%s.csv" % (itm)
        #df = pd.read_csv(fnm, dtype=mydtypes)

        #for idx, tar_row in df[df['Name'].str.contains("consec_%s" % itm)].iterrows():
        #    res = tar_row['Result']
        #    bnd = tar_row['Bound']
        #    sr = re.search("([0-9]+)", bnd)
        #    if sr is not None:
        #        bnd = int(sr.group(1))
        #    else:
        #        bnd = None
        #    time = float(tar_row['Time'][:-2])
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
