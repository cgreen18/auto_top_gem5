import os
import subprocess
import sys
import threading
import argparse
import numpy as np


MAX_PROCS = 28

global num_threads
num_threads = 0

sem = threading.Semaphore(MAX_PROCS)

global config_status
config_status = {}

status_lock = threading.Lock()

home = '/home/yara/mithuna2/green456/netsmith_autotop/auto_top_gem5'
setup = ['cd', home, ';', 'module','load','gcc',';']
gem5_build = './build/Garnet_standalone/gem5.fast'
conf_script = 'configs/auto_top/auto_top_synth.py'
topo_conf_script = 'NoCI_EscapeVirtualNetworks'
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
    'mesh':'64',
    'ns':'20',
    'lpbt':'20'}


sim_cycles = ['2147483647']
inj_rates = [str(x/100.0) for x in range(1, 11)]


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
            'ns_s_latop_noci':'3.6GHz',
            'ns_s_bwop_noci':'3.6GHz',
            'ns_m_latop_noci':'3.0GHz',
            'ns_m_bwop_noci':'3.0GHz',
            'ns_l_latop_noci':'2.7GHz',
            'ns_l_bwop_noci':'2.7GHz',
            'dbl_bfly_x_noci':'2.7GHz',
            'butter_donut_x_noci':'2.7GHz',
            'kite_small_noci':'3.6GHz',
            'kite_medium_noci':'3.0GHz',
            'kite_large_noci':'2.7GHz',
            'ft_x_noci':'3.0GHz',
            'lpbt_s_hops':'3.6GHz',
            'lpbt_s_power':'3.6GHz',
            'lpbt_m_hops':'3.0GHz',
            's':'3.6GHz',
            'm':'3.0GHz',
            'l':'2.7GHz',
            'mesh_noci':'4.0GHz'}
# topologies
noi_clks_dict.update({'mesh':'4GHz',
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
            'l':'2.7GHz'})


global map_files
map_files = []


base_flags = ['--network','garnet',
        '--mem-type', 'SimpleMemory',
        #'--garnet-deadlock-threshold','50000000',
        '--routing-algorithm', '2',
        '--use_escape_vns',
        # '--vcs-per-vnet','6',
        # '--evn_deadlock_partition','2',
        # '--evn_n_deadlock_free','1',
        # '--evn_min_n_deadlock_free','4',
        '--synth_traffic',

        # allows non power of two # of directories
        # '--mem_size','536870900'
        ]


