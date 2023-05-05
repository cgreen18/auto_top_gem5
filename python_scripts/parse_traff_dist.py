
import sys
import os

# in_path = sys.argv[1]


data_dir = str(sys.argv[1])

all_data_traff = {}
all_ctrl_traff = {}

for root, dirs, files, in os.walk(data_dir):

    if 'stats.txt' in files and 'kite_medium' in root :#sand 'blackscholes' in root:
        in_path = os.path.join(root, 'stats.txt')

        print(f'ingesting {in_path}')


        data_traff = []
        ctrl_traff = []

        with open(in_path, 'r') as inf:
            for line in inf:
                if 'ctrl_traffic_distribution.' in line:
                    ctrl_traff.append(line)
                if 'data_traffic_distribution.' in line:
                    data_traff.append(line)

        all_data_traff.update({in_path:data_traff})
        all_ctrl_traff.update({in_path:ctrl_traff})

# print(f'data_traff={all_data_traff}')


for key, value in all_data_traff.items():

    data_traff_dict = {}

    print(f'processing data {key}')


    for sl in value:
        description = sl.split(' ')[0]
        # print(f'{sl.split(" ")}')
        ivc_str = description.split('.')[-2]
        ivc_str = ivc_str.replace('n','')
        ivc = int(ivc_str)
        ovc_str = description.split('.')[-1]
        ovc_str = ovc_str.replace('n','')
        ovc=int(ovc_str)

        # print(f'{description.split(".")}')
        # quit()

        val = -1
        for e in sl.split(" ")[1:]:
            try:
                val = int(e)
                break
            except:
                pass

        try:
            data_traff_dict[ivc].update({ovc:val})
        except:
            data_traff_dict.update({ivc : {ovc : val}})

        # print(f'ivc={ivc}, ovc={ovc}, val={val}')
        # quit()

    all_data_traff[key] = data_traff_dict

for key, value in all_ctrl_traff.items():
    ctrl_traff_dict = {}

    # print(f'processing ctrl {key} : value {value}')
    # quit()

    for sl in value:
        description = sl.split(' ')[0]
        ivc_str = description.split('.')[-2]
        ivc_str = ivc_str.replace('n','')
        ivc = int(ivc_str)
        ovc_str = description.split('.')[-1]
        ovc_str = ovc_str.replace('n','')
        ovc=int(ovc_str)

        val = -1
        for e in sl.split(" ")[1:]:
            try:
                val = int(e)
                break
            except:
                pass

        try:
            ctrl_traff_dict[ivc].update({ovc:val})
        except:
            ctrl_traff_dict.update({ivc : {ovc : val}})

    # print(f'{ivc}->{ovc} : {val}')

    #print(f'data_={data_traff_dict}')
    all_ctrl_traff[key] = ctrl_traff_dict


print('\n')

for path, data_traff_dict in all_data_traff.items():
    n = 0
    inj_tot = 0
    for i in range(84):

        for j in range(84):
            try:
                val = data_traff_dict[i][j]
            except:
                continue
            # print(f'val={val}')
            # print(f'dtd={data_traff_dict}')
            if val > 0:
                # print(f's_data_n{i} [{val}] d_data_n{j}')
                inj_tot += val
        n += 1
        # print(f'{i} injected {inj_tot}')
    topo = path.split('/')[-2]
    bench = path.split('/')[-3]
    print(f'{topo:20} : {bench:20} : avg inj {inj_tot / n}')
    # print(f'{path} avg inj {inj_tot / n}')


print('\n')
#quit()
for path, data_traff_dict in all_ctrl_traff.items():
    n = 0
    inj_tot = 0
    for i in range(84):

        for j in range(84):
            val = ctrl_traff_dict[i][j]
            if val > 0:
                # print(f's_ctrl_n{i} [{val} d_ctrl_n{j}')
                inj_tot += val

        n += i
        # print(f'{i} injected {inj_tot}')
    topo = path.split('/')[-2]
    bench = path.split('/')[-3]
    print(f'{topo:20} : {bench:20} : avg inj {inj_tot / n}')
