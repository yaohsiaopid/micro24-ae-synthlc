import re
#import networkx as nx
from itertools import chain, combinations
import pandas as pd
import numpy as np
import os
import pandas as pd
import sys
sys.path.append("../src")
from util import *
from tcl_template import *
HEADERFILE="../../header_ia.sv"
PLFILE="../../xDUVPLs/perfloc_signals.txt"
OUTDIR="out"
perfloc_signals = {}
try:
    with open(PLFILE, 'r') as f:
        for line in f:
            arr = line[:-1].split(" : ")
            k = arr[0]
            v = arr[1].split(",")
            perfloc_signals[k] = v
except FileNotFoundError:
    print("File not found")
    sys.exit(1)
print(perfloc_signals)
def gen():
    pairs = []
    #get_array("../xPerfLocSubsetDiv/reachable_set.txt")
    perf_locs_names = list(perfloc_signals.keys())

    with open("get_dfg.tcl", "w") as tcl_dfg_f:
        # all sequenced pair of perf_locs
        pairs_sigs = []
        for itm in perf_locs_names:
            for itm2 in perf_locs_names:
                if itm != itm2:
                    for s1 in perfloc_signals[itm]:
                        for s2 in perfloc_signals[itm2]:
                            if not (s1, s2) in pairs_sigs:
                            #if s1 != s2 and not (s1, s2) in pairs_sigs:
                                assert(len(s1) != 0)
                                assert(len(s2) != 0)
                                tcl_dfg_f.write(template % (s1, s2))
                                pairs_sigs.append((s1, s2))

    with open("seq_pairs.txt", "w") as f:
        for itm in pairs_sigs: #pairs:
            f.write(",".join(itm) + "\n")

def pp():
    LOG="get_dfg.tcl.log"
    if not os.path.exists(LOG):
        print(LOG, " not found")
    df_edges_candidates = get_array("seq_pairs.txt")

    os.system('grep "^ADD" %s > adde.log' % LOG)
    edges_exists = []
    with open("adde.log", "r") as f:
        for line in f:
            tokens = line[:-1].split(" ")
            u, v = tokens[1], tokens[2]
            assert([u, v] in df_edges_candidates)
            edges_exists.append((u, v))
            
    pairs = []

    perf_locs_names = list(perfloc_signals.keys())

    for itm in perf_locs_names:
        for itm2 in perf_locs_names:
            if itm != itm2 and not (itm, itm2) in pairs:
                pairs.append((itm, itm2))
    #print(perfloc_signals)
    dfe_exists = []
    for p_ in pairs:
        itm, itm2 = p_
        for s1 in perfloc_signals[itm]:
            for s2 in perfloc_signals[itm2]:
                #if "issue" in s1:
                #    print(s1, s2)
                #if s1 != s2 and (s1, s2) in edges_exists:
                if (s1, s2) in edges_exists or (s1 == s2):
                    if not (itm, itm2) in dfe_exists:
                        dfe_exists.append((itm, itm2))
                        #print((itm, itm2))
                    break
            if (itm, itm2) in dfe_exists:
                break
    with open("dfg_e.txt", "w") as f:
        for p_ in dfe_exists:
            f.write("%s,%s\n" % (p_[0], p_[1]))

if len(sys.argv) < 2:
    print("gen/pp")
    exit(0)
opt = sys.argv[1]
if opt == "gen":
    gen()
elif opt == "pp":
    pp()
