
import os

import sys

DATE = 'mar20'


# topologies
noi_clks_dict = {'mesh':'4GHz',
            'cmesh':'3.6GHz',
            'cmesh_x':'3.6GHz',
            'dbl_bfly':'2.7GHz',
            'dbl_bfly_x':'2.7GHz',
            'butter_donut_x':'2.7GHz',
            'kite_small':'3.6GHz',
            'kite_medium':'3.0GHz',
            'ft_x_noci':'3.0GHz',
            'kite_large':'2.7GHz',
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
            '25ll':'2.7GHz'}


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



def write_jobscript(n_inst, topology, alg_type, lb_type, benchmark, cpu_clk, l2_size):


    outfile_name = f'{benchmark}_{topology}_{alg_type}_{lb_type}'

    inst_str = name_num_insts(n_inst)


    clk_str = f'{cpu_clk}GHz'.replace('.','')

    # outdir_name = f'slurm/job_scripts/parsec_noci_largemem_4GHzcpu_500MBL2/{inst_str}/'
    # outdir_name = f'slurm/job_scripts/parsec_noci_largemem/{inst_str}/'
    outdir_name = f'slurm/job_scripts/parsec_noci_largemem_{clk_str}_{l2_size}/{inst_str}/'


    outpath = outdir_name + outfile_name

    # slurm_out = f'parsec_noci/{benchmark}_{topology}_{inst_str}_4GHzcpu_500MBL2{DATE}.out'
    slurm_out = f'parsec_noci/{benchmark}_{topology}_{alg_type}_{lb_type}_{inst_str}_{clk_str}_{l2_size}_{DATE}.out'
    # defining what to write
    lines = []

    s = '#!/bin/bash\n'
    lines.append(s)

    s = '#SBATCH --nodes 1\n'
    lines.append(s)

    s = '#SBATCH --cpus-per-task=1\n'
    lines.append(s)

    # upping minimum required mem to avoid memory issues
    # gem5 using 32GB so ~45 to be safe
    s = '#SBATCH --mem-per-cpu=45GB\n'
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

    noi_clk = '1.8GHz'
    try:
        noi_clk = noi_clks_dict[top_type]
    except:
        print(f'Key error on topology {topology} w/ key={top_type} for noi freq.')
        # quit(-1)

    # noci restore

    # order of these following three matters
    cmd = f'./build/X86/gem5.fast'


    # output dir
    # cmd += f' -d ./paper_outputs/parsec_noci_largemem_4GHzCPU_500MBL2/{inst_str}/{benchmark}/{topology}/'
    cmd += f' -d ./parsec_results/parsec_noci_largemem_{clk_str}_{l2_size}/{inst_str}/{benchmark}/{topology}_{alg_type}_{lb_type}/'
    # cmd += f' -d ./paper_outputs/parsec_noci_largemem/{inst_str}/{benchmark}/{topology}/'

    cmd += f' configs/auto_top/auto_top_fs.py'

    # after this, order doesnt matter

    # instructions to simulate
    cmd += f' -I {n_inst}'

    # benchmark
    cmd += f' --benchmark_parsec {benchmark}'

    cmd += f' -r 1'
    # cmd += f' --checkpoint-dir ./parsec_checkpoints/parsec_checkpoints_noci/{benchmark}'

    cmd += f' --checkpoint-dir ./parsec_checkpoints/largemem/{benchmark}'


    cmd += f' --router_map_file configs/topologies/paper_solutions/{topology}.map'

    # topology and clock domains
    simple_name = topology.replace('_noci','')

    # cmd += f' --vc_map_file configs/topologies/paper_vcs_noci/{simple_name}.vc'
    # cmd += f' --nr_map_file configs/topologies/paper_nrs_noci/{simple_name}.nr'

    cmd += f' --flat_vn_map_file configs/topologies/vn_maps/{topology}_{alg_type}_{lb_type}.vn'
    cmd += f' --flat_nr_map_file configs/topologies/nr_list/{topology}_{alg_type}.nrl'

    # cmd += f' --vc_map_file configs/topologies/test_dl/{topology}.vc'
    # cmd += f' --nr_map_file configs/topologies/test_dl/{topology}.nr'

    cmd += f' --topology FS_NoCI_EscapeVirtualNetworks'


    # print(f'simple={simple_name}')

    if simple_name == 'mesh' or simple_name =='mesh_noci':
        cmd += f' --noi_routers 64'
    else:
        cmd += f' --noi_routers 20'
    
    # cmd += f' --noc_clk 3.0GHz --sys-clock 3.0GHz --ruby-clock 3.0GHz'


    cmd += f' --noc_clk {cpu_clk}GHz --sys-clock {cpu_clk}GHz --ruby-clock {cpu_clk}GHz'

    # cmd += f' --noc_clk 4.0GHz --sys-clock 4.0GHz --ruby-clock 4.0GHz'


    cmd += f' --noi_clk {noi_clk}'

    # cpu and mem config
    # cmd += ' --num-cpus 64 --mem_or_coh mem --num-dirs 16 --num-l2caches 4 --num_chiplets 4'
    cmd += ' --num-cpus 64 --mem_or_coh mem --num-dirs 16'
    
    cmd += f' --num-l2caches 64 --l2_size {l2_size} --num_chiplets 4'
    # cmd += ' --num-l2caches 64 --num_chiplets 4'
    # cmd += ' --num-cpus 64 --mem_or_coh coh --num-dirs 64 --num-l2caches 4 --num_chiplets 4'

    cmd += ' --mem-size 32GB'

    # ruby stuff
    cmd += ' --caches --ruby --network garnet'

    # FS linux stuff
    # x264 bodytrack facesim
    
    # these were taken with a different kernel. shouldnt matter but just in case
    if  benchmark == 'bodytrack' or benchmark == 'facesim':
        cmd += f' --kernel parsec_disk_image/vmlinux-5.4.49'
    elif benchmark == 'x264' or benchmark == 'dedup':
        cmd += f' --kernel parsec_disk_image/x86-linux-kernel-4.19.83'
    else:
        cmd += f' --kernel parsec_disk_image/vmlinux-4.4.186'

    cmd += f' --disk-image parsec_disk_image/x86-parsec'

    # simulation (restore)
    # cmd += f' --cpu-type X86TimingSimpleCPU --restore-with-cpu X86TimingSimpleCPU'
    cmd += f' --cpu-type X86O3CPU --restore-with-cpu X86O3CPU'

    # cmd += f' --garnet-deadlock-threshold 5000000'

    cmd += f' --routing-algorithm 2'

    cmd += ' --use_escape_vns'

    cmd += ' --vcs-per-vnet 10'

    cmd += ' --evn_deadlock_partition 1'

    cmd += ' --evn_n_deadlock_free 1'

    cmd += ' --evn_min_n_deadlock_free 9'


    cmd += '\n'

    lines.append(cmd)

    if not os.path.exists(outdir_name):
        os.makedirs(outdir_name)

    print(f'writing {outpath}')
    # print(f'{lines}')

    with open(outpath, 'w+') as of:
        # pass
        of.writelines(lines)


