
import os

import sys

DATE = 'apr28'


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



def write_jobscript(n_inst, n_warmup_inst, topology, alg_type, lb_type, benchmark, cpu_clk, l2_size, nreps=None, n_evns=None, is_picky=False, use_simple=False, n_l2s=64, all_threads=True,n_vcs=10,link_width=128,rlat=1):


    outfile_name = f'{benchmark}_{topology}_{alg_type}_{lb_type}'

    inst_str = name_num_insts(n_inst)
    warmup_inst_str = name_num_insts(n_warmup_inst)


    clk_str = f'{cpu_clk}GHz'.replace('.','')

    # construct outdir_name
    # outdir_name = f'slurm/job_scripts/parsec_noci_32GB_l2caches'
    outdir_name = f'slurm/job_scripts/parsec_noci_32GBxDDR4_l2caches'

    if nreps is not None:
        outdir_name += f'_{nreps}reps'
    if n_evns is not None:
        outdir_name += f'_{n_evns}evns'
    if n_vcs != 10:
        outdir_name += f'_{n_vcs}vcs'

    outdir_name += f'_{clk_str}_{l2_size}'
    if n_l2s == 4:
        outdir_name += f'x{n_l2s}'

    if use_simple:
        outdir_name += f'_timingsimple'

    if all_threads:
        outdir_name += f'_allthreads'

    if link_width != 128:
        outdir_name += f'_{link_width}lwidth'

    if rlat != 1:
        outdir_name += f'_{rlat}rlat'

    outdir_name += f'/{warmup_inst_str}warmup_{inst_str}simul/'


    outpath = outdir_name + outfile_name

    # slurm_out = f'parsec_noci/{benchmark}_{topology}_{inst_str}_4GHzcpu_500MBL2{DATE}.out'
    # slurm_out = f'parsec_noci/{benchmark}_{topology}_{alg_type}_{lb_type}_{inst_str}_{clk_str}_{l2_size}_32GB_l2l2caches_{DATE}.out'

    slurm_out = f'parsec_noci/{benchmark}_{topology}_{alg_type}_{lb_type}_{warmup_inst_str}_{inst_str}_{clk_str}_{l2_size}'

    if n_l2s == 4:
        slurm_out += f'x{n_l2s}'

    if use_simple:
        slurm_out +=f'_timingsimple'

    if all_threads:
        slurm_out +=f'_allthreads'

    slurm_out += f'_32GBxDDR4_l2caches'

    if nreps is not None:
        slurm_out += f'_{nreps}reps'

    if n_evns is not None:
        slurm_out += f'_{n_evns}evns'

    if n_vcs != 10:
        slurm_out += f'_{n_vcs}vcs'

    if link_width != 128:
        slurm_out += f'_{link_width}lwidth'

    if rlat != 1:
        slurm_out += f'_{rlat}rlat'

    slurm_out += f'_{DATE}.out'

    # defining what to write
    lines = []

    s = '#!/bin/bash\n'
    lines.append(s)

    s = '#SBATCH --nodes 1\n'
    lines.append(s)

    s = '#SBATCH --cpus-per-task=2\n'
    lines.append(s)

    # upping minimum required mem to avoid memory issues
    # gem5 using 32GB so ~45 to be safe
    s = '#SBATCH --mem-per-cpu=36GB\n'
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

    if 'ns_' in topology:
        top_type = topology.split('_')[1]

    if 'lpbt' in topology:
        top_type = topology.split('_')[3]

    noi_clk = '1.8GHz'
    try:
        noi_clk = noi_clks_dict[top_type]
    except:
        print(f'Key error on topology {topology} w/ key={top_type} for noi freq.')
        quit(-1)

    # noci restore

    # order of these following three matters
    cmd = f'./build/X86/gem5.fast'


    # output dir
    cmd += f' -d ./parsec_results/noci_32GBxDDR4_'
    if nreps is not None:
        cmd += f'_{nreps}reps'
    if n_evns is not None:
        cmd += f'_{n_evns}envs'
    if n_vcs != 10:
        cmd == f'_{n_vcs}vcs'

    cmd += f'_{clk_str}_{l2_size}l2'
    if n_l2s == 4:
        cmd += f'x{n_l2s}'
    if use_simple:
        cmd += f'_timingsimple'
    if all_threads:
        cmd += f'_allthreads'

    if link_width != 128:
        cmd += f'_{link_width}lwidth'

    if rlat != 1:
        cmd += f'_{rlat}rlat'

    cmd += f'/{warmup_inst_str}warmup_{inst_str}simul/{benchmark}/{topology}_{alg_type}_{lb_type}/'

    # cmd += f' -d ./paper_outputs/parsec_noci_largemem/{inst_str}/{benchmark}/{topology}/'

    if not all_threads:
        cmd += f' configs/auto_top/auto_top_fs_v2.py'
    else:
        cmd += f' configs/auto_top/auto_top_fs_v3.py'

    # after this, order doesnt matter

    # instructions to simulate
    cmd += f' -I {n_warmup_inst}'

    cmd += f' --insts_after_warmup {n_inst}'

    # benchmark
    cmd += f' --benchmark_parsec {benchmark}'

    cmd += f' -r 1'
    # cmd += f' --checkpoint-dir ./parsec_checkpoints/parsec_checkpoints_noci/{benchmark}'

    # cmd += f' --checkpoint-dir ./parsec_checkpoints/largemem/{benchmark}'

    # different checkpoint
    if n_l2s == 4:
        cmd += f' --checkpoint-dir ./parsec_noci_checkpoints/roi_checkpoint/system_7/{benchmark}'
    else:
        cmd += f' --checkpoint-dir ./parsec_noci_checkpoints/roi_checkpoint/system_5/{benchmark}'

    if nreps is not None:
        cmd += f'_{nreps}reps'

    # cmd += f' --checkpoint-dir ./parsec_noci_checkpoints/{benchmark}/no_ruby/4reps_nocaches'


    cmd += f' --router_map_file configs/topologies/paper_solutions/{topology}.map'

    # topology and clock domains
    simple_name = topology.replace('_noci','')

    # cmd += f' --vc_map_file configs/topologies/paper_vcs_noci/{simple_name}.vc'
    # cmd += f' --nr_map_file configs/topologies/paper_nrs_noci/{simple_name}.nr'

    # construct vn file name
    cmd += f' --flat_vn_map_file configs/topologies/vn_maps/{topology}_{alg_type}_{lb_type}'
    if n_evns is not None:
        cmd += f'_{n_evns}vns'
    cmd += '.vn'


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

    cmd += f' --caches'

    cmd += f' --num-l2caches {n_l2s}'
    cmd += f' --l2_size {l2_size}'

    cmd += f' --num_chiplets 4'
    # cmd += ' --num-l2caches 64 --num_chiplets 4'
    # cmd += ' --num-cpus 64 --mem_or_coh coh --num-dirs 64 --num-l2caches 4 --num_chiplets 4'

    cmd += ' --mem-size 32GB'

    # ruby stuff
    cmd += ' --ruby --network garnet'

    if link_width != 128:
        cmd += f' --link-width-bits {link_width}'

    if rlat != 1:
        cmd += f' --router-latency {rlat}'

    # FS linux stuff
    # x264 bodytrack facesim

    # these were taken with a different kernel. shouldnt matter but just in case
    # if  benchmark == 'bodytrack' or benchmark == 'facesim':
    #     cmd += f' --kernel parsec_disk_image/vmlinux-5.4.49'
    # elif benchmark == 'x264' or benchmark == 'dedup':
    #     cmd += f' --kernel parsec_disk_image/x86-linux-kernel-4.19.83'
    # else:
    #     cmd += f' --kernel parsec_disk_image/vmlinux-4.4.186'

    cmd += f' --kernel parsec_disk_image/vmlinux-5.4.49'

    cmd += f' --disk-image parsec_disk_image/x86-parsec'

    # simulation (restore)
    # cmd += f' --cpu-type X86TimingSimpleCPU --restore-with-cpu X86TimingSimpleCPU'




    if not use_simple:
        cmd += f' --cpu-type X86O3CPU'
    else:
        cmd += f' --cpu-type X86TimingSimpleCPU'

    # cmd += f' --restore-with-cpu X86KvmCPU'
    # cmd += f' --restore-with-cpu X86O3CPU'

    # cmd += f' --garnet-deadlock-threshold 5000000'

    cmd += f' --routing-algorithm 2'

    cmd += ' --use_escape_vns'

    # TODO parameterize?
    tot_evns = n_vcs
    if n_evns is not None:
        # always allow at least 1 general traffic for any number of escape vns
        tot_evns = max(tot_evns, n_evns + 1)
    cmd += f' --vcs-per-vnet {tot_evns}'

    # 1 of each DL free vn
    cmd += f' --evn_n_deadlock_free 1'

    # default
    min_dl_free = 6
    if n_evns is not None:
        min_dl_free = n_evns

    cmd += f' --evn_min_n_deadlock_free {min_dl_free}'

    dl_part = tot_evns - min_dl_free
    cmd += f' --evn_deadlock_partition {dl_part}'



    # better memory?
    cmd += ' --mem-type DDR4_2400_16x4'

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

    # all!!!!
    benchmarks = ["blackscholes", "bodytrack", "canneal", "dedup",
                         "facesim", "ferret", "fluidanimate", "freqmine",
                         "raytrace", "streamcluster", "swaptions", "vips", "x264"]


    # benchmarks = [ "blackscholes"]

    n_inst = 100000000
    try:
        n_inst = int(sys.argv[1])
    except:
        pass

    n_warmup = 100000000
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
        # if 'diam' in topo or 'vll' in topo:
        #     continue
        topologies.append(topo)


    topologies = [a for a in topologies if 'noci' in a]



    # topologies = [a for a in topologies if 'small' in a or '_l_' in a or 'mesh' in a or '_m_' in a]
    #topologies = [a for a in topologies if 'mesh' in a]
    #topologies = [a for a in topologies if 'cmesh' not in a]


    print(f'topologies ({len(topologies)})={topologies}')
    # quit()

    cpu_freqs= [i/10 for i in range(18,30,3)]


    # manually configure

    cpu_freqs = [1.8]

    # l2_sizes = ['250kB','500 kB','2MB']
    l2_sizes = ['500kB']
    l2_sizes = ['128kB']
    n_l2s = 64
    l2_sizes = ['2MB']


    # alg_types = ['naive','cload','bsorm']

    alg_types = ['cload_picky']#,'bsorm_picky']
    lb_types = ['hops']

    cpu_types = [False]#,True]

    evns = 8
    reps = 8
    is_picky = True
    n_vcs = 10
    # link widht
    link_widths = [128]#[32,64]
    rlat=1

    i=0
    for bench in benchmarks:
        for topo in topologies:
            for alg in alg_types:
                for lb in lb_types:
                    for cf in cpu_freqs:
                        for l2s in l2_sizes:
                            for if_simple in cpu_types:
                                for lw in link_widths:
                                    print(f'{bench:20} : {topo:20} : {alg:20} : {lb:20} : {str(cf):20} : {l2s:20} : {n_inst}')
                                    write_jobscript(n_inst, n_warmup, topo, alg, lb, bench, cf, l2s, n_evns=evns, nreps=reps, is_picky=is_picky, use_simple=if_simple, n_l2s=n_l2s,n_vcs=n_vcs,link_width=lw,rlat=rlat)
                                    i+=1

    print(f'\nWrote {i}')

if __name__ == '__main__':
    main()
