#!/bin/bash
DESIGNDIR=$(realpath ../cva6)
echo "====================== [SETUP_FILES]  ================================ "
echo "[RUN_JG] Preparing src_ift/hdl.f ......................................"
sed "s~DESIGNDIR~${DESIGNDIR}~" src_ift/hdl.f.template > src_ift/hdl.f
echo "[RUN_JG] Preparing src_ift_2flag/hdl.f ......................................"
sed "s~DESIGNDIR~${DESIGNDIR}~" src_ift_2flag/hdl_d.f.template > src_ift_2flag/hdl_d.f
