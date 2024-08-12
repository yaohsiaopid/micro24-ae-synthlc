#!/bin/bash
# file path being either absolute path or relative path from this directory
TOPFILE=./src/topsim.sv
FVMACRO=./src/macro.sv
DIR=src

HDLDIR=$(realpath ../cva6/core)
DESIGNDIR=$(realpath ../cva6)
echo "====================== [SETUP_FILES]  ================================ "
echo "HDLDIR: $HDLDIR"
echo "DESIGNDIR: $DESIGNDIR"
echo "[RUN_JG] Preparing jg_base.tcl.test.............................. "
sed "s~DESIGNDIR~${DESIGNDIR}~" ${DIR}/jg_base.tcl.template > jg_base.tcl.test
sed -i "s~HDLDIR~${HDLDIR}~" jg_base.tcl.test
echo "[RUN_JG] Preparing hdl.f ........................................ "
sed "s~DESIGNDIR~${DESIGNDIR}~" ${DIR}/hdl.f.template > hdl.f.test
