// Copyright 2018 ETH Zurich and University of Bologna.
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License.  You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Author: Florian Zaruba, ETH Zurich
// Date: 19.04.2017
// Description: Load Store Unit, handles address calculation and memory interface signals

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
);
    localparam ADDR_WIDTH = $clog2(NUM_WORDS);
`ifndef FUNCVERIF
LIM_ADDR: assume property (@(posedge clk_i)  addr_i <= 16'd31);
    reg [DATA_WIDTH-1:0] ram [0:31];
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
                    $display("ord_sram serve  addr %h data %h", addr_i, ram[addr_i]);
                end else begin
                    $display("ord_sram addr  %h  data %h be_i %b wdata %h", addr_i, wdata_i, be_i, local_be_i & wdata_i);
                    for (int i = 0; i < DATA_WIDTH; i++)
                        if (local_be_i[i]) ram[addr_i[4:0]][i] <= wdata_i[i];
                end 
            end
        //end 
    end

    assign rdata_o = ram[raddr_q[4:0]];
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

`endif
endmodule

module load_store_unit import ariane_pkg::*; #(
    parameter int unsigned ASID_WIDTH = 1,
    parameter ariane_pkg::ariane_cfg_t ArianeCfg = ariane_pkg::ArianeDefaultConfig
)(
    input  logic                     clk_i,
    input  logic                     rst_ni,
    input  logic                     flush_i,
    output logic                     no_st_pending_o,
    input  logic                     amo_valid_commit_i,

    input  fu_data_t                 fu_data_i,
    input  logic [riscv::VLEN-1:0]   pc_i,                     // for FVT
    output logic                     lsu_ready_o,              // FU is ready e.g. not busy
    input  logic                     lsu_valid_i,              // Input is valid

    output logic [TRANS_ID_BITS-1:0] load_trans_id_o,          // ID of scoreboard entry at which to write back
    output riscv::xlen_t             load_result_o,
    output logic                     load_valid_o,
    output exception_t               load_exception_o,         // to WB, signal exception status LD exception

    output logic [TRANS_ID_BITS-1:0] store_trans_id_o,         // ID of scoreboard entry at which to write back
    output riscv::xlen_t             store_result_o,
    output logic                     store_valid_o,
    output exception_t               store_exception_o,        // to WB, signal exception status ST exception

    input  logic                     commit_i,                 // commit the pending store
    output logic                     commit_ready_o,           // commit queue is ready to accept another commit request
    input  logic [TRANS_ID_BITS-1:0] commit_tran_id_i,

    input  logic                     enable_translation_i,     // enable virtual memory translation
    input  logic                     en_ld_st_translation_i,   // enable virtual memory translation for load/stores

    // icache translation requests
    input  icache_areq_o_t           icache_areq_i,
    output icache_areq_i_t           icache_areq_o,

    input  riscv::priv_lvl_t         priv_lvl_i,               // From CSR register file
    input  riscv::priv_lvl_t         ld_st_priv_lvl_i,         // From CSR register file
    input  logic                     sum_i,                    // From CSR register file
    input  logic                     mxr_i,                    // From CSR register file
    input  logic [riscv::PPNW-1:0]   satp_ppn_i,               // From CSR register file
    input  logic [ASID_WIDTH-1:0]    asid_i,                   // From CSR register file
    input  logic [ASID_WIDTH-1:0]    asid_to_be_flushed_i,
    input  logic [riscv::VLEN-1:0]   vaddr_to_be_flushed_i,
    input  logic                     flush_tlb_i,
    // Performance counters
    output logic                     itlb_miss_o,
    output logic                     dtlb_miss_o,

    // interface to dcache
    //input  dcache_req_o_t [2:0]      dcache_req_ports_i,
    //output dcache_req_i_t [2:0]      dcache_req_ports_o,
    //input  logic                     dcache_wbuffer_empty_i,
    //input  logic                     dcache_wbuffer_not_ni_i,
    // AMO interface
    output amo_req_t                 amo_req_o,
    input  amo_resp_t                amo_resp_i
    // PMP
    //input  riscv::pmpcfg_t [15:0]    pmpcfg_i,
    //input  logic [15:0][riscv::PLEN-3:0] pmpaddr_i
);

    wire [riscv::VLEN-1:0]    load_pc_o;                 // for FVT pc of load that is to be write back

    dcache_req_o_t [2:0]      dcache_req_ports_i;
    dcache_req_i_t [2:0]      dcache_req_ports_o;
    // data is misaligned
    logic data_misaligned;
    // --------------------------------------
    // 1st register stage - (stall registers)
    // --------------------------------------
    // those are the signals which are always correct
    // e.g.: they keep the value in the stall case
    lsu_ctrl_t lsu_ctrl;

    logic      pop_st;
    logic      pop_ld;

    // ------------------------------
    // Address Generation Unit (AGU)
    // ------------------------------
    // virtual address as calculated by the AGU in the first cycle
    logic [riscv::VLEN-1:0]   vaddr_i;
    riscv::xlen_t             vaddr_xlen;
    logic                     overflow;
    logic [7:0]               be_i;

    assign vaddr_xlen = $unsigned($signed(fu_data_i.imm) + $signed(fu_data_i.operand_a));
    assign vaddr_i = vaddr_xlen[riscv::VLEN-1:0];
    // we work with SV39 or SV32, so if VM is enabled, check that all bits [XLEN-1:38] or [XLEN-1:31] are equal
    assign overflow = !((&vaddr_xlen[riscv::XLEN-1:riscv::SV-1]) == 1'b1 || (|vaddr_xlen[riscv::XLEN-1:riscv::SV-1]) == 1'b0);

    logic                     st_valid_i;
    logic                     ld_valid_i;
    logic                     ld_translation_req;
    logic                     st_translation_req;
    logic [riscv::VLEN-1:0]   ld_vaddr;
    logic [riscv::VLEN-1:0]   st_vaddr;
    logic                     translation_req;
    logic                     translation_valid;
    logic [riscv::VLEN-1:0]   mmu_vaddr;
    logic [riscv::PLEN-1:0]   mmu_paddr;
    exception_t               mmu_exception;
    logic                     dtlb_hit;
    logic [riscv::PPNW-1:0]   dtlb_ppn;

    logic                     ld_valid;
    logic [TRANS_ID_BITS-1:0] ld_trans_id;
    logic [riscv::VLEN-1:0]   ld_pc; // for FVT
    riscv::xlen_t             ld_result;
    logic                     st_valid;
    logic [TRANS_ID_BITS-1:0] st_trans_id;
    riscv::xlen_t             st_result;

    logic [11:0]              page_offset;
    logic                     page_offset_matches;

    exception_t               misaligned_exception;
    exception_t               ld_ex;
    exception_t               st_ex;

    // -------------------
    // MMU e.g.: TLBs/PTW
    // -------------------
