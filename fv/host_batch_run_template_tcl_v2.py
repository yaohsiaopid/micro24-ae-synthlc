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
TCL_FILE_DIR=None

if len(sys.argv) == 3:
    JOB = sys.argv[1]
    TCL_FILE_DIR = sys.argv[2]
    print('JOB:',JOB)
    print('TCL file dir:', TCL_FILE_DIR)

if len(sys.argv) == 4:
    JOB = sys.argv[1]
    TCL_FILE_DIR = sys.argv[2]
    NNN = int(sys.argv[3])
    print('JOB:',JOB)
    print('TCL file dir:', TCL_FILE_DIR)
print(JOB)
assert(JOB is not None and TCL_FILE_DIR is not None)
print("NNN is %d" % NNN)
def check_csv(fnm):
    with open(fnm, "r") as f:
        for line in f:
            pass
        lastline = line[:-1]
        if "csv" in lastline:
            token = lastline.split(" ")[3]
            if os.path.exists(token) or  \
              os.path.exists(JOB + "/" + token.split("/")[-1]):
                print("skip %s %s" % (file_name, sv_file_dir))
                print("skip %s" %  (JOB + "/" + token.split("/")[-1]))
                return True

    return False


files = os.listdir(TCL_FILE_DIR)
tasks = []
cnt = 0
for itm in files:
    if itm.endswith(".tcl"):
        prefix = itm.split(".")[0]
        file_name, sv_file_dir, job = (itm, TCL_FILE_DIR, JOB + "_" + prefix)
        running = os.path.exists(job + "/" + prefix + "_rundir")
        sv_file = prefix + ".sv"
        assert(os.path.exists(TCL_FILE_DIR + "/" + sv_file))

        running = running or check_csv(sv_file_dir + "/" + file_name)

        if not running:
            tasks.append((itm, TCL_FILE_DIR, JOB, sv_file))
print(tasks)
print("lenth of tasked")
print(len(tasks))


def foo(itm):
    global NNN
    idx = 0
	
    running = False
    file_name, sv_file_dir, job, sv_file_tmp = itm
    prefix = file_name.split(".")[0]

    running = os.path.exists(job + "/" + prefix + "_rundir")
    running = running or os.path.exists(job + "/" + prefix + ".csv")
    running = running or check_csv(sv_file_dir + "/" + file_name)

    if not running:
        # run the job
        f = open(job + "/" + prefix + ".log", "w")
        subprocess.call("mkdir -p %s" % (job + "/" + prefix + "_rundir"), shell=True, stdout=f)
        #cmd = "./RUN_JG.sh -j {job} -s {filename}  -g 0".format(job = job, filename = sv_file_dir+"/"+file_name)
        cmd = "./RUN_JG.sh -j {job} -s {filename} -t {tcl} -g 0".format( \
            job = job, filename = sv_file_dir + "/" + sv_file_tmp, tcl = sv_file_dir + "/" + file_name)
        print(cmd)
        print(cmd, file=f)
        subprocess.call(cmd, shell=True, stdout=f)
        f.close()

    return None

with Pool(NNN) as p:
    print(p.map(foo, tasks))                                                                                                                                                                                                                                                           
