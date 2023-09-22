import matplotlib.pyplot as plt
import csv
import numpy as np


from matplotlib import rc

infile_name = 'dsent_sorted_micro.csv'
infile_name = 'dsent_wscop_5jul.csv'

color_dict = {'NS-LatOp Small':'tab:blue',
                'NS-BWOp Small':'tab:orange',
                'NS-SCOp Small':'tab:orange',

              'NS-LatOp Med':'tab:red',
              'NS-BWOp Med':'tab:purple',
              'NS-SCOp Med':'tab:purple',
              'NS-LatOp Large':'tab:green',
              'NS-BWOp Large':'tab:gray',
              'NS-SCOp Large':'tab:gray',

              'Kite Small':'tab:olive',
              'LPBT-Power Small':'blueviolet',
              'LPBT-Hops Small':'peru',

              'Kite Med':'tab:brown',
              'LPBT-Hops Med':'teal',

              'Butter Donut':'lightcoral',
              'Dbl Butterfly':'tab:cyan',
              'Kite Large':'mediumaquamarine',
              'Folded Torus':'goldenrod',

              'CMesh':'gold',
              'Mesh':'gold'  }

topos = []


rename_dict = { '20r_15ll_opt_ulinks_noci':'NS-LatOp Small',
                '20r_2ll_runsol_ulinks_noci':'NS-LatOp Med',
                '20r_25ll_timed7days_ulinks_noci':'NS-LatOp Large',
                '20r_15ll_opt_8bw_4diam_ulinks_noci':'NS-BWOp Small',
                '20r_4p_2ll_runsol_12bw_ulinks_noci':'NS-BWOp Med',
                '20r_4p_25ll_runsol_14bw_ulinks_noci':'NS-BWOp Large',
                'butter_donut_x':'Butter Donut',
                'cmesh_x':'CMesh',
                'dbl_bfly_x':'Dbl Butterfly',
                'kite_small':'Kite Small',
                'kite_medium':'Kite Med',
                'kite_med':'Kite Med',
                'ft_x':'Folded Torus',
                'kite_large':'Kite Large',
                'ns_s_latop':'NS-LatOp Small',
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
                'ns_s_scop':'NS-SCOp Small',
                'ns_m_scop':'NS-SCOp Med',
                'ns_l_scop':'NS-SCOp Large',
                'butter donut':'Butter Donut',
                'dbl bfly':'Dbl Butterfly',
                'kite small':'Kite Small',
                'kite med':'Kite Medium',
                'kite large':'Kite Large',
                'mesh':'Mesh',
                'lpbt_20r_5p_15ll_power_runsol_noci':'LPBT-Power Small',
                'lpbt_20r_5p_15ll_total_hops_runsol_noci':'LPBT-Hops Small',
                'lpbt_20r_5p_2ll_total_hops_runsol_noci':'LPBT-Hops Med',
                'lpbt_s_power':'LPBT-Power Small',
                'lpbt_s_latop':'LPBT-Hops Small',
                'lpbt_m_latop':'LPBT-Hops Med',
                }

desired_topologies=[
# '20r_15ll_opt', '20r_15ll_opt_ulinks',
# '20r_25ll_timed7days', '20r_25ll_timed7days_ulinks',
# '20r_2ll_opt', '20r_2ll_runsol_ulinks',

'kite_small',
'ns_s_latop',
'ns_s_bwop',

'ft_x',
'kite_medium', 
'ns_m_latop',
'ns_l_latop',
'ns_m_bwop',


'butter_donut_x', 'dbl_bfly_x',
'ns_l_bwop',
'kite_large', 
# 'cmesh_x',

'mesh'
]

# used after rename
desired_topologies = [
'Kite Small',
'LPBT-Power Small',
'LPBT-Hops Small',
'NS-LatOp Small',
# 'NS-BWOp Small',
'NS-SCOp Small',

'Folded Torus',
'Kite Med',
'LPBT-Hops Med',
'NS-LatOp Med',
# 'NS-BWOp Med',
'NS-SCOp Med',

'Butter Donut',
'Dbl Butterfly',
'Kite Large',
'NS-LatOp Large',
# 'NS-BWOp Large',
'NS-SCOp Large',
# 'Mesh'

# 'CMesh'
]



data = {}

topo_list = []

