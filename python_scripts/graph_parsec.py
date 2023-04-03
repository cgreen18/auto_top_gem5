import matplotlib.pyplot as plt
import csv
import numpy as np

# infile_name = 'paper_outputs/parsec_noci_250kBL2_10m.csv'
infile_name = 'paper_outputs/parsec_noci_500kBL2_10m.csv'
# infile_name = 'paper_outputs/parsec_noci_largemem_3GHzCPU.csv'
# infile_name = 'paper_outputs/parsec_noci_largemem_20m.csv'
infile_name = 'parsec_results/parsec_noci_largemem_18GHz_500kB_100m.csv'

use_totcycles = False
use_numcycles = False


# outfile_suffix = '250kB_10m_maxCycles'
outfile_suffix = '500kB_10m_maxCycles_both'
# outfile_suffix = '_500kB_10m'
# outfile_suffix = '_2MB_3GHz_10m_maxCycles'
# outfile_suffix = '2MB_18GHz_20m_maxCycles_3'

# use_numcycles = True
# outfile_suffix = '250kB_10m_numCycles'
# outfile_suffix = '500kB_10m_numCycles'
# outfile_suffix = '_500kB_10m'
# outfile_suffix = '_2MB_3GHz_10m_numCycles'
# outfile_suffix = '2MB_18GHz_20m_numCycles'

# use_totcycles = True
# outfile_suffix = '250kB_10m_totCycles'
# outfile_suffix = '500kB_10m_totCycles'
# outfile_suffix = '_500kB_10m'
# outfile_suffix = '_2MB_3GHz_10m_totCycles'
# outfile_suffix = '2MB_18GHz_20m_totCycles'

use_simticks = True

use_pkt_lat = True
# outfile_suffix = '2MB_18GHz_20m_pktLat'

use_both = True
# outfile_suffix = '2MB_18GHz_20m_both_numcycles_lim'
outfile_suffix = '500kB_10m_both_totcycles_lim_v3'
outfile_suffix = '500kB_10m_both_simticks_lim_v3'


bad_benches = []
# bad_benches = ['blackscholes','bodytrack','raytrace','x264']

# bad_benches = ['x264','raytrace','bodytrack','blackscholes']
# bad_benches = ['blackscholes','raytrace','x264']

# 3GHz
# bad_benches = ['raytrace','bodytrack','blackscholes']

# 20m
# bad_benches = ['blackscholes','raytrace','freqmine']
# bad_benches = ['raytrace']
# bad_benches = ['dedup']
# bad_benches = ['dedup','bodytrack','ferret','blackscholes']



# 500kB
bad_benches = ['blackscholes','raytrace']


# 250kB
# bad_benches = ['blackscholes','raytrace','x264']

topos = []


double_rename = {'Kite Small':'Kite',
'Kite Med':'Kite',
'Kite Large':'Kite',
'NS-LatOp Small':'NS-LatOp',
'NS-LatOp Med':'NS-LatOp',
'NS-LatOp Large':'NS-LatOp',
'NS-BWOp Small':'NS-BWOp',
'NS-BWOp Med':'NS-BWOp',
'NS-BWOp Large':'NS-BWOp',
}


color_dict = {'NS-LatOp Small':'tab:blue',
                'NS-BWOp Small':'tab:orange',
    
              'NS-LatOp Med':'tab:red',
              'NS-BWOp Med':'tab:purple',
              'NS-LatOp Large':'tab:green',
              'NS-BWOp Large':'tab:gray',
              
              'Kite Small':'tab:olive',
              'Kite Med':'tab:brown',
              'Butter Donut':'lightcoral',
              'Dbl Butterfly':'tab:cyan',
              'Kite Large':'mediumaquamarine',
              'Folded Torus':'goldenrod',

              'CMesh':'gold'  }

