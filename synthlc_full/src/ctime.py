import pandas as pd
import sys
sys.path.append("./src")
from csv_util import *
df = pd.read_csv(sys.argv[1], dtype=mydtypes)
time = 0
for itm in df['Time'].values:
    time += float(itm[:-2])
print(time/60, "min = ", time/3600, "hours")
