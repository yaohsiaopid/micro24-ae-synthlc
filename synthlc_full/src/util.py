import re
from gconsts import *
import os
def prep_dir(jdir):
    if not os.path.isdir(jdir):
        os.makedirs(jdir)
def get_decision_dic(ffname):
    # div_node, set of decisions where source is div_node
    tmpmap = {}
    map_allpl = {}
    pl = None
    with open(ffname, "r") as rf:
        for line in rf:
            if ":" in line:
                pl = line.split(":")[0]
                if "___final" in pl:
                    pl =pl.split("___final")[0]
                if not pl in tmpmap:
                    tmpmap[pl] = []
                    map_allpl[pl] = set()
            else:
                if len(line[:-1].split(",")) > 1 and "__final" in line[:-1]:
                   print("[WARN] final?? ", ffname)
                   #continue
                if "___final" in line:
                    line = line.replace("___final", "")
                if line[:-1] == "":
                    aset = set()
                else:
                    aset = line[:-1].split(",")
                    aset = set(aset)
                for titm in aset:
                    map_allpl[pl].add(titm)
                if pl is None:
                    print(ffname)
                    assert(0)
                if not aset in tmpmap[pl]:
                    tmpmap[pl].append(aset)
    retmap = {}
    #print("==>")
    for k, v in tmpmap.items():
        retmap[k] = []
        #print(k, v)
        for itm in v:
            add = True
            for t in v:
                if t == itm:
                    continue
                if itm.issubset(t) and len(itm) > 0:
                    add = False
                    break
            if add:
                retmap[k].append(itm)

    return retmap, map_allpl

# per line:<ddn>|<fset>
def get_decision_dic_pp_file(ffname):
    tmpmap = {}
    map_allpl = {}
    pl = None
    with open(ffname, "r") as rf:
        for line in rf:
            line = line[:-1]
            ddn, afset = line.split("|")
            ddn = transform(ddn)
            if not ddn in tmpmap:
                tmpmap[ddn] = []
            if afset == "":
                afset_ = set()
            else:
                afset = afset.split(",")
                afset_ = set([transform(pl) for pl in afset])

            if not afset_ in tmpmap[ddn]:
                tmpmap[ddn].append(afset_)

            for titm in afset_:
                if not ddn in map_allpl:
                    map_allpl[ddn] = set()
                map_allpl[ddn].add(titm)
    return tmpmap, map_allpl

def get_decision_dic_iso(ffname):
    # div_node, set of decisions where source is div_node
    tmpmap = {}
    map_allpl = {}
    pl = None
    with open(ffname, "r") as rf:
        for line in rf:
            if ":" in line:
                pl = line.split(":")[0]
                if "___final" in pl:
                    pl =pl.split("___final")[0]
                pl = transform(pl)
                if not pl in tmpmap:
                    tmpmap[pl] = []
                    map_allpl[pl] = set()
            else:
                if len(line[:-1].split(",")) > 1 and "__final" in line[:-1]:
                   print("[WARN] final?? ", ffname)
                if "___final" in line:
                    line = line.replace("___final", "")
                if line[:-1] == "":
                    aset = set()
                else:
                    arr = line[:-1].split(",")
                    aset = set()
                    for itm in arr:
                        aset.add(transform(itm))

                for titm in aset:
                    map_allpl[pl].add(titm)
                if pl is None:
                    print(ffname)
                    assert(0)
                if not aset in tmpmap[pl]:
                    tmpmap[pl].append(aset)
    retmap = {}
    #print("==>")
    for k, v in tmpmap.items():
        retmap[k] = []
        #print(k, v)
        for itm in v:
            add = True
            for t in v:
                if t == itm:
                    continue
                if itm.issubset(t) and len(itm) > 0:
                    add = False
                    break
            if add:
                retmap[k].append(itm)
    return retmap, map_allpl


def get_i_constraint(inst, iseq):
    ret = "( "
    with open("../fv/synthlc/opcodes_gen_all/%s.sv" % inst, "r") as idef: 
        for line in idef:
            tline = re.search("\((.*)\)", line)
            ret += (((tline.group(0)).replace("i0", iseq)) + " && ") 
    ret += " 1'b1 )"
    return ret
def get_i_constraint_indep(inst, iseq):
    ret = ""
    with open("../fv/synthlc/opcodes_gen_all/%s.sv" % inst, "r") as idef: 
        for line in idef:
            ret += line
    return ret
def skip_ufsm_based(instns, afset):
    skip_rs1, skip_rs2 = True, True
    skip_set = {}
    files = os.listdir("xPruning")
    instn_map = {}
    for ff_ in files:
        ii = ff_.split("_")[0]
        ff = "xPruning/" + ff_
        if not ff.endswith("_res.txt"):
            continue
        iir_map = {}
        with open(ff, "r") as f:
            for line in f:
                arr = line[:-1].split(",")
                iir_map[arr[0]] = arr[1:]
        instn_map[ii] = iir_map
        #print("->",ii, iir_map)
    # iso names
    for eachN in afset:
        for inst in instns:
            if not inst in instn_map:
                skip_rs1, skip_rs2 = False, False
                break
            if instn_map[inst][eachN][0] == "1":
                skip_rs1 = False
            if instn_map[inst][eachN][1] == "1":
                skip_rs2 = False
    return (skip_rs1, skip_rs2)