rename_dict = { '20r_15ll_opt_ulinks_noci':'NS-LatOp Small',
                '20r_2ll_runsol_ulinks_noci':'NS-LatOp Med',
                '20r_25ll_timed7days_ulinks_noci':'NS-LatOp Large',
                '20r_15ll_opt_8bw_4diam_ulinks_noci':'NS-BWOp Small',
                '20r_4p_2ll_runsol_12bw_ulinks_noci':'NS-BWOp Med',
                '20r_4p_25ll_runsol_14bw_ulinks_noci':'NS-BWOp Large',
                'butter_donut_x_noci':'Butter Donut',
                'cmesh_x_noci':'CMesh',
                'dbl_bfly_x_noci':'Dbl Butterfly',
                'kite_small_noci':'Kite Small',
                'kite_medium_noci':'Kite Med',
                'ft_x_noci':'Folded Torus',
                'kite_large_noci':'Kite Large',
                'ns_s_latop_noci':'NS-LatOp Small',
                'ns_s_bwop_noci':'NS-BWOp Small',
                'ns_m_latop_noci':'NS-LatOp Med',
                'ns_m_bwop_noci':'NS-BWOp Med',
                'ns_l_latop_noci':'NS-LatOp Large',
                'ns_l_bwop_noci':'NS-BWOp Large',
                'ns_s_latop':'NS-LatOp Small',
                'ns_s_bwop':'NS-BWOp Small',
                'ns_m_latop':'NS-LatOp Med',
                'ns_m_bwop':'NS-BWOp Med',
                'ns_l_latop':'NS-LatOp Large',
                'ns_l_bwop':'NS-BWOp Large',
                'butter donut':'Butter Donut',
                'dbl bfly':'Dbl Butterfly',
                'kite small':'Kite Small',
                'kite med':'Kite Medium',
                'kite large':'Kite Large',
                'mesh_noci':'Mesh'
                }

# desired_topologies=[
# # '20r_15ll_opt', '20r_15ll_opt_ulinks',
# # '20r_25ll_timed7days', '20r_25ll_timed7days_ulinks',
# # '20r_2ll_opt', '20r_2ll_runsol_ulinks',
# 'ns_s_latop',
# 'ns_m_latop',
# 'ns_l_latop',
# # 'ns_s_bwop',
# # 'ns_m_bwop',
# # 'ns_l_bwop',
# 'butter_donut_x', 'dbl_bfly_x',
# 'kite_large', 'kite_medium', 'kite_small',
# 'cmesh_x',

# # 'mesh'
# ]

# used after rename
desired_topologies = [
'Kite Small',

'NS-LatOp Small',
'NS-BWOp Small',

'Folded Torus',
'Kite Med',
'NS-LatOp Med',
'NS-BWOp Med',

'Butter Donut',
'Dbl Butterfly',
'Kite Large',
'NS-LatOp Large',
'NS-BWOp Large',

# 'CMesh'
]


data = {}

with open(infile_name, 'r') as inf:
    csv_inf = csv.reader(inf)

    headers = []

    bench_idx = 0
    topo_idx = 1
    cycles_idx = 11
    pkt_lat_idx = 6
    num_cycles_idx = 4
    tot_cycles_idx = 10

    for line in csv_inf:
        print(f'line={line}')

        if len(headers) == 0:
            headers = line
            topo_idx = headers.index('config')
            cycles_idx = headers.index('maxCycles')
            pkt_lat_idx = headers.index('average_packet_latency')
            num_cycles_idx = headers.index('numCycles')
            tot_cycles_idx = headers.index('cumulativeCycles')
            sim_ticks_idx = headers.index('simTicks')
            continue

        bench = line[bench_idx]
        topo = line[topo_idx]

        renamed_topo = rename_dict[topo]

        try:
            cycles_str = line[cycles_idx]

            if use_numcycles:
                # numCycles instead of maxCycles
                cycles_str = line[num_cycles_idx]

            # # totalCycles instead of maxCycles
            if use_totcycles:
                cycles_str = line[tot_cycles_idx]
                # print(f'cycles_str={cycles_str}')

            if use_simticks:
                cycles_str = line[sim_ticks_idx]

            cycles = float(cycles_str)

            print(f'cycles={cycles}')
        except:
            # print(f'defauting for topo={renamed_topo}')
            cycles = 0

        try:
            pkt_lat = float(line[pkt_lat_idx])
        except:
            pkt_lat = 0

        try:
            _ = data[bench]
        except:
            data.update({ bench : {} })

        try:
            _ = data[bench][renamed_topo]
            # _ = data[bench][topo]
        except:
            data[bench].update({renamed_topo : {}})
            # data[bench].update({topo : {}})

        data[bench][renamed_topo].update( {'maxCycles' : cycles })
        data[bench][renamed_topo].update( {'pkt_lat' : pkt_lat })
        # data[bench][topo].update( {'maxCycles' : cycles })
        # data[bench][topo].update( {'pkt_lat' : pkt_lat })


