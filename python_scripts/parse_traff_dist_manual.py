
import sys
import os

# in_path = sys.argv[1]


data_dir = str(sys.argv[1])

all_data_traff = {}
all_ctrl_traff = {}


in_path = os.path.join(sys.argv[1])

# print(f'ingesting {sys.argv[1]}')


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

    # print(f'processing data {key}')


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
        # print(f'ivc={ivc_str}, ovc_str={ovc_str}')


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

        # print(f'ivc={ivc}->ovc={ovc}, val={val}')
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

n_routers = 42
n_nodes = 16
n_dirs = 8

node_name_dict = {}


node_iter = 0

for i in range(n_nodes):
    name = f'L1_{i}'
    node_name_dict.update({node_iter : name})
    node_iter += 1

for i in range(n_nodes):
    name = f'L2_{i}'
    node_name_dict.update({node_iter : name})
    node_iter += 1

for i in range(n_dirs):
    name = f'Dir_{i}'
    node_name_dict.update({node_iter : name})
    node_iter += 1

node_name_dict.update({node_iter : 'dma0'})
node_iter += 1
node_name_dict.update({node_iter : 'io'})

def router_to_node(r):
    # L1 or L2
    if r < n_nodes*2:
        return r % n_nodes
    
    # dir
    if r < 2*n_nodes + n_dirs:
        return r - 2*n_nodes
    
    # dma
    return -1

tot_data_inj = 0

total_weighted_node_traf = [[0 for _ in range(n_nodes + 1)] for __ in range(n_nodes + 1)]

for path, data_traff_dict in all_data_traff.items():
    n = 0
    inj_tot = 0
    for i in range(n_routers):

        for j in range(n_routers):
            try:
                val = data_traff_dict[i][j]
            except:
                continue




            # print(f'val={val}')
            # print(f'dtd={data_traff_dict}')
            if val > 0:
                name_i = node_name_dict[i]
                name_j = node_name_dict[j]
                # print(f's_data_n{i} [{val}] d_data_n{j}')
                # print(f's_data_{name_i} [{val}] d_data_{name_j}')
                inj_tot += val
                tot_data_inj += val


                # data are flits
                n_i = router_to_node(i)
                n_j = router_to_node(j)
                total_weighted_node_traf[n_i][n_j] += 5*val
        n += 1
        # print(f'{i} injected {inj_tot}')
    # topo = path.split('/')[-2]
    # bench = path.split('/')[-3]
    # print(f'{topo:20} : {bench:20} : ')
    # print(f'// avg data inj {inj_tot / n}')
    # print(f'{path} avg inj {inj_tot / n}')


print('\n')
#quit()
for path, ctrl_traff_dict in all_ctrl_traff.items():
    n = 0
    inj_tot = 0
    for i in range(n_routers):

        for j in range(n_routers):

            val = ctrl_traff_dict[i][j]
            if val > 0:
                name_i = node_name_dict[i]
                name_j = node_name_dict[j]
                # print(f's_ctrl_n{i} [{val}] d_ctrl_n{j}')
                # print(f's_ctrl_{name_i} [{val}] d_ctrl_{name_j}')
                inj_tot += val

                n_i = router_to_node(i)
                n_j = router_to_node(j)
                total_weighted_node_traf[n_i][n_j] += val

        n += i
        # print(f'{i} injected {inj_tot}')
    # topo = path.split('/')[-2]
    # bench = path.split('/')[-3]
    # print(f'{topo:20} : {bench:20} :')
    # print(f'// avg ctrl inj {inj_tot / n}')

for i in range(n_nodes + 1):

    for j in range(n_nodes + 1):
        val = total_weighted_node_traf[i][j]
        name_i = f's{i}'
        name_j = f'{j}'
        if val > 0:
            print(f'{name_i} [{val}] {name_j}')

quit()

data_traff_dict = list(all_data_traff.values())[0]

ctrl_traff_dict = list( all_ctrl_traff.values())[0]


# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey

sc = 1.0 / tot_data_inj

sank = Sankey(scale=sc)



# sank.add()

for i in range(n_routers):

    s_label = f's_data_{name_i}'
    d_labels = []

    tot_s = 0
    vals = []
    

    for j in range(n_routers):
        try:
            val = data_traff_dict[i][j]
        except:
            continue




        # print(f'val={val}')
        # print(f'dtd={data_traff_dict}')
        if val > 0:
            name_i = node_name_dict[i]
            name_j = node_name_dict[j]
            
            

            # print(f's_data_n{i} [{val}] d_data_n{j}')
            # print(f's_data_{name_i} [{val}] d_data_{name_j}')
            # inj_tot += val


            tot_s += val
            vals.append(val)

            d_labels.append(f'd_data_n{j}')

            sank.add(flows=[val,-val],labels=[s_label,f'd_data_n{j}'])

    if tot_s == 0:
        continue

    s_flows = [tot_s]
    for v in vals:
        s_flows.append(-1*v)

    s_labels = [s_label]
    for l in d_labels:
        s_labels.append(l)

    print(f'flows={s_flows}. labels={s_labels}')


    sank.add(flows=s_flows,labels=s_labels)

    sank.finish()
    plt.show()
    quit()


sank.finish()

plt.show()

labels = []

for i in range(n_routers):

    for j in range(n_routers):

        val = data_traff_dict[i][j]
        if val > 0:
            name_i = node_name_dict[i]
            name_j = node_name_dict[j]
            i_node = f's_ctrl_{name_i}' 
            j_node = f'd_ctrl_{name_j}'
            if i_node not in labels:
                labels.append(i_node)
            if j_node not in labels:
                labels.append(j_node)

print(f'labels={labels}')

# import plotly.graph_objects as go

# fig = go.Figure(data=[go.Sankey(
#     node = dict(
#       pad = 15,
#       thickness = 20,
#       line = dict(color = "black", width = 0.5),
#       label = ["A1", "A2", "B1", "B2", "C1", "C2"],
#       color = "blue"
#     ),
#     link = dict(
#       source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
#       target = [2, 3, 3, 4, 4, 5],
#       value = [8, 4, 2, 8, 4, 2]
#   ))])

# fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
# fig.show()