with open(infile_name, 'r') as inf:
    csv_inf = csv.reader(inf)

    headers = []

    topo_idx = 0
    rel_dyn_pow_idx = 7
    rel_leak_pow_idx = 8
    rel_router_area = 9
    rel_wire_area = 10
    glob_rel_dyn_pow_idx = 11
    glob_rel_leak_pow_idx = 12
    glob_rel_router_area = 13
    glob_rel_wire_area = 14

    for line in csv_inf:
        print(f'line={line}')

        if len(headers) == 0:
            headers = line

            continue

        topo = line[topo_idx]

        if topo not in topo_list:
            topo_list.append(topo)

        renamed_topo = rename_dict[topo]

        try:
            dyn_pow = float(line[rel_dyn_pow_idx])
            leak_pow = float(line[rel_leak_pow_idx])

            r_area = float(line[rel_router_area])
            w_area = float(line[rel_wire_area])
        except:
            dyn_pow = 0.0
            leak_pow = 0.0

            r_area = 0.0
            w_area = 0.0

        try:
            g_dyn_pow = float(line[glob_rel_dyn_pow_idx])
        except:
            g_dyn_pow = 0.0
        
        try:
            g_leak_pow = float(line[glob_rel_leak_pow_idx])
        except:
            g_leak_pow = 0.0


        g_r_area = float(line[glob_rel_router_area])
        g_w_area = float(line[glob_rel_wire_area])

        try:
            _ = data[renamed_topo]
        except:
            data.update({ renamed_topo : {} })

        data[renamed_topo].update({'dyn_pow' : dyn_pow }) 
        data[renamed_topo].update({'leak_pow' : leak_pow })
        data[renamed_topo].update({'r_area' : r_area })
        data[renamed_topo].update({'w_area' : w_area })

        data[renamed_topo].update({'g_dyn_pow' : g_dyn_pow }) 
        data[renamed_topo].update({'g_leak_pow' : g_leak_pow })
        data[renamed_topo].update({'g_r_area' : g_r_area })
        data[renamed_topo].update({'g_w_area' : g_w_area })



for topo, met_data in data.items():
    print(f'\ttopo={topo}')
    for met, val in met_data.items():
        print(f'\t\t{met} : {val}')

# quit()

#####################################################################3

# gen graph values

# list of lists
y_vals_list = []
y_labels = []

bottom_y_vals = []
top_y_vals = []

x_val_list = []


rename_met = {
    'dyn_pow':'Dynamic Power',
    'leak_pow':'Leakage Power',
    'r_area':'Router Area',
    'w_area':'Wire Area',
    'g_dyn_pow':'Power',
    'g_leak_pow':'Power',
    'g_r_area':'Area',
    'g_w_area':'Area',
}


metrics = ['dyn_pow','leak_pow','r_area','w_area']

metrics = ['g_leak_pow','g_dyn_pow','g_r_area','g_w_area',]

# metrics = ['dyn_pow','leak_pow','g_r_area','g_w_area',]

for topo in desired_topologies:
    y_vals_list.append([])

    
    if topo not in y_labels:
            y_labels.append(topo)

    for met in metrics:

        if rename_met[met] not in x_val_list:
            new_name = rename_met[met]
            x_val_list.append(new_name)

    

        # if topo not in desired_topologies:
        #     continue




        # try:
        val = data[topo][met]
        # except:
            # val = 0
        y_vals_list[-1].append(val)

    # # leakage
    # bottom_y_vals[0].append(data[topo]['leak_pow'])


    # glob_rel_router_area

    # bottom_y_vals[1].append(data[topo]['leak_pow'])
#####################################################################3

plt.cla()
# plt.clear()


plt.rc('font', size=10) #controls default text size
plt.rc('axes', titlesize=12) #fontsize of the title
plt.rc('axes', labelsize=12) #fontsize of the x and y labels
plt.rc('xtick', labelsize=12) #fontsize of the x tick labels
plt.rc('ytick', labelsize=10) #fontsize of the y tick labels
plt.rc('legend', fontsize=9)
plt.rc('hatch',linewidth=0.75)

plt.rc('text', usetex=True)

fig = plt.figure(figsize=(7,2.5))
ax = fig.add_subplot()

plt.grid()




# plt.xlabel("Injection Rate (pkts/cpu/cycle)")
plt.ylabel("Relative to Mesh")

width = 1.0
gap = 0.25

n_benches = len(x_val_list)
mult = 21
x = np.arange(0,mult*n_benches,mult)
print(f'x({len(x)})={x}')
print(f'y_vals_list({len(y_vals_list)})={y_vals_list}')
print(f'y_vals_list[0]({len(y_vals_list[0])})={y_vals_list[0]}')

# offset = -5*(width+gap)
# for i in range(0,len(y_vals_list),2):
    # print(f'x({len(x)})={x}')
    # print(f'y_vals({len(y_vals_list)})={y_vals_list}')




last_of_size = [4,9]

blank_idx = [0,5,10]#,12]# [0,5,12]
second_skip = [5,10]#[5,7]
for_legend = []

