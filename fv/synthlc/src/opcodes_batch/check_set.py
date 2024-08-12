import os
import subprocess

BATCH_INSTNDIR="./opcodes_batch"
group_items = []
if not os.path.exists("%s/group_map.txt" % BATCH_INSTNDIR):
    sys.exit("error: can't find group_map.txt")
with open("%s/group_map.txt" % BATCH_INSTNDIR, "r") as f:
    for line in f:
        arr = line[:-1].split("|")
        assert(len(arr) == 3)
        group_items.append(arr)

RUNDIR_PER_I="/cafe/u/yaohsiao/Document/cva6_fv_asplos/fv/tsynth/i_{I}_{TAG}"
RUNDIR_PER_I_10instn="/cafe/u/yaohsiao/Document/cva6_tsynth_fv_10instn/fv/tsynth/i_{I}_{TAG}"

batch_group = []

for agroup in group_items:
    fail = False
    group_id, field, t_instns = agroup
    print("Group ", group_id, t_instns)
    t_instns = t_instns.split(",")

    tocompare = None 
    tocompare_lines = []
    #if (not "ADD" in t_instns) and (not "ADDI" in t_instns):
    #    continue
    match_cnt = None
    subgroups = []
    curgroup = []
    for instn in sorted(t_instns):
        print("==>", instn)
        curtag="v2_11_III"
        #ffname = (RUNDIR_PER_I+"/xPOPLSetsTmp/follower_set.txt").format(I=instn, TAG=curtag)
        ffname = (RUNDIR_PER_I+"/xPOPLSetsTmp_V2/follower_set_v2.txt").format(I=instn, TAG=curtag)
        if not os.path.exists(ffname):
            #ffname = (RUNDIR_PER_I_10instn+"/xPOPLSetsTmp/follower_set.txt").format(I=instn, TAG=curtag)
            ffname = (RUNDIR_PER_I_10instn+"/xSummarizeTmp_V2/follower_set_v2.txt").format(I=instn, TAG=curtag)
        if not os.path.exists(ffname):
            fail = True
            break
        if tocompare is None:
            match_cnt = 1
            curgroup = [instn]
            tocompare = ffname
            with open(tocompare, "r") as tocompare_t:
                for line in tocompare_t:
                    tocompare_lines.append(line)
            continue
        else:

            #result = subprocess.run(['diff', tocompare, ffname], stdout=subprocess.PIPE)
            #print(result.stdout.decode('utf-8'))

            curf_t = open(ffname, "r")
            with open(ffname, "r") as cur_t:
                cnt = 0
                tocompare_lines_potential = []
                for line in cur_t:
                    tocompare_lines_potential.append(line)
                    if cnt < len(tocompare_lines) and line == tocompare_lines[cnt]:
                        cnt += 1
                        continue
                    if not fail and "," in line:
                        line = sorted(line[:-1].split(","))
                        if cnt < len(tocompare_lines) and line != sorted(tocompare_lines[cnt][:-1].split(",")):
                            print("fail: ", line, tocompare_lines[cnt])
                            fail = True
                            #break
                    if not fail:
                        cnt += 1

                if cnt != len(tocompare_lines):
                    print("..??", ffname, tocompare, match_cnt)
                    fail = True
                    if match_cnt > 1:
                        tocompare_lines = tocompare_lines_potential
                        tocompare = ffname
                        print("-> curgroup ", curgroup)
                        print(instn, tocompare)
                        subgroups.append(curgroup)
                        curgroup = [instn]
                        match_cnt = 1
                        fail = False
                    else:
                        break
                else:
                    curgroup.append(instn)
                    match_cnt += 1
                    #print("--> ", ffname)
        if fail:
            break

    if not fail:
        print("!!! group: ", t_instns)
        batch_group.append(group_id)
with open("opcodes_batch/batch_transponder_2.txt", "w") as f:
    for itm in batch_group:
        f.write("%s\n" % itm)
