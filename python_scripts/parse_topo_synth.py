#!/usr/bin/python3

import os
import csv
import sys

metrics = ['average_packet_latency',
'average_flit_latency',
            'packets_received::total',
            'packets_injected::total']

def parse_block( block):

    if len(block) == 0:
        return []

    avg_flit_lat = 0

    data_dict = {}

    for line in block:
        sep = line.split()
        if len(sep) < 2:
            continue
        data = sep[1]
        for met in metrics:
            if met in line:
                data_dict.update({ met : float(data)})


    l = []
    for met in metrics:
        try:
            l.append(data_dict[met])
        except:
            l.append(-1)
    return l

if (len(sys.argv) < 3):
    print(f'not enough args')
    quit()

output_name = sys.argv[2]

one_topo = False
#if sys.argv[3] is not None:
#    one_topo = True


csv_lines = []
csv_lines.append([ 'sim_cycles', 'mixed_or_same','mem_or_coh', 'config','alg', 'inj_rate'])

for met in metrics:
    csv_lines[-1].append(met)

data_dir = str(sys.argv[1])

for root, dirs, files, in os.walk(data_dir):
    # print(f'root={root}, dirs={dirs}, files={files}')
    if 'stats.txt' in files:
        cur_path = os.path.join(root, 'stats.txt')
        #if 'size2048' not in cur_path and 'baseline' not in cur_path and 'assoc512' not in cur_path and 'assoc1024' not in cur_path:
        #    continue



        root_split = root.split('/')

        # print(f'{root_split}')
        # quit()

        cur_file = open(cur_path)
        lines = cur_file.readlines()

        # sim_cycles = root_split[1]
        # mixed_domain_or_same = root_split[2]
        # mem_or_coh = root_split[3]
        # config = root_split[4]
        # inj_rate = root_split[5]

        clk = '1.8GHz'
        topo_and_config = root_split[2]
        offset = 0
        if 'GHz' not in topo_and_config:

            continue
        else:
            offset = 1
            clk = topo_and_config.split('_')[-1]
        n_cpus = topo_and_config.split('_')[-2 - offset]
        n_dirs = topo_and_config.split('_')[-1 - offset]
        traf = root_split[3]
        sim_cycles = root_split[4]
        mixed_domain_or_same = root_split[5]
        alg = root_split[6]
        lb = root_split[6]
        mem_or_coh = root_split[7]
        topo = root_split[8]
        inj_rate = root_split[9]

        if sim_cycles == '10m':
            continue

        # if alg == 'naive_hops_3_4':
        #     continue

        # if 'yara' in root:
        #     sim_cycles = root_split[7]
        #     mixed_domain_or_same = root_split[8]
        #     mem_or_coh = root_split[9]
        #     config = root_split[10]
        #     inj_rate = root_split[11]


        data = [ sim_cycles, mixed_domain_or_same, mem_or_coh, alg, topo, traf, n_cpus ,n_dirs ,clk,inj_rate]

        # print(f'data={data}')
        # quit()

        data += parse_block( lines)


        print(data)
        if data != []:
            csv_lines.append(data)


# print(f'csv_lines({len(csv_lines)})={csv_lines}')
# quit()

output_file = open(output_name,'w+')
wr = csv.writer(output_file, delimiter=',')
wr.writerows(csv_lines)
output_file.close()

print(f'wrote to {output_name}')
