
import os
import sys

DATE = '_nov10'


# topos for parsec

desired_topologies=[\
#     '20r_15ll_opt', '20r_15ll_opt_ulinks',
# '20r_25ll_timed7days', '20r_25ll_timed7days_ulinks',
# '20r_2ll_opt', '20r_2ll_runsol_ulinks',

'butter_donut_x', 'dbl_bfly_x',
'kite_large', 'kite_medium', 'kite_small',
'cmesh_x', 'mesh',
'ft_x',
'ns_s_latop','ns_s_bwop','ns_s_scop',
'ns_m_latop','ns_m_bwop','ns_m_scop',
'ns_l_latop','ns_l_bwop','ns_l_scop',
'lpbt_s_latop','lpbt_s_power',
'lpbt_m_latop'
]

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

    benchmarks = ["blackscholes", #"canneal",
    "dedup",
                         "ferret",
                  "streamcluster", "x264"]

    # benchmarks = [ "raytrace"]

    benchmarks = ["canneal"]

    tlim_days = 2

    # filename = run_{description}_{inst_str}.sh
    # description = 'x264'
    # description = 'allbutx264'
    description = 'all'
    # description = '4vc3escape'
    description = 'dsent_scop'

    n_inst = 100000
    try:
        n_inst = int(sys.argv[1])
    except:
        pass
    inst_str = name_num_insts(n_inst)

    n_warmup_inst = 100000
    try:
        n_warmup_inst = int(sys.argv[2])
    except:
        pass

    warmup_inst_str = name_num_insts(n_warmup_inst)

    map_files = []
    # map_files_dir = './configs/topologies/map_files/'
    map_files_dir = './configs/topologies/paper_solutions/'
    for root, dirs, files in os.walk(map_files_dir):
        # print(files)
        map_files += files

    # map_files = [e for e in map_files if 'mesh' in e]

    topologies = []
    for filename in map_files:
        topo = filename.split('.')[0]

        # filter
        if 'diam' in topo or 'vll' in topo:
            continue
        topologies.append(topo)

    topologies = [a for a in topologies if a in desired_topologies]

    topologies = [a for a in topologies if 'scop' in a]


    print(f'topologies={topologies}')
    # quit()

    jobscripts = []
    for bench in benchmarks:
        for topo in topologies:
            jobscripts.append(f'dsent_{bench}_{topo}')
            # jobscripts.append(f'{bench}_{topo}_4vc3escape')


    # defining what to write
    lines = []

    s = '#!/bin/bash\n'
    lines.append(s)

    s = f'TLIM="{tlim_days}-00:00:00"\n'
    lines.append(s)

    for js in jobscripts:
        s = f'sbatch -t $TLIM slurm/job_scripts/parsec_dsent/{inst_str}warmup_{warmup_inst_str}simul/{js}\n'
        lines.append(s)

    print(lines)

    name = f'slurm/run_scripts/run_{description}_parsec_dsent_{inst_str}.sh'
    with open(name, 'w+') as of:
        of.writelines(lines)


    print(f'wrote {name}')

if __name__ == '__main__':
    main()
