IASUBSET: assume property (@(posedge clk_i) !(1'b0
  | scb_1_s12 | scb_1_s13 | scb_1_s14 | scb_1_s8 
  | scb_2_s12 | scb_2_s13 | scb_2_s14 | scb_2_s8 
  | scb_3_s12 | scb_3_s13 | scb_3_s14 | scb_3_s8 ));
IASUBSET_2: assume property (@(posedge clk_i)
// ADD
((id_stage_i.instruction[31:25] == 7'b0000000) && (id_stage_i.instruction[14:12] == 3'b000)
&& (id_stage_i.instruction[11:7] != 5'd0) && (id_stage_i.instruction[6:0] == 7'b0110011))
||
// BEQ
((id_stage_i.instruction[14:12] == 3'b000) && (id_stage_i.instruction[6:0] == 7'b1100011))
|| 
// SW
((id_stage_i.instruction[14:12] == 3'b010) && (id_stage_i.instruction[6:0] == 7'b0100011))
|| 
// LW
((id_stage_i.instruction[14:12] == 3'b010) && (id_stage_i.instruction[11:7] != 5'd0) && (id_stage_i.instruction[6:0] == 7'b0000011))
|| 
// NOP
(id_stage_i.instruction == 32'h00000013)
||
// DIV
((id_stage_i.instruction[31:25] == 7'b0000001) && (id_stage_i.instruction[14:12] == 3'b100) &&
(id_stage_i.instruction[11:7] != 5'd0) && (id_stage_i.instruction[6:0] == 7'b0110011))
);
