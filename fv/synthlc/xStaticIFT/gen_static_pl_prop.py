import os
import sys
sys.path.append("../src")
from util import *
if len(sys.argv) != 2:
    print("gen/pp")
    exit(0)
iid_map = {}        
pl_signals = {}
with open("../../xDUVPLs/perfloc_signals.txt", "r") as f:
    for line in f:
        pl, sigs = line[:-1].split(" : ")
        sigs = sigs.split(",")
        pl_signals[pl] = sigs
        iid_map[sigs[0]] = pl + "_t0"
arr = []
for k, v in iid_map.items():
    arr.append(v)
template = '''
`define T_FROM_I
`define BORTHRS
`define STATIC
UFSM_%d: cover property (@(posedge clk_i) instn_begin ##[0:$] %s);
'''
def gen():
    if not os.path.isdir("out"):
            os.mkdir("out")
    for idx, itm in enumerate(arr):
        with open("out/%d.sv" % idx, "w") as f:
            f.write(template % (idx, itm))
def pp():
    if not os.path.isdir("out"):
            os.mkdir("out")
    retarr = []
    for idx, itm in enumerate(arr):
        FILE = "%d.csv" % idx
        df = pd.read_csv(FILE, dtype=mydtypes)
        res, _, _ = df_query(df, "UFSM_%d" % idx)
        if res == "covered":
            retarr.append(itm)
    print("Any static channel exist?")
    print(retarr)

if sys.argv[1] == "gen":
    gen()
else:
    pp()
