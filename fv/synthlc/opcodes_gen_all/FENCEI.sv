`define SYSINSN
i_FENCEI_0: assume property (i0[31:20] == 12'b000000000000);
i_FENCEI_1: assume property (i0[19:15] == 5'b00000);
i_FENCEI_2: assume property (i0[14:12] == 3'b001);
i_FENCEI_3: assume property (i0[11:7] == 5'b00000);
i_FENCEI_4: assume property (i0[6:0] == 7'b0001111);

