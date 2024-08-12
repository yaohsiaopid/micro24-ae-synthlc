A_enter_hb_final = '''
A_{e0nm}_hb_{e1nm}: assume property (@(posedge CLK) (!{e0}_hpn & {e0}) |-> ((!{e1}_hpn) or ({e1} ##1 {e1})));
'''
A_final_hb_final = '''
A_{e0nm}_hb_{e1nm}: assume property (@(posedge CLK) ($past({e0}) & !{e0}) |->  ((!{e1}_hpn) | {e1}));
'''
A_final_hb_enter = '''
A_{e0nm}_hb_{e1nm}: assume property (@(posedge CLK) ($past({e0}) & !{e0}) |-> (!{e1}_hpn));
'''
A_enter_concur_final = '''
A_{e0nm}_concur_{e1nm}: assume property (@(posedge CLK) ({e0} & !{e0}_hpn) |-> ({e1} ##1 !{e1}));
'''
A_final_concur_final = '''
A_{e0nm}_concur_{e1nm}: assume property (@(posedge CLK) ($past({e0}) & !{e0}) |-> ($past({e1}) & !{e1}));
'''
A_final_concur_enter = '''
A_{e0nm}_concur_{e1nm}: assume property (@(posedge CLK) ($past({e0}) & !{e0}) |-> ($past(!{e1}_hpn & {e1})));
'''

A_enter_hb_enter = '''
A_{e0}_hb_{e1}: assume property (@(posedge CLK) ({e0} & !{e0}_hpn) |-> !({e1} | {e1}_hpn));
'''
A_enter_concur_enter = '''
A_{e0}_concur_{e1}: assume property (@(posedge CLK) ({e0} & !{e0}_hpn) |-> ({e1} & !{e1}_hpn));
A_{e0}_concur_{e1}_2: assume property (@(posedge CLK) ({e1} & !{e1}_hpn) |-> ({e0} & !{e0}_hpn));
'''
C_final_hb_enter = '''
CS_{e0nm}_hb_{e1nm}: cover property (@(posedge CLK) {e0} ##1 (!{e0} & !({e1}_hpn | {e1})) ##[0:$] set_r);
'''
C_final_concur_enter = '''
CS_{e0nm}_concur_{e1nm}: cover property (@(posedge CLK) ({e0} & {e1} & !{e1}_hpn) ##1 (!{e0}) ##[0:$] set_r);
'''
C_enter_hb_final = '''
CS_{e0nm}_hb_{e1nm}: cover property (@(posedge CLK) !{e0} ##1 ({e0} & ((!{e1}_hpn) | {e1})) ##[1:$] {e1} ##[0:$] set_r);
'''
C_enter_concur_final = '''
CS_{e0nm}_concur_{e1nm}: cover property (@(posedge CLK) ({e0} & !{e0}_hpn & {e1}) ##1 (!{e1}) ##[0:$] set_r);
'''
C_final_hb_final = '''
CS_{e0nm}_hb_{e1nm}: cover property (@(posedge CLK) {e0} ##1 (!{e0} & ((!{e1}_hpn) | {e1})) ##[0:$] set_r);
'''
C_final_concur_final = '''
CS_{e0nm}_concur_{e1nm}: cover property (@(posedge CLK) ({e0} & {e1}) ##1 !({e0} | {e1}) ##[0:$] set_r);
'''


C_hb_prop = '''
CS_{e0}_hb_{e1}: cover property (@(posedge CLK) ({e0} & !{e0}_hpn & !({e1}_hpn | {e1})) ##[0:$] set_r);
'''
C_concur_prop = '''
CS_{e0}_concur_{e1}: cover property (@(posedge CLK) ({e0} & !{e0}_hpn & {e1} & !{e1}_hpn) ##[0:$] set_r);
'''
CS_COMB_prop = '''
CS_{cnt}: cover property (@(posedge CLK) 
    (!set_r [*0:$] ##1 set_r) and 
'''
CS_COMB_prop_e = '''
    (!{itm} [*0:$] ##1 {itm} [*{cnt}] ##1 !{itm}) and 
'''
# TO BE REPLACE: CLK, RESET
CS_prop = '''
CS_{itm}_{cnt}: cover property (@(posedge CLK) 
    !{itm} ##1 {itm} [*{cnt}] ##1 !{itm});
'''
CS_prop_gt = '''
CS_gt_{itm}_{cnt}: cover property (@(posedge CLK) 
    {itm} [*{cnt}] ##1 !{itm} ##[0:$] {s});
'''

