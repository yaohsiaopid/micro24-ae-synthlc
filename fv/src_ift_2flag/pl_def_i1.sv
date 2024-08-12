wire i1_serdiv_unit_divide_s1 = 
	(ex_stage_i.i_mult.i_div.pc_q == pc1) && 
	(ex_stage_i.i_mult.i_div.state_q == 2'd1) && 
	 1'b1; 
wire i1_serdiv_unit_divide_s2 = 
	(ex_stage_i.i_mult.i_div.pc_q == pc1) && 
	(ex_stage_i.i_mult.i_div.state_q == 2'd2) && 
	 1'b1; 
wire i1_id_stage_s1 = 
	(id_stage_i.\issue_q.sbe.pc == pc1) && 
	(id_stage_i.\issue_q.valid == 1'd1) && 
	 1'b1; 
wire i1_issue_s1 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc1) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd1) && 
	 1'b1; 
wire i1_issue_s2 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc1) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire i1_issue_s8 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc1) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire i1_issue_s16 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc1) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire i1_issue_s32 = 
	(issue_stage_i.i_issue_read_operands.pc_o == pc1) && 
	(issue_stage_i.i_issue_read_operands.alu_valid_q == 1'd1) && 
	(issue_stage_i.i_issue_read_operands.lsu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.mult_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.fpu_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.csr_valid_q == 1'd0) && 
	(issue_stage_i.i_issue_read_operands.branch_valid_q == 1'd0) && 
	 1'b1; 
wire i1_lsq_enq_0_s1 = 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[0].pc == pc1) && 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[0].valid == 1'd1) && 
	 1'b1; 
wire i1_lsq_enq_1_s1 = 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[1].pc == pc1) && 
	(ex_stage_i.lsu_i.lsu_bypass_i.\mem_q[1].valid == 1'd1) && 
	 1'b1; 
wire i1_scb_0_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_0_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd1) && 
	 1'b1; 
wire i1_scb_0_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_0_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[0].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[0].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd0) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd0)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_1_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_1_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd1) && 
	 1'b1; 
wire i1_scb_1_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_1_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[1].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[1].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd1) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd1)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_2_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_2_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd1) && 
	 1'b1; 
wire i1_scb_2_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_2_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[2].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[2].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd2) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd2)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_3_s12 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_3_s13 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd1) && 
	 1'b1; 
wire i1_scb_3_s14 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd1) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire i1_scb_3_s8 = 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.pc == pc1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].issued == 1'd1) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.valid == 1'd0) && 
	(issue_stage_i.i_scoreboard.\mem_q[3].sbe.ex.valid == 1'd0) && 
	(((issue_stage_i.i_scoreboard.\mem_n[3].issued == 1'b0) && ((issue_stage_i.i_scoreboard.commit_ack_i[1] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[1] == 2'd3) || (issue_stage_i.i_scoreboard.commit_ack_i[0] == 1'b1 && issue_stage_i.i_scoreboard.\commit_pointer_q[0] == 2'd3)))  == 1'd0) && 
	 1'b1; 
wire i1_stb_com_0_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[0].pc == pc1) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[0].valid == 1'd1) && 
	 1'b1; 
wire i1_stb_com_1_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[1].pc == pc1) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\commit_queue_q[1].valid == 1'd1) && 
	 1'b1; 
wire i1_stb_spec_0_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[0].pc == pc1) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[0].valid == 1'd1) && 
	 1'b1; 
wire i1_stb_spec_1_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[1].pc == pc1) && 
	(ex_stage_i.lsu_i.i_store_unit.store_buffer_i.\speculative_queue_q[1].valid == 1'd1) && 
	 1'b1; 
wire i1_load_unit_s1 = 
	(ex_stage_i.lsu_i.i_load_unit.\load_data_q.ld_pc == pc1) && 
	(ex_stage_i.lsu_i.i_load_unit.valid_o == 1'd1) && 
	 1'b1; 
wire i1_store_unit_s1 = 
	(ex_stage_i.lsu_i.i_store_unit.st_pc_q == pc1) && 
	(ex_stage_i.lsu_i.i_store_unit.state_q == 2'd1) && 
	 1'b1; 
wire i1_store_unit_s3 = 
	(ex_stage_i.lsu_i.i_store_unit.st_pc_q == pc1) && 
	(ex_stage_i.lsu_i.i_store_unit.state_q == 2'd3) && 
	 1'b1; 
wire i1_load_unit_buff_s1 = 
	(ex_stage_i.lsu_i.load_pc_o == pc1) && 
	(ex_stage_i.lsu_i.load_valid_o == 1'd1) && 
	 1'b1; 
wire i1_csr_buffer_s1 = 
	(ex_stage_i.csr_buffer_i.\csr_reg_q.pc == pc1) && 
	(ex_stage_i.csr_buffer_i.\csr_reg_q.valid == 1'd1) && 
	 1'b1; 
wire i1_mult_s1 = 
	(ex_stage_i.i_mult.i_multiplier.pc_q == pc1) && 
	(ex_stage_i.i_mult.i_multiplier.mult_valid_q == 1'd1) && 
	 1'b1; 

wire i1_load_unit_op_s1 = 
	(ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc == pc1) && 
    (ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) &&
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd1) && 
	 1'b1; 
wire i1_load_unit_op_s2 = 
	(ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc == pc1) && 
    (ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) &&
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd2) && 
	 1'b1; 
wire i1_load_unit_op_s3 = 
	(ex_stage_i.lsu_i.i_load_unit.\lsu_ctrl_i.pc == pc1) && 
    (ex_stage_i.lsu_i.i_load_unit.valid_i == 1'd1) &&
	(ex_stage_i.lsu_i.i_load_unit.state_q == 4'd3) && 
	 1'b1; 
wire i1_mem_req_s1 = 
    (ex_stage_i.lsu_i.i_ord_sram.pc_i == pc1) && 
    (ex_stage_i.lsu_i.i_ord_sram.req_i == 1'b1) &&
    1'b1;
wire i1_in_some_pl = |{
i1_serdiv_unit_divide_s1
, i1_serdiv_unit_divide_s2
, i1_id_stage_s1
, i1_issue_s1
, i1_issue_s2
, i1_issue_s8
, i1_issue_s16
, i1_issue_s32
, i1_lsq_enq_0_s1
, i1_lsq_enq_1_s1
, i1_scb_0_s12
, i1_scb_0_s13
, i1_scb_0_s14
, i1_scb_0_s8
, i1_scb_1_s12
, i1_scb_1_s13
, i1_scb_1_s14
, i1_scb_1_s8
, i1_scb_2_s12
, i1_scb_2_s13
, i1_scb_2_s14
, i1_scb_2_s8
, i1_scb_3_s12
, i1_scb_3_s13
, i1_scb_3_s14
, i1_scb_3_s8
, i1_stb_com_0_s1
, i1_stb_com_1_s1
, i1_stb_spec_0_s1
, i1_stb_spec_1_s1
, i1_load_unit_s1
, i1_store_unit_s1
, i1_store_unit_s3
, i1_load_unit_buff_s1
, i1_csr_buffer_s1
, i1_mult_s1
, i1_load_unit_op_s1
, i1_load_unit_op_s2
, i1_load_unit_op_s3
, i1_mem_req_s1
};
