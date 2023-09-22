import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


from matplotlib import rc

import csv
import sys


# shortcut
MAX_VAL = 11#7#20#None
MAX_Y = 20
STEP = 0.005

desired_topologies_30r=[
        # '30r_4p_25ll_runsol',
        # '30r_15ll_opt',
        '30r_kite_small',
        '30r_4p_15ll_runsol_ulinks',

        '30r_ft_x',
        '30r_kite_med',
        '30r_4p_2ll_runsol_ulinks',
        '30r_butter_donut_x',
        '30r_dbl_bfly_x',
        '30r_kite_large',
        '30r_4p_25ll_runsol_ulinks',


        # '30r_4p_2ll_runsol',
                # '30r_butter_donut_x',

        ]



rename_dict = {
    # '30r_15ll_opt':'NS-Sym Small',
     '30r_4p_15ll_runsol_ulinks':'NS-LatOp Small',
# '30r_4p_25ll_runsol':'NS-Sym Large',
'30r_4p_25ll_runsol_ulinks':'NS-LatOp Large',
# '30r_4p_2ll_runsol':'NS-Sym Medium',
 '30r_4p_2ll_runsol_ulinks':'NS-LatOp Med',
'30r_butter_donut_x':'Butter Donut', '30r_dbl_bfly_x':'Dbl Butterfly',
'30r_kite_large':'Kite Large', '30r_kite_med':'Kite Med', '30r_kite_small':'Kite Small',
'30r_ft_x':'Folded Torus',
'cmesh_x':'CMesh', 'mesh':'Mesh'}

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

color_dict = {'NS-LatOp Small':'tab:red',
                'NS-BWOp Small':'tab:green',

              'NS-LatOp Med':'tab:red',
              'NS-BWOp Med':'tab:green',

              'NS-LatOp Large':'tab:red',
              'NS-BWOp Large':'tab:green',

              'NS-SCOp Small':'tab:blue',
              'NS-SCOp Med':'tab:blue',
              'NS-SCOp Large':'tab:blue',

            #   'Kite Small':'tab:brown',
              'Kite Small':'lightcoral',
              'LPBT-Power Small':'blueviolet',
              'LPBT-Hops Small':'peru',

            #   'Kite Med':'tab:brown',
              'Kite Med':'lightcoral',
              'LPBT-Hops Med':'peru',
              'Folded Torus':'tab:grey',
            #   'Butter Donut':'lightcoral',
              'Butter Donut':'tab:brown',

              'Dbl Butterfly':'tab:cyan',
            #   'Kite Large':'tab:brown',
              'Kite Large':'lightcoral',

              'CMesh':'gold'
              }

# latop='s'
# bwop='D'
# prev='o'

latop='o'
bwop='o'
prev='D'

label_to_marker={
'NS-LatOp Small':latop,
                'NS-BWOp Small':bwop,

              'NS-LatOp Med':latop,
              'NS-BWOp Med':bwop,
              'NS-LatOp Large':latop,
              'NS-BWOp Large':bwop,

              'Kite Small':prev,
              'Kite Med':prev,
              'Folded Torus':prev,
              'Butter Donut':prev,
              'Dbl Butterfly':prev,
              'Kite Large':prev,

}



topo_to_marker={
'ns_s_latop':latop,
'ns_m_latop':latop,
'ns_l_latop':latop,
'ns_s_bwop':bwop,
'ns_s_scop':bwop,
'20r_4p_15ll_runsol_scbw':bwop,

'ns_m_bwop':bwop,
'ns_m_scop':bwop,
'20r_4p_2ll_runsol_scbw':bwop,

'ns_l_bwop':bwop,
'ns_l_scop':bwop,
'20r_4p_25ll_runsol_scbw':bwop,

'butter_donut_x':prev,
'dbl_bfly_x':prev,
'kite_large':prev,
'kite_medium':prev,
'kite_small':prev,
'ft_x':prev,
'lpbt_s_power':prev,
                'lpbt_s_latop':prev,
                'lpbt_m_latop':prev,
# 'cmesh_x', 'mesh'
}

desired_topologies=[
#     '20r_15ll_opt', '20r_15ll_opt_ulinks',
# '20r_25ll_timed7days', '20r_25ll_timed7days_ulinks',
# '20r_2ll_opt', '20r_2ll_runsol_ulinks',

'kite_small',
'lpbt_s_latop',
'lpbt_s_power',
'ns_s_latop',
# 'ns_s_bwop',
# '20r_4p_15ll_runsol_scbw',
'ns_s_scop',


'ft_x',
'kite_medium',
'lpbt_m_latop',

'ns_m_latop',
# 'ns_m_bwop',

# TODO here
# '20r_4p_2ll_runsol_scbw',
'ns_m_scop',


'butter_donut_x',
'dbl_bfly_x',
'kite_large',
'ns_l_latop',
# 'ns_l_bwop',
# '20r_4p_25ll_runsol_scbw',
'ns_l_scop',




# 'cmesh_x', 'mesh'
]



