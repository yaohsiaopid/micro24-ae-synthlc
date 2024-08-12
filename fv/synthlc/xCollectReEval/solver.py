from cvc5.pythonic import *
import networkx as nx
from itertools import chain, combinations
import textwrap
import pandas as pd
import numpy as np
import os
import pandas as pd
import sys
class MySolver:
    def __init__(self,
        TR,
        edge_weight,
        implied_edges_same_iid,
        iid_map_tmp,
        edge_weight_single, 
        enter_concurrent_pairs, 
        whb_edge
        ):
        
        self.TR = TR
        self.edge_weight = edge_weight
        self.implied_edges_same_iid = implied_edges_same_iid
        self.iid_map_tmp = iid_map_tmp
        self.edge_weight_single = edge_weight_single
        self.enter_concurrent_pairs = enter_concurrent_pairs
        self.whb_edge = whb_edge
        self.solver = SolverFor('QF_LIRA')
        self.variables = {}
        self.tempvars = 0

    def push(self):
        self.solver.push()
    def pop(self):
        self.solver.pop()

    def add_at_same_time(self, e):
        self.solver += (self.variables[e[0]] != self.variables[e[1]])

    def add_hb(self, e):
        self.solver += (self.variables[e[0]] >= self.variables[e[1]])

    def test_unsat(self):
        r = (self.solver.check() == unsat)
        if r:
            return True
        else:
            return False

    def add_e_cyc(self, e, cyc):
        self.solver += (self.variables[e[0]] + cyc == self.variables[e[1]])

    def test_added_es(self):
        r = (self.solver.check() == sat)
        if r:
            return True
        else:
            return False

    def test_e_cyc(self, e, c):
        self.solver.push()
        self.solver += (self.variables[e[0]] + c == self.variables[e[1]])
        r = (self.solver.check() == sat)
        self.solver.pop()
        if r:
            return True
        else:
            return False

    def test_e_1cyc(self, e):
        self.solver.push()
        self.solver += (self.variables[e[0]] + 1 != self.variables[e[1]])
        r = (self.solver.check() == unsat)
        self.solver.pop()
        if r:
            return True
        else:
            return False
    def check_hb_possibility(self, e):
        self.push()
        self.solver += (self.variables[e[0]] < self.variables[e[1]])
        can_hb = True 
        if self.test_unsat():
            can_hb = False      
        self.pop()
        return can_hb
         
    def check_imp_hb(self, e):
        self.push()
        # opposite of hb
        self.add_hb(e)
        aws_hb = False
        if self.test_unsat():
            aws_hb = True
        self.pop()
        return aws_hb

    def add_constraints(self):
        for n in self.TR.nodes():
            self.variables[n] = Int('%s' % n)
            
        reduce_e = list(self.TR.edges)
        for e in reduce_e:
            if e in self.edge_weight:
                new_t = Int('t%d' % self.tempvars)
                self.tempvars += 1
                cyc_e = self.edge_weight[e]
                tmpcnstrnt = []
                for r in cyc_e:
                    tmpcnstrnt.append(new_t == r)
                if len(tmpcnstrnt) > 1:
                    self.solver += Or(*tmpcnstrnt)
                elif len(tmpcnstrnt) == 1:
                    self.solver += tmpcnstrnt[0]
                else:
                    assert(0)
                self.solver += (self.variables[e[0]] + new_t == self.variables[e[1]])
                #print("add %s + new_t == %s " % e)
                #print(new_t)

            elif e in self.implied_edges_same_iid:
                self.solver += (self.variables[e[0]] + 1 ==
                        self.variables[e[1]])
                #print("add %s + 1 == %s " % e)

            elif self.iid_map_tmp[e[0]] == self.iid_map_tmp[e[1]]:
                self.solver += (self.variables[e[0]] + 1 ==
                        self.variables[e[1]])
                #print("add %s + 1 == %s " % e)
            elif e in self.edge_weight_single:
                self.solver += (self.variables[e[0]] + 1 ==
                        self.variables[e[1]])
                #print("add %s + 1 == %s " % e)
            else:
                self.solver += (self.variables[e[0]] < self.variables[e[1]])
                pass
                #print("skip %s %s" % e)

        for e in self.whb_edge:
            if e[0] in self.TR.nodes() and e[1] in self.TR.nodes():
                self.solver += (self.variables[e[0]] <= self.variables[e[1]])
        
        nodes = list(self.TR.nodes)
        for itm in self.enter_concurrent_pairs:
            a, b = itm 
            if a in nodes and b in nodes:
                self.solver += (self.variables[a] == self.variables[b])

        self.solver.push()
        r = self.solver.check()
        #print(r)
        # pythonic sat
        assert(r == sat)

