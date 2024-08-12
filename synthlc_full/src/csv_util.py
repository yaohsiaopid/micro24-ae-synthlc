import numpy as np
import pandas as pd
import os
import re
#########

mydtypes = { "Task": 'str', "Name": 'str', "Result": 'str', "Engine": 'str',
"Bound": 'str', "Time": 'str', "Note": 'str'}
################################################################################
# df: DataFrame, from pd.read_csv("...")
# prop: property name
################################################################################
def df_query(df, prop, cover_prop=True, exact_name=False):
    if cover_prop:
        if not ":" in prop and (not exact_name):
        #if not ":" in prop:
            prop = "." + prop
        tar_row = df[df['Name'].str.endswith(prop)]
        if (len(tar_row) != 1):
            tar_row = df[df['Name'].str.contains(prop)]
        if (len(tar_row) != 1):
            print("tar row is size ", len(tar_row), "??", prop)
            assert(0)
        res = tar_row['Result'].values[0] 
        bnd = tar_row['Bound'].values[0]
        sr = re.search("([0-9]+)", bnd)
        if sr is not None:
            bnd = int(sr.group(1))
        else:
            bnd = None
        time = float(tar_row['Time'].values[0][:-2])
        return (res, bnd, time)
    return (None, None, None)

class MyStat:
    def __init__(self):
        self.comps = []
        self.incomps = []
    def add(self, res: str, bnd: int, time: float):
        if res in ["covered", "unreachable", "cex", "proven"]:
            self.comps.append(time)
        else:
            self.incomps.append((time, bnd))
    def output(self, ff):
        with open(ff, "w") as f:
            f.write("%d,%f\n" % (len(self.comps), sum(self.comps)))
            for itm in self.comps:
                f.write("%f," % itm)
            f.write("\n")
            t = sum([r[0] for r in self.incomps])
            f.write("%d,%f\n" % (len(self.incomps), t))
            for itm in self.incomps:
                f.write("%f," % itm[0])
            f.write("\n")
            for itm in self.incomps:
                f.write("%d," % itm[1])
            f.write("\n")