assume_path='''
A_PATH: assume property (@(posedge CLK) first |-> s_eventually ({s}));
'''
################################################################################
# 1. Cycle Counter 
################################################################################
cntr_t = '''
reg [7-1:0] cnt_{s1};
reg [2-1:0] state_{s1};
always @(posedge CLK) begin
    if (RESET)
        state_{s1} <= 2'd0;  
    else if (serdiv_unit_divide)
        state_{s1} <= 2'd1;  
    else if (state_{s1}[0] & ~{s1})
        state_{s1} <= 2'd2;  
end

always @(posedge CLK) begin
    if (RESET)
        cnt_{s1} <= {7{1'b0}};
    else if ({s1} & ~state_{s1}[1])
        cnt_{s1} <= cnt_{s1} + 1;
end 
'''
anchor_node_cyc = '''
CYC_{cnt}_{s1}: assume property (@(posedge CLK) 
  first |-> strong(~{s1} [*0:$] ##1 {s1} [*{cnt}] ##1 ~{s1})
});
'''
node_reach_cyc_tcl = '''
cover -name C_{s1}_{cnt} {{@(posedge CLK) 
  ~{s1} ##1 {s1} [*{cnt}] ##1 ~{s1} 
}};
'''
################################################################################
# 2. Aux regs and happens-before relation
################################################################################

pair_dep_t2= '''
DEP_{cnt}_b: cover property (@(posedge CLK) !{s1}_hpn && {s2}_hpn);
'''

pair_dep_t = '''
DEP_{cnt}_a: assume property (@(posedge CLK) !{s1});
DEP_{cnt}_b: assert property (@(posedge CLK) !{s2});
'''
c_two_pl_t = '''
C_{cnt}: cover property (@(posedge CLK) ({s1}_hpn && {s2}_hpn));
'''
no_s1_t = '''
N_{s1}: assume property (@(posedge CLK) !{s1});
'''

hpn_reg_t2 = '''
reg {s1}_hpn;
always @(posedge CLK) begin
    if (RESET)
        {s1}_hpn <= 1'b0;
    else if ({s1})
        {s1}_hpn <= 1'b1;
end
'''

hpn_reg_t = '''
reg {s1}_hpn;
always @(posedge CLK) begin
    if (RESET) 
        {s1}_hpn <= 1'b0;
    else if ({s1})
        {s1}_hpn <= 1'b1;
end
reg {s2}_hpn;
always @(posedge CLK) begin
    if (RESET) 
        {s2}_hpn <= 1'b0;
    else if ({s2})
        {s2}_hpn <= 1'b1;
end
'''

ENTER_A_HB_ENTER_B_HEURISTIC_t2 = '''
reg no_dep, intra_df;
reg past_s2;
reg past_s1_fsm, past_s1;
reg intra_df_2;
always @(posedge CLK) begin
    past_s2 <= {s2};
    //past_s1_fsm <= {s1}_fsm;
    past_s1 <= {s1};
    //if (RESET)
    //    no_dep <= 1'b0;
    //else if (!past_s2 && {s2} && !past_s1_fsm)
    //    no_dep <= 1'b1;
end 
always @(posedge CLK) begin
    if (RESET)
        intra_df <= 1'b0;
    else if (!past_s2 && {s2} && past_s1)
        intra_df <= 1'b1;
end 
//always @(posedge CLK) begin
//    if (RESET)
//        intra_df_2 <= 1'b0;
//    else if (!past_s2 && {s2} && past_s1 & {s1})
//        intra_df_2 <= 1'b1;
//end 

//HEUB_{cnt}_c0: cover property (@(posedge CLK) {hpn_s} && no_dep); //$past(~{s2}) && {s2} && !($past({s1}_fsm)));
HEUB_{cnt}_c1: cover property (@(posedge CLK) {hpn_s} && intra_df); //$past(~{s2}) && {s2} && ($past({s1})));
//HEUB_{cnt}_c2: cover property (@(posedge CLK) {hpn_s} && intra_df_2); //$past(~{s2}) && {s2} && ($past({s1})));
'''

