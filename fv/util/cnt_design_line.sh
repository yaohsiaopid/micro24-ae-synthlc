#!/bin/bash
ACC=0
for ln in $(cat cnt_hdl.f.test)
do
    if [ -f "${ln}" ]
    then
        echo $ln
        N=$(cat $ln | sed '/^\s*\/\//d;/^\s*$/d' | wc -l)
        ACC=$(($ACC + $((N)))) 
    fi

done

echo $ACC
