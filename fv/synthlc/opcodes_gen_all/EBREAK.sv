`define SYSINSN
i_EBREAK_0: assume property (i0[31:20] == 12'b000000000001);
i_EBREAK_1: assume property (i0[19:15] == 5'b00000);
i_EBREAK_2: assume property (i0[14:12] == 3'b000);
i_EBREAK_3: assume property (i0[11:7] == 5'b00000);
i_EBREAK_4: assume property (i0[6:0] == 7'b1110011);
