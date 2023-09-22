
import sys
import os
import math

# in_path = sys.argv[1]


data_dir = str(sys.argv[1])


data_dir_split = data_dir.split('/')
print(f'data_dir_split={data_dir_split}')
config = data_dir_split[1]
n_insts = data_dir_split[2]


def get_val_from_line(l):
    val = -1
    for e in l.split(" ")[1:]:
        try:
            val = int(e)
            return val

        except:
            pass
    return val


def get_float_val_from_line(l):
    val = -1
    for e in l.split(" ")[1:]:
        try:
            val = float(e)
            return val

        except:
            pass
    return val

all_data_traff = {}
all_ctrl_traff = {}
all_cycles_dict = {}
all_tot_cycles_dict = {}
all_pkts_dict = {}
all_flits_dict = {}

all_tot_insts_dict = {}
all_comm_insts_dict = {}

desired_which = 2




n_routers = 42
n_nodes = 16
n_dirs = 8


for root, dirs, files, in os.walk(data_dir):

    if 'stats.txt' in files :#sand 'blackscholes' in root:
        in_path = os.path.join(root, 'stats.txt')


        if 'canneal' not in in_path:
            print(f'skipping')
            continue

        bench = root.split('/')[-1]
        if 'skylake' in bench:
            bench = bench.split('_')[0]

        print(f'ingesting {bench}')


        data_traff = []
        ctrl_traff = []
        numCycles = 0
        totCycles = 0
        numPkts = 0
        numFlits = 0
        # avgIPC = 0
        avgIPC = 1

        totInsts = 0
        totCommInsts = 0

        simTicks = 0

        which = 0


        with open(in_path, 'r') as inf:
            for line in inf:

                # there are three sets of stats

                if 'Begin' in line:
                    which += 1

                if 'ctrl_traffic_distribution.' in line:
                    if which == desired_which:
                        ctrl_traff.append(line)
                    # ctrl_traff.append(line)
                if 'data_traffic_distribution.' in line:
                    if which == desired_which:
                        data_traff.append(line)
                    # data_traff.append(line)
                # cycles
                if 'system.switch_cpus0.numCycles' in line:

                    if which == desired_which:
                        
                        numCycles = get_val_from_line(line)
                if 'simTicks' in line:

                    if which == desired_which:
                        
                        simTicks = get_val_from_line(line)
                        # print(f'found ticks {simTicks} from line {line}')
                # dummy regex
                for i in range(n_nodes):
                    if f'system.switch_cpus{i}.numCycles' in line:
                        if which == desired_which:
                        
                            totCycles += get_val_from_line(line) 

                # dummy regex
                for i in range(n_nodes):
                    if f'system.switch_cpus{i}.numInsts' in line:
                        if which == desired_which:
                        
                            totInsts += get_val_from_line(line) 

                # dummy regex
                for i in range(n_nodes):
                    if f'system.switch_cpus{i}.committedInsts' in line:
                        if which == desired_which:
                        
                            totCommInsts += get_val_from_line(line) 

                if 'system.ruby.network.packets_injected::total' in line:
                    # print(f'line = {line}, which={which}')

                    if which == desired_which:
                        
                        numPkts = get_val_from_line(line)
                if 'system.ruby.network.flits_injected::total' in line:

                    # print(f'line = {line}, which={which}')

                    if which == desired_which:
                        
                        numFlits = get_val_from_line(line)

                if 'ipc' in line:

                    # print(f'line = {line}, which={which}')

                    if which == desired_which:
                        
                        ipc = get_float_val_from_line(line)
                        # print(f'ipc={ipc} from line {line}')
                        avgIPC *= ipc

                # get max 

        # avgIPC = avgIPC / n_nodes
        avgIPC = math.pow(avgIPC, 1/n_nodes)

        bench = root

        all_data_traff.update({bench:data_traff})
        all_ctrl_traff.update({bench:ctrl_traff})
        all_cycles_dict.update({bench:numCycles})
        all_tot_cycles_dict.update({bench:totCycles})
        all_pkts_dict.update({bench:numPkts})
        all_flits_dict.update({bench:numFlits})

        all_comm_insts_dict.update({bench:totCommInsts})
        all_tot_insts_dict.update({bench:totInsts})

