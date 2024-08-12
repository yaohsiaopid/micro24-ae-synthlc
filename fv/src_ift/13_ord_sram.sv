module ord_sram #(
    int unsigned DATA_WIDTH = 64,
    int unsigned NUM_BYTES = 8,
    int unsigned NUM_WORDS  = 65536
)(
   input  logic                          clk_i,
   input  logic                          rst_ni,

   input  logic                          req_i,
   input  logic                          we_i,
   input  logic [$clog2(NUM_WORDS)-1:0]  addr_i,
   input  logic [DATA_WIDTH-1:0]         wdata_i,
   input  logic [NUM_BYTES-1:0]          be_i,
   input  logic [riscv::VLEN-1:0]        pc_i,                     // for FVT
   output logic [DATA_WIDTH-1:0]         rdata_o
, input [15:0] addr_i_t0
, output [63:0] rdata_o_t0
, input [63:0] pc_i_t0
, input [7:0] be_i_t0
, input [63:0] wdata_i_t0
, input we_i_t0
, input req_i_t0
);
    localparam ADDR_WIDTH = $clog2(NUM_WORDS);
`ifndef FUNCVERIF
LIM_ADDR: assume property (@(posedge clk_i)  addr_i <= 16'd31);
    reg [DATA_WIDTH-1:0] ram [0:31];
    reg [DATA_WIDTH-1:0] ram_t0 [0:31];
    reg [ADDR_WIDTH-1:0] raddr_q;
    reg [ADDR_WIDTH-1:0] raddr_q_t0;
    reg [DATA_WIDTH-1:0] local_be_i;

    always @* begin
        local_be_i = '0;
        if (be_i[0]) local_be_i[7:0]   = {8{1'b1}};
        if (be_i[1]) local_be_i[15:8]  = {8{1'b1}};
        if (be_i[2]) local_be_i[23:16] = {8{1'b1}};
        if (be_i[3]) local_be_i[31:24] = {8{1'b1}};
        if (be_i[4]) local_be_i[39:32] = {8{1'b1}};
        if (be_i[5]) local_be_i[47:40] = {8{1'b1}};
        if (be_i[6]) local_be_i[55:48] = {8{1'b1}};
        if (be_i[7]) local_be_i[63:56] = {8{1'b1}};
    end 
    // 1. randomize array
    // 2. randomize output when no request is active
    
    always @(posedge clk_i) begin
        if (!rst_ni) begin
            raddr_q <= '0;
            raddr_q_t0 <= '0;
            ram_t0 <= '{default: '0};
        end else begin
        //if (!rst_ni) begin
            // sb.S init
            //ram[1024] <= 64'hefefefefefefefef;//64'hff00ff0000ff00ff;
            //ram[1025] <= 64'hf00ff00f0ff0efef;

            // sw.S init
            //ram[1024] <= 64'hff00ff0000ff00ff;
            //ram[1025] <= 64'hf00ff00f0ff00ff0;
        //end else begin
            if (req_i) begin
                if (!we_i) begin
                    raddr_q <= addr_i;
                    raddr_q_t0 <= addr_i_t0;
                    $display("ord_sram serve  addr %h data %h", addr_i, ram[addr_i]);
                end else begin
                    $display("ord_sram addr  %h  data %h be_i %b wdata %h", addr_i, wdata_i, be_i, local_be_i & wdata_i);
                    for (int i = 0; i < DATA_WIDTH; i++)
                        if (local_be_i[i]) ram[addr_i[4:0]][i] <= wdata_i[i];
                    `ifdef BLK_T_T_ARCH
                    for (int i = 0; i < DATA_WIDTH; i++)
                        if (local_be_i[i]) ram_t0[addr_i[4:0]][i] <= '0; //wdata_i_t0[i];
                    `else 
                    for (int i = 0; i < DATA_WIDTH; i++)
                        if (local_be_i[i]) ram_t0[addr_i[4:0]][i] <= wdata_i_t0[i];
                    `endif

                end 
            end
        end
        //end 
    end

    assign rdata_o = ram[raddr_q[4:0]];
    assign rdata_o_t0 = raddr_q_t0 | ram_t0[raddr_q[4:0]];
`else

    reg [DATA_WIDTH-1:0] ram [0:NUM_WORDS-1];
    reg [ADDR_WIDTH-1:0] raddr_q;
    reg [DATA_WIDTH-1:0] local_be_i;

    always @* begin
        local_be_i = '0;
        if (be_i[0]) local_be_i[7:0]   = {8{1'b1}};
        if (be_i[1]) local_be_i[15:8]  = {8{1'b1}};
        if (be_i[2]) local_be_i[23:16] = {8{1'b1}};
        if (be_i[3]) local_be_i[31:24] = {8{1'b1}};
        if (be_i[4]) local_be_i[39:32] = {8{1'b1}};
        if (be_i[5]) local_be_i[47:40] = {8{1'b1}};
        if (be_i[6]) local_be_i[55:48] = {8{1'b1}};
        if (be_i[7]) local_be_i[63:56] = {8{1'b1}};
    end 
    // 1. randomize array
    // 2. randomize output when no request is active
    always @(posedge clk_i) begin
        //if (!rst_ni) begin
        //end else begin
            if (req_i) begin
                if (!we_i) begin
                    raddr_q <= addr_i;
                    $display("FUNCTEST ord_sram serve  addr %h data %h", addr_i, ram[addr_i]);
                end else begin
                    $display("FUNCTEST ord_sram addr  %h  data %h be_i %b wdata %h", addr_i, wdata_i, be_i, local_be_i & wdata_i);
                    for (int i = 0; i < DATA_WIDTH; i++)
                        if (local_be_i[i]) ram[addr_i][i] <= wdata_i[i];
                end 
            end
        //end 
    end

    assign rdata_o = ram[raddr_q];
    assign rdata_o_t0 = '0;

`endif
endmodule
