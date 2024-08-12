import os
import sys
import re
sys.path.append("../synthlc/src")
from util import *
pre = '''
set fileId [open "%s" "w"]
'''
post = '''
close $fileId
'''

CMD = '''
set T [get_signal_info -width {%s}]
puts $fileId "%s,$T"
'''
inf = None
try:
    inf = open("../annotation_pcr_ufsms.txt", "r")
except FileNotFoundError:
    print("File not found")
    sys.exit(1)
def get_width():
    pwd = os.getcwd()
    ff = "%s/sig_width.txt" % pwd
    outf = open("get_sig_width.tcl", "w")
    outf.write(pre % ff)

    nm = None
    pcr = None
    for line in inf:
        if line[0] == "#" or len(line[:-1]) == 0:
            nm = None
            pcr = None
            continue
        if nm is None:
            nm = line[:-1]
        elif pcr is None:
            pcr = line[:-1]
        else:
            ufsm_sig = line[:-1].split(",")[0]
            if "==" in ufsm_sig: 
                print(ufsm_sig)
                continue
            outf.write(CMD % (ufsm_sig, re.sub(r'([\[\]])', r'\\\1', ufsm_sig)))

    outf.write(post)
    outf.close()
def postproc_gen(nm, pcr, ufsms, ufsms_w, ufsms_f, ufsms_cond):
    total_cnt = 1
    for w, f in zip(ufsms_w, ufsms_f):
        if f is not None:
            total_cnt *= 1
        else:
            total_cnt *= (2**w)
    #print("==>", total_cnt, nm)
    pl_def = {}
    pl_sig = {}
    pl_seqs = []
    for idx in range(1, total_cnt):
        vals = []
        tmp_idx = idx
        for w, f in zip(ufsms_w[::-1], ufsms_f[::-1]):
            if f is None:
                vv = tmp_idx % (2**w)
                tmp_idx = tmp_idx / (2**w)
            else:
                vv = f
            vals = [vv] + vals
        pl_name = "%s_s%d" % (nm, idx)
        def_s = ("wire %s = \n" % pl_name)
        def_s += ("\t(%s == pc0) && \n" % pcr)

        for ss, wid, vv in zip(ufsms, ufsms_w, vals):
            def_s += ("\t(%s == %d'd%d) && \n" % (ss, wid, vv))
        def_s += "\t 1'b1; \n"
        pl_seqs.append(pl_name)
        pl_def[pl_name] = def_s
        composition_sig = [pcr]
        for itm in ufsms:
            if "==" in itm:
                composition_sig += ufsms_cond[itm]
            else:
                composition_sig.append(itm)

        pl_sig[pl_name] = composition_sig
        #outf.write("\t(%s == pc0) && \n")
    return pl_def, pl_sig, pl_seqs
def postproc(nm, pcr, ufsms, ufsms_w, ufsms_f, outf):
    total_cnt = 1
    for w, f in zip(ufsms_w, ufsms_f):
        if f is not None:
            total_cnt *= 1
        else:
            total_cnt *= (2**w)
    print("==>", total_cnt, nm)
    sigs = []
    for idx in range(1, total_cnt):
        vals = []
        tmp_idx = idx
        for w, f in zip(ufsms_w[::-1], ufsms_f[::-1]):
            if f is None:
                vv = tmp_idx % (2**w)
                tmp_idx = tmp_idx / (2**w)
            else:
                vv = f
            vals = [vv] + vals
        outf.write("wire %s_s%d = \n" % (nm, idx))
        sigs.append("%s_s%d" % (nm, idx))

        for ss, wid, vv in zip(ufsms, ufsms_w, vals):
            outf.write("\t(%s == %d'd%d) && \n" % (ss, wid, vv))

        outf.write("\t 1'b1; \n");
        #outf.write("\t(%s == pc0) && \n")
    return sigs

def gen_duv_pl_checks():
    # enumerate the valuation of ufsm: cannot be all zero (assume the reset
    # state valuation) and passing the non-reset state valuation (if specified)
    pwd = os.getcwd()
    ff = "%s/sig_width.txt" % pwd
    sig_width_map = {}
    try:
        with open(ff, "r") as widthf:
            for line in widthf:
                arr = line[:-1].split(",")
                sig_width_map[arr[0]] = int(arr[1])
    except FileNotFoundError:
        print(ff + " not found")
        sys.exit(1)
    outf = open("perf_loc.sv", "w")
    nm = None
    pcr = None
    ufsms = []
    ufsms_w = []
    ufsms_f = []
    chk_sigs = []
    for line in inf:
        if (line[0] == "#" or len(line[:-1]) == 0) and nm is not None:
            sigs = postproc(nm, pcr, ufsms, ufsms_w, ufsms_f, outf)
            chk_sigs += sigs

        if line[0] == "#" or len(line[:-1]) == 0:
            nm = None
            pcr = None
            ufsms = []
            ufsms_w = []
            ufsms_f = []
            continue
        if nm is None:
            nm = line[:-1]
        elif pcr is None:
            pcr = line[:-1]
        else:
            arr = line[:-1].split(",")
            ufsm_sig = arr[0]
            fix_val = None
            if not "==" in ufsm_sig and len(arr) == 2:
                fix_val = int(arr[1])
            ufsms_f.append(fix_val)
            if "==" in ufsm_sig: # commit/predicate condition
                ufsms_w.append(1)
            else:
                ufsms_w.append(sig_width_map[ufsm_sig])
            ufsms.append(ufsm_sig)

    sigs = postproc(nm, pcr, ufsms, ufsms_w, ufsms_f, outf)
    chk_sigs += sigs
    for itm in chk_sigs: 
        outf.write("CHECK_%s: cover property (%s);\n" % (itm, itm))