ENTER_A_HB_ENTER_B_HEURISTIC_t = '''
HEUB_{cnt}_c0: cover property (@(posedge CLK) $past(~{s2}) && {s2} && !($past({s1}_fsm)));
HEUB_{cnt}_c1: cover property (@(posedge CLK) $past(~{s2}) && {s2} && ($past({s1})));
'''

ENTER_A_HP_ENTER_B_t = '''
`ifndef WHB
HB_{cnt}: assert property (@(posedge CLK) ({s1} && !{s1}_hpn) |-> !({s2}_hpn || {s2}));
`else 
//C_{cnt}: cover property (@(posedge CLK) ({s1} && !{s1}_hpn) && ({s2} && !{s2}_hpn));
WHB_{cnt}: assert property (@(posedge CLK) ({s1} && !{s1}_hpn) |-> !{s2}_hpn);
WHB_CONCUR_{cnt}: assert property (@(posedge CLK) ({s1} && !{s1}_hpn) |-> ({s2} && !{s2}_hpn));
`endif 
'''

imp_t = '''
IMP_{s1}_{s2}: assert property (@(posedge CLK) {s1} |-> {s2});
'''

################################################################################# 
# 3. For s1 that stay for longer than 1 cycle, the HB relation of its final cycle
#with other nodes
################################################################################# 
# i. Check ( the final cycle of s1 ) happens-before entering s2:
#   a) The requisite is that entering s2 should not always happens-before
#      entering of s1. (In this case nothing to be checked)
#   b) HB: 
#                 **
#    s1 .. | s1 | s1 | !s1
#                    |  s2    
#   c) WHB OR ALWAYS SAME CYCLE
#                 **
#    s1 .. | s1 | s1 | !s1
#               | s2    

assume_s2_over_2cyc = '''
S2_STAY_AT_LEAST_TWO: assume property (@(posedge CLK) first |-> s_eventually
    ( !{s2} [*0:$] ##1 {s2} ##1 {s2}));
'''
HB_leaving_s1_hb_s2 = '''
`ifndef WHB
HB_LEAVING_{s1}_{s2}: assert property (@(posedge CLK) 
    ($past({s1}, 2) && 
        $past({s1}) && {not_s1}) |-> 
    $past(!({s2}_hpn || {s2})));
`else 
WHB_LEAVING_{s1}_hb_{s2}: assert property (@(posedge CLK) 
    ($past({s1}, 2) && 
        $past({s1}) && {not_s1}) |-> $past(!({s2}_hpn)));
WHB_CONCUR_LEAVING_{s1}_hb_{s2}: assert property (@(posedge CLK) 
    ($past({s1}, 2) && 
        $past({s1}) && {not_s1}) |-> $past(!({s2}_hpn) && {s2}));
`endif 
'''
# ii. Check entering s1 happens-before (final cycle of s2):
#   a) The requisite is that entering s1 doesn't always happens-before entering
#       of s2 or same cycle
#   b) HB:
#            s1
#    s2 .. | s2 | s2 | !s2
#                 **
#   c) WHB:
#                 s1
#    s2 .. | s2 | s2 | !s2
#                 **

