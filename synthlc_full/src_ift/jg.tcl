
set assert_report_incompletes 1
set FPV 1

proc exit_if_error {} {
    if [get_message -number error] {
        exit -force
    }
    after 10000 exit_if_error
}
exit_if_error

# 
exec UPDATEFILE

analyze -sv09 -f jg_hdl.f
elaborate -bbox_m {\frontend} -top ariane

# Clock specification
clock clk_i

reset !rst_ni
set_engine_mode {K C Tri I N AD AM Hp B}
set_proofgrid_per_engine_max_jobs 32
set_proofgrid_max_jobs 32
set_prove_time_limit 12m
set_prove_per_property_time_limit 12m
#TASKCREATION

task -set mytask

#PROVE_ACTION
puts "END"
report -task mytask -csv -results -file "CSVNAME.csv" -force
exit