offset = -8.5*(width+gap)
for i in range(0,len(y_vals_list)):
    # print(f'x({len(x)})={x}')
    # print(f'y_vals({len(y_vals_list)})={y_vals_list}')
    offset += width+gap
    lab = y_labels[i]
    col = color_dict[lab]

    if i in blank_idx:
        for_legend.append(ax.bar(x[0] + offset,0,color='none') )
    # if i in second_skip:
        
    #     offset += 2*gap
        # for_legend.append(ax.bar(x[0] + offset,0,color='none') )
    for_legend.append(ax.bar(x[0] + offset,0,color=col,label=lab) )

    print(f'y_vals {i} : {lab} : y_vals_list[i]={y_vals_list[i]}')


    ax.bar(x[0] + offset, y_vals_list[i][0],width, color=col,label=lab,edgecolor='black', linewidth=0.5,hatch='////')
    # lab = y_labels[i]
    # col = color_dict[lab]
    ax.bar(x[0] + offset, y_vals_list[i][1],width, color=col,label=lab,bottom=y_vals_list[i][0],edgecolor='black', linewidth=0.5,hatch='oooo')
    # ax.bar(x[1] + offset, y_vals_list[i][1],width, color=col,label=lab,edgecolor='black', linewidth=0.5,hatch='oooo')

    ax.bar(x[1] + offset, y_vals_list[i][2],width, color=col,label=lab,edgecolor='black', linewidth=0.5,hatch='xxxx')
    # ax.bar(x[2] + offset, y_vals_list[i][2],width, color=col,label=lab,edgecolor='black', linewidth=0.5,hatch='xxxx')
    # lab = y_labels[i]
    # col = color_dict[lab]
    ax.bar(x[1] + offset, y_vals_list[i][3],width, color=col,label=lab,bottom=y_vals_list[i][2],edgecolor='black', linewidth=0.5,hatch='....')
    # ax.bar(x[2] + offset, y_vals_list[i][3],width, color=col,label=lab,bottom=y_vals_list[i][2],edgecolor='black', linewidth=0.5,hatch='....')



    if i in last_of_size:
        offset +=2*gap



ax.set_xticks(x)


ax.set_xticklabels(x_val_list)#,horizontalalignment='left', rotation=-30, rotation_mode="anchor")

y = np.arange(0.0,1.55,0.5)
ax.set_yticks(y)
ax.set_ylim([0.0,1.2])
ax.set_xlim([-10.5,31.5])


handles, labels = ax.get_legend_handles_labels()

# blank_idx = [0,6,7,8,11,12,16]
# proxy0 = plt.plot([],[],color='none',label=' ')
# proxy6 = plt.plot([],[],color='none',label=' ')
# p7 = plt.plot([],[],color='none',label=' ')

# proxy8 = plt.plot([],[],color='none',label=' ')
# p11 = plt.plot([],[],color='none',label=' ')
# p12 = plt.plot([],[],color='none',label=' ')
# p16 = plt.plot([],[],color='none',label=' ')


# handles.insert(7,p7[0])
# handles.insert(11,p7[0])
# handles.insert(12,p7[0])
# handles.insert(16,p7[0])



# handles.insert(0,proxy0[0])
# handles.insert(7,proxy6[0])
# handles.insert(8,proxy8[0])

# labels.insert(0,' ')
# labels.insert(6,' ')
# labels.insert(7,' ')

# labels.insert(8,' ')
# labels.insert(11,' ')
# labels.insert(12,' ')
# labels.insert(16,' ')


custom_labels = [
r'\underline{Small}',
'Kite',
'LPBT-Hops',
'LPBT-Power',
'NS-LatOp',

# 'NS-BWOp',
'NS-SCOp',

r'\underline{Medium}',

'Folded Torus',
'Kite',
'LPBT-Hops',
# '',

# '',
'NS-LatOp',
# 'NS-BWOp',
'NS-SCOp',

# '',

r'\underline{Large}',
'Butter Donut',
'Dbl Butterfly',
'Kite',
# '',
'NS-LatOp',
# 'NS-BWOp',
'NS-SCOp',

# 'CMesh',
'Mesh'

]


leg1 = ax.legend(for_legend, custom_labels,ncol=3,bbox_to_anchor=(0.12, 1.02, 1., .102))


custom_labels = ['Leakage Power','Dynamic Power','Router Area','Wire Area',]
custom_handles = []
custom_handles.append(ax.bar([0],[0],edgecolor='k',facecolor='none',label=custom_labels[0],hatch='////'))
custom_handles.append(ax.bar([0],[0],edgecolor='k',facecolor='none',label=custom_labels[1],hatch='oooo'))
custom_handles.append(ax.bar([0],[0],edgecolor='k',facecolor='none',label=custom_labels[2],hatch='xxxx'))
custom_handles.append(ax.bar([0],[0],edgecolor='k',facecolor='none',label=custom_labels[3],hatch='....'))

leg2 = ax.legend(custom_handles,custom_labels,ncol=2,loc='upper left')
ax.add_artist(leg1)

outname = f'./dsent_22nm_stacked_globpow_wscop.png'
print(f'writing to {outname}')
plt.savefig(outname,bbox_inches='tight',dpi=800)