HB_s1_hb_leaving_s2 = '''
// if precondition in unreachable meaning s2 already left when s1 enters
`ifndef WHB
HB_{s1}_LEAVING_{s2}: assert property (@(posedge CLK) 
    ($past(!{s1}_hpn) && {s1} && ({s2}_hpn || {s2})) |=>
     {s2});
`else 
WHB_{s1}_LEAVING_{s2}: assert property (@(posedge CLK) 
    ($past(!{s1}_hpn) && {s1} && {s2}_hpn) |->
    {s2});
WHB_CONCUR_{s1}_LEAVING_{s2}: assert property (@(posedge CLK) 
    ($past(!{s1}_hpn) && {s1} && {s2}_hpn && {s2}) |=>
    {not_s2});
`endif 
'''
# iii. Check final cycle of s1 happens-before final cycle of s2
#  a) HB:
#                 **
#    s1 .. | s1 | s1 | !s1
#         s2 .. | s2 | s2 | !s2
#                       **
#  b) WHB:
#                 **
#    s1 .. | s1 | s1 | !s1
#    s2 .. | s2 | s2 | !s2
#                 **
HB_leaving_s1_hb_leaving_s2 = '''
`ifndef WHB
HB_LEAVING_{s1}_LEAVING_{s2}: assert property (@(posedge CLK) 
    ($past({s1}, 2) && $past({s1}) && {not_s1}) |-> 
    (({s2}_hpn && {s2}) || !{s2}_hpn));
`else 
WHB_LEAVING_{s1}_LEAVING_{s2}: assert property (@(posedge CLK) 
    ($past({s1}, 2) && $past({s1}) && {not_s1}) |-> 
    $past(({s2}_hpn && {s2}) || !{s2}_hpn));
WHB_CONCUR_LEAVING_{s1}_LEAVING_{s2}: assert property (@(posedge CLK) 
    ($past({s1}, 2) && $past({s1}) && {not_s1}) |-> 
    ($past({s2}, 2) && $past({s2}) && {not_s2})); 
`endif 
'''

################################################################################# 
# 4. To check edge weight to be 1 cycles
#with other nodes
################################################################################# 
assert_1cyc_e1_enter_e0_final ='''
reg e1_past_1;
reg e0_past_1;
always @(posedge CLK) begin
  e1_past_1 <= {e1};
  e0_past_1 <= {e0};
end

reg one_cyc;
always @(posedge CLK) begin
    if (RESET) begin
        one_cyc <= 1'b0;
    end else if (!e1_past_1 && {e1} && e0_past_1 && !{e0}) begin
        one_cyc <= 1'b1;
    end
end

EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
   ({s}) |-> one_cyc
);
'''
assert_1cyc_e1_enter_e0_enter ='''
reg e1_past_1;
reg e0_past_1;
reg e0_past_2;
always @(posedge CLK) begin
  e1_past_1 <= {e1};
  e0_past_1 <= {e0};
  e0_past_2 <= e0_past_1;
end

reg one_cyc;
always @(posedge CLK) begin
    if (RESET) begin
        one_cyc <= 1'b0;
    end else if (!e1_past_1 && {e1} && !e0_past_2 && e0_past_1) begin
        one_cyc <= 1'b1;
    end
end

EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
   ({s}) |-> one_cyc
);

//EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
//    ($past(!{e1}) && {e1}) |-> ($past(!{e0}, 2) && $past({e0})));
////     ($past(!{e0}) && {e0}) |-> (!{e1} ##1 {e1}));
//// !e0  e0
////     !e1 e1 
'''
assert_1cyc_e1_enter_e0_final_nopath ='''
EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
    ($past(!{e1}) && {e1}) |-> ($past({e0}) && !{e0}));
// e0 .. e0 !e0
//      !e1 e1
'''


assert_1cyc_e1_enter_e0_enter_nopath ='''
EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
    ($past(!{e1}) && {e1}) |-> ($past(!{e0}, 2) && $past({e0})));
//     ($past(!{e0}) && {e0}) |-> (!{e1} ##1 {e1}));
// !e0  e0
//     !e1 e1 
'''
assert_1cyc_e1_final_e0_final_nopath='''
EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
   ({e0} [*2] ##1 !{e0}) |-> // one_cyc
    ({e1} ##1 !{e1})
);
'''

