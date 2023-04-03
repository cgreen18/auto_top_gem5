
import os
import sys


# topos for parsec

desired_topologies=[

    'ns_s_latop','ns_s_bwop',
    'ns_m_latop','ns_m_bwop',
    'ns_l_latop','ns_l_bwop',

    'ft_x_noci',

    'butter_donut_x_noci', 'dbl_bfly_x_noci',

    'kite_large_noci', 'kite_medium_noci', 
    'kite_small_noci',

    'cmesh_x_noci', 'mesh_noci'
    ]

# desired_topologies = ['ft_x_noci']

def name_num_insts(sc):
    try:
        sc = int(sc)
    except:
        pass

    # if 3 digits at k level
    if sc // 1000 < 1000:
        return f'{sc//1000}k'
    #
    elif sc // 1000000 < 1000:
        return f'{sc//1000000}m'
    else:
        return f'{sc//1000000000}b'


def main():

    benchmarks = ["blackscholes", "bodytrack", "canneal", "dedup",
                         "facesim", "ferret", "fluidanimate", "freqmine",
                         "raytrace", "streamcluster", "swaptions", "vips", "x264"]



    benchmarks = ["blackscholes", "bodytrack",
                         "facesim", "ferret", "freqmine",
                         "raytrace", "streamcluster",
                         "dedup",  "x264"]

    # benchmarks = ["facesim",
    #                      "raytrace", ]


    # filename = run_{description}_noci_{inst_str}.sh
    # description = 'x264'
    # description = 'allbutx264'
    description = 'all'
    # description = '4vc3escape'
    description = 'injejallvcs'
    description = 'ft_2mb_20m'
    description = 'cload'

    n_inst = 100000
    try:
        n_inst = int(sys.argv[1])
    except:
        pass
    inst_str = name_num_insts(n_inst)

    map_files = []
    # map_files_dir = './configs/topologies/map_files/'
    map_files_dir = './configs/topologies/paper_solutions/'
    for root, dirs, files in os.walk(map_files_dir):
        # print(files)
        map_files += files

    map_files = [e for e in map_files if 'noci' in e]

    topologies = []
    for filename in map_files:
        topo = filename.split('.')[0]


        topologies.append(topo)

    # topologies = [a for a in topologies if a in desired_topologies]
    # topologies = [a for a in topologies if '20r' in a]

    print(f'topologies={topologies}')
    # quit()

    alg_types = ['cload']
    lb_types = ['hops']


    jobscripts = []
    for bench in benchmarks:
        for topo in topologies:
            for a_t in alg_types:
                for l_b in lb_types:
                    jobscripts.append(f'{bench}_{topo}_{a_t}_{l_b}')
                    # jobscripts.append(f'{bench}_{topo}_4vc3escape')


    # defining what to write
    lines = []

    s = '#!/bin/bash\n'
    lines.append(s)

    s = 'TLIM="20-00:00:00"\n'
    lines.append(s)

    cpu_freqs= [i/10 for i in range(18,30,3)]

    cpu_freqs =[1.8]

    l2_sizes = ['250kB','500kB','2MB']
    l2_sizes = ['500kB']

    for js in jobscripts:
        for cf in cpu_freqs:
            for l2s in l2_sizes:
                clk_str = f'{cf}GHz'.replace('.','')
                s = f'sbatch --exclude=mnemosyne -t $TLIM slurm/job_scripts/parsec_noci_largemem_{clk_str}_{l2s}/{inst_str}/{js}\n'
                # s = f'sbatch --exclude=mnemosyne -t $TLIM slurm/job_scripts/parsec_noci_largemem/{inst_str}/{js}\n'

                lines.append(s)

    print(lines)

    name = f'slurm/run_scripts/run_{description}_noci_{inst_str}.sh'
    with open(name, 'w+') as of:
        of.writelines(lines)

    print(f'\nWrote to: {name}')



if __name__ == '__main__':
    main()
