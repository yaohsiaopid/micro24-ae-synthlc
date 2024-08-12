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
                line2=None
                if len(line[:-1].split(",")) > 1 and "__final" in line[:-1]:
                   print("[WARN] final?? ", ffname)
                   #continue
                   line2 = []
                   for itm in line[:-1].split(","):
                       if not "__final" in itm or itm == pl + "___final":
                           line2.append(itm.replace("___final", ""))
                 
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

                if line2 is not None:
                    print("--> line2:", line2)
                    aset = set(line2)
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
        print(k, v)
        for itm in v:
            add = True
            #for t in v:
            #    if t == itm:
            #        continue
            #    if itm.issubset(t) and len(itm) > 0:
            #        add = False
            #        break
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


class I_ITSELF:
    def __init__(self, instn, tar_dir):
        self.tar_dir = tar_dir
        self.instn = instn
    def get_map(self):        
        st = False
        todoff = "{tdir}/dec_maps_v2.txt".format(tdir=self.tar_dir)

        if not os.path.exists(todoff):
            print("Not yet done even generated")
            print("FAIL no dec_maps")
            return False

        decisions_ = {}
        ret = []
        with open(todoff, "r") as f:
            for line in f:
                line=line[:-1]
                if st:
                    cnt, decision_node, fset = line.split("|")
                    if fset == "":
                        fset_ = []
                    else:
                        fset_ = fset.split(",")
                    if not decision_node in decisions_:
                        decisions_[decision_node] = []
                    decisions_[decision_node].append((cnt, fset_)) #fset.split(",")))
                if "========" in line:
                    st = True
        return decisions_

    def check_results(self):
        todo_raw = []
        todoff = "./dec_maps_v2.txt".format(tdir=self.tar_dir)
        st = False
        if not os.path.exists(todoff):
            print("Not yet done even generated")
            print("FAIL no dec_maps")
            return False
        decisions_ = {}
        ret = []
        with open(todoff, "r") as f:
            for line in f:
                line=line[:-1]
                if st:
                    cnt, decision_node, fset = line.split("|")
                    if not decision_node in decisions_:
                        decisions_[decision_node] = []
                    decisions_[decision_node].append(fset.split(","))
                    todo_raw.append((cnt, decision_node, fset.split(",")))
                if "========" in line:
                    st = True
        todo = []
        for itm in todo_raw:
            dec_node = itm[1] 
            if len(decisions_[dec_node]) > 1:
                todo.append(itm)
        if len(todo) != len(todo_raw):
            print("DIFFERENT, ", todoff) 
        fail = False
        for itm in todo:
            csvff = "{tdir}/{cnt}.csv".format(tdir=self.tar_dir, cnt=itm[0])
            if not os.path.exists(csvff):
                print(csvff)
                fail = True
                #print("--> ", self.instn, cnt, len(todo))
            ret.append((csvff, itm[0], itm[1], itm[2]))
        #return True
        if fail:
            #print("---")
            return [ ] #False
        #print("-")
        return ret
class DivDecNode:
    def __init__(self):
        # None: not applicable because no such field
        self.cnt = 0
        self.follower_sets = []

        # True/False: applicable and result return covered/undeter
        # with greater than 1 different non-iso-morphic follower set 

        self.noniso_rs1dep = None
        self.noniso_rs2dep = None

        # iso_rs1dep and rs1_iso_taint_only_one should be mutually exclusive
        # with greater than 1 different but isomorphic follower set (i.e.,
        #stb_com_0 and stb_com_1 is counted as 2, while in above case is 1)
        self.iso_rs1dep = None
        self.iso_rs2dep = None
        
        # Only 1 (isormorphic) follower set is tainted
        self.rs1_iso_taint_only_one = None
        self.rs2_iso_taint_only_one = None
    def addcnt(self, afset=None):
        self.cnt += 1
        if afset is not None:
            if not afset in self.follower_sets:
                self.follower_sets.append(afset)

    def rs1false(self):
        self.iso_rs1dep = False
        self.rs1_iso_taint_only_one = False
        self.noniso_rs1dep = False
    def rs2false(self):
        self.iso_rs2dep = False
        self.rs2_iso_taint_only_one = False
        self.noniso_rs2dep = False
    def str(self):
        def t(i):
            if i is None:
                return -1
            elif i:
                return 1
            return 0
        #noniso_rs1, noniso_rs2, rs1, rs2, rs1_only_one, rs2_only_one 
        return "%d,%d,%d,%d,%d,%d" % (
            t(self.noniso_rs1dep), t(self.noniso_rs2dep), 
            t(self.iso_rs1dep), t(self.iso_rs2dep), 
            t(self.rs1_iso_taint_only_one), t(self.rs2_iso_taint_only_one))
    def __eq__(self, other):
        return ((other.iso_rs1dep == self.iso_rs1dep) and 
          (other.rs1_iso_taint_only_one == self.rs1_iso_taint_only_one) and \
          (other.noniso_rs1dep == self.noniso_rs1dep) and \
          (other.iso_rs2dep == self.iso_rs2dep) and \
          (other.rs2_iso_taint_only_one == self.rs2_iso_taint_only_one) and \
          (other.noniso_rs2dep == self.noniso_rs2dep))
