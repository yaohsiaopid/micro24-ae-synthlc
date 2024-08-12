#!/usr/bin/bash
cd xStaticIFT
python3 gen_static_pl_prop.py gen

cd ../../
python3 host_batch_run_template_v2.py synthlc/xStaticIFT synthlc/xStaticIFT/out IFT_static
cd synthlc/xStaticIFT
python3 gen_static_pl_prop.py pp
