
import sys

in_path = sys.argv[1]

sankey_lines = []

sankey_type = '.ni_rejected.'

with open(in_path, 'r') as inf:
    for line in inf:
        if sankey_type in line:
            sankey_lines.append(line)

        if 'average_packet_latency' in line:
            print(f'# avg pkt lat = {line.split(" ")[1]}')

sankey_dict = {}

for sl in sankey_lines:
    ivc = -1
    ovc = -1
    description = sl.split(' ')[0]
    ivc_str = description.split('.')[-2]
    ivc_str = ivc_str.replace('s','')
    ivc = int(ivc_str)
    ovc_str = description.split('.')[-1]
    ovc_str = ovc_str.replace('d','')
    ovc=int(ovc_str)

    for e in sl.split(" ")[1:]:
        try:
            val = int(e)
            break
        except:
            pass

    try:
        sankey_dict[ivc].update({ovc:val})
    except:
        sankey_dict.update({ivc : {ovc : val}})

# totvcs = 4
# ns = totvcs*3



# mysum = 0
# for i in range(totvcs):
#     for j in range(ns):
#         mysum += sankey_dict[i][j]


# print(f'ilow [{mysum}] olow')

# mysum = 0
# for i in range(2*totvcs,3*totvcs):
#     for j in range(ns):
#         mysum += sankey_dict[i][j]

# print(f'ihigh [{mysum}] ohigh')
ns=20

mysum = 0
for i in range(ns):
    for j in range(ns):
        mysum += sankey_dict[i][j]


print(f'// total rejects {mysum}')

for i in range(ns):
    for j in range(ns):
        if sankey_dict[i][j] > 0:
            print(f'ni_s{i} [{sankey_dict[i][j]}] ni_d{j}')


print(f'//{in_path}')

sankey_lines = []

sankey_type = '.r_rejected.'

with open(in_path, 'r') as inf:
    for line in inf:
        if sankey_type in line:
            sankey_lines.append(line)

        split_line = [x for x in line.split(" ") if x!='']

        if 'average_packet_latency' in line:
            print(f'// avg pkt lat = {line.split(" ")[1]}')

        if 'packets_injected::total' in line:
            print(f'// pkts injected = {split_line[1]}')
        if 'packets_received::total' in line:
            print(f'// pkts received = {split_line[1]}')

sankey_dict = {}

for sl in sankey_lines:
    ivc = -1
    ovc = -1
    description = sl.split(' ')[0]
    ivc_str = description.split('.')[-2]
    ivc_str = ivc_str.replace('s','')
    ivc = int(ivc_str)
    ovc_str = description.split('.')[-1]
    ovc_str = ovc_str.replace('d','')
    ovc=int(ovc_str)

    for e in sl.split(" ")[1:]:
        try:
            val = int(e)
            break
        except:
            pass

    try:
        sankey_dict[ivc].update({ovc:val})
    except:
        sankey_dict.update({ivc : {ovc : val}})

# totvcs = 4
# ns = totvcs*3



mysum = 0
for i in range(ns):
    for j in range(ns):
        mysum += sankey_dict[i][j]


print(f'// total rejects {mysum}')

# mysum = 0
# for i in range(2*totvcs,3*totvcs):
#     for j in range(ns):
#         mysum += sankey_dict[i][j]

# print(f'ihigh [{mysum}] ohigh')

ns=20
for i in range(ns):
    for j in range(ns):
        if sankey_dict[i][j] > 0:
            # print(f'r_s{i} [{sankey_dict[i][j]}] r_d{j}')
            print(f'r_d{j} [{sankey_dict[i][j]}] r_s{i}')