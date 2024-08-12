import numpy as np
import pandas as pd
import os
from itertools import chain, combinations
import re
from HB_template import *

GLBCLK=os.environ.get("CLK")
if GLBCLK is None:
    raise Exception("NOT FOUND ENV VAR: CLK")
GLBTOPMOD=os.environ.get("TOPMOD")
if GLBTOPMOD is None:
    raise Exception("NOT FOUND ENV VAR: TOPMOD")


mydtypes = {
    "Task": 'str',
    "Name": 'str', 
    "Result": 'str', 
    "Engine": 'str',
    "Bound": 'str',
    "Time": 'str',
    "Note": 'str'}
def get_time_total(FILE):
    df = pd.read_csv(FILE)
    time_eval = sum(df['Time'].apply(lambda x:  float(re.sub('[^0-9.]', '', x))))         
    return time_eval  
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))
def check_file(FILE, exit_on_fail=True):
    if not os.path.exists(FILE):
        print(FILE, "doesn't exists")
        if exit_on_fail:
            exit(0)
        return False
    return True
def get_array(FILE, arr_as_ele=False, exit_on_fail=True):
    if not check_file(FILE, exit_on_fail=exit_on_fail):
        return []
    ret = []
    with open(FILE, "r") as f:
        for line in f:
            if "," in line:
                ret.append(line[:-1].split(","))
                #print(ret[-1])
            else:
                if arr_as_ele:
                    ret.append([line[:-1]])
                else:
                    ret.append(line[:-1])
    return ret
def dump_array(arr, fn):
    with open(fn, "w") as f:
        for itm in arr:
            f.write(",".join(itm) + "\n")
def get_perflocs(HEADERFILE, start_tag = True):
    if not os.path.exists(HEADERFILE):
        assert(0)
    with open(HEADERFILE, 'r') as f:
        st = False if start_tag else True
        ret = []
        for line in f:
            if st and "wire" in line[:5]:
                perfloc = line.split(" ")[1]
                ret.append(perfloc)
            if "Performing location" in line:
                st = True
    return ret

def get_results(ff, prop_list):
    if not os.path.exists(ff):
        print(ff, "not found")
        return [("ERR", float('inf'))] * len(prop_list)
    csv_ = pd.read_csv(ff)
    ret = []
    for prop in prop_list:
        r_ = csv_[csv_['Name'] == prop]
        if len(r_) != 1:
            ret.append(("ERR", float('inf')))
        else:
            ret.append((r_['Result'].values[0], float(r_['Time'].values[0][:-2])))
    return ret
def proc_row(row):
    try:
        res = row['Result'].values[0] 
        bnd = row['Bound'].values[0]
        sr = re.search("([0-9]+)", bnd)
        if sr is not None:
            bnd = int(sr.group(1))
        else:
            bnd = None
        time = float(row['Time'].values[0][:-2])
        return (res, bnd, time)
    except:
        return (None, None, None)
def df_query(df, prop, cover_prop=True, exact_name=False):
    if cover_prop:
        if not ":" in prop and (not exact_name):
        #if not ":" in prop:
            prop = "." + prop
        tar_row = df[df['Name'].str.endswith(prop)]
        if (len(tar_row) != 1):
            print("tar row is size ", len(tar_row), "??", prop)
            assert(0)
        res = tar_row['Result'].values[0] 
        bnd = tar_row['Bound'].values[0]
        sr = re.search("([0-9]+)", bnd)
        if sr is not None:
            bnd = int(sr.group(1))
        else:
            bnd = None
        time = float(tar_row['Time'].values[0][:-2])
        return (res, bnd, time)
    return (None, None, None)

def get_result(ff, prop):
    if not os.path.exists(ff):
        return ("ERR", float('inf'))
    # return (result, time)
    csv_ = pd.read_csv(ff)
    r_ = csv_[csv_['Name'] == prop]
    if len(r_) != 1:
        return ("ERR", float('inf'))
    else:
        return (r_['Result'].values[0], float(r_['Time'].values[0][:-2]))


def print_stat_arr(time_point):
    print("all time point(%d):" % len(time_point))
    if len(time_point) > 0:
        print("\ttotal:", np.sum(time_point))
        print("\tmean:", np.mean(time_point))
        print("\tmax:", np.max(time_point))
        print("\tstd:", np.std(time_point))

def print_stat(time_point, det_time_point):
    print("all time point(%d):" % len(time_point))
    if len(time_point) > 0:
        print("\ttotal:", np.sum(time_point))
        print("\tmean:", np.mean(time_point))
        print("\tmax:", np.max(time_point))
        print("\tstd:", np.std(time_point))
        print("determined time point(%d):" % len(det_time_point))
        print("\ttotal:", np.sum(det_time_point))
        print("\tmean:", np.mean(det_time_point))
        print("\tmax:", np.max(det_time_point))
        print("\tstd:", np.std(det_time_point))
def foo():
    print("J")

def assume_path_sv(reachable_nodes, aSet):
    # return the sv format
    s = ""
    ret_s = ""
    for pl in reachable_nodes:
        if not pl in aSet:
            ret_s += no_s1_t.format(s1=pl)
        else:
            ret_s += hpn_reg_t2.format(s1=pl)
            s += "{s1}_hpn && ".format(s1=pl)
    s += "1 "
    return ret_s + assume_path.format(s=s)

def get_cyc_list_from_fname(fnm, exit_on_fail=True):
    # return over1cyc_pl and perset_pl_cyc
    cyc_list = get_array(fnm, exit_on_fail=exit_on_fail)
    over1cyc_pl = set()
    perset_pl_cyc = {}
    for itm in cyc_list:
        set_idx, u, cyc = int(itm[0]), itm[1], itm[2:]
        cyc_cnt = [int(r) > 1 for r in cyc]
        # at least one greater than 1 
        if sum(cyc_cnt) >= 1:
            over1cyc_pl.add(u)
        if perset_pl_cyc.get(int(set_idx)) is None:
            perset_pl_cyc[set_idx] = {}
        perset_pl_cyc[set_idx][u] = cyc
    print(perset_pl_cyc)
    return (over1cyc_pl, perset_pl_cyc)

