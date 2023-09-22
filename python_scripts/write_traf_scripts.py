import sys
import os

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



DATE = 'sept13'

benchmarks = [
            "canneal", 
            "bodytrack",
            "streamcluster", "vips", 
            "swaptions", "fluidanimate",
            "facesim", "raytrace",
            "ferret",  "freqmine",
            "blackscholes", 
            "dedup","x264"
            ]

n_inst = int(sys.argv[1])

n_inst_str = name_num_insts(n_inst)

n_cpus = 16
n_dirs = 8

use_skylake = True

for benchmark in benchmarks:


    slurm_out = f'parsec_traffic_analysis/{benchmark}_{n_inst_str}_{n_cpus}cpu_{n_dirs}dir_4GHz'
    slurm_out += f'_{DATE}.out'

    lines = []

    s = '#!/bin/bash\n'
    lines.append(s)

    s = '#SBATCH --nodes 1\n'
    lines.append(s)

    s = '#SBATCH --mem-per-cpu=36GB\n'
    lines.append(s)

    s = f'#SBATCH --output=slurm/outputs/{slurm_out}\n'
    lines.append(s)

    s = 'cd $SLURM_SUBMIT_DIR\n'
    lines.append(s)

    s='source setup.sh\n'
    lines.append(s)

    cmd = f'srun'

    cmd += f' ./build/X86/gem5.fast'


    outdir = f' -d ./parsec_traffic_analysis/{n_cpus}cpu_{n_dirs}dir_4GHz/{n_inst_str}/{benchmark}'
    if use_skylake:
        outdir += '_skylake'


    cmd += outdir

    cmd += f' configs/auto_top/auto_top_fs_analyze_parsec.py'
    
    cmd += f' --benchmark_parsec {benchmark}'
    
    cmd += f' --cpu-type X86KvmCPU --switch_cpu X86O3CPU --kernel parsec_disk_image/vmlinux-4.4.186 --disk-image parsec_disk_image/x86-parsec'
    
    cmd += f' --num-cpus {n_cpus} --num-l2caches {n_cpus}'

    cmd += f' --num-dirs {n_dirs}'

    # like skylake
    if use_skylake:
        cmd += f' --use_skylake'
        cmd += f' --l1d_size 64kB --l1d_assoc 16'
        cmd += f' --l1i_size 64kB --l1i_assoc 16'
        cmd += f' --l2_size 2MB --l2_assoc 16'


    cmd += f' --caches --ruby --network garnet --topology OneToOneGarnet --routing-algorithm 2 --use_escape_vns --vcs-per-vnet 4 --evn_deadlock_partition 2 --evn_n_deadlock_free 1 --evn_min_n_deadlock_free 2'
    
    clk = 4
    cmd += f' --cpu-clock {clk}GHz --sys-clock {clk}GHz --ruby-clock {clk}GHz'

    config_name = f'cpu_parsec_{n_cpus}cpu_{n_dirs}dir_1t1'
    cmd += f' --router_map_file configs/topologies/paper_solutions/{config_name}.map --flat_vn_map_file configs/topologies/vn_maps3/{config_name}_naive_hops_2vns.vn --flat_nr_map_file configs/topologies/nr_list3/{config_name}_naive.nrl'
    
    cmd += f' --insts_after_warmup {n_inst}'

    cmd += f' --n_iters 2'

    lines.append(cmd)


    out_dir = f'slurm/job_scripts/parsec_traffic_analysis/'
    out_file = f'{n_inst_str}/{benchmark}'
    if use_skylake:
        out_file += '_skylake'

    # clk
    out_file += '_4GHz'

    out_path = os.path.join(out_dir, out_file)

    with open(out_path, 'w+') as of:
        of.writelines(lines)
        print(f'wrote to {out_path}')
        print(f'\t{lines}')
