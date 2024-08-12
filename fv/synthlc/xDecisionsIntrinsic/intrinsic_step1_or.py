################################################################################
# From decisions/decision_op_dep_gen.py
# Check if a decision can depend on any of its own operands
################################################################################
import pandas as pd
import math
import numpy as np
import sys
import os
sys.path.append("../../src_ift_utils")
from gconsts import *
from util import *
from IFT_template import *


class I_ITSELF:
    def __init__(self, instn, tar_dir):
        self.tar_dir = tar_dir
        self.instn = instn
    def check_results(self):
        # TODO
        assert(0)
        todo = []
        todoff = "{tdir}/dec_maps_v2.txt".format(tdir=self.tar_dir)
        st = False
        if not os.path.exists(todoff):
            print("Not yet done even generated")
            return False

        with open(todoff, "r") as f:
            for line in f:
                line=line[:-1]
                if st:
                    cnt, decision_node, fset = line.split("|")
                    todo.append((cnt, decision_node, fset))
                if "========" in line:
                    st = True

        for itm in todo:
            if not os.path.exists("{tdir}/{cnt}.csv".format(tdir=self.tar_dir, cnt=itm[0])):
                print("--> ", self.instn, cnt, len(todo))
                return False

        return True

arr = []

OPFIELD="../../src/opfields.txt"
instn_to_field = {}
with open(OPFIELD, "r") as f:
    for line in f:
        line = line[:-1]
        instn = line.split("|")[0]
        arr = line.split("|")[1]
        v = []
        if arr != "": #len(line.split("|")) > 1:
            v = line.split("|")[1].split(",")
        instn_to_field[instn] = v
instn = None
#print(instn_to_field)
# under i_<INSTN>_out/xIFT_intrinsic
def gen(instn):

    ffname = "../xSummarize/follower_set_v2.txt"

    if not os.path.exists(ffname):
        assert(0)

    iii = ""
    with open("../idef.sv", "r") as idef:
        for line in idef:
            iii += line
    
    #if os.path.isdir("{I}_IFT/itself/bothfield/out".format(I=instn)):
    #    continue

    ##################################################################################
    #prep_dir("{I}_IFT/dyn/rs1/out".format(I=instn))
    #prep_dir("{I}_IFT/dyn/rs2/out".format(I=instn))

    #prep_dir("{I}_IFT/itself/rs1/out".format(I=instn))

    ##################################################################################
    ## Each file should be a decision only
    # IUV itself
    # both op 
    tar_dir = "bothfield" #
    TFIELD="bothrs_"
    DEFINEOPTAINT="`define BORTHRS"
    print('->', instn_to_field[instn])
    if len(instn_to_field[instn]) == 1:
        TFIELD="rs1_"
        DEFINEOPTAINT="`define RS1"
        tar_dir = "rs1" #{I}_IFT/itself/rs1".format(I=instn)
        print("==> ONLYRS1", instn)
    if len(instn_to_field[instn]) == 0:
        if os.path.isdir(tar_dir):
            print("REMOVE ", tar_dir)
        tar_dir = None
        return
    
    prep_dir("{tardir}/out".format(tardir=tar_dir))

    div_node_decision, div_node_all_uniq_pl = get_decision_dic(ffname)
    print(" div map ", div_node_decision)
    print(" div node all uniq pl ", div_node_all_uniq_pl)


    decision_log = open("./dec_maps_v2.txt", "w")
    for decision_node, follower_sets in div_node_decision.items():
        for afset in follower_sets:
            afset = sorted(afset)
            print("%s|%s" % (decision_node, ",".join(afset)), file=decision_log)
    print("==============", file=decision_log)
    cnt = 0
    for decision_node, follower_sets in div_node_decision.items():
        if len(follower_sets) == 1:
            continue
        uniq_pl_in_all_pl_set = sorted(div_node_all_uniq_pl[decision_node])
        for afset in follower_sets:
            afset = sorted(afset)
            followerset = "("
            if not decision_node in afset:
                followerset += "!{node} &&".format(node=decision_node)
            for eachN in uniq_pl_in_all_pl_set:
                if eachN == "":
                    continue
                followerset += "{ina}{node} && ".format(
                        node = eachN,
                        ina = ("" if (eachN in afset) else "!")
                )
         
            followerset += " 1'b1)"
            if len(afset) == 0:
                #print("J")
                t0 = "|{"
                for eachN in uniq_pl_in_all_pl_set:
                    if eachN == "":
                        continue
                    t0 += (eachN + "_t0 ,")
                t0 += "1'b0}"

            else:
                t0 = "|{"
                for eachN in afset:
                    t0 += (eachN + "_t0 ,")
                t0 += "1'b0}"
            print("%d|%s|%s" % (cnt, decision_node, ",".join(afset)), file=decision_log)
            outstring = itself_template
            rep_pairs = [ 
                ("OP_TAINT", DEFINEOPTAINT), 
                #("OP_TAINT", "`define RS1"), 
                ("INSTN_CONSTRAINT", iii),
                ("DECNODE", decision_node), 
                ("FOLLOWERSET", followerset),
                #("FIELD", "rs1_" + str(cnt)),
                ("FIELD",  TFIELD + str(cnt)),
                ("TT0", t0),
                ]
            for tt in rep_pairs:
                outstring = outstring.replace(tt[0], tt[1])
            with open("{tdir}/out/{ID}.sv".format(tdir=tar_dir, ID=cnt), "w") as outf:
                outf.write(outstring)
            cnt += 1
    
    decision_log.close()
    

opt = sys.argv[1]
if opt == "gen":
    if sys.argv[2] == "":
        print("pass instn name")
    else:
        gen(sys.argv[2])
elif opt == "pp":
    assert(0)
    pp()
elif opt == "gen_s2":
    assert(0)
    gen_s2()
        
