
import os

import sys

DATE = 'jul5'



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


# topologies
noi_clks_dict = {'mesh':'4GHz',
            'cmesh':'3.6GHz',
            'cmesh_x':'3.6GHz',
            'dbl_bfly':'2.7GHz',
            'dbl_bfly_x':'2.7GHz',
            'butter_donut_x':'2.7GHz',
            'kite_small':'3.6GHz',
            'kite_medium':'3.0GHz',
            'kite_large':'2.7GHz',
            'ft_x':'3.0GHz',
            'dbl_bfly_x_noci':'2.7GHz',
            'butter_donut_x_noci':'2.7GHz',
            'kite_small_noci':'3.6GHz',
            'kite_medium_noci':'3.0GHz',
            'kite_large_noci':'2.7GHz',
            'mesh_noci':'4GHz',
            'cmesh_x_noci':'3.6GHz',
            # these will match part of name of our files
            '15ll':'3.6GHz',
            '2ll':'3.0GHz',
            '25ll':'2.7GHz',
            's':'3.6GHz',
            'm':'3.0GHz',
            'l':'2.7GHz'}


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



def write_jobscript(n_inst, warmup_inst_num,topology, benchmark,alg_type='mclb',lb_type='hops',all_threads=True,n_evns=4, n_vcs=6,moesi=False):

    # hotfix
    if 'mesh' in topology:
        alg_type = 'naive'


    outfile_name = f'dsent_{benchmark}_{topology}'

    inst_str = name_num_insts(n_inst)


    warmup_inst_str = name_num_insts(warmup_inst_num)


    outdir_name = f'slurm/job_scripts/parsec_dsent/{warmup_inst_str}warmup_{inst_str}simul/'



    outpath = outdir_name + outfile_name



    slurm_out = f'parsec_dsent/dsent_{benchmark}_{topology}_{inst_str}_{DATE}.out'


    # defining what to write
    lines = []

    s = '#!/bin/bash\n'
    lines.append(s)

    s = '#SBATCH --nodes 1\n'
    lines.append(s)

    # s = '#SBATCH --cpus-per-task=2\n'
    # lines.append(s)

    # upping minimum required mem to avoid memory issues
    # gem5 using 32GB so ~45 to be safe
    s = '#SBATCH --mem-per-cpu=10GB\n'
    lines.append(s)

    s = f'#SBATCH --output=slurm/outputs/{slurm_out}\n'
    lines.append(s)

    s = 'cd $SLURM_SUBMIT_DIR\n'
    lines.append(s)

    s='source setup.sh\n'
    lines.append(s)

    top_type = topology
    if '20r' in topology:
        # capture 15ll / 2ll / 25ll portion
        # now 11, 18, 19

        top_type = topology.split('_')[1]
        if top_type == '4p':
            top_type =  topology.split('_')[2]

    if 'ns_' in topology or 'lpbt' in topology:
        top_type = topology.split('_')[1]

    noi_clk = '1.8GHz'
    try:
        noi_clk = noi_clks_dict[top_type]
    except:
        print(f'Key error on topology {topology} w/ key={top_type} for noi freq.')
        quit(-1)

    # simple
    # cmd = f'./build/X86/gem5.fast -d ./outputs/parsec_simplest/{inst_str}/{benchmark}/{topology}/ configs/auto_top/at_fs_2.py --topology FS_wEscapeVCs --noi_routers 20 --noc_clk 1.8GHz --sys-clock 1.8GHz --ruby-clock 1.8GHz --noi_clk {noi_clk} --router_map_file configs/topologies/map_files/{topology}.map --vc_map_file configs/topologies/vc_files/{topology}.vc --nr_map_file configs/topologies/nr_files/{topology}.nr --num-cpus 20 --num-dirs 20 --num-l2caches 20 --benchmark_parsec {benchmark} --checkpoint-dir outputs/parsec_checkpoints/{benchmark}/ --network garnet --routing-algorithm 2 --use_escape_vcs --vcs-per-vnet 4 --vc_deadlock_partition 2 --vc_n_deadlock_free 1 --vc_min_n_deadlock_free 2 --caches --ruby --kernel parsec-disk-image/x86-linux-kernel-4.19.83 --disk-image parsec-disk-image/x86-parsec -r 1 --cpu-type X86TimingSimpleCPU --restore-with-cpu X86TimingSimpleCPU -I {n_inst}'

    # noci
    # cmd = f'./build/X86/gem5.fast -d ./outputs/parsec_noci/{inst_str}/{benchmark}/{topology}/ configs/auto_top/at_fs_2.py --topology FS_NoCI_wEscapeVCs --noi_routers 20 --noc_clk 1.8GHz --sys-clock 1.8GHz --ruby-clock 1.8GHz --noi_clk {noi_clk} --router_map_file configs/topologies/noci_maps/{topology}.map --vc_map_file configs/topologies/vc_files/{topology}.vc --nr_map_file configs/topologies/nr_files/{topology}.nr --num-cpus 64 --num-dirs 16 --num-l2caches 4 --benchmark_parsec {benchmark} --checkpoint-dir outputs/parsec_checkpoints/{benchmark}/ --network garnet --routing-algorithm 2 --use_escape_vcs --vcs-per-vnet 4 --vc_deadlock_partition 0 --vc_n_deadlock_free 1 --vc_min_n_deadlock_free 4 --caches --ruby --kernel parsec-disk-image/x86-linux-kernel-4.19.83 --disk-image parsec-disk-image/x86-parsec  -r 1 --cpu-type X86TimingSimpleCPU --restore-with-cpu X86TimingSimpleCPU -I {n_inst}'

    # noci restore

    # order of these following three matters
    cmd = f'./build/X86/gem5.fast'
    if moesi:
        cmd = f'./build/X86_MOESI_hammer/gem5.fast'

    cmd += f' -d ./parsec_results/dsent_32GB'
    if n_evns is not None:
        cmd += f'_{n_evns}envs'
    if n_vcs != 10:
        cmd == f'_{n_vcs}vcs'

    cmd += f'/{warmup_inst_str}warmup_{inst_str}simul/{benchmark}/{topology}_{alg_type}_{lb_type}/'

    # cmd += f' -d ./paper_outputs/parsec_simplest/{inst_str}/{benchmark}/{topology}/'


    if not all_threads:
        cmd += f' configs/auto_top/auto_top_fs_v2.py'
    else:
        cmd += f' configs/auto_top/auto_top_fs_v3.py'


    # after this, order doesnt matter

    # instructions to simulate
    cmd += f' -I {n_inst}'

    cmd += f' --insts_after_warmup {n_inst}'

    # benchmark
    cmd += f' --benchmark_parsec {benchmark}'

    cmd += f' -r 1'
    # cmd += f' --checkpoint-dir ./parsec_checkpoints/parsec_checkpoints_noci/{benchmark}'

    cmd += f' --checkpoint-dir ./parsec_noci_checkpoints/roi_checkpoint/system_8/{benchmark}'


    cmd += f' --router_map_file configs/topologies/paper_solutions/{topology}.map'

    # topology and clock domains
    simple_name = topology.replace('_noci','')

    # construct vn file name
    vn_dir = 'vn_maps3'
    if 'mesh_noci' in topology:
        vn_dir = 'vn_maps3'
    elif alg_type == 'augmclb':
        vn_dir = 'vn_maps_augmclb'
    elif alg_type == 'mclb':
        vn_dir = 'vn_maps_mclb'

    cmd += f' --flat_vn_map_file configs/topologies/{vn_dir}/{topology}_{alg_type}_{lb_type}'

    if n_evns is not None:
        cmd += f'_{n_evns}vns'
    cmd += '.vn'

    nrl_dir = 'nr_list3'
    if 'mesh_noci' in topology:
        nrl_dir = 'nr_list3'
    elif alg_type == 'augmclb':
        nrl_dir = 'nr_list_augmclb'
    elif alg_type == 'mclb':
        nrl_dir = 'nr_list_mclb'

    cmd += f' --flat_nr_map_file configs/topologies/{nrl_dir}/{topology}_{alg_type}.nrl'

    # cmd += f' --vc_map_file configs/topologies/test_dl/{topology}.vc'
    # cmd += f' --nr_map_file configs/topologies/test_dl/{topology}.nr'

    cmd += f' --topology FS_EscapeVirtualNetworks'
    # cmd += f' --topology EscapeVirtualNetworks'

    # print(f'simple={simple_name}')

    if simple_name == 'mesh' or simple_name =='mesh_noci':
        cmd += f' --noi_routers 64'
    else:
        cmd += f' --noi_routers 20'

    cmd += f' --noc_clk 1.8GHz --sys-clock 1.8GHz --ruby-clock 1.8GHz'

    cmd += f' --noi_clk {noi_clk}'

    # cpu and mem config
    cmd += ' --num-cpus 20 --mem_or_coh mem --num-dirs 16'
    # cmd += ' --num-cpus 64 --mem_or_coh coh --num-dirs 64 --num-l2caches 4 --num_chiplets 4'


    cmd += f' --mem-size 32GB'

    # TODO uncomment for other benchmark types
    cmd += f' --caches'
    cmd += f' --num-l2caches 20 --l2_size 2MB'


    # ruby stuff
    cmd += ' --ruby --network garnet'

    # FS linux stuff
    cmd += f' --kernel parsec_disk_image/vmlinux-5.4.49'

    cmd += f' --disk-image parsec_disk_image/x86-parsec'

    # simulation (restore)
    cmd += f' --cpu-type X86TimingSimpleCPU'

    #cmd += f' --restore-with-cpu X86TimingSimpleCPU'
    # cmd += f' --cpu-type X86O3CPU --restore-with-cpu X86O3CPU'

    cmd += f' --routing-algorithm 2'

    cmd += ' --use_escape_vns'

    cmd += f' --vcs-per-vnet {n_vcs}'

    dl_part = n_vcs - n_evns

    cmd += f' --evn_deadlock_partition {dl_part }'

    cmd += ' --evn_n_deadlock_free 1'

    cmd += f' --evn_min_n_deadlock_free {n_evns}'


    cmd += '\n'

    lines.append(cmd)

    if not os.path.exists(outdir_name):
        os.makedirs(outdir_name)

    print(f'writing {outpath}')

    with open(outpath, 'w+') as of:

        of.writelines(lines)


