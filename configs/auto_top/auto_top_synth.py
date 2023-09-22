# Copyright (c) 2023 Purdue University
# Copyright (c) 2016 Georgia Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Conor Green

import m5
from m5.objects import *
from m5.defines import buildEnv
from m5.util import addToPath
import os, argparse, sys

addToPath('../')

from common import Options
from ruby import Ruby


def ingest_map(path_name):

    print(f'ingesting {path_name}')

    r_map = []

    with open(path_name, 'r') as in_file:

        # for _router in range(0,n_routers):
        #     row = in_file.readline()
        for row in in_file:
            row = row.replace('\n','')
            r_conns = row.split(" ")
            if '' in r_conns:
                r_conns.remove('')
            # print(f'row={row}')
            # print(r_conns)
            # print(type(r_conns[0]))

            try:
                r_conns = [int(elem) for elem in r_conns]
            except Exception as e:
                print(f'e={e}')
                r_conns = [int(float(elem)) for elem in r_conns]
            r_map.append(r_conns)

    #print(f'r_map({len(r_map)})={r_map}')

    # print(f'n_routers={n_routers}')

    # assert(len(r_map) == n_routers)

    return r_map




# Get paths we might need.  It's expected this file is in m5/configs/example.
config_path = os.path.dirname(os.path.abspath(__file__))
config_root = os.path.dirname(config_path)
m5_root = os.path.dirname(config_root)

parser = argparse.ArgumentParser()
Options.addNoISAOptions(parser)

parser.add_argument("--synthetic", default="uniform_random",
                    choices=['uniform_random', 'tornado', 'bit_complement', \
                             'bit_reverse', 'bit_rotation', 'neighbor', \
                             'shuffle', 'transpose','vc_test'])

parser.add_argument("-i", "--injectionrate", type=float, default=0.1,
                    metavar="I",
                    help="Injection rate in packets per cycle per node. \
                        Takes decimal value between 0 to 1 (eg. 0.225). \
                        Number of digits after 0 depends upon --precision.")

parser.add_argument("--precision", type=int, default=3,
                    help="Number of digits of precision after decimal point\
                        for injection rate")

parser.add_argument("--sim-cycles", type=int, default=1000,
                    help="Number of simulation cycles")

parser.add_argument("--num-packets-max", type=int, default=-1,
                    help="Stop injecting after --num-packets-max.\
                        Set to -1 to disable.")

parser.add_argument("--single-sender-id", type=int, default=-1,
                    help="Only inject from this sender.\
                        Set to -1 to disable.")

parser.add_argument("--single-dest-id", type=int, default=-1,
                    help="Only send to this destination.\
                        Set to -1 to disable.")

# parser.add_argument("--inj-vnet", type=int, default=-1,
#                     choices=[-1,0,1,2],
#                     help="Only inject in this vnet (0, 1 or 2).\
#                         0 and 1 are 1-flit, 2 is 5-flit.\
#                         Set to -1 to inject randomly in all vnets.")

# for auto top
parser.add_argument("--router_map_file", type=str, default="configs/topologies/paper_solutions/kite_large.map",
                    help=".sol file with router map.")

parser.add_argument("--vc_map_file", type=str, default="configs/topologies/paper_vcs/kite_large.vc",
                    help=".vc file with vc map.")

parser.add_argument("--nr_map_file", type=str, default="configs/topologies/paper_nrs/kite_large.nr",
                    help=".nr file with next rotuer map.")

parser.add_argument("--flat_nr_map_file", type=str, 
                    default="configs/topologies/nrl_files/kite_large_naive.nrl",
                    help=".")

parser.add_argument("--flat_vn_map_file", type=str,
                    default="configs/topologies/vn_maps/kite_large_naive_none.vn",
                    help=".")

parser.add_argument("--inj-vnet", type=int, default=-2,
                    choices=[-2,-1,0,1,2],
                    help="Only inject in this vnet (0, 1, or 2).\
                        -1 => inject randomly in all vnets.\
                        -2 => inject randomly vnet 0 or 2.")

parser.add_argument("--num_chiplets", type=int, default=4,
                help="number of chiplets on the system")

parser.add_argument("--cpus-per-router", type=int, default=4,
                    help="TODO")

parser.add_argument("--noc_rows", type=int, default=4,
                    help="TODO")

parser.add_argument("--noi_rows", type=int, default=4,
                    help="TODO")

parser.add_argument("--noi_routers", type=int, default=20,
                    help="TODO")

parser.add_argument("--noc_clk", type=str, default='1.8GHz',
                    help="TODO")

parser.add_argument("--noi_clk", type=str, default='1.8GHz',
                    help="TODO")

parser.add_argument("--mem_or_coh", type=str, default='mem',
                    help="TODO")


parser.add_argument("--evn_deadlock_partition", type=int, default=0,
                    help="TODO")

parser.add_argument("--evn_n_deadlock_free", type=int, default=2,
                    help="TODO")

parser.add_argument("--evn_min_n_deadlock_free", type=int, default=2,
                    help="TODO")

parser.add_argument("--use_escape_vns",action='store_true')

parser.add_argument("--use_vll",action='store_true')

parser.add_argument('--synth_traffic',action='store_true')

parser.add_argument('--vc_to_test',type=int,default=-1)

# Add the ruby specific and protocol specific options
#
Ruby.define_options(parser)

args = parser.parse_args()

cpus = []


# VN map
flat_vn_map = ingest_map(args.flat_vn_map_file)


n_noi = args.noi_routers
np = args.num_cpus


# reads and writes
# vnet 0 and 1 = -2
cpus += [ GarnetSyntheticTraffic(
                     num_packets_max=args.num_packets_max,
                     single_sender=args.single_sender_id,
                     single_dest=args.single_dest_id,
                     sim_cycles=args.sim_cycles,
                     traffic_type=args.synthetic,
                     inj_rate=args.injectionrate,
                     inj_vnet=args.inj_vnet,
                     precision=args.precision,
                     num_dest=args.num_dirs,
                     ) \
         for i in range(args.num_cpus) ]

print(f'cpus({len(cpus)})={cpus})')


# create the desired simulated system
system = System(cpu = cpus, mem_ranges = [AddrRange(args.mem_size)])


# Create a top-level voltage domain and clock domain
system.voltage_domain = VoltageDomain(voltage = args.sys_voltage)

system.clk_domain = SrcClockDomain(clock = args.sys_clock,
                                   voltage_domain = system.voltage_domain)

Ruby.create_system(args, False, system)

# Create a seperate clock domain for Ruby
system.ruby.clk_domain = SrcClockDomain(clock = args.ruby_clock,
                                        voltage_domain = system.voltage_domain)



i = 0
for ruby_port in system.ruby._cpu_ports:
     #
     # Tie the cpu test ports to the ruby cpu port
     #
     cpus[i].test = ruby_port.in_ports
     i += 1

# print(f' system.ruby = { system.ruby}')



# -----------------------
# run simulation
# -----------------------

print("autotop_synth:: About to run simulation")

root = Root(full_system = False, system = system)
root.system.mem_mode = 'timing'

# print(f'\tattrs...')
# for k,v in system.ruby.__dict__.items():
#     print(f'\t\t{k} : {v}')
# print('-'*72)
# quit(-1)

# Not much point in this being higher than the L1 latency
m5.ticks.setGlobalFrequency('1ps')

# instantiate configuration
m5.instantiate()

# simulate until program terminates
exit_event = m5.simulate(args.abs_max_tick)

print('Exiting @ tick', m5.curTick(), 'because', exit_event.getCause())
