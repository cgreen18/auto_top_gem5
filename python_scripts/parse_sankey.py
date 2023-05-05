
import sys

in_path = sys.argv[1]

sankey_lines = []

with open(in_path, 'r') as inf:
    for line in inf:
        if '.sankey.' in line:
            sankey_lines.append(line)

sankey_dict = {}

for sl in sankey_lines:
    ivc = -1
    ovc = -1
    description = sl.split(' ')[0]
    ivc_str = description.split('.')[-2]
    ivc_str = ivc_str.replace('vcvn','')
    ivc = int(ivc_str)
    ovc_str = description.split('.')[-1]
    ovc_str = ovc_str.replace('vcvn','')
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

totvcs = 9
ns = totvcs*3

for i in range(ns):
    for j in range(ns):
        if sankey_dict[i][j] > 0:
            print(f'ivn{i} [{sankey_dict[i][j]}] ovn{j}')