def main():

    # all
    benchmarks = ["blackscholes", "bodytrack", "canneal", "dedup",
                         "facesim", "ferret", "fluidanimate", "freqmine",
                         "raytrace", "streamcluster", "swaptions", "vips", "x264"]


    benchmarks = ["blackscholes", "bodytrack",
                         "facesim", "ferret", "freqmine",
                         "raytrace", "streamcluster",
                         "dedup",  "x264"]

    # benchmarks = ["facesim",
    #                      "raytrace", ]

    # benchmarks = [ "blackscholes"]

    n_inst = 100000
    try:
        n_inst = int(sys.argv[1])
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
        # if 'diam' in topo or 'vll' in topo:
        #     continue
        topologies.append(topo)


    topologies = [a for a in topologies if 'noci' in a]



    print(f'topologies ({len(topologies)})={topologies}')
    # quit()

    cpu_freqs= [i/10 for i in range(18,30,3)]


    # manually configure

    cpu_freqs = [1.8]

    l2_sizes = ['250kB','500kB','2MB']
    l2_sizes = ['500kB']

    alg_types = ['cload']
    lb_types = ['hops']

    for bench in benchmarks:
        for topo in topologies:
            for alg in alg_types:
                for lb in lb_types:
                    for cf in cpu_freqs:
                        for l2s in l2_sizes:
                            print(f'{bench:20} : {topo:20} : {alg:20} : {lb:20} : {str(cf):20} : {l2s:20} : {n_inst}')
                            write_jobscript(n_inst, topo, alg, lb, bench, cf, l2s)

if __name__ == '__main__':
    main()