assert_1cyc_e1_final_e0_final ='''
reg e0_past_1;
reg e0_past_2;
reg e1_past_1;
always @(posedge CLK) begin
    e0_past_1 <= {e0};
    e0_past_2 <= e0_past_1;
    e1_past_1 <= {e1};
end

reg one_cyc;
always @(posedge CLK) begin
    if (RESET) begin
        one_cyc <= 1'b0;
    end else if (!{e1} && e1_past_1 && !e0_past_1 && e0_past_2) begin
        one_cyc <= 1'b1;
    end
end

EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
   ({s}) |-> one_cyc
);

//EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
//    ($past({e0}) && !{e0}) |-> ({e1} ##1 !{e1}));
// e0 .. e0 !e0
//      e1  e1  !e1
'''
assert_1cyc_e1_final_e0_enter_nopath = '''
EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
    ($past(!{e0}) && {e0}) |=> ({e1} ##1 !{e1}));
// !e0  e0
//      e1  e1  !e1
'''
assert_1cyc_e1_final_e0_enter ='''
reg e0_past_3;
reg e0_past_2;
reg e0_past_1;
reg e1_past_1;
always @(posedge CLK) begin
    e0_past_1 <= {e0};
    e0_past_2 <= e0_past_1;
    e0_past_3 <= e0_past_2;
    e1_past_1 <= {e1};
end
reg one_cyc;
always @(posedge CLK) begin
    if (RESET) begin
        one_cyc <= 1'b0;
    end else if (!{e1} && e1_past_1 && e0_past_2 && !e0_past_3) begin
        one_cyc <= 1'b1;
    end
end

EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
   ({s}) |-> one_cyc
);
//EDGE_1CYC_{todoidx}: assert property (@(posedge CLK) 
//    ($past(!{e0}) && {e0}) |=> ({e1} ##1 !{e1}));
// !e0  e0
//      e1  e1  !e1
'''

##################################################################################
## for (s1 |-> s2) and not (s2 |-> s1)
## - if s1 stays longer than one cycle
##  - leaving s1 happens-before entering s2?
##    conflict, since leaving s1 meaning leaving s2
##  - entering s2 happens-before leaving s1?
##     weakly happens-before if we can see evidence of 
##     cover (enter s2 and enter s1 at same cycle) otherwise strong
##     happens-before
## - if s2 stays longer than one cycle 
##  - leaving s2 (either !s2 or s1 now already)  happens-before enter s1?
##     assert ($past(s2) & !s2) |-> !s1_hpn)
##  - entering s1 happens-before leaving s2?
##     ~s1_hpn & s1 & s2_hpn |-> 
#HB_leaving_s1_hb_s2_imp = '''
#`ifndef WHB
#// assuming entering s1 only ever once and we issue only once 
#// s1 implies s2 then leaving s1 means {s1} & !{s2} and now its {s2}
#// for all trace that have reach s2 and s1
#HB_LEAVING_{cnt}: assert property (@(posedge CLK) 
#    ($past({s1} && !{s2}) && {s2}) |-> 
#    $past(!({s2}_hpn || {s2})));
#`else 
#WHB_LEAVING_{cnt}: assert property (@(posedge CLK) 
#    ($past({s1}) && !{s1}) |-> $past(!({s2}_hpn)));
#`endif 
#'''
##################################################################################

#################################################################################
## for when any pair of pl may be inclusive of one
## NOW: any pair of pl should be exclusive. i.e., exists no pl1 that implies pl2
#################################################################################
#
## entering of u and variable cycle leaving u 
## leaving s1_2 hb entering s2 while s2
## if s1_2 is stronger than s1
#HB_LEAVING_sticky ='''
#`ifndef WHB
#HB_LEAVING_{cnt}: assert property (@(posedge CLK) 
#    ($past({s1} & !{s1_2}) && {s1_2}) |-> 
#    $past(!({s2}_hpn || {s2})));
#`else
#//C_{cnt}: cover property (@(posedge CLK) 
#//  ({s1} && !{s1}_hpn) && ({s2} && !{s2}_hpn));
#WHB_LEAVING_{cnt}: assert property (@(posedge CLK) 
#    ($past({s1} & !{s1_2}) && {s1_2}) |-> 
#    $past(!({s2}_hpn)));
#`endif
#'''
#
