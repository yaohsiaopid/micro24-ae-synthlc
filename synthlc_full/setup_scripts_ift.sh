#!/bin/bash
DESIGNDIR=$(realpath ../cva6)
echo "====================== [SETUP_FILES]  ================================ "
echo "[RUN_JG] Preparing src_ift/hdl.f ......................................"
sed "s~DESIGNDIR~${DESIGNDIR}~" src_ift/hdl.f.template > src_ift/hdl.f
