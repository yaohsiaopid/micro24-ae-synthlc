import os
import subprocess
#subprocess.call("lscpu", shell=True)
import pandas as pd
import matplotlib.pyplot as plt

def plot_table(ret_arr, i_p_id, instn):
    ret_arr = [str(itm) for itm in ret_arr]
    rows = []
    rows.append(["", "", ""])
    for itm in ["Branch", "DIV*", "JALR", "Load", "REM*", "Store"]:
        for lb in ["N", "D"]:
            for op in ["rs1", "rs2"]: 
                rows.append([itm, lb, op])
     

    tablef = "table_6_{gid}.txt".format(gid=instn) #i_p_id)
    if os.path.exists(tablef):
        with open(tablef, "r") as f:
            idx = 0
            for line in f:
                rows[idx] += line[:-1].split(",")
                idx += 1
    idx = 0
    for itm in ret_arr:            
        rows[idx].append(itm)
        idx += 1
    with open(tablef, "w") as f:
        for itm in rows:
            f.write(",".join(itm[3:]) + "\n")

    fig, ax = plt.subplots()

    # Hide axes
    ax.axis('tight')
    ax.axis('off')
    #print(rows)
    # Create the table and add it to the figure
    table = ax.table(cellText=rows, cellLoc='center', loc='center')
    #colWidths = [0.12, 0.01, 0.02, 0.01])
    table.auto_set_column_width(list(range(len(rows[0]))))
    # Adjust table properties if needed
    #table.scale(1, 1.5)  # Adjust scale for better fit

    # iterate through cells of a table
    for i in range(len(rows)):
        for j in range(len(rows[i])):
            cell = table[i, j]
            if cell.get_text().get_text() == "0":
                cell.get_text().set_color("white")
                cell.set_facecolor("white")
            elif cell.get_text().get_text() == "1":
                cell.get_text().set_color("black")
                cell.set_facecolor("black")
    # Save the table as an image file (optional)
    plt.savefig("table_6_%s.png" % instn, dpi=300, bbox_inches='tight')
#
#        tablef = "table_6_{gid}.txt".format(gid=i_p_id)
#        if not os.path.exists(tablef):
#            with open(tablef, "w") as f:
#                f.write(16 * " " + "\n")
#                for itm in ["Branch", "DIV*", "JALR", "Load", "REM*", "Store"]:
#                    for lb in ["N", "D"]:
#                        for op in ["rs1", "rs2"]: 
#                            f.write(itm.rjust(10," ") + " " + lb + " " + op + "\n")
#        new_f = open(tablef + ".tmp", "w")
#        idx = 0
#        with open(tablef, "r") as f:
#            for line in f:
#                new_f.write(line[1:-1] + " " + str(ret_arr[idx]).ljust(2, " ") + "\n")
#                idx += 1
#        new_f.close()
#        os.system("mv " + tablef +".tmp" + " " + tablef)
