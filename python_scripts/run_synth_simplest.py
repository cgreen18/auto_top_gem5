

import os
import subprocess
import sys
import threading
import argparse


MAX_PROCS = 16

global num_threads
num_threads = 0

sem = threading.Semaphore(MAX_PROCS)

global config_status
config_status = {}

status_lock = threading.Lock()

home = '/home/min/a/green456/heterogarnet/gem5'
setup = ['cd', home, ';', 'module','load','gcc',';']

# TODO change
gem5_build = './build/Garnet_standalone/gem5.opt'
conf_script = 'configs/auto_top/auto_top_synth.py'
topo_conf_script = 'EscapeVirtualNetworks'
topology_to_n_routers_dict = {
    'cmesh_x':'20',
    'butter_donut_x':'20',
    'kite_large':'20',
    'kite_medium':'20',
    'ft_x':'20',
    'kite_small':'20',
    'cmesh':'24',
    'dbl_bfly':'24',
    'dbl_bfly_x':'20',
    'mesh':'64'}


sim_cycles = ['2147483647']
inj_rates = [str(x/100.0) for x in range(1, 11)]


noc_clk = '1.8GHz'


desired_topologies=[

    # '20r_15ll_opt_8bw_4diam_ulinks_noci',
    # '20r_15ll_opt_ulinks_noci',

    # '20r_2ll_runsol_ulinks_noci',
    # '20r_4p_2ll_runsol_12bw_ulinks_noci',

    # '20r_25ll_timed7days_ulinks_noci',
    # '20r_4p_25ll_runsol_14bw_ulinks_noci',

    # 'ns_s_latop.map','ns_s_bwop.map',
    # 'ns_m_latop.map',
    'ns_m_bwop.map',
    # 'ns_l_latop.map','ns_l_bwop.map',
    # 'ns_s_memopt.map','ns_m_memopt.map','ns_l_memopt.map',

    # 'ft_x.map',

    # 'butter_donut_x.map', 'dbl_bfly_x.map',

    # 'kite_large.map', 'kite_medium.map', 'kite_small.map',

    # 'cmesh_x.map', 'mesh.map'
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
            'ft_x':'3.0GHz',
            'kite_large':'2.7GHz',
            # these will match part of name of our files
            '15ll':'3.6GHz',
            '2ll':'3.0GHz',
            '25ll':'2.7GHz',
            'ns_s_latop':'3.6GHz',
            'ns_s_bwop':'3.6GHz',
            'ns_m_latop':'3.0GHz',
            'ns_m_bwop':'3.0GHz',
            'ns_l_latop':'2.7GHz',
            'ns_l_bwop':'2.7GHz',
            'ns_s_memopt':'3.6GHz',
            'ns_m_memopt':'3.0GHz',
            'ns_l_memopt':'2.7GHz',
            }


global map_files
map_files = []


base_flags = ['--network','garnet',
        '--mem-type', 'SimpleMemory',
        '--garnet-deadlock-threshold','50000000',
        '--routing-algorithm', '2',
        '--use_escape_vcs',
        '--vcs-per-vnet','6',
        '--vc_deadlock_partition','0',
        '--vc_n_deadlock_free','2',
        '--vc_min_n_deadlock_free','3',
        '--synth_traffic'  # allows non power of two # of directories
        ]


