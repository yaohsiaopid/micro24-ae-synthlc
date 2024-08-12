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

IFT=False
IFT_static=False

if len(sys.argv) == 3:
    JOB = sys.argv[1]
    SV_FILE_DIR = sys.argv[2]
    print('JOB:',JOB)
    print('SV file dir:', SV_FILE_DIR)

if len(sys.argv) == 4:
    JOB = sys.argv[1]
    SV_FILE_DIR = sys.argv[2]
    if sys.argv[3] == "IFT":
        IFT = True
    elif sys.argv[3] == "IFT_static":
        IFT_static = True
    else:
        NNN = int(sys.argv[3])
    print('JOB:',JOB)
    print('SV file dir:', SV_FILE_DIR)
   

assert(JOB is not None and SV_FILE_DIR is not None)
print("NNN is %d" % NNN)


files = os.listdir(SV_FILE_DIR)
tasks = []
cnt = 0
for itm in files:
    file_name, sv_file_dir, job = (itm, SV_FILE_DIR, JOB)
    prefix = file_name.split(".")[0]
    running = os.path.exists(job + "/" + prefix + "_rundir")
    running = running or os.path.exists(job + "/" + prefix + ".csv")
    if "sv" in itm and (not running) and itm[0] != '.': 
        tasks.append((itm, SV_FILE_DIR, JOB))
        cnt += 1
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
        if IFT_static:
            cmd = "./RUN_JG_ift.sh -j {job} -s {filename} -h src_ift_2flag/hdl_d.f -f src_ift_2flag/cellift_top_rewrite_2flags_d.sv -p src_ift_2flag/common_header_2flag.sv -t src_ift_2flag/jg.tcl -g 0".format(job = job, filename=sv_file_dir+"/"+file_name)
        print(cmd)
        print(cmd, file=f)
        subprocess.call(cmd, shell=True, stdout=f)
        f.close()

    return None

with Pool(NNN) as p:
    print(p.map(foo, tasks))                                                                                                                                                                                                                                                           
