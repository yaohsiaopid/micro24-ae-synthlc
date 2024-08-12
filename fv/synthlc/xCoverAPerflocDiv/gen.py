import os 
import pandas as pd
import sys
sys.path.append("../../src")
from util import *
if len(sys.argv) != 2:
    print("gen/pp")
    exit(0)
HEADERFILE="../header.sv"
OUTDIR="out"
perflocs = get_perflocs(HEADERFILE)
print("perflocs: ", perflocs)
h_ = ""
with open(HEADERFILE, "r") as f:
    for line in f:
        h_ += line

def gen():
    if not os.path.isdir(OUTDIR):
        os.mkdir(OUTDIR)
    with open(OUTDIR+"/cover_individual.sv", "w") as f:
        f.write(h_)
        for idx, itm in enumerate(perflocs):
            f.write('''C_{CNT}: cover property (@(posedge {CLK}) {S});\n'''.format(CLK=GLBCLK, CNT=idx, S=itm))

def gen_s2():
    FILE = "cover_individual.csv"
    plist = ["C_%d" % i for i in range(len(perflocs))]

    if os.path.exists(FILE):
        df = pd.read_csv(FILE, dtype=mydtypes)
        t_ = 'assume property (@(posedge CLK) !{s});\n'.replace("CLK", GLBCLK)
        for idx, itm in enumerate(perflocs):
            res, _, _ = df_query(df, "C_%d" % idx)
            if res == "covered":
                with open(OUTDIR+"/%d.sv" % idx, "w") as f:
                    f.write(h_)
                    f.write(t_.format(s=itm))
    else:
        assert(0)

def stats():
    print("====== stats ==============")

    FILE = "cover_individual.csv"
    plist = ["C_%d" % i for i in range(len(perflocs))]

    comps = []
    incomps = []
    if os.path.exists(FILE):
        df = pd.read_csv(FILE, dtype=mydtypes)
        for itm in plist:
            res, bnd, time = df_query(df, itm)
            if res in ["covered", "unreachable", "cex", "proven"]:
                comps.append(time)
            else:
                incomps.append((time, bnd))
            
    for idx, itm in enumerate(perflocs):
        FILE = "%d.csv" % idx
        if os.path.exists(FILE):
            df = pd.read_csv(FILE, dtype=mydtypes)
        else:
            continue
        #print(FILE)
        res, bnd, time = df_query(df,":noConflict")

        if res in ["covered", "unreachable", "cex", "proven"]:
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


def pp():
    print("====== pp ==============")
    FILE="cover_individual.csv"
    cover_set = []
    undetermined = []
    if os.path.exists(FILE):
        #print("individual covered:")
        #plist = ["ariane.C_%d" % i for i in range(len(perflocs))]
        TMPLT=GLBTOPMOD + ".C_%d"
        #    "vscale_sim_top.C_%d"
        plist = [TMPLT % i for i in range(len(perflocs))]
        ret = get_results(FILE, plist)
        for itm, r in zip(perflocs, ret):
            if r[0] == "covered":
                cover_set.append(itm)
                #print(itm, r)
            if r[0] == "undetermined":
                #print("undetermined....???? ", itm)
                undetermined.append(itm)

        with open("cover_individual.txt", "w") as f:
            for itm in cover_set:
                f.write(itm + "\n")

        with open("undetermined.txt", "w") as f:
            for itm in undetermined:
                f.write(itm + "\n")

    #print("====================")
    always_set = []
    for idx, itm in enumerate(perflocs):
        FILE="%d.csv" % idx
        r_, t_ = get_result(FILE, ":noConflict")
        if (r_ == "cex"):
            always_set.append(itm)
        #print("{idx},{s},{r},{t}".format(idx=idx,s=itm,r=r_,t=t_))
    with open("always_reach.txt", "w") as f:
        for itm in always_set:
            f.write(itm + "\n")
    #print(always_set)
    #print("====================")

opt = sys.argv[1]
if opt == "gen":
    gen()
elif opt == "pp":
    pp()
elif opt == "stats":
    stats()
elif opt == "gen_s2":
    gen_s2()
        
