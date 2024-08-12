
sanity_template = '''
INSTN_CONSTRAINT

// decision
DECSANITY: cover property (@(posedge clk_i) 
    DECNODE ##1 
    // follower set
    (
      FOLLOWERSET
    )
);
'''

dynamic_template_header = '''
`define T_FROM_I
`define DYNAMIC
OP_TAINT

OVERLAP: assume property (@(posedge clk_i) 
    DECNODE |-> 
    (i1_in_some_pl)
);
'''
itself_template_prop = '''
`define T_FROM_IUV
OP_TAINT
INSTN_CONSTRAINT

// decision
DEP_FIELD: cover property (@(posedge clk_i)
    DECNODE ##1 
    // follower set
    (
        (
          FOLLOWERSET
        ) && 
        (TT0
        )
    )

    
);
'''
itself_template = '''
`define T_FROM_IUV
OP_TAINT
INSTN_CONSTRAINT

// decision
DECSANITY: cover property (@(posedge clk_i) 
    DECNODE ##1 
    // follower set
    (
      FOLLOWERSET
    )
);

DEP_FIELD: cover property (@(posedge clk_i)
    DECNODE ##1 
    // follower set
    (
        (
          FOLLOWERSET
        ) && 
        (TT0
        )
    )

    
);
'''
dynamic_template_header = '''
`define T_FROM_I
`define DYNAMIC
OP_TAINT

OVERLAP: assume property (@(posedge clk_i) 
    DECNODE |-> 
    (i1_in_some_pl)
);
'''

decision_template = '''
DEP_I_FIELD: cover property (@(posedge clk_i)
    (INSTN_CONSTRAINT &&
    I1_CONSTRAINT &&
    DECNODE) ##1 
    // follower set
    (
        (
          FOLLOWERSET
        ) && 
        (TT0
        )
    )
);
'''

dynamic_template = '''
`define T_FROM_I
`define DYNAMIC
OP_TAINT
INSTN_CONSTRAINT

I1_CONSTRAINT


OVERLAP: assume property (@(posedge clk_i) 
    DECNODE |-> 
    (i1_in_some_pl)
);

DEP_I_FIELD: cover property (@(posedge clk_i)
    DECNODE ##1 
    // follower set
    (
        (
          FOLLOWERSET
        ) && 
        (TT0
        )
    )

    
);
'''
static_template = '''
`define T_FROM_I
`define STATIC
OP_TAINT
INSTN_CONSTRAINT

I1_CONSTRAINT

DEP_I_FIELD: cover property (@(posedge clk_i)
    DECNODE ##1 
    // follower set
    (
        (
          FOLLOWERSET
        ) && 
        (TT0
        )
    )

    
);
'''
