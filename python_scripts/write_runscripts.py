
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

    # benchmarks = ["blackscholes", "bodytrack", "canneal", "dedup",
    #                      "facesim", "ferret", "fluidanimate", "freqmine",
    #                      "raytrace", "streamcluster", "swaptions", "vips", "x264"]

    # important ones, in order
    benchmarks = [ "canneal", "bodytrack",
                        "swaptions", "fluidanimate",
                        "facesim", "raytrace"]

    # all, important in order, others not
    benchmarks = [ "canneal", "bodytrack",
                        "swaptions", "fluidanimate",
                        "facesim", "raytrace",
                        "blackscholes", "dedup",
                        "ferret",  "freqmine",
                        "streamcluster", "vips", "x264"]



    benchmarks = [ "canneal", "bodytrack",
                        "streamcluster", "vips", 
                        "swaptions", "fluidanimate",
                        "facesim", "raytrace",
                        
                        "ferret",  "freqmine",
                        "blackscholes", 
                        "dedup","x264"
                        ]

    # benchmarks = [ "dedup",
    #                      "swaptions", "vips", "x264"]

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

    description = 'repeated_benchmarks'

    description = 'bsorm_w_warmup'

    description = '4reps_8evns_cload'

    description = '9evns_bsorm_cload'

    # description = 'timing_simple_picky_small_cload_4reps'
    description = 'mesh_all_clk_o3_simple_cload_4reps'

    description = 'cload_picky_4reps_8evns_fast_smallL2'

    description = 'small_bits_and_cache'

    description = 'last_second_10m_8reps'

    niceness = 5

    n_inst = 100000000
    try:
        n_inst = int(sys.argv[1])
    except:
        pass
    inst_str = name_num_insts(n_inst)

    n_warmup = 100000000
    try:
        n_warmup = int(sys.argv[2])
    except:
        pass
    warm_str = name_num_insts(n_warmup)

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
    # topologies = [a for a in topologies if 'small' in a or '_s_' in a or 'mesh' in a]
    # topologies = [a for a in topologies if 'med' in a or '_m_' in a ]

    #topologies = [a for a in topologies if 'cmesh' not in a]

    # topologies = [a for a in topologies if 'cmesh' not in a]

    # topologies = [a for a in topologies if 'small' in a or '_l_' in a or 'mesh' in a or '_m_' in a]

    print(f'topologies={topologies}')
    # quit()

    # alg_types = ['naive','cload','bsorm']

    alg_types = ['cload_picky']#,'bsorm_picky']

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

    s = 'TLIM="16-00:00:00"\n'
    lines.append(s)

    s = f'NICE={niceness}\n'
    lines.append(s)

    cpu_freqs= [i/10 for i in range(18,30,3)]

    cpu_freqs =[1.8]

    l2_sizes = ['250kB','500kB','2MB']
    l2_sizes = ['500kB']
    l2_sizes = ['2MB']
    n_l2s = 64

    reps = 8
    n_evns = 8
    tot_vcs = 10
    # is_picky = True

    use_simple = [False]
    all_threads = True
    link_widths = [None]#[32,64]
    router_lat = None

    for js in jobscripts:
        for cf in cpu_freqs:
            for l2s in l2_sizes:
                for us in use_simple:
                    for lw in link_widths:
                        clk_str = f'{cf}GHz'.replace('.','')
                        # s = f'sbatch --exclude=mnemosyne -t $TLIM slurm/job_scripts/parsec_noci_largemem_{clk_str}/{inst_str}/{js}\n'

                        js_path = f'slurm/job_scripts/parsec_noci_32GBxDDR4_l2caches'

                        if reps is not None:
                            js_path += f'_{reps}reps'
                        if n_evns is not None:
                            js_path += f'_{n_evns}evns'
                        if tot_vcs != 10:
                            js_path += f'_{tot_vcs}vcs'
                        # if is_picky:
                        #     js_path += '_picky'

                        js_path += f'_{clk_str}_{l2s}'

                        if n_l2s == 4:
                            js_path += f'x{n_l2s}'

                        if us:
                            js_path += f'_timingsimple'

                        if all_threads:
                            js_path += f'_allthreads'

                        if lw is not None:
                            js_path += f'_{lw}lwidth'

                        if router_lat is not None:
                            js_path += f'_{router_lat}rlat'

                        js_path += f'/{warm_str}warmup_{inst_str}simul/{js}'

                        s = f'sbatch --exclude=mnemosyne --nice=$NICE -t $TLIM {js_path}\n'




                        # s = f'sbatch --exclude=mnemosyne -t $TLIM slurm/job_scripts/parsec_noci_largemem/{inst_str}/{js}\n'

                        lines.append(s)

    print(lines)

    name = f'slurm/run_scripts/run_{description}_noci_{inst_str}.sh'
    with open(name, 'w+') as of:
        of.writelines(lines)

    print(f'\nWrote to: {name}')



if __name__ == '__main__':
    main()