//    if (MMU_PRESENT && (riscv::XLEN == 64)) begin : gen_mmu_sv39
//        mmu #(
//            .INSTR_TLB_ENTRIES      ( 16                     ),
//            .DATA_TLB_ENTRIES       ( 16                     ),
//            .ASID_WIDTH             ( ASID_WIDTH             ),
//            .ArianeCfg              ( ArianeCfg              )
//        ) i_cva6_mmu (
//            // misaligned bypass
//            .misaligned_ex_i        ( misaligned_exception   ),
//            .lsu_is_store_i         ( st_translation_req     ),
//            .lsu_req_i              ( translation_req        ),
//            .lsu_vaddr_i            ( mmu_vaddr              ),
//            .lsu_valid_o            ( translation_valid      ),
//            .lsu_paddr_o            ( mmu_paddr              ),
//            .lsu_exception_o        ( mmu_exception          ),
//            .lsu_dtlb_hit_o         ( dtlb_hit               ), // send in the same cycle as the request
//            .lsu_dtlb_ppn_o         ( dtlb_ppn               ), // send in the same cycle as the request
//            // connecting PTW to D$ IF
//            .req_port_i             ( dcache_req_ports_i [0] ),
//            .req_port_o             ( dcache_req_ports_o [0] ),
//            // icache address translation requests
//            .icache_areq_i          ( icache_areq_i          ),
//            .asid_to_be_flushed_i,
//            .vaddr_to_be_flushed_i,
//            .icache_areq_o          ( icache_areq_o          ),
//            .pmpcfg_i,
//            .pmpaddr_i,
//            .*
//        );
//    end else if (MMU_PRESENT && (riscv::XLEN == 32)) begin : gen_mmu_sv32
//        cva6_mmu_sv32 #(
//            .INSTR_TLB_ENTRIES      ( 16                     ),
//            .DATA_TLB_ENTRIES       ( 16                     ),
//            .ASID_WIDTH             ( ASID_WIDTH             ),
//            .ArianeCfg              ( ArianeCfg              )
//        ) i_cva6_mmu (
//            // misaligned bypass
//            .misaligned_ex_i        ( misaligned_exception   ),
//            .lsu_is_store_i         ( st_translation_req     ),
//            .lsu_req_i              ( translation_req        ),
//            .lsu_vaddr_i            ( mmu_vaddr              ),
//            .lsu_valid_o            ( translation_valid      ),
//            .lsu_paddr_o            ( mmu_paddr              ),
//            .lsu_exception_o        ( mmu_exception          ),
//            .lsu_dtlb_hit_o         ( dtlb_hit               ), // send in the same cycle as the request
//            .lsu_dtlb_ppn_o         ( dtlb_ppn               ), // send in the same cycle as the request
//            // connecting PTW to D$ IF
//            .req_port_i             ( dcache_req_ports_i [0] ),
//            .req_port_o             ( dcache_req_ports_o [0] ),
//            // icache address translation requests
//            .icache_areq_i          ( icache_areq_i          ),
//            .asid_to_be_flushed_i,
//            .vaddr_to_be_flushed_i,
//            .icache_areq_o          ( icache_areq_o          ),
//            .pmpcfg_i,
//            .pmpaddr_i,
//            .*
//        );
//    end else begin : gen_no_mmu
        assign  icache_areq_o.fetch_valid  = icache_areq_i.fetch_req;
        assign  icache_areq_o.fetch_paddr  = icache_areq_i.fetch_vaddr[riscv::PLEN-1:0];
        assign  icache_areq_o.fetch_exception      = '0;

        assign dcache_req_ports_o[0].address_index = '0;
        assign dcache_req_ports_o[0].address_tag   = '0;
        assign dcache_req_ports_o[0].data_wdata    = 64'b0;
        assign dcache_req_ports_o[0].data_req      = 1'b0;
        assign dcache_req_ports_o[0].data_be       = 8'hFF;
        assign dcache_req_ports_o[0].data_size     = 2'b11;
        assign dcache_req_ports_o[0].data_we       = 1'b0;
        assign dcache_req_ports_o[0].kill_req      = '0;
        assign dcache_req_ports_o[0].tag_valid     = 1'b0;

        assign itlb_miss_o = 1'b0;
        assign dtlb_miss_o = 1'b0;
        assign dtlb_ppn    = mmu_vaddr[riscv::PLEN-1:12];
        assign dtlb_hit    = 1'b1;

        assign mmu_exception = '0;

        always_ff @(posedge clk_i or negedge rst_ni) begin
            if (~rst_ni) begin
                mmu_paddr         <= '0;
                translation_valid <= '0;
            end else begin
                mmu_paddr         <=  mmu_vaddr[riscv::PLEN-1:0];
                translation_valid <= translation_req;
            end
        end
