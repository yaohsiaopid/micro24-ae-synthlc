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
    echo "Pass an argument such as as \`./run_an_instn_demo_ift.sh LW.sv\`"
    exit
else
    echo "===> Processing: $1"
    fnm="$1"
fi

# This folder name
SYNTHLCFOLD=$(basename $(pwd))


filename=$(basename $fnm)
fileprefix="${filename%.*}"

INAME="i_${fileprefix}_out" 
echo "${fnm}"

INSTN="$INSTNDIR/$fnm"
echo "=========== INSTN ============="
echo "- Directory: $INAME"
echo "- Instruction file: $INSTN"
cat $INSTN
echo "==============================="

if [ ! -d "$INAME" ]; then 
    echo "Directory does not exists $INAME"
    exit 0
fi
cp $INSTN $INAME/idef.sv

cd $INAME

########## 
## STEP 1 
########## 
echo "
================================================================================
STEP 1 at $(pwd) $(date)
================================================================================
"

DIR=xDecisionsIntrinsic
PYSCRPT=intrinsic_step1_or
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and do only post-proc step"
else 
    cp -r ../${DIR} .
    cd ${DIR}
    python3 ${PYSCRPT}.py gen ${fileprefix}

    for itm in $(find . -name "*.sv")
    do
        echo "IASUBSET_DEMO: assume property (@(posedge clk_i) !(1'b0 | scb_1_s12 | scb_1_s13 | scb_1_s14 | scb_1_s8 | scb_2_s12 | scb_2_s13 | scb_2_s14 | scb_2_s8 | scb_3_s12 | scb_3_s13 | scb_3_s14 | scb_3_s8 ));" >> ${itm}
    done
    cd ..

    # at $INAME
    cd ../../
    

    if [ -d ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield ];
    then
        python3 host_batch_run_template_v2.py \
            ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield \
            ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield/out IFT
    fi
    if [ -d ./$SYNTHLCFOLD/$INAME/${DIR}/rs1 ];
    then
        python3 host_batch_run_template_v2.py \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs1 \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs1/out IFT
    fi

    cd ./$SYNTHLCFOLD/$INAME

    PYSCRPT=intrinsic_step2_perfield
    cd ${DIR}
    python3 ${PYSCRPT}.py gen ${fileprefix}

    for itm in $(find . -name "*.sv")
    do

        if ! grep -q "IASUBSET" ${itm};
        then
        echo "IASUBSET_DEMO: assume property (@(posedge clk_i) !(1'b0 | scb_1_s12 | scb_1_s13 | scb_1_s14 | scb_1_s8 | scb_2_s12 | scb_2_s13 | scb_2_s14 | scb_2_s8 | scb_3_s12 | scb_3_s13 | scb_3_s14 | scb_3_s8 ));" >> ${itm}
        fi
    done

    cd ..

    # at $INAME
    cd ../../

    if [ -d ./$SYNTHLCFOLD/$INAME/${DIR}/rs1 ];
    then
        python3 host_batch_run_template_v2.py \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs1 \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs1/out IFT
    fi

    if [ -d ./$SYNTHLCFOLD/$INAME/${DIR}/rs2 ];
    then
        python3 host_batch_run_template_v2.py \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs2 \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs2/out IFT
    fi

    cd ./$SYNTHLCFOLD/$INAME

    PYSCRPT=intrinsic_step2_perfield
    cd ${DIR}
    python3 ${PYSCRPT}.py pp ${fileprefix}
    cd ../
    # TODO
    #echo "TODO"
     #noniso_rs1, noniso_rs2, rs1, rs2, rs1_only_one, rs2_only_one 
     # grep "<=E=>{I},{n},{res}" decision source, noniso_rs1, noniso_rs2, rs1, rs2, rs1_only_one, rs2_only_one 

    #cd ./$SYNTHLCFOLD/$INAME

    #cd ../../
fi

echo "
================================================================================
STEP 2 at $(pwd) $(date)
================================================================================
"

DIR=xDecisionsDyn
PYSCRPT=dyn_step1_older
# can be younger and older 
if [ -d "${DIR}" ]; then 
    echo "Directory exists ${DIR} and do only post-proc step"
else 
    cp -r ../${DIR} .
    cd ${DIR}
    python3 ${PYSCRPT}.py gen ${fileprefix}

    # {bothfield, rs1}/out/{group_id}_{decision_id}.sv, where group_id is a set of candidate transmitters 
    cd ..

    # at $INAME
    cd ../../

    if [ -d ./$SYNTHLCFOLD/$INAME/${DIR}/rs1 ];
    then
        python3 host_batch_run_template_v2.py \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs1 \
            ./$SYNTHLCFOLD/$INAME/${DIR}/rs1/out IFT
    fi

    if [ -d ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield ];
    then
        python3 host_batch_run_template_v2.py \
            ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield \
            ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield/out IFT
    fi

    cd ./$SYNTHLCFOLD/$INAME

    PYSCRPT=dyn_step2_perfield
    cd ${DIR}
    python3 ${PYSCRPT}.py gen
    cd ../

    # at $INAME
    cd ../../

    if [ -d ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield_perfield ];
    then
        python3 host_batch_run_template_v2.py \
            ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield_perfield \
            ./$SYNTHLCFOLD/$INAME/${DIR}/bothfield_perfield/out IFT
    fi

    cd ./$SYNTHLCFOLD/$INAME

fi
    PYSCRPT=dyn_step2_perfield
    cd ${DIR}
    python3 ${PYSCRPT}.py pp ${fileprefix} | tee leakage_signature.log
    cd ../../
#fi 
