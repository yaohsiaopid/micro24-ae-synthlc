set_engine_mode {K C Tri I N AD AM G3 Hp B}
set_prove_time_limit 15m 
cover -name set_r {@(posedge clk_i) set_r}
prove -property {mytask::set_r}
set RET [get_property_info -list status mytask::set_r]
if { $RET == "covered" } { 
    set_prove_per_property_time_limit 5m  
    set_prove_time_limit 10m
    prove -task mytask -from {mytask::set_r}
} 
if { $RET != "unreachable" } {
    set_prove_time_limit 10m 
    prove -property {.*CS.*} -regexp 
}

report -task mytask -csv -results -file "CSVNAME.csv" -force
exit   
