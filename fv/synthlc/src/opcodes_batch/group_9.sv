group_9_i0: assume property (
(i0[14:12] == 3'b000 && i0[6:0] == 7'b1100011 &&  1'b1 ) || 
(i0[14:12] == 3'b001 && i0[6:0] == 7'b1100011 &&  1'b1 ) || 
(i0[14:12] == 3'b100 && i0[6:0] == 7'b1100011 &&  1'b1 ) || 
(i0[14:12] == 3'b101 && i0[6:0] == 7'b1100011 &&  1'b1 ) || 
(i0[14:12] == 3'b110 && i0[6:0] == 7'b1100011 &&  1'b1 ) || 
(i0[14:12] == 3'b111 && i0[6:0] == 7'b1100011 &&  1'b1 ) || 
1'b0);
// BEQ,BNE,BLT,BGE,BLTU,BGEU