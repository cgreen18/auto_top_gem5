import os
import subprocess
import sys
import threading
import argparse
import numpy as np

MAX_PROCS = 13

global num_threads
num_threads = 0

sem = threading.Semaphore(MAX_PROCS)

global config_status
config_status = {}

status_lock = threading.Lock()

global which_sag_lock
which_sag_lock = threading.Lock()

global g_which_sag
g_which_sag = 7

home = '/home/yara/mithuna2/green456/netsmith_autotop/auto_top_gem5'
setup = ['cd', home, ';', 'module','load','gcc',';']
gem5_build = './build/X86/gem5.fast'
conf_script = 'configs/auto_top/auto_top_fs_analyze_parsec.py'
topo_conf_script = 'OneToOneGarnet'


base_flags = [
        '--kernel parsec_disk_image/vmlinux-4.4.186',
        '--disk-image parsec_disk_image/x86-parsec',
        '--caches',
        '--ruby',
        '--network','garnet',

        '--routing-algorithm', '2',
        '--use_escape_vns',
        ]


global outdir
outdir = './parsec_traffic_analysis/'

class BenchmarkRun:

    def name_sim_cycles(self,sc):
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

    def __init__(self, bench, n_cycles, noc_clk, n_cpus, n_dirs, use_skylake, big_caches, bitwidth):

        self.a_cycles = n_cycles
        self.bench = bench

        self.n_cpus = n_cpus
        self.n_dirs = n_dirs

        self.use_skylake = use_skylake
        self.big_caches = big_caches

        self.bitwidth = bitwidth

        self.alg_type = 'naive'
        self.lb_type = 'hops'
        self.hetero = False

        # topology configs
        self.topology = f'cpu_parsec_{self.n_cpus}cpu_{self.n_dirs}dir_1t1'

        # the vn map and nr list files have to be named and located as such
        self.topology_map_file = os.path.join('configs/topologies/paper_solutions/',self.topology)

        self.min_n_dl_free = 2
        self.n_evns =2
        self.tot_vcs = 4
        self.n_dl_free = 1
        self.dl_part = self.tot_vcs - self.n_dl_free*self.min_n_dl_free

        vn_dir = 'configs/topologies/vn_maps3/'

        vn_file = f'{self.topology}_{self.alg_type}_{self.lb_type}_{self.n_evns}vns.vn'
        self.topology_vn_file = os.path.join(vn_dir,vn_file)

        nrl_dir = 'configs/topologies/nr_list3/'

        nrl_file = f'{self.topology}_{self.alg_type}.nrl'
        self.topology_nr_list_file = os.path.join(nrl_dir,nrl_file)

        sd_str = 'mixed'

        self.noc_clk = f'{noc_clk}GHz'

        self.noi_clk = self.noc_clk

        top_type = self.topology
        if '_s_' in self.topology:
            top_type = 's'
        elif '_m_' in self.topology:
            top_type = 'm'
        elif '_l_' in self.topology:
            top_type = 'l'
        elif '2ll' in self.topology:
            top_type = 'm'
        elif '15ll' in self.topology:
            top_type = 's'

        print(f'top_type={top_type}')

        if self.hetero:
            try:
                self.noi_clk = noi_clks_dict[top_type]
            except:
                print(f'Key error on topology {self.topology} w/ key={top_type} for noi freq.')
                quit(-1)


        
        cpu_desc = f'{self.noc_clk}'
        if self.use_skylake:
            cpu_desc += '_sky'
        if self.big_caches:
            cpu_desc += '_bigCaches'
        if self.bitwidth != 128:
            cpu_desc += f'_{bitwidth}bw'

        self.cpu_desc = cpu_desc

        self.sys_desc = f'{self.n_cpus}cpus_{self.n_dirs}dirs'

        out_path_suffix = f'{self.name_sim_cycles(self.a_cycles)}cycles/{self.sys_desc}/{self.cpu_desc}/{self.bench}/'

        self.output_dir = os.path.join(outdir,out_path_suffix)

    def run(self, which_saguaro):

        global config_status

        cmd = []

        cmd = ['ssh',f'saguaro{which_saguaro}']

        cmd += setup

        # for testing
        # cmd += ['touch','ssh_success.txt']
        # cmd += ['echo',f'"yippee sag{which_saguaro}"','>>','ssh_success.txt']
        # print(' '.join(cmd))
        # res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
        # return

        cmd += [gem5_build,
                # '--stdout-file log.out --stderr-file log.err -r -e',
                '-d', self.output_dir,
                conf_script,
                '--topology',topo_conf_script
                ]

        cmd += base_flags

        cmd += ['--benchmark_parsec',self.bench]

        cmd += ['--router_map_file',self.topology_map_file,
                '--flat_vn_map_file',self.topology_vn_file,
                '--flat_nr_map_file',self.topology_nr_list_file,]

        cmd += ['--cpu-clock',self.noc_clk,
                '--sys-clock',self.noc_clk,
                '--ruby-clock',self.noc_clk]


        # cmd += ['--insts_after_warmup',f'{self.n_insts}']
        cmd += ['--analysis_cycles',f'{self.a_cycles}']
        cmd += ['--n_iters','2']

        cmd += ['--cpu-type','X86KvmCPU']
        cmd += ['--switch_cpu','X86O3CPU']


        n_cpus = self.n_cpus
        n_dirs = self.n_dirs

        # cmd += ['--mem-size','3200000']
        # cmd += ['--mem-size','131072']
        cmd += ['--num-dirs', str(n_dirs)]
        cmd += ['--num-cpus',str(n_cpus)]
        cmd += ['--num-l2caches',str(n_cpus)]



        cmd += ['--vcs-per-vnet',f'{self.tot_vcs}',
                '--evn_deadlock_partition',f'{self.dl_part}',
                '--evn_n_deadlock_free',f'{self.n_dl_free}',
                '--evn_min_n_deadlock_free',f'{self.min_n_dl_free}']

        if self.use_skylake:
            cmd += ['--use_skylake']
        
        if self.big_caches:
            cmd += ['--l1d_size','64kB',
                    '--l1d_assoc','16',
                    '--l1i_size','64kB',
                    '--l1i_assoc','16',
                    '--l2_size','4MB',
                    '--l2_assoc','16']
        else:
            cmd += ['--l1d_size','64kB',
                    '--l1d_assoc','8',
                    '--l1i_size','64kB',
                    '--l1i_assoc','8',
                    '--l2_size','2MB',
                    '--l2_assoc','8']

        if self.bitwidth != 128:
            cmd += ['--link-width-bits',f'{self.bitwidth}']

        os.chdir(home)

        # comment in/out to test script
        ###############################################################

        print(' '.join(cmd))
        return

        res = None

        # subprocess.run(setup, shell=True)
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)


        status = 'No error'
        if res.returncode != 0:
            print("Config " + f'{self.sys_desc}_{self.cpu_desc}'  + ": gem5 exited with error code " \
                    + str(res.returncode))
            status = str(res.returncode)

        else:
            print("Config " + f'{self.sys_desc}_{self.cpu_desc}' + " complete.")

        try:
            with open(os.path.join(self.output_dir, "stdout_stderr"), "w+") as fp:
                fp.writelines(res.stdout)
                fp.writelines(res.stderr)
        except:
            pass
        _dict = {f'{self.sys_desc}_{self.cpu_desc} ({self.output_dir})' : status}

        status_lock.acquire()
        config_status.update(_dict)
        # for config, status in config_status.items():
        #     print(config + ':\t' + status)
        status_lock.release()