bench_list = []
topo_list = []
for bench, topo_data in data.items():
    
    if bench not in bench_list:
        bench_list.append(bench)

    mesh_base_cycles = topo_data['Mesh']['maxCycles']
    if mesh_base_cycles == 0:
        continue
    mesh_rel_cycles = 1
    topo_data['Mesh'].update({'relCycles' : mesh_rel_cycles})

    mesh_base_pkt_lat = topo_data['Mesh']['pkt_lat']
    topo_data['Mesh'].update({'rel_pkt_lat':1})

    for topo, met_data in topo_data.items():
        if topo not in topo_list:
            topo_list.append(topo)
        this_cycles = met_data['maxCycles']
        try:
            this_rel_cycles = mesh_base_cycles / this_cycles
        except:
            this_rel_cycles = 0
        met_data.update({ 'relCycles' : this_rel_cycles })

        # this_pkt_lat = met_data['pkt_lat']
        try:
            # rel_pkt_lat = met_data['pkt_lat'] / mesh_base_pkt_lat
            rel_pkt_lat = mesh_base_pkt_lat / met_data['pkt_lat']

        except:
            rel_pkt_lat = 0
        met_data.update({'rel_pkt_lat':rel_pkt_lat})




## calc goemean
gmeans = []

data.update({'geomean' : {}})

for topo in desired_topologies:
    
    runprod = 1
    n_elems = 0

    for bench in bench_list:
        if bench in bad_benches:
            continue
        
        try:
            val = data[bench][topo]['relCycles']
        except:
            val = 1
        runprod *= val
        n_elems += 1

    gmean = runprod**(1/n_elems)
    gmeans.append(gmean)
    data['geomean'].update({topo : {}})
    data['geomean'][topo].update({'relCycles' : gmean})

for topo in desired_topologies:
    
    runprod = 1
    n_elems = 0

    for bench in bench_list:
        if bench in bad_benches:
            continue
        
        try:
            val = data[bench][topo]['rel_pkt_lat']
        except:
            val = 1
        runprod *= val
        n_elems += 1

    gmean = runprod**(1/n_elems)
    gmeans.append(gmean)
    data['geomean'][topo].update({'rel_pkt_lat' : gmean})

for topo,topo_data in data['geomean'].items():
    print(f'{topo} geomean rel cycles={topo_data["relCycles"]}')
for topo,topo_data in data['geomean'].items():
    print(f'{topo} geomean pkt lat={topo_data["rel_pkt_lat"]}')
# quit()


bench_list.sort()

bench_list.append('geomean')







for bench, topo_data in data.items():

    print(f'bench={bench}')
    for topo, met_data in topo_data.items():
        print(f'\ttopo={topo}')
        for met, val in met_data.items():
            print(f'\t\t{met} : {val}')




# gen graph values

# list of lists
y_vals_list = []
y_labels = []

secondary_y_vals_list = []

x_val_list = []


for topo in desired_topologies:

    # if topo not in desired_topologies:
    #     continue

    y_vals_list.append([])
    secondary_y_vals_list.append([])

    try:
        new_name = double_rename[topo]
    except:
        new_name = topo

    y_labels.append(topo)


    for bench in bench_list:
        # print(f'data[bench][topo]={data[bench][topo]}')
        if bench in bad_benches:
            continue
        
        if bench not in x_val_list:
            x_val_list.append(bench)

        print(f'data[{bench}][{topo}]={data[bench][topo]}')

        try:
            val = data[bench][topo]['relCycles']
        except:
            val = 0
        y_vals_list[-1].append(val)


        try:
            val = data[bench][topo]['rel_pkt_lat']
        except:
            val = 0
        secondary_y_vals_list[-1].append(val)












plt.cla()
# plt.clear()
plt.rc('font', size=10) #controls default text size
plt.rc('axes', titlesize=15) #fontsize of the title
plt.rc('axes', labelsize=14) #fontsize of the x and y labels
plt.rc('xtick', labelsize=14) #fontsize of the x tick labels
plt.rc('ytick', labelsize=10) #fontsize of the y tick labels
plt.rc('legend', fontsize=12)