# print(f'data_traff={all_data_traff}')

        # 1GHz => 1000 tick period
        # 4GHz => 250 tick period

        # print(f'\tflits = {numFlits} [flits/system] (/3*16 = {numPkts/(3.0*16.0)} pkts/cpu) over num_cycles = {numCycles}, tot_cycles = {totCycles}')
        config = root.split('/')
        simCycles = simTicks / 500

        # TODO remove
        # n_cycles = root.split('/')
        simCycles = 100000000

        n_avg_pkts = numFlits / 3
        
        
        try:
            val = numFlits / (3.0*totCycles)
            # print(f'\t={numFlits / (3.0*16.0*numCycles)}')
            # print(f'\t={val}')
            new_inj_rate = n_avg_pkts / simCycles
        except:
            new_inj_rate = 0
            pass






        print(f'-'*72)
        print(f'config={bench}')
        print(f'\tinsts={totInsts} ({totInsts/n_nodes} per cpu), comm insts={totCommInsts}, simTicks = {simTicks}, simCycles={simCycles}')

        print(f'\tnew_inj_rate = {new_inj_rate}')
        print(f'\t\tnumFlits = {numFlits}. simTicks = {simTicks}')
        print(f'\tavg ipc={avgIPC}')

        print('='*72)
quit()

for key, value in all_data_traff.items():

    data_traff_dict = {}

    print(f'processing data pkts for benchmark {key}')


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

    print(f'processing ctrl pkts for benchmark {key}')


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

# quit()


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
    n = -1

    # L1 or L2
    if r < n_nodes*2:
        # return r % n_nodes
        n = r % n_nodes
    
    # dir
    elif r < 2*n_nodes + n_dirs:
        # return r - 2*n_nodes
        n = r - 2*n_nodes
    
    # dma
    # return -1
    # n = -1

    # print(f'router_to_node : r={r}->{n}')

    return n

total_weighted_node_traf = [[0 for _ in range(n_nodes + 1)] for __ in range(n_nodes + 1)]

for bench, data_traff_dict in all_data_traff.items():
    tot_data_inj = 0


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

                if 'Dir' in name_i or 'Dir' in name_j:
                    continue


                # data are flits
                n_i = router_to_node(i)
                n_j = router_to_node(j)
                # print(f'\ts_data_n{i} [{val}] d_data_n{j}')
                total_weighted_node_traf[n_i][n_j] += 5*val
        n += 1

    # write_data_traf(bench, tot_data_inj, )

print('\n')
#quit()
for path, ctrl_traff_dict in all_ctrl_traff.items():
    n = 0
    inj_tot = 0
    for i in range(n_routers):

        for j in range(n_routers):

            try:
            
                val = ctrl_traff_dict[i][j]
            except:
                continue
            if val > 0:
                name_i = node_name_dict[i]
                name_j = node_name_dict[j]
                # print(f's_ctrl_n{i} [{val}] d_ctrl_n{j}')
                # print(f's_ctrl_{name_i} [{val}] d_ctrl_{name_j}')
                inj_tot += val

                if 'Dir' in name_i or 'Dir' in name_j:
                    continue


                n_i = router_to_node(i)
                n_j = router_to_node(j)
                total_weighted_node_traf[n_i][n_j] += val

        n += i

for i in range(n_nodes + 1):

    for j in range(n_nodes + 1):
        val = total_weighted_node_traf[i][j]
        name_i = f's{i}'
        name_j = f'd{j}'
        if val > 0:
            print(f'{name_i} [{val}] {name_j}')

quit()

print('\n')
quit()