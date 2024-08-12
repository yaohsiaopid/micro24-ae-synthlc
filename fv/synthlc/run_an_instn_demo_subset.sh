#!/usr/bin/bash
# non-interference case
# heuristic only handle undetermined cases line 435
set -e 
set -o pipefail

PWD=$(pwd)
PWD_PREFIX=$(basename ${PWD})
# assumption/opcdoe for the instn
INSTNDIR=opcodes_gen_all
# run over all
INSTN_FILES=$(ls $INSTNDIR)
fnm=DIV.sv
if [ -z $1 ];
then
    echo "Pass an argument such as as \`./run_an_instn_demo.sh LW.sv\`"
    exit
else
    echo "===> Processing: $1"
    fnm="$1"
fi

# This folder name
SYNTHLCFOLD=$(basename $(pwd))


filename=$(basename $fnm)
fileprefix="${filename%.*}"

INAME="i_${fileprefix}_isa_subset_out" 
echo "${fnm}"

if [ -d "$INAME" ]; then 
    echo "Directory exists $INAME. Remove [y/n]"
    read confirmed
    if [ $confirmed == "y" ]; then
        rm -rf "$INAME"
        mkdir $INAME
    fi
else
    echo "Working on $INAME"
    mkdir $INAME
fi

INSTN="$INSTNDIR/$fnm"
echo "=========== INSTN ============="
echo "- Directory: $INAME"
echo "- Instruction file: $INSTN"
cat $INSTN
echo "==============================="


echo ${PWD}
echo ${PWD_PREFIX}


echo " >>>>>>> Using NI header to demonstrate the path synthesis <<<<<<< "
HEADERFILE=$(realpath ../header_ia_subset.sv)

echo "HEADERFILE: $HEADERFILE"


# Shared by all instructions 
if [ ! -f "xGenPerfLocDfgDiv/dfg_e.txt" ]; then
    exit
fi 
echo "========== DFG E prepared ========== "


##### per instruction #####

cp $HEADERFILE $INAME/header.sv
cat $INSTN >> $INAME/header.sv

cd $INAME


########## 
## STEP 1 
########## 
echo "
================================================================================
STEP 1 at $(pwd) $(date)
================================================================================
"

DIR=xCoverAPerflocDiv
PYSCRPT=gen
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and do only post-proc step"
else 
    cp -r ../${DIR} .
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    # at $INAME
    cd ../../ ; 

      python3 host_batch_run_template_v2.py \
      ./$SYNTHLCFOLD/$INAME/${DIR} \
      ./$SYNTHLCFOLD/$INAME/${DIR}/out

      cd ./$SYNTHLCFOLD/$INAME

      
      cd ${DIR}; python3 ${PYSCRPT}.py gen_s2; cd ..

      # at $INAME
      cd ../../ ; 
      python3 host_batch_run_template_v2.py \
      ./$SYNTHLCFOLD/$INAME/${DIR} \
      ./$SYNTHLCFOLD/$INAME/${DIR}/out
        
      cd ./$SYNTHLCFOLD/$INAME
fi

# at $INAME
cd ${DIR}; 
python3 ${PYSCRPT}.py pp; 
python3 ${PYSCRPT}.py stats; 
cd ../


########## 
## STEP 2
########## 
echo "
================================================================================
STEP 2 at $(pwd) $(date)
================================================================================
"
DIR=xPairwiseDepDiv
PYSCRPT=xPairwiseDep_post
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .
fi
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    # at $INAME
    cd ../../ ; 
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out 

    cd ./$SYNTHLCFOLD/$INAME
#fi

# at $INAME
cd ${DIR}; 
python3 ${PYSCRPT}.py pp;
python3 ${PYSCRPT}.py stats; 
cd ../

######### 
# STEP 3
######### 
echo "
================================================================================
STEP 3 at $(pwd) $(date)
================================================================================
"

DIR=xPerfLocSubsetDiv
PYSCRPT=xPerfLocSubsetDiv
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    # at $INAME
    cd ../../ ; 
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/covertest

    cd ./$SYNTHLCFOLD/$INAME
fi

# at $INAME
cd ${DIR}; 
python3 ${PYSCRPT}.py pp; 
python3 ${PYSCRPT}.py stats; 
cd ../



######### 
# STEP 4
######### 
echo "
================================================================================
STEP 4 at $(pwd) $(date)
================================================================================
"

DIR=xHBPerfG_dfg_v3_div
PYSCRPT=xHBPerf_dfg_v3
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    # at $INAME
    cd ../../ ; 
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out

    cd ./$SYNTHLCFOLD/$INAME


    echo "gen_s2"

    cd ${DIR}; python3 ${PYSCRPT}.py gen_s2; cd ..

    # at $INAME
    cd ../../ ; 
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out

    cd ./$SYNTHLCFOLD/$INAME
fi


# at $INAME
cd ${DIR}; 
python3 ${PYSCRPT}.py pp; 
python3 ${PYSCRPT}.py stats; 
cd ../