global outdir
outdir = './synth_outputs/noci'

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


    def __init__(self, map_file, memcoh, sim_cycle, inj_rate, hetero, alg_type, lb_type, n_evns, tot_vcs, noc_clk, n_cpus, dir_mult, weighted_mclb):

        # simulation configs
        self.mem_or_coh = memcoh
        self.sim_cycles = sim_cycle
        self.inj_rate = inj_rate

        self.n_cpus = n_cpus
        self.dir_mult = dir_mult

        # topology configs
        self.topology = ((map_file).split('.')[0])
        self.alg_type = alg_type
        self.lb_type = lb_type
        self.topology_and_routing = f'{self.topology}_{self.alg_type}_{self.lb_type}'

        # the vn map and nr list files have to be named and located as such
        self.topology_map_file = os.path.join('configs/topologies/paper_solutions/',map_file)

        self.min_n_dl_free = n_evns
        self.n_evns = n_evns
        self.tot_vcs = tot_vcs
        self.n_dl_free = 1
        self.dl_part = self.tot_vcs - self.n_dl_free*self.min_n_dl_free

        vn_dir = 'configs/topologies/vn_maps/'
        if weighted_mclb:
            vn_dir = 'configs/topologies/vn_maps_augmclb_nocnocweighted/'

        vn_file = f'{self.topology}_{alg_type}_{lb_type}_{n_evns}vns.vn'
        self.topology_vn_file = os.path.join(vn_dir,vn_file)

        nrl_dir = 'configs/topologies/nr_list/'
        if weighted_mclb:
            nrl_dir = 'configs/topologies/nr_list_augmclb_nocnocweighted/'

        nrl_file = f'{self.topology}_{alg_type}.nrl'
        self.topology_nr_list_file = os.path.join(nrl_dir,nrl_file)

        self.hetero = hetero

        inj_rate_str = inj_rate.replace('.','_')

        sd_str = 'mixed'
        if not hetero:
            sd_str = 'same'



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

        if hetero:
            try:
                self.noi_clk = noi_clks_dict[top_type]
            except:
                print(f'Key error on topology {self.topology} w/ key={top_type} for noi freq.')
                quit(-1)

        #self.output_dir = f'./outputs/{self.sim_cycles}/{self.noi_clk}/{self.mem_or_coh}/{self.topology}/{inj_rate_str}/''

        n_routers = -1
        if 'mesh' in self.topology:
            n_routers = '64'
        else:
            n_routers = '20'

        self.n_routers = n_routers

        desc = f'{self.alg_type}_{self.lb_type}_{self.n_evns}_{self.tot_vcs}_{self.n_cpus}cpus_{self.dir_mult}xdirs_{self.noc_clk}'

        out_path_suffix = f'{self.name_sim_cycles(self.sim_cycles)}/{sd_str}/{desc}/{self.mem_or_coh}/{self.topology}/{inj_rate_str}/'

        self.output_dir = os.path.join(outdir,out_path_suffix)

    def run(self):

        global config_status

        cmd = []

        # cmd += setup

        cmd += [gem5_build,
                # '--stdout-file log.out --stderr-file log.err -r -e',
                '-d', self.output_dir,
                conf_script,
                '--topology',topo_conf_script,
                '--noi_routers',self.n_routers,
                '--sim-cycles',self.sim_cycles,
                '--injectionrate',self.inj_rate,
                '--noc_clk',self.noc_clk,
                '--sys-clock',self.noc_clk,
                '--ruby-clock',self.noc_clk,
                '--noi_clk',self.noi_clk,
                '--router_map_file',self.topology_map_file,
                '--flat_vn_map_file',self.topology_vn_file,
                '--flat_nr_map_file',self.topology_nr_list_file,
                '--ruby'
                ]

        if self.mem_or_coh == 'mem':
            base_dirs = 16

            cmd += ['--mem_or_coh','mem']
        # coh
        else:

            base_dirs = self.n_cpus
            cmd += ['--mem_or_coh','coh']

        n_cpus = self.n_cpus
        n_dirs = self.dir_mult*base_dirs

        # cmd += ['--mem-size','3200000']
        # cmd += ['--mem-size','131072']
        cmd += ['--num-dirs', str(n_dirs)]
        cmd += ['--num-cpus',str(n_cpus)]

        cmd += base_flags



        cmd += ['--vcs-per-vnet',f'{self.tot_vcs}',
                '--evn_deadlock_partition',f'{self.dl_part}',
                '--evn_n_deadlock_free',f'{self.n_dl_free}',
                '--evn_min_n_deadlock_free',f'{self.min_n_dl_free}']

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
            print("Config " + self.topology_map_file + ": gem5 exited with error code " \
                    + str(res.returncode))
            status = str(res.returncode)

        else:
            print("Config " + self.topology_map_file + " complete.")

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

    # to limit number alg types
    parser.add_argument('--naive_only',action='store_true')
    parser.add_argument('--bsorm_only',action='store_true')
    parser.add_argument('--cload_only',action='store_true')
    parser.add_argument('--augmclb_only',action='store_true')
    parser.add_argument('--alg',type=str)

    # to limit load balncing
    parser.add_argument('--no_lb_only',action='store_true')
    parser.add_argument('--hops_lb_only',action='store_true')
    parser.add_argument('--paths_lb_only',action='store_true')


    parser.add_argument('--inj_start',type=float,default=0.01)
    parser.add_argument('--inj_end',type=float,default=0.1)
    parser.add_argument('--inj_step',type=float,default=0.01)

    parser.add_argument('--n_evn',type=int)
    parser.add_argument('--tot_vcs',type=int)

    parser.add_argument('--sys_clk',type=float,default=2.0)
    parser.add_argument('--num_cpus',type=int,default=128)
    parser.add_argument('--dir_mult',type=int,default=8)

    parser.add_argument('--map_file_dir',type=str,default='./configs/topologies/paper_solutions/')

    parser.add_argument('--weighted_mclb',action='store_true')


    args = parser.parse_args()

    sim_cycle = args.sim_cycles

    map_files_dir = args.map_file_dir
    for root, dirs, files in os.walk(map_files_dir):
        # print(files)
        map_files += files


    # if args.inj_start is not None or\
    #         args.inj_end is not None or\
    #         args.inj_step is not None:
    #     # factor of 100 since range only takes ints
    #     # should np.linspace or something later
    #     a = int(1000*args.inj_start)
    #     b = int(1000*args.inj_end)
    #     c = int(1000*args.inj_step)

    #     inj_rates = [str(x/1000.0) for x in range(a,b,c)]

    inj_rates = np.arange(args.inj_start, args.inj_end,args.inj_step)
    inj_rates = [str(round(x,4)) for x in inj_rates]

    # print(f'inj_rates={inj_rates}')
    # quit()

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
                        or 'ft' in s\
                        or 'lpbt' in s]


    ###################################################################
    # here for manual changes

    undesired = []#['butter','mesh','cmesh']

    for u in undesired:
        map_files = [s for s in map_files if u not in s]
    ###################################################################


    # map_files = [s for s in map_files if 'butter' in s]
    map_files = [s for s in map_files if 'noci' in s]

    map_files = ['mesh_noci.map']

    print(f'map_files={map_files}')
    # quit()

    alg_types = ['naive','bsorm','bsorm_zindexed','cload_picky']#,'cload_zindexed']

    if args.naive_only:
        alg_types = ['naive']
    elif args.bsorm_only:
        alg_types = ['bsorm','bsorm_zindexed']
    elif args.cload_only:
        alg_types = ['cload_picky']#,'cload_zindexed']
    elif args.augmclb_only:
        alg_types = ['augmclb']

    if args.alg is not None:
        alg_types = [args.alg]

    lb_types = ['none','hops','paths']

    if args.no_lb_only:
        lb_types = ['none']
    elif args.hops_lb_only:
        lb_types = ['hops']
    elif args.paths_lb_only:
        lb_types = ['paths']


    # map_files = [s for s in map_files if 'kite_large' in s]

    n_evns = [3,4]

    if args.n_evn:
        n_evns = [int(args.n_evn)]

    tot_vcs = 4
    if args.tot_vcs:
        tot_vcs = [int(args.tot_vcs)]

    clk = args.sys_clk
    n_cpus = args.num_cpus
    dir_mult = args.dir_mult

    weighted_mclb = args.weighted_mclb


    i = 0
    for het in het_tf:
        for mc in memcoh:
            for ir in inj_rates:
                for sf in map_files:
                    for a_t in alg_types:
                        for lb_t in lb_types:
                            for vn in n_evns:
                                for tv in tot_vcs:
                                    print(f'{i:04} : Adding {sf} {a_t} {lb_t} {ir} {mc}')
                                    runs += [BenchmarkRun(sf, mc, sim_cycle, ir, het, a_t, lb_t, vn, tv, clk, n_cpus, dir_mult,weighted_mclb)]
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