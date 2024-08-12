#!/bin/bash

if which jg >/dev/null; then
    :
else
    echo "FAIL to find jg" 
    exit
fi
# file path being either absolute path or relative path from this directory
TOPFILE=./src/topsim.sv
HEADER=""
#FVMACRO=./src/macro.sv

HDLDIR=$(realpath ../core)
DESIGNDIR=$(realpath ..)
#echo "====================== [RUN_JG]  ================================ "
#echo "HDLDIR: $HDLDIR"
#echo "DESIGNDIR: $DESIGNDIR"
#echo "[RUN_JG] Preparing jg_base.tcl.test.............................. "
#sed "s~DESIGNDIR~${DESIGNDIR}~" jg_base.tcl.template > jg_base.tcl.test
#sed -i "s~HDLDIR~${HDLDIR}~" jg_base.tcl.test
#echo "[RUN_JG] Preparing hdl.f ........................................ "
#sed "s~DESIGNDIR~${DESIGNDIR}~" hdl.f.template > hdl.f.test

Q=0
#FFILE=hdl.f
FFILE=hdl.f.test
CUSTOMTCL=
gui=1
JOB=
SVA=
STCL=
TCL=./jg_base.tcl.test
#TCL=./jg_base.tcl
#TCL=./jg_base_nrst.tcl

SYM="0"
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    --sym)
    #TCL="$2"
    TCL=./jg_base_nrst.tcl
    SYM="1"
    shift # past argument
    shift # past value
    ;;
    -j|--job)
    JOB="$2"
    shift # past argument
    shift # past value
    ;;
    -s|--sva)
    SVA="$2"
    shift # past argument
    shift # past value
    ;;
    -g|--gui)
    gui="$2"
    shift # past argument
    shift # past value
    ;;
    -f|--file)
    TOPFILE="$2"
    shift 
    shift
    ;;
    -p|--preface)
    HEADER="$2"
    shift
    shift
    ;;
    -t|--tcl)
    #CUSTOMTCL="$2"
    TCL="$2"
    shift 
    shift
    ;;
    -q|--quite)
    Q=1
    shift
    ;;
    -h|--hdl)
    FFILE="$2"
    shift 
    shift
    ;;
    --help)
        echo "-j/--job <jobDir> -s/--sva <sva file path> -g/--gui <0/1(deafult) (--sym 1)>"
        exit 0
    shift # past argument
    ;;
    --default)
    DEFAULT=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done

if [ ! -d $JOB ]; then
    echo "[RUN_JG] $JOB doesn't exists!"
    exit 0
fi

if [ ! -f "$TCL" ] || [ ! -f "$FFILE" ]; then
    echo "[RUN_JG] $TCL or $FFILE doesn't exists! Run setup_scripts.sh first"
    exit 0
fi

filename=$(basename -- "$SVA")
extension="${filename##*.}"
filename="${filename%.*}"
TOPV="${JOB}/${filename}_top.sv"
TCLF="${JOB}/${filename}_.tcl"
HDLF="${JOB}/${filename}_hdls.f"
SETUPFILE=${JOB}/${filename}_update_file_.sh
echo "[RUN_JG] $SETUPFILE"
if [ -f "$SVA" ] && [ -f "$TOPFILE" ]; then
    echo "SYMBOLIC? $SYM"
    if [ "$SYM" -eq "1" ]; then
        { echo "+define+FVT"; echo "+define+SYMSTART";  head -n 21 "$FFILE"; echo "${TOPV}" ; tail -n +22 "$FFILE"; } > $HDLF
    else 
        { head -n 21 "$FFILE"; echo "${TOPV}" ; tail -n +22 "$FFILE"; } > $HDLF
        #echo "src/aux_mod.sv"; 
    fi 
    echo "[RUN_JG] SVA is $SVA"
    echo "[RUN_JG] HDLF is $HDLF"
else
    echo "[RUN_JG] $SVA or $TOPFILE doesn't exists!"
    exit 0
fi

if [ -f $SVA ]; then
    echo "[RUN_JG] ADD DEFINE"
    echo "===================="
    #grep "define" $SVA | awk '{ printf "+define+" $2 "\n" }'
    #echo "===================="
    #{ grep "define" $SVA | awk '{ printf "+define+" $2 "\n" }' ; cat $HDLF; } > "${HDLF}.tmp"
    #mv "${HDLF}.tmp" $HDLF

    grep "define" $SVA | awk '{ if (!$3) print "+define+" $2 }'
    echo "===================="
    { grep "define" $SVA | awk '{ if (!$3) print "+define+" $2 }' ; cat $HDLF; } > "${HDLF}.tmp"   
    mv "${HDLF}.tmp" $HDLF
fi


if [ -z ${HEADER} ]; then