//    end


    // ------------------------------------------------------------------------
    // NO_CACHE: single R/W port sram
    // ------------------------------------------------------------------------
    reg sel_lsu_q;
    dcache_req_i_t      dcache_req_ports_o_st;
    dcache_req_i_t      dcache_req_ports_o_ld;
    dcache_req_o_t      dcache_req_ports_i_ld;
    dcache_req_o_t      dcache_req_ports_i_st;

    // Since it issues one instruction at a cycle only, older store enters
    // store units before younger load. For a back-to-back store-x then load-x,
    // when load-x is in load unit, the previous store has already enters.
    //          
    //  st x at store_unit | 
    //                     | st x post to spec buf      |
    //                     | ld x at load unit (pa cam) | st x in spec buf
    //                     | pa cam on all buf and new  |
    //                     | entry being posted to spec |
    //                     | buf stb

    // as long as page_offset_matches in store buffers, they are older store,
    // and it serves older store first 
    // If no match, load has higher priority in original wt_dcache system
    wire sel_lsu = (dcache_req_ports_o_ld.data_req && page_offset_matches) ? 1 : 
                    (dcache_req_ports_o_ld.data_req ? 0 : 1);  
    // load has higher priority

NO_LOAD_STORE_UNIT_SIMULT: assert property (@(posedge clk_i)
    !(dcache_req_ports_o_st.data_req && dcache_req_ports_o_ld.data_req));

    always @(posedge clk_i) begin
        if (dcache_req_ports_o_ld.data_req && page_offset_matches) begin
            $display("!!! page offset matches!! sel_lsu is %b", sel_lsu);
        end 
        if (dcache_req_ports_o_ld.data_req) begin
            $display("ld_req!");
        end 
        if (dcache_req_ports_o_st.data_req) begin
            $display("st_req!");
        end 
    end 

    wire ord_sram_req_i = sel_lsu ? dcache_req_ports_o_st.data_req : dcache_req_ports_o_ld.data_req ;
    wire ord_sram_we_i = sel_lsu ? dcache_req_ports_o_st.data_req : 0; 
