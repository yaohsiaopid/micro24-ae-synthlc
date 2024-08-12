#!/usr/bin/bash
if [ ! -f xDUVPLs/reachable_duvpls.sv ];
then
    cd xDUVPLs
    python3 gen.py gen
    touch xDUVPLs.sv
    cd ../
    ./RUN_JG.sh -j xDUVPLs -s xDUVPLs/xDUVPLs.sv -t xDUVPLs/get_sig_width.tcl -g 0

    cd xDUVPLs
    python3 gen.py gen_s2
    cd ../
    ./RUN_JG.sh -j xDUVPLs -s xDUVPLs/perf_loc.sv -g 0

    cd xDUVPLs
    python3 gen.py pp
    cd ../
fi

cat src/header_fv.sv > header_ia.sv
echo "
// =============================================================================
// ## Performing location annotation
// ============================================================================= 

" >> header_ia.sv
cat xDUVPLs/reachable_duvpls.sv >> header_ia.sv



cat src/header_fv_nia.sv > header_nia.sv
echo "
// =============================================================================
// ## Performing location annotation
// ============================================================================= 

" >> header_nia.sv
cat xDUVPLs/reachable_duvpls.sv >> header_nia.sv

cat src/header_fv.sv > header_ia_subset.sv
echo "
// =============================================================================
// ## Performing location annotation
// ============================================================================= 

" >> header_ia_subset.sv
cat xDUVPLs/reachable_duvpls.sv >> header_ia_subset.sv
cat src/header_fv_subset.sv >> header_ia_subset.sv