rename_dict = {
    '20r_15ll_opt':'NS-Sym Small', '20r_15ll_opt_ulinks':'NS-Asym Small',
'20r_25ll_timed7days':'NS-Sym Large', '20r_25ll_timed7days_ulinks':'NS-Asym Large',
'20r_2ll_opt':'NS-Sym Medium', '20r_2ll_runsol_ulinks':'NS-Asym Medium',
'ns_s_latop':'NS-LatOp Small','ns_s_bwop':'NS-BWOp Small',
'ns_m_latop':'NS-LatOp Med','ns_m_bwop':'NS-BWOp Med',
'ns_l_latop':'NS-LatOp Large','ns_l_bwop':'NS-BWOp Large',
'butter_donut_x':'Butter Donut', 'dbl_bfly_x':'Dbl Butterfly',
'kite_large':'Kite Large', 'kite_medium':'Kite Med', 'kite_small':'Kite Small',
'ft_x':'Folded Torus',
'cmesh_x':'CMesh', 'mesh':'Mesh',
    'lpbt_20r_5p_15ll_power_runsol_noci':'LPBT-Power Small',
    'lpbt_20r_5p_15ll_total_hops_runsol_noci':'LPBT-Hops Small',
    'lpbt_20r_5p_2ll_total_hops_runsol_noci':'LPBT-Hops Med',
                'lpbt_s_power':'LPBT-Power Small',
                'lpbt_s_latop':'LPBT-Hops Small',
                'lpbt_m_latop':'LPBT-Hops Med',
                    # '30r_15ll_opt':'NS-Sym Small',
     '30r_4p_15ll_runsol_ulinks':'NS-LatOp Small',
# '30r_4p_25ll_runsol':'NS-Sym Large',
'30r_4p_25ll_runsol_ulinks':'NS-LatOp Large',
# '30r_4p_2ll_runsol':'NS-Sym Medium',
 '30r_4p_2ll_runsol_ulinks':'NS-LatOp Med',
'30r_butter_donut_x':'Butter Donut', '30r_dbl_bfly_x':'Dbl Butterfly',
'30r_kite_large':'Kite Large', '30r_kite_med':'Kite Med', '30r_kite_small':'Kite Small',
'30r_ft_x':'Folded Torus',
'cmesh_x':'CMesh', 'mesh':'Mesh',

'20r_4p_15ll_runsol_scbw':'NS-SCOp Small',
'20r_4p_2ll_runsol_scbw':'NS-SCOp Med',
'20r_4p_25ll_runsol_scbw':'NS-SCOp Large',


'ns_s_scop':'NS-SCOp Small',
'ns_m_scop':'NS-SCOp Med',
'ns_l_scop':'NS-SCOp Large',

}


