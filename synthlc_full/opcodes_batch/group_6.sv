group_6_i0: assume property (
(i0[14:12] == 3'b001 && i0[11:7] != 5'd0 && i0[6:0] == 7'b1110011 &&  1'b1 ) || 
(i0[14:12] == 3'b010 && i0[11:7] != 5'd0 && i0[6:0] == 7'b1110011 &&  1'b1 ) || 
(i0[14:12] == 3'b011 && i0[11:7] != 5'd0 && i0[6:0] == 7'b1110011 &&  1'b1 ) || 
1'b0);
// CSRRW,CSRRS,CSRRC