global outdir
outdir = './paper_outputs/synth_20r_simplest_large_coh_sat_2'

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


    def __init__(self, sol_file, memcoh, sim_cycle, inj_rate, hetero, use_vll):
        self.mem_or_coh = memcoh
        self.topology_sol_file = 'configs/topologies/paper_solutions/' + sol_file
        self.sim_cycles = sim_cycle
        self.inj_rate = inj_rate

        self.topology = ((sol_file).split('.')[0])


        self.topology_vn_file = f'configs/topologies/vn_maps/{self.topology}_naive_none.vn'

        self.topology_nrl_file = f'configs/topologies/nr_list/{self.topology}_naive.nrl'

        self.hetero = hetero
        self.use_vll = use_vll

        inj_rate_str = inj_rate.replace('.','_')

        uvl = ''
        if use_vll:
            uvl = '_use_vll'

        sd_str = 'mixed'
        if not hetero:
            sd_str = 'same'


        self.output_dir = f'{outdir}/{self.name_sim_cycles(self.sim_cycles)}/{sd_str}/{self.mem_or_coh}/{self.topology}/{inj_rate_str}/'
        # self.output_dir = f'{outdir}/{self.name_sim_cycles(self.sim_cycles)}/{sd_str}/{self.mem_or_coh}/{self.topology}/'

        top_type = self.topology
        # if '20r' in self.topology:
        #     # capture 15ll / 2ll / 25ll portion
        #     top_type = self.topology.split('_')[1]

        self.noc_clk = noc_clk


        top_type = self.topology
        # if '20r' in self.topology:
        #     # capture 15ll / 2ll / 25ll portion
        #     # now 11, 18, 19

        #     top_type = self.topology.split('_')[1]
        #     if top_type == '4p':
        #         top_type = self.topology.split('_')[2]


        self.noi_clk = self.noc_clk

        if hetero:
            try:
                self.noi_clk = noi_clks_dict[top_type]
            except:
                print(f'Key error on topology {self.topology} w/ key={top_type} for noi freq.')
                quit(-1)
        #self.output_dir = f'./outputs/{self.sim_cycles}/{self.noi_clk}/{self.mem_or_coh}/{self.topology}/{inj_rate_str}/''

        n_routers = -1
        if 'ns_' in self.topology:
            n_routers = '20'
        else:
            try:
                n_routers = topology_to_n_routers_dict[self.topology]
            except:
                print(f'Key error on topology {self.topology} w/ key={self.topology} for noi freq.')
                print(f'dict={topology_to_n_routers_dict}, key={self.topology}')
                return

        self.n_routers = n_routers
        self.topo_conf_script = topo_conf_script


    def run(self):

        global config_status

        cmd = []

        # cmd += setup

        cmd += [gem5_build,
                # '--stdout-file log.out --stderr-file log.err -r -e',
                '-d', self.output_dir,
                conf_script,
                '--topology',self.topo_conf_script,
                '--noi_routers',self.n_routers,
                '--sim-cycles',self.sim_cycles,
                '--injectionrate',self.inj_rate,
                '--noc_clk',self.noc_clk,
                '--sys-clock',self.noc_clk,
                '--ruby-clock',self.noc_clk,
                '--noi_clk',self.noi_clk,
                '--router_map_file',self.topology_sol_file,
                '--vc_map_file',self.topology_vn_file,
                '--nr_map_file',self.topology_nrl_file,
                '--ruby'
                ]


        if self.mem_or_coh == 'mem':
            if self.n_routers == '20' or self.n_routers == '24':
                cmd += ['--num-dirs', '8']
                # cmd += ['--num-dirs','8']
                # cmd += ['--num-dirs','32']
            elif self.n_routers == '64':
                cmd += ['--num-dirs', '16']
            
            cmd += ['--mem_or_coh','mem']
        else:

            cmd += ['--num-dirs', self.n_routers]
            # cmd += ['--num-dirs', '40']

            cmd += ['--mem_or_coh','coh']

            # this is a multiple of 20, to match n_routers
            if self.n_routers == '20':
                cmd += ['--mem-size','536870900']

        cmd += ['--num-cpus',self.n_routers]
        # cmd += ['--num-cpus','40']

        if self.use_vll:
            cmd += ['--use_vll']


        cmd += base_flags


        os.chdir(home)

        print(' '.join(cmd))
        return
        
        # subprocess.run(setup, shell=True)
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)


        status = 'No error'
        if res.returncode != 0:
            print("Config " + self.topology_sol_file + ": gem5 exited with error code " \
                    + str(res.returncode))
            status = str(res.returncode)

        else:
            print("Config " + self.topology_sol_file + " complete.")

        try:
            with open(os.path.join(self.output_dir, "stdout_stderr"), "w+") as fp:
                fp.writelines(res.stdout)
                fp.writelines(res.stderr)
        except:
            pass
        _dict = {f'{self.topology} ({self.output_dir})' : status}

        status_lock.acquire()
        config_status.update(_dict)
        # for config, status in config_status.items():
        #     print(config + ':\t' + status)
        status_lock.release()

# Bench should be BenchmarkRun object
def run_benchmark(bench):
    sem.acquire()
    try:
        bench.run()
    except Exception as e:
        print(f'During run, exception...\n\t{e}')
    sem.release()


def main():



    global map_files
    global inj_rates

    parser = argparse.ArgumentParser()

    parser.add_argument('-s','--sim_cycles',type=str,
                default='1000',help='TODO')
    parser.add_argument('--mem_only',action='store_true')
    parser.add_argument('--coh_only',action='store_true')

    parser.add_argument('--samefreq_only',action='store_true')
    parser.add_argument('--mixedfreq_only',action='store_true')

    parser.add_argument('--ours_only',action='store_true')
    parser.add_argument('--prev_only',action='store_true')

    parser.add_argument('--inj_start',type=float,default=0.01)
    parser.add_argument('--inj_end',type=float,default=0.1)
    parser.add_argument('--inj_step',type=float,default=0.01)

    parser.add_argument('--use_vll',action='store_true')

    parser.add_argument('--map_file_dir',type=str,default='./configs/topologies/paper_solutions/')


    args = parser.parse_args()

    sim_cycle = args.sim_cycles

    map_files_dir = args.map_file_dir
    for root, dirs, files in os.walk(map_files_dir):
        # print(files)
        map_files += files

    # map_files = [s for s in map_files if 'kite_small' in s]

    if args.inj_start is not None or\
            args.inj_end is not None or\
            args.inj_step is not None:
        # factor of 100 since range only takes ints
        # should np.linspace or something later
        a = int(1000*args.inj_start)
        b = int(1000*args.inj_end)
        c = int(1000*args.inj_step)

        inj_rates = [str(x/1000.0) for x in range(a,b,c)]

    runs = []

    memcoh = ['mem','coh']
    if args.mem_only:
        memcoh = ['mem']
    elif args.coh_only:
        memcoh = ['coh']
    
    het_tf = [True, False]
    if args.samefreq_only:
        het_tf = [False]
    elif args.mixedfreq_only:
        het_tf = [True]

    # start back
    map_files.reverse()

    if args.ours_only:
        map_files = [s for s in map_files if 'ns_' in s]
    if args.prev_only:
        map_files = [s for s in map_files if 'kite' in s\
                        or 'bfly' in s\
                        or 'butter' in s\
                        or 'mesh'\
                        or 'ft' in s]

    # map_files = [s for s in map_files if 'butter' in s]
    map_files = [s for s in map_files if s in desired_topologies]


    use_vll = args.use_vll

    for het in het_tf:
        for mc in memcoh:
            for ir in inj_rates:
                for sf in map_files:
                    runs += [BenchmarkRun(sf, mc, sim_cycle, ir, het, use_vll)]

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
