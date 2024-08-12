// src/fv_header.sv IFT instrumented version
property CONST (N);
    @(posedge clk_i) N == $past(N);
endproperty

 reg first;
 `ifdef SYMSTART
 wire rst_ni_psuedo;
 `endif
 always @(posedge clk_i) begin
 `ifdef SYMSTART
     if (!rst_ni_psuedo) begin
 `else
     if (!rst_ni) begin
 `endif
         first <= 1;
     end else if (first == 1) begin
         first <= 0;
     end
 end

assign \amo_resp.ack_t0 = '0;
assign \amo_resp.result_t0 = '0;
assign \fetch_entry_if_id.address_t0 = '0;
assign \fetch_entry_if_id.branch_predict.cf_t0 = '0;
assign \fetch_entry_if_id.branch_predict.predict_address_t0 = '0;
assign \fetch_entry_if_id.ex.cause_t0 = '0;
assign \fetch_entry_if_id.ex.tval_t0 = '0;
assign \fetch_entry_if_id.ex.valid_t0 = '0;
assign \tmp_icache_dreq_cache_if.data_t0 = '0;
assign \tmp_icache_dreq_cache_if.ex.cause_t0 = '0;
assign \tmp_icache_dreq_cache_if.ex.tval_t0 = '0;
assign \tmp_icache_dreq_cache_if.ex.valid_t0 = '0;
assign \tmp_icache_dreq_cache_if.ready_t0 = '0;
assign \tmp_icache_dreq_cache_if.vaddr_t0 = '0;
assign \tmp_icache_dreq_cache_if.valid_t0 = '0;
assign \tmp_icache_dreq_if_cache.kill_s1_t0 = '0;
assign \tmp_icache_dreq_if_cache.kill_s2_t0 = '0;
assign \tmp_icache_dreq_if_cache.req_t0 = '0;
assign \tmp_icache_dreq_if_cache.spec_t0 = '0;
assign \tmp_icache_dreq_if_cache.vaddr_t0 = '0;
//assign ex_stage_i.\amo_resp_i.result_t0 = '0;
//assign ex_stage_i.\icache_areq_i.fetch_req_t0 = '0;
//assign ex_stage_i.\icache_areq_i.fetch_vaddr_t0 = '0;
//assign ex_stage_i.i_mult.i_div.i_lzc_a.\gen_lzc.sel_nodes_t0 = '0;
//assign ex_stage_i.i_mult.i_div.i_lzc_b.\gen_lzc.sel_nodes_t0 = '0;
//assign ex_stage_i.lsu_i.\dcache_req_ports_i_st.data_rdata_t0 = '0;
//assign ex_stage_i.lsu_i.\dcache_req_ports_i_st.data_rvalid_t0 = '0;
//assign fetch_valid_if_id_t0 = '0;
//assign \fetch_entry_if_id.instruction_t0 = '0;
// Post-trace: any instruction encoding but invalid 
// Assume IUV issued at first cycle after reset
// Symbolic reset on the memory and regfile
`define INTRA_TRANSMITTER 

// =============================================================================
// Frontend-legal-setup (since we bbox) and processor in operation
// =============================================================================

//BBOX_AMO_REQ: assume property (@(posedge clk_i) 
//      commit_stage_i.amo_resp_i.ack == 1'b0);
//BRANCH: assume property (@(posedge clk_i) 
//      id_stage_i.fetch_entry_i.branch_predict.predict_address != pc0);

NON_EXCEPTION_FRONTEND: assume property (@(posedge clk_i)
  \fetch_entry_if_id.ex.valid == 1'b0
  // tag this fetched instruction is not exceptioned already at front-end
  // (e.g., INSTR_PAGE_FAULT or INSTR_ACCESS_FAULT)
);
IF_ID_CONTRACT: assume property (@(posedge clk_i)
  // yet ack then hold
  (id_stage_i.fetch_entry_valid_i && !(fetch_ready_id_if)) |=>
  (
  ($past(id_stage_i.fetch_entry_valid_i ) == id_stage_i.fetch_entry_valid_i ) &&
  ($past(id_stage_i.instruction ) == id_stage_i.instruction ) &&
  ($past(id_stage_i.\fetch_entry_i.address ) == id_stage_i.\fetch_entry_i.address )
  )
);

