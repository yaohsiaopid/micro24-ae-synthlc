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
