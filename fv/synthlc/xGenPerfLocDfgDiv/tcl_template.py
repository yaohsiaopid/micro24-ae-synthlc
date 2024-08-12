template = '''
# curly brace to avoid string interpolcation
set S1 {%s}
set S2 {%s}
set s1_exist [catch { get_signal_info -logic $S1 } type1]
if { $s1_exist == 1 } {
    puts "fail to find $S1"
}
set s2_exist [catch {get_signal_info -logic $S2 } type2] 
if { $s2_exist == 1 } {
    puts "fail to find $S2"
}
if { $s1_exist == 0 && $s2_exist == 0 } {
  set path [graph -shortest_path -from  $S1 -to $S2 -type register]  
  puts "$S1 $S2, $path"
  puts "$type1 $type2"
  set len [llength $path]
  if { $type1 == "flop" && $type2 == "flop" && $len == 2 } {
        puts "ADD $S1 $S2"
  }
  if { $type1 == "flop" && $type2 == "wire" && $len <= 3 } {
        puts "ADD $S1 $S2"
  }
  if { $type1 == "wire" && $type2 == "wire" } {
      if { $len == 2 } {
            puts "ADD(ww2) $S1 $S2"
        } elseif { $len == 3 } {
            puts "ADD(ww) $S1 $S2"
        } 
  }
  if { $type1 == "wire" && $type2 == "flop" } {
    set ele2 [lindex $path 1]
    set ele3 [lindex $path 2]
    if { $len == 2 } {
        puts "ADD $S1 $S2"
    }
  }
} 
puts "--------------------------------"
'''

