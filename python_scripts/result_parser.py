#!/usr/bin/python3

import os
import csv
import sys

metrics = ['average_packet_latency',
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
    print(f'format: <python> <script> <input_dir> <output_file_name>')
    quit()

output_name = sys.argv[2]

output_file = open(output_name,'w+')

csv_lines = []
csv_lines.append([ 'sim_cycles', 'mixed_or_same','mem_or_coh', 'topo', 'alg_type','lb_type', 'inj_rate'])

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


        cur_file = open(cur_path)
        lines = cur_file.readlines()

        # sim_cycles = root_split[1]
        # mixed_domain_or_same = root_split[2]
        # mem_or_coh = root_split[3]
        # config = root_split[4]
        # inj_rate = root_split[5]


        sim_cycles = root_split[2]
        mixed_domain_or_same = root_split[3]
        mem_or_coh = root_split[4]
        topo = root_split[5]
        alg_type = root_split[6]
        lb_type = root_split[7]
        inj_rate = root_split[8]

        if 'yara' in root:
            sim_cycles = root_split[7]
            mixed_domain_or_same = root_split[8]
            mem_or_coh = root_split[9]
            config = root_split[10]
            inj_rate = root_split[11]


        data = [ sim_cycles, mixed_domain_or_same, mem_or_coh, topo, alg_type, lb_type, inj_rate]



        data += parse_block( lines)


        print(data)
        if data != []:
            csv_lines.append(data)

        # quit()

wr = csv.writer(output_file, delimiter=',')
wr.writerows(csv_lines)

output_file.close()
