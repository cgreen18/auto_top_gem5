
import sys
import os
data_dir = sys.argv[1]


ipc_lines = []
n_insts_lines = []


for root, dirs, files, in os.walk(data_dir):

    if 'stats.txt' in files:
        in_path = os.path.join(root, 'stats.txt')


        topo = root.split('/')[-1]
        bench = root.split('/')[-2]

        util = 0

        with open(in_path, 'r') as inf:
            for line in inf:
                if 'avg_link_utilization' in line:
                    ipc_lines.append(line)

                    l_split = line.split(' ')
                    for l in l_split:
                        try:
                            util = float(l)
                        except:
                            pass

        print(f'{bench} : {topo} : {util}')
