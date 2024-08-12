`define SYSINSN
i_FENCE_0: assume property (i0[31:28] == 4'b0000);
i_FENCE_1: assume property (i0[19:15] == 5'b00000);
i_FENCE_2: assume property (i0[14:12] == 3'b000);
i_FENCE_3: assume property (i0[11:7] == 5'b00000);
i_FENCE_4: assume property (i0[6:0] == 7'b0001111);
