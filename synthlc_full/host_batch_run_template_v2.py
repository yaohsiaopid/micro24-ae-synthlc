import os
import re
import random
from multiprocessing import Semaphore, Pool, Manager, Lock, Array, Semaphore, Value
import subprocess
import sys
import fcntl
NNN = 3
if os.getenv("NNN"):
    NNN = int(os.getenv("NNN"))
JOB=None
SV_FILE_DIR=None

IFT=True
IFT_static=False

if len(sys.argv) == 3:
    JOB = sys.argv[1]
    SV_FILE_DIR = sys.argv[2]
    print('JOB:',JOB)
    print('SV file dir:', SV_FILE_DIR)

   
idx = 1
seq_script=False
if "--seq" in sys.argv[1]:
    seq_script=True
    if NNN > 2:
        NNN = 2
    idx = 2
    
#assert(JOB is not None and SV_FILE_DIR is not None)
print("NNN is %d" % NNN)

tasks = []
for JOB, SV_FILE_DIR in zip(sys.argv[(idx)::2], sys.argv[(idx+1)::2]):
    print(JOB, SV_FILE_DIR)
    files = os.listdir(SV_FILE_DIR)
    for itm in files:
        file_name, sv_file_dir, job = (itm, SV_FILE_DIR, JOB)
        prefix = file_name.split(".")[0]
        running = os.path.exists(job + "/" + prefix + "_rundir")
        running = running or os.path.exists(job + "/" + prefix + ".csv")
        if "sv" in itm and (not running) and itm[0] != '.': 
            tasks.append((itm, SV_FILE_DIR, JOB))
print(tasks)
print("lenth of tasked")
print(len(tasks))

def foo(itm):
    global NNN
    idx = 0
	
    running = False
    file_name, sv_file_dir, job = itm
    prefix = file_name.split(".")[0]

    running = os.path.exists(job + "/" + prefix + "_rundir")
    running = running or os.path.exists(job + "/" + prefix + ".csv")

    if not running:
        # run the job
        f = open(job + "/" + prefix + ".log", "w")
        subprocess.call("mkdir -p %s" % (job + "/" + prefix + "_rundir"), shell=True, stdout=f)
        cmd = "./RUN_JG.sh -j {job} -s {filename}  -g 0".format(job = job, filename = sv_file_dir+"/"+file_name)
        #cmd = "./RUN_JG.sh -j {job} -s {filename} -p tsynth/header_v2_11_inter_q_auto.sv -g 0".format(job = job, filename = sv_file_dir+"/"+file_name)
        if IFT:
            assert(not IFT_static)
            cmd = " ./RUN_JG_ift.sh -j {job} -s {filename} -h src_ift/hdl.f -f src_ift/cellift_top_rewrite.sv -p src_ift/common_header.sv -t src_ift/jg.tcl -g 0".format(job = job, filename=sv_file_dir+"/"+file_name)
            if seq_script:
                cmd = " ./RUN_JG_ift.sh -j {job} -s {filename} -h src_ift/hdl.f -f src_ift/cellift_top_rewrite.sv -p src_ift/common_header.sv -t src_ift/jg_seq_prove.tcl -g 0".format(job = job, filename=sv_file_dir+"/"+file_name)
        if IFT_static:
            cmd = "./RUN_JG_ift.sh -j {job} -s {filename} -h src_ift_2flag/hdl_d.f -f src_ift_2flag/cellift_top_rewrite_2flags_d.sv -p src_ift_2flag/common_header_2flag.sv -t src_ift_2flag/jg.tcl -g 0".format(job = job, filename=sv_file_dir+"/"+file_name)
            assert(0)
        print(cmd)
        print(cmd, file=f)
        subprocess.call(cmd, shell=True, stdout=f)
        f.close()

    return None

with Pool(NNN) as p:
    print(p.map(foo, tasks))                                                                                                                                                                                                                                                           
