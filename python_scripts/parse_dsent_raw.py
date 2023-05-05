

import sys

in_file = sys.argv[1]


desired_topologies=[\
#     '20r_15ll_opt', '20r_15ll_opt_ulinks',
# '20r_25ll_timed7days', '20r_25ll_timed7days_ulinks',
# '20r_2ll_opt', '20r_2ll_runsol_ulinks',

'butter_donut_x', 'dbl_bfly_x',
'kite_large', 'kite_medium', 'kite_small',
'cmesh_x', 'mesh',
'ft_x',
'ns_s_latop','ns_s_bwop',
'ns_m_latop','ns_m_bwop',
'ns_l_latop','ns_l_bwop',
'lpbt_s_latop','lpbt_s_power',
'lpbt_m_latop']


topo = None
met_key = None

data_dict = {}


next_two_lines_are_sums = False

with open(in_file, 'r') as inf:
    for line in inf:

        line = line.replace('\n','')

        split_line = line.split(' ')
        for s in split_line:
            if s in desired_topologies:
                topo = s

                data_dict.update({topo:{}})
            # print(f's={s}.')
        
        # print(f'line={line}, topo={topo}')

        val_line = False
        if 'Sum' in line:
            next_two_lines_are_sums = True
        if 'Dynamic' in line:
            met_key = 'dyn'
            val_line = True
        elif 'Leakage' in line:
            met_key = 'leak'
            val_line = True

        if next_two_lines_are_sums and val_line:
            val = -1.0

            for s in split_line:
                try:
                    val = float(s)
                except:
                    pass

            if val == -1.0:
                print(f'eror parsing {line}')

            try:        
                data_dict[topo][met_key] += val
            except:
                data_dict[topo].update({met_key : val})

        if 'Leakage' in line:
            next_two_lines_are_sums = False

print(f'data_dict={data_dict}')


name = 'dsent_power_1m.csv'

types = ['dyn','leak']

out_lines = []
l = 'topo,'
for t in types:
    l += f'{t},'
l += '\n'
out_lines.append(l)

for key, met_dict in data_dict.items():
    l = f'{key},'
    for val in met_dict.values():
        l += f'{val},'
    l += '\n'
    out_lines.append(l)

with open(name,'w+') as of:
    of.writelines(out_lines)

print(f'wrote to {name}')