echo "
if [ -f \"$SVA\" ] && [ -f \"$TOPFILE\" ]; then
    { head -n -1 \"$TOPFILE\"; cat \"$SVA\" ; echo \"\" ; tail -n 1 \"$TOPFILE\"; } > \"${TOPV}\" #\"${DIR}/${DUMPNAME}_top.sv\"
else 
    echo \"[RUN_JG] no property at $SVA is found or no $TOPFILE\"
    exit 0
fi
" > $SETUPFILE

else 

echo "
if [ -f \"$SVA\" ] && [ -f \"$TOPFILE\" ]; then
    { head -n -1 \"$TOPFILE\";  cat \"$HEADER\" ; cat \"$SVA\" ; echo \"\" ; tail -n 1 \"$TOPFILE\"; } > \"${TOPV}\" #\"${DIR}/${DUMPNAME}_top.sv\"
else 
    echo \"[RUN_JG] no property at $SVA is found or no $TOPFILE\"
    exit 0
fi
" > $SETUPFILE

fi

chmod +x $SETUPFILE


sed "s~CSVNAME~${JOB}/${filename}~" $TCL > $TCLF
sed -i "s~jg_hdl.f~${HDLF}~" $TCLF
sed -i "s~JOBDIR~${JOB}~" $TCLF
sed -i "s~UPDATEFILE~$SETUPFILE~" $TCLF

if [ -f "$JOB/run.tcl" ]; then
    sed -i "s~#SOURCE_TCL~include ${JOB}/run.tcl~" $TCLF
fi 

if [ "$CUSTOMTCL" != "" ]; then
    sed -i "s~set CUSTOMTCL 0~set CUSTOMTCL 1~" $TCLF
    sed -i "s~#CUSTOMTCL~source $CUSTOMTCL~" $TCLF
fi

echo "[RUN_JG] TCLF is $TCLF"


#LISTS=$(grep "assert" $SVA)
#CLISTS=$(grep "cover" $SVA)

LISTS=$(grep "^[a-zA-Z].*: assert" $SVA | awk '{ print "-copy {.*" $1 ".*} " }' | sed -e "s/://g" |  tr -d '\n')

CLISTS=$(grep "^[a-zA-Z].*: cover" $SVA | awk '{ print "-copy {.*" $1 ".*} " }' | sed -e "s/://g" |  tr -d '\n')
CMDTASK="task -create mytask -copy_assumes $LISTS $CLISTS -regexp"
#-copy_asserts -copy_covers " 


if [ "$LISTS" == "" ] && [ "$CLISTS" == "" ] ; then
    sed -i "s~#ASSUMPTION~set CA 1~" $TCLF
    echo "CHECK ASSUMPTION!"
fi

DOCHECKASSUME=$(grep "RUN_CHECK_ASSUMPTION" $SVA)
echo $DOCHECKASSUME
if [ "$DOCHECKASSUME" != "" ]; then
    sed -i "s~#ASSUMPTION~set CA 1~" $TCLF
    echo "MANUALLY CHECK ASSUMPTION!"
fi

sed -i "s~#TASKCREATION~$CMDTASK~" $TCLF
echo "[RUN_JG] CMDTASK: $CMDTASK"
sed -i "s~#PROVE_ACTION~prove -task mytask~" $TCLF
#sed -i "s~#PROVE_ACTION~prove -all~" $TCLF


#if [ "$gui" -eq "1" ]; then
#    sed -i "s~exit~## exit~" $TCLF
#fi

DATE=$(date +%y-%m-%d-%H_%M_%S)
PROJ="${JOB}/${filename}_jgsession_$DATE"
if [ "$gui" -eq "0" ]; then
    echo "[RUN_JG] no gui"
    echo "[RUN_JG] jg -no_gui -fpv $TCLF -proj $PROJ"
    jg -no_gui -fpv $TCLF -proj $PROJ
    RUNDIR="${JOB}/${filename}_rundir"

    if [ "$Q" -eq "1" ]; then
        exit 1
    else 
        if [ ! -d $RUNDIR ]; then
            mkdir $RUNDIR
        fi
        mv $PROJ $RUNDIR
        mv $TOPV $RUNDIR
        mv $TCLF $RUNDIR
        mv $HDLF $RUNDIR
        mv $SETUPFILE $RUNDIR
    fi
else
    echo "[RUN_JG] gui"
    echo "[RUN_JG] jg -fpv $TCLF -proj $PROJ"
    sed -i "s~exit~#exit~" $TCLF
    if [ -z "$DISPLAY" ]; then
        echo "no x server"
        exit 1
    else 
        #jg -fpv $TCLF  -proj $PROJ & 
        jg -fpv $TCLF  -proj $PROJ & 
    fi 
fi 

