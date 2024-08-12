export CLK="clk_i"
export TOPMOD="ariane"  
export RESET="!rst_ni"
cp src/HB_template.py.template src/HB_template.py
sed -i "s~RESET~${RESET}~" src/HB_template.py
sed -i "s~CLK~${CLK}~" src/HB_template.py

