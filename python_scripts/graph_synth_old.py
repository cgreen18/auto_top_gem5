import csv
from operator import xor
# import matplotlib
import matplotlib.pyplot as plt
import sys

global file_name
file_name = 'synth_outputs/csvs/experiment_per_topo.csv'

global out_fig_name
out_fig_name = 'synth_outputs/graphs/per_topo.png'

metrics = ['average_flit_latency']
metrics = ['average_packet_latency']


kite_paper_topologies = ['kite_small', 'butter_donut_x', 'cmesh',
'cmesh_x', 'dbl_bfly', 'kite_large', 'kite_medium', 'mesh']

ours_simple = ['20r_15ll_opt','20r_2ll_opt','20r_25ll_timed3days',]

ours_constrained = [


'20r_15ll_opt_whop_8bw_4diam', '20r_15ll_opt_whop_8bw_4diam_ulinks',
'20r_15ll_opt_whop_ulinks',

'20r_2ll_timed3days_10bw_4diam',
'20r_2ll_timed3days_10bw_4diam_ulinks', '20r_2ll_timed3days_12bw_4diam_ulinks',
'20r_2ll_timed3days', '20r_25ll_timed3days_12bw_4diam', '20r_25ll_timed3days_12bw_4diam_ulinks',

'20r_25ll_timed3days_ulinks', '20r_25ll_timed3days_whop'
]

desired_topologies = kite_paper_topologies + ours_simple

desired_topologies=[\
#     '20r_15ll_opt', '20r_15ll_opt_ulinks',
# '20r_25ll_timed7days', '20r_25ll_timed7days_ulinks',
# '20r_2ll_opt', '20r_2ll_runsol_ulinks',

'butter_donut_x', 'dbl_bfly_x',
'kite_large', 'kite_medium', 'kite_small',
# 'cmesh_x', 'mesh',
'ft_x',
'ns_s_latop','ns_s_bwop',
'ns_m_latop','ns_m_bwop',
'ns_l_latop','ns_l_bwop',
'lpbt_s_latop','lpbt_s_power',
'lpbt_m_latop']

global leg_labels
leg_labels = []

global topologies
topologies = []


# {'same'/'mixed': {'mem'/'coh': {'topology': {'inj_rate' : [average_flit_latency] } } } }

global data
data = {}

def parse_row(row):

    global data
    global topologies

    if_same_mixed = row['mixed_or_same']
    try:
        data[if_same_mixed]
    except:
        data.update({if_same_mixed : {}})

    if_mem_coh = row['mem_or_coh']
    try:
        data[if_same_mixed][if_mem_coh]
    except:
        data[if_same_mixed].update({if_mem_coh : {}})

    config = row['config']
    if config not in topologies:
        topologies.append(config)
    try:
        data[if_same_mixed][if_mem_coh][config]
    except:
        data[if_same_mixed][if_mem_coh].update({config : {}})
    
    inj_rate = row['inj_rate']
    inj_rate = float(inj_rate.replace('_','.'))
    try:
        data[if_same_mixed][if_mem_coh][config][inj_rate]
    except:
        data[if_same_mixed][if_mem_coh][config].update({inj_rate : []})

    for metric in metrics:
        val = row[metric]


        try:
            val = float(val)
        except:
            val = None

        data[if_same_mixed][if_mem_coh][config][inj_rate].append(val)

    # print(f'row={row} : {val}')
    

def parse_synth_data_():
    global data

    local_data = {}

    print(f'Opening {file_name}')

    with open(file_name, 'r') as file:
        csv_file = csv.DictReader(file)

        print('opened')

        for row in csv_file:
            # print(row)

            parse_row(row)


    # print(data)

# quick = ['20r_15ll_opt','20r_2ll_opt','20r_25ll_timed3days']




# data_dict = { tops : {inj_rates (num) : avg_flit_lat (num)} }
def plot_a_subplot(data_dict, ax, memcoh):
    global leg_labels

    for top, inj_lat_dict in data_dict.items():
        if top not in desired_topologies:
            continue

        print(f'top={top}, inj_lat_dcit={inj_lat_dict}')
        ax = plot_a_top_on_subplot(top, inj_lat_dict, ax, memcoh)


    leg_labels = ax.get_legend_handles_labels()
    # print(f'leg_lables={leg_labels}')
    # input('cont?')

    return ax



# data_dict = {inj_rates (num) : avg_flit_lat (num)}
def plot_a_top_on_subplot(top, data_dict, ax, cohmem):

    if len(data_dict) == 0:
        return

    # sort

    sort_keys = [k for k in data_dict.keys()]
    sort_keys.sort()

    x = sort_keys
    y = [data_dict[k] for k in sort_keys]

    ax.scatter(x, y, marker = '+', label=top)
    # ax.plot(x, y, marker = '+', label=top)

    if cohmem == 'mem':
        x_range = [0.01,0.15]
        y_range = [5000,20000]
    else:
        x_range = [0.01,0.19]
        y_range = [5000,20000]



    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    return ax




def plot_all_synth_traffic():

    
    # {'same'/'mixed': {'mem'/'coh': {'topology': {'inj_rate' : [average_flit_latency] } } } }

    row = 0
    col = 1

    n_rows = 2
    n_cols = 3

    fig, axes = plt.subplots(n_rows, n_cols)
    for sm in ['same','mixed']:
        for mc in ['mem','coh']:

            print(f'row={row}, col={col}')


            this_ax = axes[row][col]

            # one graph here
            try:
                topology_data_dict = data[sm][mc]
            except:
                continue
            # data_dict = { tops : {inj_rates (num) : avg_flit_lat (num)} }
            this_ax = plot_a_subplot(topology_data_dict, this_ax, mc)

            plt.subplot(this_ax)
            # plt.show()

            # for top, top_data in topology_data_dict.items():
            #     skip_top = False

            #     this_data = {}

            #     if '20r' in top:
            #         if top not in quick:
            #             skip_top = True

            #     inj_vals = top_data.keys()
            #     x = [float(v.replace('_','.')) for v in inj_vals]

            #     y = []

            #     for val_list in top_data.values():
            #         for val in val_list:
            #             try:
            #                 y.append(float(val))
            #             except:
            #                 print(f'val_list={val_list}')
            #                 print(f'top={top}')
            #                 skip_top = True

            #     if skip_top:
            #         continue

            #     for i in range(len(x)):
            #         key = x[i]
            #         val = y[i]
                    
            #         if key < .1:
                    
            #             this_data.update({key:val})



            #     print(f'x={x}')
            #     print(f'y={y}')



            #     plt.scatter(this_data.keys(),this_data.values(),label=top)
            #     # plt.plot(x,y,label=top, marker="+")

            #     leg_labels = plt.gca().get_legend_handles_labels()
                


            
            if col == n_cols -1:
                col = 0
                row += 1

            col += 1
    plt.subplot(n_rows, n_cols,1)
    # plt.legend()#loc = 'upper left')
    plt.legend(leg_labels[0],leg_labels[1])
    plt.savefig(out_fig_name,dpi=1000,bbox_inches='tight')
    print(f'wrote to {out_fig_name}')
    plt.show()
    

                # input('next?')


def main():

    global file_name
    global out_fig_name

    if sys.argv[1]:
        file_name = sys.argv[1]

    if sys.argv[2]:
        out_fig_name = sys.argv[2]



    parse_synth_data_()

    print(f'data({len(data)})={data}')

    quit()

    plot_all_synth_traffic()

if __name__ == '__main__':
    main()