`ifndef FUNCVERIF
    wire [16-1:0] ord_sram_addr_i = sel_lsu ? dcache_req_ports_o_st.virtual_address[3+16-1:3] : dcache_req_ports_o_ld.virtual_address[3+16-1:3];
`else
    wire [25-1:0] ord_sram_addr_i = sel_lsu ? dcache_req_ports_o_st.virtual_address[3+25-1:3] : dcache_req_ports_o_ld.virtual_address[3+25-1:3];
`endif
    wire [riscv::VLEN-1:0]  ord_sram_pc_i = sel_lsu ? dcache_req_ports_o_st.pc : dcache_req_ports_o_ld.pc; // for FVT

    localparam data_size = 64;
    localparam num_size = 8;

    wire [data_size-1:0] ord_sram_wdata_i = sel_lsu ? dcache_req_ports_o_st.data_wdata : '0;
    wire [num_size-1:0] ord_sram_be_i = sel_lsu? dcache_req_ports_o_st.data_be : dcache_req_ports_o_ld.data_be; 
    wire [data_size-1:0] ord_sram_rdata_o;

    reg ld_serve_prev;
    always @(posedge clk_i) begin
        if (!rst_ni) 
            ld_serve_prev <= 0;
        else 
            ld_serve_prev <= (ord_sram_req_i && ord_sram_we_i == 0);
    end 
    assign dcache_req_ports_i_ld.data_rvalid = ld_serve_prev;
    assign dcache_req_ports_i_ld.data_rdata = ord_sram_rdata_o;
    assign dcache_req_ports_i_ld.data_gnt = (sel_lsu == 0);

    assign dcache_req_ports_i_st.data_gnt = (sel_lsu == 1); 


    ord_sram #(
    `ifndef FUNCVERIF
        .DATA_WIDTH(64),
        .NUM_BYTES(8),
        .NUM_WORDS(32)
    `else
        .DATA_WIDTH(64),
        .NUM_BYTES(8),
        .NUM_WORDS(2**25)
    `endif

    ) i_ord_sram (
        .clk_i                 ( clk_i                ),
        .rst_ni                ( rst_ni               ),
        .req_i                 ( ord_sram_req_i       ), 
        .we_i                  ( ord_sram_we_i        ), 
        .addr_i                ( ord_sram_addr_i      ),
        .wdata_i               ( ord_sram_wdata_i     ),
        .be_i                  ( ord_sram_be_i        ),
        .pc_i                  ( ord_sram_pc_i        ),
        .rdata_o               ( ord_sram_rdata_o     )
    );

    
    
    logic store_buffer_empty;
    // ------------------
    // Store Unit
    // ------------------
    store_unit i_store_unit (
        .clk_i,
        .rst_ni,
        .flush_i,
        .no_st_pending_o,
        .store_buffer_empty_o  ( store_buffer_empty   ),

        .valid_i               ( st_valid_i           ),
        .lsu_ctrl_i            ( lsu_ctrl             ),
        .pop_st_o              ( pop_st               ),
        .commit_i,
        .commit_ready_o,
        .amo_valid_commit_i,

        .valid_o               ( st_valid             ),
        .trans_id_o            ( st_trans_id          ),
        .result_o              ( st_result            ),
        .ex_o                  ( st_ex                ),
        // MMU port
        .translation_req_o     ( st_translation_req   ),
        .vaddr_o               ( st_vaddr             ),
        .paddr_i               ( mmu_paddr            ),
        .ex_i                  ( mmu_exception        ),
        .dtlb_hit_i            ( dtlb_hit             ),
        // Load Unit
        .page_offset_i         ( page_offset          ),
        .page_offset_matches_o ( page_offset_matches  ),
        // AMOs
        .amo_req_o,
        .amo_resp_i,
        // to memory arbiter
        //.req_port_i             ( dcache_req_ports_i [2] ),
        .req_port_i_tmp         ( dcache_req_ports_i_st  ),
        //.req_port_o             ( dcache_req_ports_o [2] ),
        .req_port_o_tmp         ( dcache_req_ports_o_st  )
    );

    // ------------------
    // Load Unit
    // ------------------
    load_unit #(
        .ArianeCfg ( ArianeCfg )
    ) i_load_unit (
        .valid_i               ( ld_valid_i           ),
        .lsu_ctrl_i            ( lsu_ctrl             ),
        .pop_ld_o              ( pop_ld               ),

        .valid_o               ( ld_valid             ),
        .trans_id_o            ( ld_trans_id          ),
        .pc_o                  ( ld_pc                ),
        .result_o              ( ld_result            ),
        .ex_o                  ( ld_ex                ),
        // MMU port
        .translation_req_o     ( ld_translation_req   ),
        .vaddr_o               ( ld_vaddr             ),
        .paddr_i               ( mmu_paddr            ),
        .ex_i                  ( mmu_exception        ),
        .dtlb_hit_i            ( dtlb_hit             ),
        .dtlb_ppn_i            ( dtlb_ppn             ),
        // to store unit
        .page_offset_o         ( page_offset          ),
        .page_offset_matches_i ( page_offset_matches  ),
        .store_buffer_empty_i  ( store_buffer_empty   ),
        // to memory arbiter
        //.req_port_i            ( dcache_req_ports_i [1] ),
        .req_port_i_tmp         ( dcache_req_ports_i_ld  ),
        //.req_port_o            ( dcache_req_ports_o [1] ),
        .req_port_o_tmp        ( dcache_req_ports_o_ld  ), 
        .commit_tran_id_i,
        .*
    );

    // ----------------------------
    // Output Pipeline Register
    // ----------------------------
    shift_reg #(
        .dtype ( logic[$bits(ld_valid) + $bits(ld_trans_id) + $bits(ld_result) + $bits(ld_ex) + $bits(ld_pc) - 1: 0]),
        .Depth ( NR_LOAD_PIPE_REGS )
    ) i_pipe_reg_load (
        .clk_i,
        .rst_ni,
        .d_i ( {ld_valid, ld_trans_id, ld_result, ld_ex, ld_pc} ),
        .d_o ( {load_valid_o, load_trans_id_o, load_result_o, load_exception_o, load_pc_o} )

    );

    shift_reg #(
        .dtype ( logic[$bits(st_valid) + $bits(st_trans_id) + $bits(st_result) + $bits(st_ex) - 1: 0]),
        .Depth ( NR_STORE_PIPE_REGS )
    ) i_pipe_reg_store (
        .clk_i,
        .rst_ni,
        .d_i ( {st_valid, st_trans_id, st_result, st_ex} ),
        .d_o ( {store_valid_o, store_trans_id_o, store_result_o, store_exception_o} )
    );

    // determine whether this is a load or store
    always_comb begin : which_op

        ld_valid_i = 1'b0;
        st_valid_i = 1'b0;

        translation_req      = 1'b0;
        mmu_vaddr            = {riscv::VLEN{1'b0}};

        // check the operator to activate the right functional unit accordingly
        unique case (lsu_ctrl.fu)
            // all loads go here
            LOAD:  begin
                ld_valid_i           = lsu_ctrl.valid;
                translation_req      = ld_translation_req;
                mmu_vaddr            = ld_vaddr;
            end
            // all stores go here
            STORE: begin
                st_valid_i           = lsu_ctrl.valid;
                translation_req      = st_translation_req;
                mmu_vaddr            = st_vaddr;
            end
            // not relevant for the LSU
            default: ;
        endcase
    end


    // ---------------
    // Byte Enable
    // ---------------
    // we can generate the byte enable from the virtual address since the last
    // 12 bit are the same anyway
    // and we can always generate the byte enable from the address at hand
    assign be_i = be_gen(vaddr_i[2:0], extract_transfer_size(fu_data_i.operator));

    // ------------------------
    // Misaligned Exception
    // ------------------------
    // we can detect a misaligned exception immediately
    // the misaligned exception is passed to the functional unit via the MMU, which in case
    // can augment the exception if other memory related exceptions like a page fault or access errors
    always_comb begin : data_misaligned_detection

        misaligned_exception = {
            {riscv::XLEN{1'b0}},
            {riscv::XLEN{1'b0}},
            1'b0
        };

        data_misaligned = 1'b0;

        if (lsu_ctrl.valid) begin
            case (lsu_ctrl.operator)
                // double word
                LD, SD, FLD, FSD,
                AMO_LRD, AMO_SCD,
                AMO_SWAPD, AMO_ADDD, AMO_ANDD, AMO_ORD,
                AMO_XORD, AMO_MAXD, AMO_MAXDU, AMO_MIND,
                AMO_MINDU: begin
                    if (lsu_ctrl.vaddr[2:0] != 3'b000) begin
                        data_misaligned = 1'b1;
                    end
                end
                // word
                LW, LWU, SW, FLW, FSW,
                AMO_LRW, AMO_SCW,
                AMO_SWAPW, AMO_ADDW, AMO_ANDW, AMO_ORW,
                AMO_XORW, AMO_MAXW, AMO_MAXWU, AMO_MINW,
                AMO_MINWU: begin
                    if (lsu_ctrl.vaddr[1:0] != 2'b00) begin
                        data_misaligned = 1'b1;
                    end
                end
                // half word
                LH, LHU, SH, FLH, FSH: begin
                    if (lsu_ctrl.vaddr[0] != 1'b0) begin
                        data_misaligned = 1'b1;
                    end
                end
                // byte -> is always aligned
                default:;
            endcase
        end

        if (data_misaligned) begin

            if (lsu_ctrl.fu == LOAD) begin
                misaligned_exception = {
                    riscv::LD_ADDR_MISALIGNED,
                    {{riscv::XLEN-riscv::VLEN{1'b0}},lsu_ctrl.vaddr},
                    1'b1
                };

            end else if (lsu_ctrl.fu == STORE) begin
                misaligned_exception = {
                    riscv::ST_ADDR_MISALIGNED,
                    {{riscv::XLEN-riscv::VLEN{1'b0}},lsu_ctrl.vaddr},
                    1'b1
                };
            end
        end

        if (en_ld_st_translation_i && lsu_ctrl.overflow) begin

            if (lsu_ctrl.fu == LOAD) begin
                misaligned_exception = {
                    riscv::LD_ACCESS_FAULT,
                    {{riscv::XLEN-riscv::VLEN{1'b0}},lsu_ctrl.vaddr},
                    1'b1
                };

            end else if (lsu_ctrl.fu == STORE) begin
                misaligned_exception = {
                    riscv::ST_ACCESS_FAULT,
                    {{riscv::XLEN-riscv::VLEN{1'b0}},lsu_ctrl.vaddr},
                    1'b1
                };
            end
        end
    end

    // ------------------
    // LSU Control
    // ------------------
    // new data arrives here
    lsu_ctrl_t lsu_req_i;

    assign lsu_req_i = {lsu_valid_i, vaddr_i, overflow, {{64-riscv::XLEN{1'b0}}, fu_data_i.operand_b}, be_i, fu_data_i.fu, fu_data_i.operator, fu_data_i.trans_id
     , pc_i  // for FVT 
    }; 

    lsu_bypass lsu_bypass_i (
        .lsu_req_i          ( lsu_req_i   ),
        .lsu_req_valid_i    ( lsu_valid_i ),
        .pop_ld_i           ( pop_ld      ),
        .pop_st_i           ( pop_st      ),

        .lsu_ctrl_o         ( lsu_ctrl    ),
        .ready_o            ( lsu_ready_o ),
        .*
    );

endmodule

// ------------------
// LSU Control
// ------------------
// The LSU consists of two independent block which share a common address translation block.
// The one block is the load unit, the other one is the store unit. They will signal their readiness
// with separate signals. If they are not ready the LSU control should keep the last applied signals stable.
// Furthermore it can be the case that another request for one of the two store units arrives in which case
// the LSU control should sample it and store it for later application to the units. It does so, by storing it in a
// two element FIFO. This is necessary as we only know very late in the cycle whether the load/store will succeed (address check,
// TLB hit mainly). So we better unconditionally allow another request to arrive and store this request in case we need to.
module lsu_bypass import ariane_pkg::*; (
    input  logic      clk_i,
    input  logic      rst_ni,
    input  logic      flush_i,

    input  lsu_ctrl_t lsu_req_i,
    input  logic      lsu_req_valid_i,
    input  logic      pop_ld_i,
    input  logic      pop_st_i,

    output lsu_ctrl_t lsu_ctrl_o,
    output logic      ready_o
    );

    lsu_ctrl_t [1:0] mem_n, mem_q;
    logic read_pointer_n, read_pointer_q;
    logic write_pointer_n, write_pointer_q;
    logic [1:0] status_cnt_n, status_cnt_q;

    logic  empty;
    assign empty = (status_cnt_q == 0);
    assign ready_o = empty;

    always_comb begin
        automatic logic [1:0] status_cnt;
        automatic logic write_pointer;
        automatic logic read_pointer;

        status_cnt = status_cnt_q;
        write_pointer = write_pointer_q;
        read_pointer = read_pointer_q;

        mem_n = mem_q;
        // we've got a valid LSU request
        if (lsu_req_valid_i) begin
            mem_n[write_pointer_q] = lsu_req_i;
            write_pointer++;
            status_cnt++;
        end

        if (pop_ld_i) begin
            // invalidate the result
            mem_n[read_pointer_q].valid = 1'b0;
            read_pointer++;
            status_cnt--;
        end

        if (pop_st_i) begin
            // invalidate the result
            mem_n[read_pointer_q].valid = 1'b0;
            read_pointer++;
            status_cnt--;
        end

        if (pop_st_i && pop_ld_i)
            mem_n = '0;

        if (flush_i) begin
            status_cnt = '0;
            write_pointer = '0;
            read_pointer = '0;
            mem_n = '0;
        end
        // default assignments
        read_pointer_n  = read_pointer;
        write_pointer_n = write_pointer;
        status_cnt_n    = status_cnt;
    end

    // output assignment
    always_comb begin : output_assignments
        if (empty) begin
            lsu_ctrl_o = lsu_req_i;
        end else begin
            lsu_ctrl_o = mem_q[read_pointer_q];
        end
    end

    // registers
    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (~rst_ni) begin
            mem_q           <= '0;
            status_cnt_q    <= '0;
            write_pointer_q <= '0;
            read_pointer_q  <= '0;
        end else begin
            mem_q           <= mem_n;
            status_cnt_q    <= status_cnt_n;
            write_pointer_q <= write_pointer_n;
            read_pointer_q  <= read_pointer_n;
        end
    end
endmodule

