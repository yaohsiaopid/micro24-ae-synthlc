import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib
import pandas as pd
import math
import numpy as np
import sys
import subprocess

import os
from gconsts import *
from util import *
from IFT_template import *
from csv_util import *
iid_map = {}        
pl_signals = {}
with open("../fv/xDUVPLs/perfloc_signals.txt", "r") as f:
    for line in f:
        pl, sigs = line[:-1].split(" : ")
        pl_signals[pl] = sigs.split(",")
ufsm_arr = []
iid_map_rev = {}
for k, v in pl_signals.items():
    if not v[0] in iid_map:
        iid_map[v[0]] = [k]
        iid_map_rev[k] = v[0]
        ufsm_arr.append(k + "_t0")
    else:
        iid_map[v[0]].append(k)
#print(ufsm_arr)

todo_instns = ["SB","SH","SW","SD"]
fields = []

BATCH_INSTNDIR="./opcodes_batch"
group_items_transmitter  = {}
if not os.path.exists("%s/group_map.txt" % BATCH_INSTNDIR):
    sys.exit("error: can't find group_map.txt")
with open("%s/group_map.txt" % BATCH_INSTNDIR, "r") as f:
    for line in f:
        arr = line[:-1].split("|")
        assert(len(arr) == 3)
        gid, fields, instns = arr[0], arr[1], arr[2]
        for t in instns.split(","):
            group_items_transmitter[t] = fields
tar_dir = "xPruning"
prep_dir(tar_dir + "/out")

for instn in todo_instns:
    
    fields = group_items_transmitter[instn]
    if fields == "rs1":
        continue
    # rs1rs2
    for tag, defm in zip(["rs1", "rs2"], ["`define RS1", "`define RS2"]):
        tar_file = "{tdir}/out/{instn}_{tag}.sv".format(tdir=tar_dir, instn=instn, tag=tag)
        outf = open(tar_file, "w")
        outf.write("`define T_FROM_IUV\n")
        outf.write(defm + "\n")
        iii = get_i_constraint_indep(instn, "i0")
        outf.write(iii)

        for idx, itm in enumerate(ufsm_arr):
            outf.write("C_%d: cover property (@(posedge clk_i) %s);\n" % (idx, itm))
        outf.close()
cmd = "python3 host_batch_run_template_v2.py {tdir} {tdir}/out".format(tdir=tar_dir)
print(cmd)
subprocess.call(cmd, shell=True) 

# pp

for instn in todo_instns:
    
    fields = group_items_transmitter[instn]
    if fields == "rs1":
        continue
    # rs1rs2
    res_itm_map = {}
    for tag, defm in zip(["rs1", "rs2"], ["`define RS1", "`define RS2"]):
        csvfile = "{tdir}/{instn}_{tag}.csv".format(tdir=tar_dir, instn=instn, tag=tag)
        df = pd.read_csv(csvfile, dtype=mydtypes)
        outf = open(tar_file, "w")
        for idx, itm in enumerate(ufsm_arr):
            res, bnd, time = df_query(df, "C_%d" % idx)
            k = itm.split("_t0")[0]
            # iso pl name
            k_ = iid_map_rev[k]
            if not k_ in res_itm_map:
                res_itm_map[k_] = [0, 0]
            if res == "covered":
                if tag == "rs1":
                    res_itm_map[k_][0] = 1
                else:
                    res_itm_map[k_][1] = 1
    # pcr, rs1, rs2
    tarfile = "{tdir}/{instn}_res.txt".format(tdir=tar_dir, instn=instn)
    with open(tarfile, "w") as f:
        iso_name = []
        for k, v in res_itm_map.items():
            for pl in iid_map[k]: # that shares the same ufsm
                nm = transform(pl)
                if not nm in iso_name: 
                    f.write("%s,%d,%d\n" % (nm, v[0], v[1]))
                    iso_name.append(nm)

