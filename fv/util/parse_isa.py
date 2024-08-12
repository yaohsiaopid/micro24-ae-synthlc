import os
import re
import sys
# TODO manual header part
if not os.path.isdir("opcodes"):
    os.mkdir("opcodes")
intns = {}
with open("src/instr-table.tex", "r") as f:
    row_arr = []
    st = False
    for line in f:
        if line[0] == "&": # or "multicolumn{10}" in line:
            if len(row_arr) > 0:
                if st:
                    #print(row_arr)
                    # process the instruction
                    instn_name = None
                    instn_bitfield = []
                    for itm in row_arr:
                        if not "multicolumn" in itm:
                            continue
                        n = re.search("{([0-9]+)}", itm)
                        if n is not None: 
                            tmps = itm.split("{")[3].split("}")[0]
                            if tmps != "" and re.search("[a-zA-Z]", tmps) is None:
                                constant = re.search("([0-9]+)", tmps)
                                #print(tmps, row_arr)
                                instn_bitfield.append((
                                    int(n.group(1)), constant.group(1)))
                            else:
                                if "rd" in itm:
                                    instn_bitfield.append((
                                        int(n.group(1)), 1))
                                else:
                                    instn_bitfield.append((
                                        int(n.group(1)), None))


                        ret_instn = re.search(r"\& ([a-zA-Z]+) \\", itm)
                        if ret_instn is not None:
                            assert(instn_name is None)
                            instn_name = ret_instn.group(1)
                    if instn_name is not None: 
                        #print(instn_name, instn_bitfield, row_arr)
                        intns[instn_name] = instn_bitfield

                        
                for itm in row_arr:
                    if "M Standard Extension" in itm or \
                        "I Base Instruction Set" in itm:
                        st = True
                        print("START", row_arr)
                        break
                    if st and "multicolumn{10}" in itm:
                        st = False
                        print("EEND", row_arr)
                row_arr = []
        else:
            row_arr.append(line[:-1])




arr = [31, 27, 26, 25, 24, 20, (19,15), (14,12), (11,7), (6,0)]
#arr = [31, 28, 27, 26, 25, 24, 23, 20, (19,15), (14,12), (11,7), (6,0)]
for k, v in intns.items():  
    idx = 0
    if "FENCE" in k: 
        print("TODO: SKIP FENCE AT THE MOMENT")
        continue
    print(k, v)
    constraints = []
    for itm in v:
        col, const = itm
        print('cc', col, const)
        if col != 1: #idx != (idx + col - 1):
            msb = arr[idx]
            if not isinstance(msb, int):
                #print("JJ", type(msb))
                msb = msb[1]
            lsb = arr[idx + col - 1]
            if not isinstance(lsb, int):
                lsb = lsb[1]
        else:
            msb = arr[idx][0]
            lsb = arr[idx][1]

        if const is not None:
            if isinstance(const, int):
                # rd reg
                cc = "i0[%d:%d] != 5'd0" % (msb, lsb)
                if not "JALR" in k:
                    constraints.append(cc)
            else:
                cc = "i0[%d:%d] == %d'b%s" % (msb, lsb, len(const), const)
                constraints.append(cc)
        idx += col
    #print("==========")
    with open("opcodes/%s.sv" % k, "w") as f:
        for idx, itm in enumerate(constraints):
            f.write("i_%s_%d: assume property (%s);\n" % (k, idx, itm))

arr = [
"LUI", "AUIPC", "JAL", "JALR", "BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU", "LB", "LH", "LW", "LBU", "LHU", "SB", "SH", "SW", "ADDI", "SLTI", "SLTIU", "XORI", "ORI", "ANDI", "SLLI", "SRLI", "SRAI", "ADD", "SUB", "SLL", "SLT", "SLTU", "XOR", "SRL", "SRA", "OR", "AND", "FENCE", "ECALL", "EBREAK", "LWU", "LD", "SD", "SLLI", "SRLI", "SRAI", "ADDIW", "SLLIW", "SRLIW", "SRAIW", "ADDW", "SUBW", "SLLW", "SRLW", "SRAW", "CSRRW", "CSRRS", "CSRRC", "CSRRWI", "CSRRSI", "CSRRCI", "MUL", "MULH", "MULHSU", "MULHU", "DIV", "DIVU", "REM", "REMU", "MULW", "DIVW", "DIVUW", "REMW", "REMUW", "FENCE", "FENCE.I"]
print("TODO")
for itm in arr:
    if not (os.path.exists("opcodes/%s.sv" % itm)):
        print(itm)
