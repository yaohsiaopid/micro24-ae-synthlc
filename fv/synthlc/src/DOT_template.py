dot_header = '''
digraph G {
    edge [penwidth=2];
    node [ shape=box, fontsize=20, penwidth=2, fontname="roboto"];
    esep=0.5;
    layout=neato;
    overlap=scale;
    splines=true;
'''
label = '''
l_{nm} [label=\"{nm}\"; pos=\"0,-{loc}!\"; shape=none];
'''
uhb_node = '''
n_{nm} [label=\"\"; pos=\"2,-{loc}!\"; shape=circle ]; \n
'''
uhb_node_color = '''
n_{nm} [style=filled, color=black, fillcolor="{color}", label=\"\"; pos=\"2,-{loc}!\"; shape=circle ]; \n
'''
uhb_edge_label = '''
n_{u} -> n_{v} [color="{color}", label="{e_s}"];
'''
uhb_edge = '''
n_{u} -> n_{v} [color="{color}"];
'''
color_names = [
"#000000",
"#4B0082",
"#006400",
"#DA70D6",
"#6495ED",
"#2F4F4F",
"#F0E68C",
"#CD853F",
"#A52A2A",
"#00008B",
"#FFA500"
]
footer = '''

'''

list_rows = [
    "id_stage_s1",
    "issue_s1",
    "issue_s2",
    "issue_s8",
    "issue_s16",
    "issue_s32",
    "lsq_enq_0_s1",
    "lsq_enq_1_s1",
    "serdiv_unit_divide_s1",
    "serdiv_unit_divide_s2",
    "stb_spec_0_s1",
    "stb_spec_1_s1",
    "load_unit_s1",
    "store_unit_s1",
    "store_unit_s3",
    "load_unit_buff_s1",
    "csr_buffer_s1",
    "mult_s1",
    "load_unit_op_s1",
    "load_unit_op_s2",
    "load_unit_op_s3",
    "scb_0_s12",
    "scb_0_s13",
    "scb_0_s14",
    "scb_0_s8",
    "scb_1_s12",
    "scb_1_s13",
    "scb_1_s14",
    "scb_1_s8",
    "scb_2_s12",
    "scb_2_s13",
    "scb_2_s14",
    "scb_2_s8",
    "scb_3_s12",
    "scb_3_s13",
    "scb_3_s14",
    "scb_3_s8",
    "stb_com_0_s1",
    "stb_com_1_s1",
    "mem_req_s1",
]