def gen_synth_20r_3subplots(infile_name='./synth_outputs/simple_2b.csv', param_mem_or_coh='coh',param_alg='cload'):

    print(f'reading from {infile_name}')
    # input('press any key')

    data = {}
    configs = []

    with open(infile_name, 'r') as inf:
        csv_inf = csv.reader(inf)

        headers = []

        time_axis = []

        for line in csv_inf:

            if len(headers) == 0:
                headers = line
                continue

            if '' in line:
                line.remove('')

            # if 'coh' in line:
            #     continue


            # print(f'{line}')
            # quit()


            mem_or_coh = line[2]
            config = line[4]
            alg = line[3]

            # new order
            config = line[3]

            # diff between original script
            config = config.replace('_noci','')

            alg = line[4]


            # if param_alg not in alg:
            #     print(f'{param_alg} not in {alg}')
            #     continue


            inj_rate_str = line[5]
            # inj_rate_str = line[4]

            try:
                pkt_lat_str = line[6]
                # pkt_lat_str = line[5]
            except:
                pkt_lat_str = '100000000.0'
                # pkt_lat_str = '0'

            configs.append(config)

            # hotfix
            if len(inj_rate_str) == 3:
                inj_rate_str = inj_rate_str + '0'

            inj_rate = float(inj_rate_str.split('_')[-1])
            factor = 100
            
            if len(inj_rate_str.split('_')[-1]) >= 3:
                # print(f'odd')
                factor = 1000

            inj_rate = inj_rate / factor

            # parse and convert to ns
            pkt_lat = float(pkt_lat_str) / 1000.0

            # init
            try:
                _ = data[mem_or_coh]
            except:
                data.update({mem_or_coh : {} })

            try:
                _ = data[mem_or_coh][config]
            except:
                data[mem_or_coh].update({config : {}})

            data[mem_or_coh][config].update({inj_rate : pkt_lat})



    for memcoh, config_data_dict in data.items():
        # if memcoh == 'coh':
            # continue
        print(f'{memcoh}')
        for config,inj_data_dict in config_data_dict.items():
            print(f'\t{config}')
            for ir, pl in inj_data_dict.items():
                print(f'\t\t{ir} : {pl}')

    # quit()

    ######################################################################################

    plt.cla()
    # plt.clear()
    plt.rc('font', size=16) #controls default text size
    plt.rc('axes', titlesize=14) #fontsize of the title
    plt.rc('axes', labelsize=14) #fontsize of the x and y labels
    plt.rc('xtick', labelsize=10) #fontsize of the x tick labels
    plt.rc('ytick', labelsize=10) #fontsize of the y tick labels
    plt.rc('legend', fontsize=12)


    plt.rc('text', usetex=True)

    fig = plt.figure(figsize=(7,4))

    axes = []
    axes.append(fig.add_subplot(3,1,1))
    axes.append(fig.add_subplot(3,1,2))
    axes.append(fig.add_subplot(3,1,3))



    # for memcoh, config_data_dict in data.items():
    #     print(f'{memcoh}')
    #     for config,inj_data_dict in config_data_dict.items():
    #         print(f'\t{config}')
    #         for ir, pl in inj_data_dict.items():
    #             print(f'\t\t{ir} : {pl}')


    config_data_dict = data[param_mem_or_coh]
    # for config,inj_data_dict in config_data_dict.items():
    #     if config not in desired_topologies:
    #         print(f'config {config} not in desired {desired_topologies}')
    #         continue

    mylabels = []


    max_x = .2

    for config in desired_topologies:
        try:
            inj_data_dict = config_data_dict[config]
        except:
            continue
        # print(f'\t{config}')
        injs = []
        lats = []

        max_val = len(inj_data_dict)

        # print(f'max_val={max_val}')
        # quit()

        if MAX_VAL is not None:
            max_val = MAX_VAL

        # print(f'({len(inj_data_dict)}) {inj_data_dict}')
        # quit()

        # X = [i/100.0 for i in range(1,max_val+1)]

        step = STEP

        X = [round(x,3) for x in np.arange(0.005,(max_val+1)/100.0,step)]

        for x in X:
            injs.append(x)

            try:
                lat = inj_data_dict[x]
            
            # no data point
            except:
                lat = 100000
                #lat = 0

            lats.append(lat)

        max_x = max(X)

        # for ir, pl in inj_data_dict.items():
            # print(f'\t\t{ir} : {pl}')



            # injs.append(ir)
            # lats.append(pl)

        # small
        size = 0
        if '_m_' in config:
            size = 1
        elif 'ft_x' in config:
            size = 1
        elif 'med' in config:
            size = 1
        elif '_l_' in config:
            size = 2
        elif 'dbl' in config or 'butt' in config:
            size = 2
        elif 'large' in config:
            size = 2
        elif '2ll' in config:
            size = 1
        elif '25ll' in config:
            size = 2

        print(f'{config} : size={size}')


        new_name = rename_dict[config]
        mylabels.append(new_name)
        mark = topo_to_marker[config]
        col = color_dict[new_name]



        sorted_lats = [x for _,x in sorted(zip(injs,lats))]
        sorted_injs= [x for x,_ in sorted(zip(injs,lats))]


        # print(f'plotting {sorted_injs} : {sorted_lats}')
        print(f'plotting {sorted(zip(injs,lats))}')

        # plt.plot(injs, lats, label=new_name,linestyle='--',marker=mark, markersize=5,color=col)
        axes[size].plot(sorted_injs, sorted_lats, label=new_name,linestyle='--',marker=mark, markersize=5,color=col)

    # print(f'my_labels={mylabels}')
    # quit()

    y = np.arange(0.0,36,10)
    y_minor = np.arange(0.0,35,5)

    for ax in axes:
        ax.set_yticks(y)
        ax.set_yticks(y_minor,minor=True)




    x = np.arange(0,.34,.05)
    xmin = np.arange(0,.4,.01)

    # axes[2].set_xticks(x)
    # axes[2].set_xticks(xmin,minor=True)

    # max_x = .4
    max_y = 40.0

    if MAX_Y is not None:
        max_y = MAX_Y

    for ax in axes:

        ax.set_xticks(x)
        ax.set_xticks(xmin,minor=True)

        # plt.grid(which='major',alpha=0.5)
        # plt.grid(which='minor',alpha=0.2)
        # plt.ylim([6, 22.5])
        # plt.xlim([0.0, 0.18])
        ax.grid(which='major',alpha=0.5)
        ax.grid(which='minor',alpha=0.2)
        ax.set_ylim([0, max_y ])
        ax.set_xlim([0.0, max_x])

    axes[1].set_xticklabels([])
    axes[0].set_xticklabels([])

    axes[2].set_xlabel("Injection Rate  (pkts/cpu/cycle)")
    axes[1].set_ylabel("Avg. Pkt. Latency (ns)")
    # plt.grid()

    twins = []
    for ax in axes:
        twins.append(ax.twinx())

    twins[0].set_ylabel('Small')
    twins[1].set_ylabel('Medium')
    twins[2].set_ylabel('Large')
    twins[0].set_yticklabels([])
    twins[1].set_yticklabels([])
    twins[2].set_yticklabels([])

    labels = []
    handles = []
    for ax in axes:
        _handles, _labels = ax.get_legend_handles_labels()
        for h in _handles:
            handles.append(h)
        for l in _labels:
            labels.append(l)



    # handles, labels = ax.get_legend_handles_labels()

    proxy0 = plt.plot([],[],color='none',label=' ')
    proxy7 = plt.plot([],[],color='none',label=' ')
    proxy14 = plt.plot([],[],color='none',label=' ')

    # proxy8 = plt.plot([],[],color='none',label=' ')
    # proxy9 = plt.plot([],[],color='none',label=' ')


    handles.insert(0,proxy0[0])
    handles.insert(6,proxy7[0])
    handles.insert(12,proxy14[0])
    # handles.insert(7,proxy7[0])
    # handles.insert(14,proxy14[0])

    # handles.insert(4,proxy4[0])
    # handles.insert(8,proxy8[0])
    # handles.insert(9,proxy9[0])
    # # print(proxy3)

    # # print(handles)
    # # quit()

    labels.insert(0,r'\underline{Small}')
    labels.insert(6,r'\underline{Medium}')
    labels.insert(12,r'\underline{Large}')
    # labels.insert(7,r'\underline{Medium}')
    # labels.insert(14,r'\underline{Large}')

    # # handles, labels = ax.get_legend_handles_labels()

    # proxy0 = plt.plot([],[],color='none',label=' ')
    # proxy6 = plt.plot([],[],color='none',label=' ')
    # proxy12 = plt.plot([],[],color='none',label=' ')

    # # proxy8 = plt.plot([],[],color='none',label=' ')
    # # proxy9 = plt.plot([],[],color='none',label=' ')


    # handles.insert(0,proxy0[0])
    # handles.insert(6,proxy6[0])
    # handles.insert(12,proxy12[0])

    # # handles.insert(4,proxy4[0])
    # # handles.insert(8,proxy8[0])
    # # handles.insert(9,proxy9[0])
    # # # print(proxy3)

    # # # print(handles)
    # # # quit()

    # labels.insert(0,r'\underline{Small}')
    # labels.insert(6,r'\underline{Medium}')
    # labels.insert(12,r'\underline{Large}')

    # labels.insert(4,' ')
    # labels.insert(8,' ')
    # labels.insert(9,' ')



    # plt.legend(mylabels,ncol=3, bbox_to_anchor=(-0.1, 1.0, 1., .102), loc='lower left')


    print(f'handles={handles}')
    print(f'labels={labels}')

    if True:#param_mem_or_coh == 'coh':
        axes[0].legend(handles, labels,ncol=3,bbox_to_anchor=(-0.07, 1.05, 0.2, 0.1), loc='lower left', )


    name = f'./synth_outputs/graphs/noci_84r_{param_mem_or_coh}_{param_alg}.png'
    plt.savefig(name,bbox_inches='tight',dpi=900)
    print(f'wrote to {name}')


def main():



    try:
        memcoh = sys.argv[2]
    except:
        memcoh ='coh'

    try:
        alg = sys.argv[3]

    except:
        alg = 'naive'

    in_name = sys.argv[1]
    gen_synth_20r_3subplots(infile_name = in_name, param_mem_or_coh=memcoh, param_alg=alg)

    # try:

    #     # gen_synth_30r_3subplots(infile_name=in_name,param_mem_or_coh=memcoh)
    # except:
    #     gen_synth_20r_3subplots(param_mem_or_coh=memcoh)
    #     # gen_synth_30r_3subplots(param_mem_or_coh=memcoh)


    # gen_synth_20r_coh(infile_name = in_name)

    # gen_synth_30r_mem()
    #gen_synth_30r()
    pass


if __name__ == '__main__':
    main()