# Bench should be BenchmarkRun object
def run_benchmark(bench):
    global g_which_sag

    which_sag_lock.acquire()
    which = g_which_sag
    g_which_sag += 1
    if g_which_sag > 9:
        g_which_sag = 1
    which_sag_lock.release()
    
    sem.acquire()



    try:
        bench.run(which)
    except Exception as e:
        print(f'During run, exception...\n\t{e}')


    sem.release()

    # for i in range(N_SAGS):
    #     l = 
    #     if not l.locked():
    #         l.acquire()
        
    #         l.release()



def main():

    parser = argparse.ArgumentParser()


    parser.add_argument('--sys_clk',type=float)
    parser.add_argument('--num_cpus',type=int)
    parser.add_argument('--num_dirs',type=int)
    parser.add_argument('--n_insts',type=int)
    parser.add_argument('--cycles',type=int)

    parser.add_argument('--use_skylake',action='store_true')
    parser.add_argument('--big_caches',action='store_true')

    parser.add_argument('--bitwidth',type=int)

    parser.add_argument('--benchmark',type=str)


    args = parser.parse_args()




    benchmarks = [
                "canneal", 
                "facesim",
                "bodytrack",
                "fluidanimate",
                "raytrace",
                "streamcluster", 
                "swaptions",   
                "ferret",
                "freqmine",
                "dedup",
                "blackscholes", 
                "x264",
                "vips"
                ]

    if args.benchmark:
        benchmarks = [args.benchmark] 

    clks = [1,2,4]
    if args.sys_clk:
        clks = [args.sys_clk]

    n_cpus = [16, 32]
    if args.num_cpus:
        n_cpus = [args.num_cpus]

    n_dirs = [8,16]
    if args.num_dirs:
        n_dirs = [args.num_dirs]
    
    n_insts = [1000, 100000]
    if args.n_insts:
        n_insts = [args.n_insts]

    cycles = [1000, 100000]
    if args.cycles:
        cycles = [args.cycles]

    use_skys = [False]#,True]
    if args.use_skylake:
        use_skys = [True]

    big_caches = [False]#,True]
    if args.big_caches:
        big_caches = [True]

    bitwidths = [64,32]#,128]
    if args.bitwidth:
        bitwidths = [args.bitwidth]

    i = 0
    runs = []
    for b in benchmarks:
        for nc in n_cpus:
            for nd in n_dirs:
                for c in clks:
                    # for ni in n_insts:
                    for cy in cycles:
                        for us in use_skys:
                            for bc in big_caches:
                                for bw in bitwidths:
                                    #     def __init__(self, bench, n_insts, noc_clk, n_cpus, n_dirs, use_skylake, big_caches, bitwidth):
                                    print(f'{i:04} : Adding {b} for {cy} cycles')
                                    print(f'\tw/ {nc}cpus, {nd}dirs @ {c}GHz, bitwidth {bw}')
                                    print(f'\tw/ skylake? {us} and big $? {bc}')
                                    runs += [BenchmarkRun(b, cy, c, nc, nd, us, bc, bw)]
                                    i+=1

    #quit()

    threads = [threading.Thread(target=run_benchmark, args=(x,)) for x in runs]


    # threads = [threads[0]]

    global num_threads
    num_threads = len(threads)

    print("Dispatching " + str(num_threads) + " threads")

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("Done")

    status_lock.acquire()
    for config, status in config_status.items():
        print(config + ':\t' + status)
    status_lock.release()

if __name__ == '__main__':
    main()
