#!/usr/bin/bash
mypath=$(pwd)
tdir=$1
bnm=$(basename ${tdir})
cd $tdir
echo "Task,Name,Result,Engine,Bound,Time,Note" > ${mypath}/total_time_${bnm}.csv

for itm in $(find . -name "*.csv")
do
  grep -v "?" ${itm} | grep "mytask" >> ${mypath}/total_time_${bnm}.csv
done
cd ${mypath}
python3 src/ctime.py ${mypath}/total_time_${bnm}.csv
