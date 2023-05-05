
import sys

in_path = sys.argv[1]

ipc_lines = []
n_insts_lines = []

with open(in_path, 'r') as inf:
    for line in inf:
        if '.ipc' in line:
            ipc_lines.append(line)
        if '.switch_cpus' in line and 'numInsts' in line:
            n_insts_lines.append(line)

ipc_dict = {}

n_nans = 0

for sl in ipc_lines:

    description = sl.split(' ')[0]
    ivc_str = description.split('.')[-2]
    ivc_str = ivc_str.replace('switch_cpus','')
    
    # ivc_str = ivc_str.replace('cpu','')
    ivc = int(ivc_str)

    for e in sl.split(" ")[1:]:
        try:
            val = float(e)
            break
        except:
            pass

    if 'nan' in sl:
        ipc_dict.update({ivc:0})
        continue
    else:
        ipc_dict.update({ivc:val})

n_insts_dict = {}


for sl in n_insts_lines:

    description = sl.split(' ')[0]
    ivc_str = description.split('.')[1]
    ivc_str = ivc_str.replace('switch_cpus','')
    
    # ivc_str = ivc_str.replace('cpu','')
    ivc = int(ivc_str)

    for e in sl.split(" ")[1:]:
        try:
            val = int(e)
            break
        except:
            pass

    if 'nan' in sl:
        n_insts_dict.update({ivc:0})
        continue
    else:
        n_insts_dict.update({ivc:val})

for i in range(64):
    try:
        if ipc_dict[i] > 0:
            print(f'ivn{i} [{ipc_dict[i]}] / {n_insts_dict[i]}')
    except:
        pass