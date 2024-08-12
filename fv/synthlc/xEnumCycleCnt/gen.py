import sys
import pandas as pd
import os
sys.path.append("../../src")
from util import *

HEADERFILE="../header.sv"
h_ = ""
with open(HEADERFILE, "r") as f:
    for line in f:
        h_ += line

t_ = ''
with open("template_iterloop.tcl", "r") as f:
    for line in f:
        t_ += line

def gen():
    if not os.path.isdir("out"):
        print("creating dir out")
        os.mkdir("out")
    csvdir=os.getcwd()
    pl_max = "../xPerfLocCycleCount/max_cycle_per_pl_covered.txt" 
    with open(pl_max, "r") as f:
        for line in f:
            a = line[:-1].split(",")
            assert(len(a) == 2)
            pl, n = a
            if "scb" in pl:
                if not "_0_" in pl:
                    continue
            if n == "1":
                continue
            with open("out/%s.tcl" % pl, "w") as outf:
                outf.write(t_ % (pl, n, "%s/%s.csv" % (csvdir, pl)))
                #instn + "_" + pl + ".csv"))
            with open("out/%s.sv" % pl, "w") as outf:
                outf.write(h_)

def proc():
    pl_max = "../xPerfLocCycleCount/max_cycle_per_pl_covered.txt" 
    pl_map = {}
    csvdir=os.getcwd()
    with open(pl_max, "r") as f:
        for line in f:
            a = line[:-1].split(",")
            assert(len(a) == 2)
            pl, n = a
            # TODO
            if "scb" in pl:
                if not "_0_" in pl:
                    continue
            if n == "1":
                continue
            df = pd.read_csv("%s/%s.csv" % (csvdir, pl), dtype=mydtypes)
            arr = []
            for itm in df[df['Name'].str.contains("CS_")]['Name'].values:
                arr.append(itm.split("_")[-1])
            pl_map[pl] = arr
    with open("res.txt", "w") as outf:
        for k, v in pl_map.items():
            outf.write("%s:%s\n" % (k, ",".join(v)))


if len(sys.argv) != 2:
    print("gen/pp")
    exit(0)

opt = sys.argv[1]
if opt == "gen":
    gen()
elif opt == "pp":
    proc()
