set_prove_time_limit 5m
set itm {%s}
#foreach itm $perfloc {
# Step 1 search the max number that itm can stay consecutively
set min {0}
set max {70}
set cnt {0}
set max_cyc {70}
while 1 {
  if { $cnt == 10 } {
    break
  } 
  set cnt [expr {$cnt + 1}]
  set pivotValue [expr {($min + $max)/2}]
  puts "min $min max $max $pivotValue"
  set CMD "cover -name consec_$itm\_$pivotValue  {@(posedge CLK) $itm \[*$pivotValue\] ##1 !$itm }"
  puts $CMD
  try { 
    eval $CMD
  } on error {} {
    puts "END OF WHILE LOOP: $pivotValue"

    set max_cyc $pivotValue
    break
  } 
  set CMD "prove -property {consec_$itm\_$pivotValue}"
  puts $CMD
  eval $CMD
  set CMD "get_property_info -list status mytask::consec_$itm\_$pivotValue"
  set RET [eval $CMD]
  if { $RET != "covered" } { 
      # unreacblea or undetermined?
      set max [expr {$pivotValue - 1}]
  } else {
      set min [expr {$pivotValue + 1}]
  }
  

}
#
report -csv -file %s 