######### 
# STEP 5
######### 
echo "
================================================================================
STEP 5 at $(pwd) $(date)
================================================================================
"

# 1. For each reachable PL set, get revisit information for each PL for 
# 2. For each IUV PLs, is it re-visitable and what is max cycle that it is
# revisited 
DIR=xPerfLocCycleCount
PYSCRPT=xPerfLocCycleCountAllSet
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .

    cd ${DIR}; 
    python3 ${PYSCRPT}.py gen; 
    mkdir -p out; cp ../header.sv out;
    cd ..

    # at $INAME
    cd ../../ ; 
    #python3 host_batch_run_template_tcl.py \
    python3 host_batch_run_template_tcl_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out

    cd ./$SYNTHLCFOLD/$INAME
     
    cd ${DIR};
    python3 ${PYSCRPT}.py gen_s2;
    cd ..; # at $INAME
     
    echo "JJJ"
    cd ../../;
    #python3 host_batch_run_template_tcl.py \
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out2
    

    cd ./$SYNTHLCFOLD/$INAME

fi

# at $INAME
cd ${DIR}; 
python3 ${PYSCRPT}.py pp; 
python3 ${PYSCRPT}.py stats; 
cd ../



######### 
# STEP 6
######### 
echo "
================================================================================
STEP 6 at $(pwd) $(date)
================================================================================
"
# HB related to leaving revisited PLs
DIR=xHBPerfG_leaving
PYSCRPT=xHBPerfG_leaving
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .

    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    # at $INAME
    cd ../../ ; 
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out 

    cd ./$SYNTHLCFOLD/$INAME

    echo "gen_s2"

    cd ${DIR}; python3 ${PYSCRPT}.py gen_s2; cd ..

    # at $INAME
    cd ../../ ; 
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out 

    cd ./$SYNTHLCFOLD/$INAME
fi

# at $INAME
cd ${DIR}; 
python3 ${PYSCRPT}.py pp; 
python3 ${PYSCRPT}.py stats; 
cd ../

######### 
# STEP 7
######### 
echo "
================================================================================
STEP 7 at $(pwd) $(date)
Explore all combinations of entering order (if not determined by proven HB
edges) 
================================================================================
"

DIR=xCollectReEval
PYSCRPT=aggregate_cyccnt_comp


if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    cd ../../;
    python3 host_batch_run_template_tcl_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out_complete

    cd ./$SYNTHLCFOLD/$INAME

fi

######### 
# STEP 8
######### 
echo "
================================================================================
STEP 8 at $(pwd)
Given STEP 7 entering-order combination results
generate combination for leaving-order
================================================================================
"
DIR=xCollectReEvalLeaveOrder
PYSCRPT=aggregate_cyccnt_comp


if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .
fi
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    cd ../../;
    python3 host_batch_run_template_tcl_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out_complete_2

    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out_complete_2_setcover

    cd ./$SYNTHLCFOLD/$INAME

    
######### 
# STEP 9
######### 
echo "
================================================================================
STEP 9 at $(pwd)
Given STPE 7 entering-order 
      STEP 8 leaving order 
generate all possible combination
================================================================================
"
DIR=xConstructPaths
PYSCRPT=aggregate_cyccnt_comp_final


if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    cd ../../;
    python3 host_batch_run_template_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out_complete_3

    cd ./$SYNTHLCFOLD/$INAME
fi

######### 
# STEP 10
######### 
echo "
================================================================================
STEP 10 at $(pwd) $(date)
Given STPE 7 entering-order 
      STEP 8 leaving order 
      STEP 9 test all possible combination
      Generate follower_set.txt (decisions)
================================================================================
"
DIR=xSummarize
PYSCRPT=aggregate_cyccnt_stats_iso


if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and skip"
else 
    cp -r ../${DIR} .
    cd ${DIR}
    #python3 ${PYSCRPT}.py gen > stats_iso_trial5.log
    python3 aggregate_cyccnt_stats_iso_follower_set_decision_regen_v2.py gen > run.log
    cd ..
fi


######### 
# STEP 11
######### 
echo "
================================================================================
STEP 11 at $(pwd) $(date)
Cycle enumeration
================================================================================
"

DIR=xEnumCycleCnt
PYSCRPT=gen

if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and do only post-proc step"
else 
    cp -r ../${DIR} .
    cd ${DIR}; python3 ${PYSCRPT}.py gen; cd ..

    # at $INAME
    cd ../../ ; 
    python3 host_batch_run_template_tcl_v2.py \
    ./$SYNTHLCFOLD/$INAME/${DIR} \
    ./$SYNTHLCFOLD/$INAME/${DIR}/out

    cd ./$SYNTHLCFOLD/$INAME
fi

#at $INAME
cd ${DIR}
python3 ${PYSCRPT}.py pp;
python3 ${PYSCRPT}.py stats;
cd ../

echo "AT $(pwd)"


