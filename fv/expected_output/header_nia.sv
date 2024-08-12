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
  i_frontend.fetch_entry_o.ex.valid == 1'b0
  // tag this fetched instruction is not exceptioned already at front-end
  // (e.g., INSTR_PAGE_FAULT or INSTR_ACCESS_FAULT)
);
IF_ID_CONTRACT: assume property (@(posedge clk_i)
  // yet ack then hold
  (id_stage_i.fetch_entry_valid_i && !(fetch_ready_id_if)) |=>
  (
  ($past(id_stage_i.fetch_entry_valid_i) == id_stage_i.fetch_entry_valid_i) &&
  ($past(id_stage_i.instruction) == id_stage_i.instruction) &&
  ($past(id_stage_i.fetch_entry_i.address) == id_stage_i.fetch_entry_i.address)
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
                    id_stage_i.fetch_entry_i.address == pc0);

pc0_i0_assoc_1: assume property (@(posedge clk_i) 
    id_stage_i.fetch_entry_i.address == pc0 |-> id_stage_i.instruction == i0);
pc0_i0_assoc_2: assume property (@(posedge clk_i) 
    id_stage_i.fetch_entry_i.address == pc0 |-> 
    (id_stage_i.fetch_entry_valid_i == 1'b1 && 
`ifndef SYSINSN
    id_stage_i.decoded_instruction.ex.valid == 1'b0) 
`else
    id_stage_i.fetch_entry_i.ex.valid == 1'b0)
`endif
    // IF issuing a valid request, i.e. no exception raised so far at IF
);


NO_INSTN_INTERFERENCE_1: assume property (@(posedge clk_i) first |-> 
        instn_begin);
NO_INSTN_INTERFERENCE_2: assume property (@(posedge clk_i) first |=> 
    always !(id_stage_i.fetch_entry_valid_i));

ISSUE_ONCE: assume property (@(posedge clk_i) instn_begin |=> 
        always !(id_stage_i.fetch_entry_i.address == pc0));

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
	(id_stage_i.issue_q.sbe.pc == pc0) && 
	(id_stage_i.issue_q.valid == 1'd1) && 
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
	(ex_stage_i.lsu_i.lsu_bypass_i.mem_q[0].pc == pc0) && 
	(ex_stage_i.lsu_i.lsu_bypass_i.mem_q[0].valid == 1'd1) && 
	 1'b1; 
wire lsq_enq_1_s1 = 
	(ex_stage_i.lsu_i.lsu_bypass_i.mem_q[1].pc == pc0) && 
	(ex_stage_i.lsu_i.lsu_bypass_i.mem_q[1].valid == 1'd1) && 
	 1'b1; 
wire scb_0_s12 = 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire scb_0_s13 = 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd0)))  == 1'd1) && 
	 1'b1; 
wire scb_0_s14 = 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire scb_0_s8 = 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire scb_1_s12 = 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire scb_1_s13 = 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd1)))  == 1'd1) && 
	 1'b1; 
wire scb_1_s14 = 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire scb_1_s8 = 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire scb_2_s12 = 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire scb_2_s13 = 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd2)))  == 1'd1) && 
	 1'b1; 
wire scb_2_s14 = 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire scb_2_s8 = 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire scb_3_s12 = 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire scb_3_s13 = 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd3)))  == 1'd1) && 
	 1'b1; 
wire scb_3_s14 = 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire scb_3_s8 = 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.pc == pc0) && 
	(issue_stage_i.i_scoreboard.mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire stb_com_0_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.commit_queue_q[0].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.commit_queue_q[0].valid == 1'd1) && 
	 1'b1; 
wire stb_com_1_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.commit_queue_q[1].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.commit_queue_q[1].valid == 1'd1) && 
	 1'b1; 
wire stb_spec_0_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.speculative_queue_q[0].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.speculative_queue_q[0].valid == 1'd1) && 
	 1'b1; 
wire stb_spec_1_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.speculative_queue_q[1].pc == pc0) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.speculative_queue_q[1].valid == 1'd1) && 
	 1'b1; 
wire load_unit_s1 = 
	(ex_stage_i.lsu_i.i_load_unit.load_data_q.ld_pc == pc0) && 
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
	(ex_stage_i.csr_buffer_i.csr_reg_q.pc == pc0) && 
	(ex_stage_i.csr_buffer_i.csr_reg_q.valid == 1'd1) && 
	 1'b1; 
wire mult_s1 = 
	(ex_stage_i.i_mult.i_multiplier.pc_q == pc0) && 
	(ex_stage_i.i_mult.i_multiplier.mult_valid_q == 1'd1) && 
	 1'b1; 
wire load_unit_op_s1 = 
	(ex_stage_i.lsu_i.i_load_unit.lsu_ctrl_i.pc == pc0) && 
	(ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) && 
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd1) && 
	 1'b1; 
wire load_unit_op_s2 = 
	(ex_stage_i.lsu_i.i_load_unit.lsu_ctrl_i.pc == pc0) && 
	(ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) && 
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd2) && 
	 1'b1; 
wire load_unit_op_s3 = 
	(ex_stage_i.lsu_i.i_load_unit.lsu_ctrl_i.pc == pc0) && 
	(ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) && 
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd3) && 
	 1'b1; 
wire mem_req_s1 = 
	(ex_stage_i.lsu_i.i_ord_sram.pc_i == pc0) && 
	(ex_stage_i.lsu_i.i_ord_sram.req_i == 1'd1) && 
	 1'b1; 