def clean():
    print("removing ..")
    for i in range(100):
        if os.path.exists("get_sig_width.tcl.%d" % i):
            continue
        else:
            os.rename("get_sig_width.tcl", "get_sig_width.tcl.%d" % i)
            os.rename("sig_width.txt", "sig_width.txt.%d" % i)
            os.rename("perf_loc.sv", "perf_loc.sv.%d" % i)
            break
# output: "perfloc_signals.txt" "reachable_duvpls.sv"
def gen_header():
    FILE = "perf_loc.csv"
    reachable = []
    if os.path.exists(FILE):
        df = pd.read_csv(FILE, dtype=mydtypes)
        for idx, row in df[df["Name"].str.contains("CHECK")].iterrows():
            if row['Result'] == "covered":
                reachable.append(row['Name'].split(".")[1][6:])
    else:
        assert(0)
    print(reachable)
    pwd = os.getcwd()
    ff = "%s/sig_width.txt" % pwd
    sig_width_map = {}
    try:
        with open(ff, "r") as widthf:
            for line in widthf:
                arr = line[:-1].split(",")
                sig_width_map[arr[0]] = int(arr[1])
    except FileNotFoundError:
        print(ff + " not found")
        sys.exit(1)
    pl_sv_f = open("reachable_duvpls.sv", "w")
    pl_sig_f = open("perfloc_signals.txt", "w")
    nm = None
    pcr = None
    ufsms = []
    ufsms_w = []
    ufsms_f = []
    ufsms_cond = {}
    for line in inf:
        if (line[0] == "#" or len(line[:-1]) == 0) and nm is not None:
            pl_def_map, pl_sig_map, pl_seq = postproc_gen(nm, pcr, ufsms, ufsms_w, ufsms_f, ufsms_cond)
            if "issue" in nm:
                for itm in pl_seq:
                    if itm in reachable:
                        pl_sv_f.write(pl_def_map[itm])
                        pl_sig_f.write("%s : " % itm)
                        pl_sig_f.write(",".join(pl_sig_map[itm]) + "\n")
            else:
                for itm in reachable:
                    if itm in pl_def_map:
                        pl_sv_f.write(pl_def_map[itm])
                        pl_sig_f.write("%s : " % itm)
                        pl_sig_f.write(",".join(pl_sig_map[itm]) + "\n")

        if line[0] == "#" or len(line[:-1]) == 0:
            nm = None
            pcr = None
            ufsms = []
            ufsms_w = []
            ufsms_f = []
            continue
        if nm is None:
            nm = line[:-1]
        elif pcr is None:
            pcr = line[:-1]
        else:
            arr = line[:-1].split(",")
            ufsm_sig = arr[0]
            fix_val = None
            if not "==" in ufsm_sig and len(arr) == 2:
                fix_val = int(arr[1])
            ufsms_f.append(fix_val)
            if "==" in ufsm_sig: # commit/predicate condition
                ufsms_w.append(1)
                ufsms_cond[ufsm_sig] = arr[1:]
                #print(ufsm_sig, " :: ", arr[1:])
            else:
                ufsms_w.append(sig_width_map[ufsm_sig])
            ufsms.append(ufsm_sig)

    pl_def_map, pl_sig_map, pl_seq = postproc_gen(nm, pcr, ufsms, ufsms_w, ufsms_f, ufsms_cond)
    for itm in reachable:
        if itm in pl_def_map:
            pl_sv_f.write(pl_def_map[itm])
            pl_sig_f.write("%s : " % itm)
            pl_sig_f.write(",".join(pl_sig_map[itm]) + "\n")
    pl_sv_f.close()
    pl_sig_f.close()

opt = sys.argv[1]
if opt == "clean":
    clean()
if opt == "gen":
    get_width()
elif opt == "gen_s2":
    gen_duv_pl_checks()
elif opt == "pp":
    gen_header()
inf.close()