IN_OP_MODE: assume property (@(posedge clk_i) rst_ni == 1'd1);
NOHALT: assume property (@(posedge clk_i) commit_stage_i.halt_i == 1'b0);

// =============================================================================
// Set up instruction of interest 
// =============================================================================
wire [32-1:0] i0;
i0_const: assume property (@(posedge clk_i) CONST(i0));

// =============================================================================
// Set up pc value, instruction issue, and execution contexts
// =============================================================================
// (pc0, i0)
wire [64-1:0] pc0;

pc0_const: assume property (@(posedge clk_i) CONST(pc0));
pc0_nozero: assume property (@(posedge clk_i) pc0 != '0);

wire instn_begin = (id_stage_i.fetch_entry_valid_i && 
                    id_stage_i.\fetch_entry_i.address == pc0);

pc0_i0_assoc_1: assume property (@(posedge clk_i) 
    id_stage_i.\fetch_entry_i.address == pc0 |-> id_stage_i.instruction == i0);
pc0_i0_assoc_2: assume property (@(posedge clk_i) 
    id_stage_i.\fetch_entry_i.address == pc0 |-> 
    (id_stage_i.fetch_entry_valid_i == 1'b1 && 
`ifndef SYSINSN
    id_stage_i.\decoded_instruction.ex.valid == 1'b0) 
`else
    id_stage_i.\fetch_entry_i.ex.valid == 1'b0)
`endif
    // IF issuing a valid request, i.e. no exception raised so far at IF
);

VALID_INSTN: assume property (@(posedge clk_i) id_stage_i.fetch_entry_valid_i );

ISSUE_ONCE: assume property (@(posedge clk_i) instn_begin |=> 
        always !(id_stage_i.\fetch_entry_i.address == pc0));
EVENTUAL_ISSUE: assume property (@(posedge clk_i) first |->
    s_eventually(instn_begin));
EXE_IUV: assume property (@(posedge clk_i) instn_begin |-> fetch_ready_id_if);

// =============================================================================
// ## Performing location annotation
// ============================================================================= 
wire serdiv_unit_divide_s1 = 
	(ex_stage_i.i_mult.i_div.pc_q == pc0) && 
	(ex_stage_i.i_mult.i_div.state_q == 2'd1) && 
	 1'b1; 
wire serdiv_unit_divide_s2 = 
	(ex_stage_i.i_mult.i_div.pc_q == pc0) && 
	(ex_stage_i.i_mult.i_div.state_q == 2'd2) && 
	 1'b1; 
wire id_stage_s1 = 
	(id_stage_i.\issue_q.sbe.pc == pc0) && 
	(id_stage_i.\issue_q.valid == 1'd1) && 
	 1'b1; 
wire issue_s1 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc0) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd1) && 
	 1'b1; 
wire issue_s2 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc0) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire issue_s8 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc0) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire issue_s16 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc0) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire issue_s32 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc0) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire lsq_enq_0_s1 = 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[0].pc == pc0) && 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[0].valid == 1'd1) && 
	 1'b1; 
wire lsq_enq_1_s1 = 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[1].pc == pc0) && 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[1].valid == 1'd1) && 
	 1'b1; 
wire scb_0_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire scb_0_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd1) && 
	 1'b1; 
wire scb_0_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire scb_0_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire scb_1_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire scb_1_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd1) && 
	 1'b1; 
wire scb_1_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire scb_1_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire scb_2_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire scb_2_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd1) && 
	 1'b1; 
wire scb_2_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire scb_2_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire scb_3_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire scb_3_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd1) && 
	 1'b1; 
wire scb_3_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire scb_3_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire stb_com_0_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[0].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[0].valid == 1'd1) && 
	 1'b1; 
wire stb_com_1_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[1].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[1].valid == 1'd1) && 
	 1'b1; 
wire stb_spec_0_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[0].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[0].valid == 1'd1) && 
	 1'b1; 
wire stb_spec_1_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[1].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[1].valid == 1'd1) && 
	 1'b1; 
wire load_unit_s1 = 
	(ex_stage_i.lsu_i.i_load_unit.\load_data_q.ld_pc == pc0) && 
	(ex_stage_i.lsu_i.i_load_unit.valid_o == 1'd1) && 
	 1'b1; 
wire store_unit_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.st_pc_q == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.state_q == 2'd1) && 
	 1'b1; 
wire store_unit_s3 = 
	(ex_stage_i.lsu_i.i_store_unit.st_pc_q == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.state_q == 2'd3) && 
	 1'b1; 
wire load_unit_buff_s1 = 
	(ex_stage_i.lsu_i.load_pc_o == pc0) && 
	(ex_stage_i.lsu_i.load_valid_o == 1'd1) && 
	 1'b1; 
wire csr_buffer_s1 = 
	(ex_stage_i.csr_buffer_i.\csr_reg_q.pc == pc0) && 
	(ex_stage_i.csr_buffer_i.\csr_reg_q.valid == 1'd1) && 
	 1'b1; 
wire mult_s1 = 
	(ex_stage_i.i_mult.i_multiplier.pc_q == pc0) && 
	(ex_stage_i.i_mult.i_multiplier.mult_valid_q == 1'd1) && 
	 1'b1; 

wire load_unit_op_s1 = 
	(ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc == pc0) && 
    (ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) &&
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd1) && 
	 1'b1; 
wire load_unit_op_s2 = 
	(ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc == pc0) && 
    (ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) &&
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd2) && 
	 1'b1; 
wire load_unit_op_s3 = 
	(ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc == pc0) && 
    (ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) &&
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd3) && 
	 1'b1; 
wire mem_req_s1 = 
    (ex_stage_i.lsu_i.i_ord_sram.pc_i == pc0) && 
    (ex_stage_i.lsu_i.i_ord_sram.req_i == 1'b1) &&
    1'b1;
// ================================================================================ 
// Taint signals
// ================================================================================ 

wire serdiv_unit_divide_s1_t0 = |{ex_stage_i.i_mult.i_div.state_q_t0 ,ex_stage_i.i_mult.i_div.pc_q_t0  };
wire serdiv_unit_divide_s2_t0 = |{ex_stage_i.i_mult.i_div.state_q_t0 ,ex_stage_i.i_mult.i_div.pc_q_t0  };
wire id_stage_s1_t0 = |{id_stage_i.\issue_q.sbe.pc_t0 ,id_stage_i.\issue_q.valid_t0  };
wire issue_s1_t0 = |{issue_stage_i.i_issue_read_operands.csr_valid_q_t0 ,issue_stage_i.i_issue_read_operands.branch_valid_q_t0 ,issue_stage_i.i_issue_read_operands.fpu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.mult_valid_q_t0 ,issue_stage_i.i_issue_read_operands.alu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.pc_o_t0 ,issue_stage_i.i_issue_read_operands.lsu_valid_q_t0  };
wire issue_s2_t0 = |{issue_stage_i.i_issue_read_operands.csr_valid_q_t0 ,issue_stage_i.i_issue_read_operands.branch_valid_q_t0 ,issue_stage_i.i_issue_read_operands.fpu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.mult_valid_q_t0 ,issue_stage_i.i_issue_read_operands.alu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.pc_o_t0 ,issue_stage_i.i_issue_read_operands.lsu_valid_q_t0  };
wire issue_s8_t0 = |{issue_stage_i.i_issue_read_operands.csr_valid_q_t0 ,issue_stage_i.i_issue_read_operands.branch_valid_q_t0 ,issue_stage_i.i_issue_read_operands.fpu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.mult_valid_q_t0 ,issue_stage_i.i_issue_read_operands.alu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.pc_o_t0 ,issue_stage_i.i_issue_read_operands.lsu_valid_q_t0  };
wire issue_s16_t0 = |{issue_stage_i.i_issue_read_operands.csr_valid_q_t0 ,issue_stage_i.i_issue_read_operands.branch_valid_q_t0 ,issue_stage_i.i_issue_read_operands.fpu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.mult_valid_q_t0 ,issue_stage_i.i_issue_read_operands.alu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.pc_o_t0 ,issue_stage_i.i_issue_read_operands.lsu_valid_q_t0  };
wire issue_s32_t0 = |{issue_stage_i.i_issue_read_operands.csr_valid_q_t0 ,issue_stage_i.i_issue_read_operands.branch_valid_q_t0 ,issue_stage_i.i_issue_read_operands.fpu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.mult_valid_q_t0 ,issue_stage_i.i_issue_read_operands.alu_valid_q_t0 ,issue_stage_i.i_issue_read_operands.pc_o_t0 ,issue_stage_i.i_issue_read_operands.lsu_valid_q_t0  };
wire lsq_enq_0_s1_t0 = |{ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[0].pc_t0 ,ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[0].valid_t0  };
wire lsq_enq_1_s1_t0 = |{ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[1].valid_t0 ,ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[1].pc_t0  };
wire scb_0_s12_t0 = |{issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_n[0].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid_t0  };
wire scb_0_s13_t0 = |{issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_n[0].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid_t0  };
wire scb_0_s14_t0 = |{issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_n[0].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid_t0  };
wire scb_0_s8_t0 = |{issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_n[0].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid_t0  };
wire scb_1_s12_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].issued_t0 ,issue_stage_i.i_scoreboard.\mem_n[1].issued_t0  };
wire scb_1_s13_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].issued_t0 ,issue_stage_i.i_scoreboard.\mem_n[1].issued_t0  };
wire scb_1_s14_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].issued_t0 ,issue_stage_i.i_scoreboard.\mem_n[1].issued_t0  };
wire scb_1_s8_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[1].issued_t0 ,issue_stage_i.i_scoreboard.\mem_n[1].issued_t0  };
wire scb_2_s12_t0 = |{issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_n[2].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].issued_t0  };
wire scb_2_s13_t0 = |{issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_n[2].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].issued_t0  };
wire scb_2_s14_t0 = |{issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_n[2].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].issued_t0  };
wire scb_2_s8_t0 = |{issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\mem_n[2].issued_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc_t0 ,issue_stage_i.i_scoreboard.\mem_q[2].issued_t0  };
wire scb_3_s12_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.\mem_n[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc_t0  };
wire scb_3_s13_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.\mem_n[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc_t0  };
wire scb_3_s14_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.\mem_n[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc_t0  };
wire scb_3_s8_t0 = |{issue_stage_i.i_scoreboard.\commit_pointer_q[0]_t0 ,issue_stage_i.i_scoreboard.\commit_pointer_q[1]_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid_t0 ,issue_stage_i.i_scoreboard.commit_ack_i_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid_t0 ,issue_stage_i.i_scoreboard.\mem_n[3].issued_t0 ,issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc_t0  };
wire stb_com_0_s1_t0 = |{ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[0].pc_t0 ,ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[0].valid_t0  };
wire stb_com_1_s1_t0 = |{ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[1].valid_t0 ,ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[1].pc_t0  };
wire stb_spec_0_s1_t0 = |{ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[0].pc_t0 ,ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[0].valid_t0  };
wire stb_spec_1_s1_t0 = |{ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[1].pc_t0 ,ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[1].valid_t0  };
wire load_unit_s1_t0 = |{ex_stage_i.lsu_i.i_load_unit.\load_data_q.ld_pc_t0 ,ex_stage_i.lsu_i.i_load_unit.valid_o_t0  };
wire store_unit_s1_t0 = |{ex_stage_i.lsu_i.i_store_unit.state_q_t0 ,ex_stage_i.lsu_i.i_store_unit.st_pc_q_t0  };
wire store_unit_s3_t0 = |{ex_stage_i.lsu_i.i_store_unit.state_q_t0 ,ex_stage_i.lsu_i.i_store_unit.st_pc_q_t0  };
wire load_unit_buff_s1_t0 = |{ex_stage_i.lsu_i.load_valid_o_t0 ,ex_stage_i.lsu_i.load_pc_o_t0  };
wire csr_buffer_s1_t0 = |{ex_stage_i.csr_buffer_i.\csr_reg_q.valid_t0 ,ex_stage_i.csr_buffer_i.\csr_reg_q.pc_t0  };
wire mult_s1_t0 = |{ex_stage_i.i_mult.i_multiplier.pc_q_t0 ,ex_stage_i.i_mult.i_multiplier.mult_valid_q_t0  };
wire load_unit_op_s1_t0 = |{ex_stage_i.lsu_i.i_load_unit.valid_i_t0 ,ex_stage_i.lsu_i.i_load_unit.state_q_t0 ,ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc_t0  };
wire load_unit_op_s2_t0 = |{ex_stage_i.lsu_i.i_load_unit.valid_i_t0 ,ex_stage_i.lsu_i.i_load_unit.state_q_t0 ,ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc_t0  };
wire load_unit_op_s3_t0 = |{ex_stage_i.lsu_i.i_load_unit.valid_i_t0 ,ex_stage_i.lsu_i.i_load_unit.state_q_t0 ,ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc_t0  };
wire mem_req_s1_t0 = |{ex_stage_i.lsu_i.i_ord_sram.pc_i_t0 ,ex_stage_i.lsu_i.i_ord_sram.req_i_t0  };

// ================================================================================ 
// {I0_DEF}
// ================================================================================ 

NOT1: assume property (@(posedge clk_i) ~(|(fetch_valid_if_id_t0 )));
NOT2: assume property (@(posedge clk_i) ~(|(\fetch_entry_if_id.address_t0 )));
`ifdef T_FROM_I
// we consider IUV and I_T does no have input/output dependencies
//NO_IO_DEP_1: assume (@(posedge clk_i) 
//     
//);

//NO_IO_DEP_2: assume property (@(posedge clk_i)
//    !(|{issue_stage_i.i_scoreboard.rs3_o_t0,
//        issue_stage_i.i_scoreboard.rs2_o_t0, 
//        issue_stage_i.i_scoreboard.rs1_o_t0}));
`endif

//
`define OPERAND_TAINT
// so the operand_a/b_q is cutpoint



`ifdef T_FROM_I
wire [32-1:0] i1;
wire [64-1:0] pc1;
DIFF_PC: assume property (@(posedge clk_i) pc1 != pc0);
pc1_const: assume property (@(posedge clk_i) CONST(pc1));
pc1_nozero: assume property (@(posedge clk_i) pc1 != '0);

wire i1_instn_begin = (id_stage_i.fetch_entry_valid_i && 
                    id_stage_i.\fetch_entry_i.address == pc1);
ISSUE_ONCE_I1: assume property (@(posedge clk_i) i1_instn_begin |=> 
        always !(id_stage_i.\fetch_entry_i.address == pc1));

pc1_i0_assoc_1: assume property (@(posedge clk_i) 
    id_stage_i.\fetch_entry_i.address == pc1 |-> id_stage_i.instruction == i1);
pc1_i0_assoc_2: assume property (@(posedge clk_i) 
    id_stage_i.\fetch_entry_i.address == pc1 |-> 
    (id_stage_i.fetch_entry_valid_i == 1'b1 && 
    id_stage_i.\decoded_instruction.ex.valid == 1'b0) 
    // IF issuing a valid request, i.e. no exception raised so far at IF
);
i1_const: assume property (@(posedge clk_i) CONST(i1));

`include "src_ift/pl_def_i1.sv"
// I1 definition

// Issue HB
`ifndef YNG
reg i1_issued_before;
always @(posedge clk_i) begin
    if (!rst_ni) 
        i1_issued_before <= 1'b0;
    else if (i1_instn_begin)
        i1_issued_before <= 1'b1;
end 
I1_ISSUE_HB_I0: assume property (@(posedge clk_i) instn_begin |-> i1_issued_before);
`else
reg i0_issued_before;
always @(posedge clk_i) begin
    if (!rst_ni) 
        i0_issued_before <= 1'b0;
    else if (instn_begin)
        i0_issued_before <= 1'b1;
end 
I1_ISSUE_HB_I0: assume property (@(posedge clk_i) i1_instn_begin |-> i0_issued_before);
`endif

`endif

`ifdef T_FROM_IUV 
wire read_op_i = //(issue_stage_i.i_issue_read_operands.\issue_instr_i.pc == pc0);
                (issue_stage_i.i_issue_read_operands.pc_o == pc0);
`endif
`ifdef T_FROM_I

wire read_op_i = //(issue_stage_i.i_issue_read_operands.\issue_instr_i.pc == pc1);
                (issue_stage_i.i_issue_read_operands.pc_o == pc1);
`endif
`ifdef BORTHRS

I0_T0_BOTH: assume property (@(posedge clk_i) 
    read_op_i |-> 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[0]_t0 == {64{1'b1}} 
    ( issue_stage_i.i_issue_read_operands.operand_a_q_t0 == {64{1'b1}} 
     && issue_stage_i.i_issue_read_operands.operand_b_q_t0 == {64{1'b1}}
    )
    );
I0_T1_BOTH: assume property (@(posedge clk_i) 
    !read_op_i |-> 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[0]_t0 == {64{1'b0}} 
    (issue_stage_i.i_issue_read_operands.operand_a_q_t0 == {64{1'b0}} 
     && issue_stage_i.i_issue_read_operands.operand_b_q_t0 == {64{1'b0}}
     )
    );

`endif
`ifdef RS1
I0_T0: assume property (@(posedge clk_i) 
    read_op_i |-> 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[0]_t0 == {64{1'b1}} 
    issue_stage_i.i_issue_read_operands.operand_a_q_t0 == {64{1'b1}} 
    );
I0_T1: assume property (@(posedge clk_i) 
    !read_op_i |-> 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[0]_t0 == {64{1'b0}} 
    issue_stage_i.i_issue_read_operands.operand_a_q_t0 == {64{1'b0}} 
    );
I0_T2: assume property (@(posedge clk_i) 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[1]_t0 == {64{1'b0}} );
    issue_stage_i.i_issue_read_operands.operand_b_q_t0 == {64{1'b0}});

`endif

`ifdef RS2
I0_T0: assume property (@(posedge clk_i) 
    read_op_i |-> 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[1]_t0 == {64{1'b1}} 
    issue_stage_i.i_issue_read_operands.operand_b_q_t0 == {64{1'b1}} 
    );
I0_T1: assume property (@(posedge clk_i) 
    !read_op_i |-> 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[1]_t0 == {64{1'b0}} 
    issue_stage_i.i_issue_read_operands.operand_b_q_t0 == {64{1'b0}} 
    );
I0_T2: assume property (@(posedge clk_i) 
    //issue_stage_i.i_issue_read_operands.i_ariane_regfile.\rdata_o[0]_t0 == {64{1'b0}} );
    issue_stage_i.i_issue_read_operands.operand_a_q_t0 == {64{1'b0}});
`endif

IFR: assume property (@(posedge clk_i)  ~(|(id_stage_i.instruction_t0 )));
// taint for PLs


`ifdef DYNAMIC
// PER_I
//PRETRACE: cover property (@(posedge clk_i)
////                                          <decision_follower_set>
//     i1_instn_begin ##[0:$] instn_begin ##[0:$] issue_s32  ##[0:$] 
//    (i1_scb_3_s13 | i1_scb_2_s13 | i1_scb_1_s13 | i1_scb_0_s13)
//    );
////                                          <divergent decision node | decision_follower_set>
//OVERLAP: assume property (@(posedge clk_i)      issue_s32 |-> 
//    (i1_scb_3 | i1_scb_2 | i1_scb_1 | i1_scb_0 |
//    i1_id_stage_s1 | 
//    i1_issue_s1
//    )
//);
`endif