fig = plt.figure(figsize=(14,2))
ax = fig.add_subplot()

plt.ylabel('Execution Speedup')

if use_both:
    ax2 = ax.twinx()
    plt.ylabel('Pkt. Latency Reduction (+)')

# plt.xlabel("Injection Rate (pkts/cpu/cycle)")
# plt.ylabel("Speedup")
# ax.set_label('Execution Speedup')
# if use_both:
#     ax2.set_label('Avg. Pkt. Latency Reduction')

width = 0.4
gap = 0.05


last_of_size = [2,6]


n_benches = len(x_val_list)
mult = 7
x = np.arange(0,mult*n_benches,mult)

offset = -7*(width+gap)
for i in range(len(y_vals_list)):
    # print(f'x({len(x)})={x}')
    # print(f'y_vals({len(y_vals_list)})={y_vals_list}')
    offset += width+gap
    lab = y_labels[i]

    try:
        new_lab = double_rename[lab]
    except:
        new_lab = lab
    col = color_dict[lab]

    if use_both:
        ax.bar(x + offset, y_vals_list[i],width, edgecolor='black',linewidth=0.5,color=col,label=new_lab)
        ax2.scatter(x+offset,secondary_y_vals_list[i],color='k',marker='+',label=y_labels[i])

    elif not use_pkt_lat:
        ax.bar(x + offset, y_vals_list[i],width, edgecolor='black',linewidth=0.5,color=col,label=new_lab)
    else:
    # secondary_y_vals_list[]
        ax.bar(x + offset, secondary_y_vals_list[i],width, edgecolor='black',linewidth=0.5,color=col,label=new_lab)
        # ax2.scatter(x+offset,secondary_y_vals_list[i],color='k',marker='+',label=y_labels[i])
    if i in last_of_size:
        offset += 4*gap


ax.set_xticks(x)
ax.set_xticklabels(x_val_list)#,horizontalalignment='left', rotation=-20, rotation_mode="anchor")


ax.set_xlim([-3.5,52.5])


y = np.arange(0.5,3.0,0.5)
y_minor = np.arange(0.8,4.0,0.1)
ax.set_yticks(y)
ax.set_yticks(y_minor,minor=True)

ax.set_ylim([0.8,1.5])

ax.grid(which='major',alpha=0.5)
ax.grid(which='minor',alpha=0.2)

if use_both:
    ax2.grid(which='minor',alpha=0.2)

handles, labels = ax.get_legend_handles_labels()

p0 = plt.plot([],[],color='none',label=' ')
p4 = plt.plot([],[],color='none',label=' ')
p7 = plt.plot([],[],color='none',label=' ')
p8 = plt.plot([],[],color='none',label=' ')

p11 = plt.plot([],[],color='none',label=' ')
p12 = plt.plot([],[],color='none',label=' ')

p16 = plt.plot([],[],color='none',label=' ')


# proxy3 = plt.plot([],[],color='none',label=' ')
# proxy7 = plt.plot([],[],color='none',label=' ')

handles.insert(0,p0[0])
handles.insert(4,p4[0])
handles.insert(7,p7[0])

handles.insert(8,p8[0])
handles.insert(11,p11[0])
handles.insert(12,p12[0])


handles.insert(16,p16[0])

# handles.insert(7,proxy7[0])

labels.insert(0,'Small')
labels.insert(4,'Medium')
labels.insert(7,' ')

labels.insert(8,' ')
labels.insert(11,' ')
labels.insert(12,'Large')

labels.insert(16,' ')

# labels.insert(7,' ')

# ax.legend(handles, labels,ncol=6,bbox_to_anchor=(.1, 1.2))

# ax.legend(handles, labels,ncol=5,bbox_to_anchor=(0.225, 1.02, 1., .102))

ax.legend(handles, labels,ncol=5,bbox_to_anchor=(0.225, 2.02, 1., .102))

# plt.title(outfile_suffix)

# plt.grid(linestyle='-', linewidth=0.5)

outname=f'./parsec_results/graphs/parsec_bar_{outfile_suffix}.png'
print(f'writing out to : {outname}')
plt.savefig(outname,bbox_inches='tight')#,dpi=800)
print(f'wrote out to : {outname}')

plt.show()