def main():

    benchmarks = ["blackscholes", "bodytrack", "canneal", "dedup",
                         "facesim", "ferret", "fluidanimate", "freqmine",
                         "raytrace", "streamcluster", "swaptions", "vips", "x264"]


    benchmarks = ["blackscholes",# "canneal",
                        "dedup",
                          "ferret", "streamcluster", "x264"]

    benchmarks = ["freqmine", "raytrace",]

    benchmarks = ["canneal"]

    n_inst = 100000
    try:
        n_inst = int(sys.argv[1])
    except:
        pass

    n_warmup = 100000
    try:
        n_warmup = int(sys.argv[2])
    except:
        pass

    map_files = []
    # map_files_dir = './configs/topologies/map_files/'
    map_files_dir = './configs/topologies/paper_solutions/'
    for root, dirs, files in os.walk(map_files_dir):
        # print(files)
        map_files += files

    topologies = []
    for filename in map_files:
        topo = filename.split('.')[0]

        # filter
        if 'diam' in topo or 'vll' in topo:
            continue
        topologies.append(topo)

    # print(f'topologies={topologies}')


    topologies = [a for a in topologies if a in desired_topologies]

    print(f'topologies={topologies}')
    # quit()

    for bench in benchmarks:
        for topo in topologies:

            write_jobscript(n_inst,n_warmup , topo, bench, moesi=True)


if __name__ == '__main__':
    main()
