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
# Author: Tushar Krishna

import m5
from m5.objects import *
from m5.defines import buildEnv
from m5.util import addToPath
import os, argparse, sys

addToPath('../')

from common import Options
from ruby import Ruby

# Get paths we might need.  It's expected this file is in m5/configs/example.
config_path = os.path.dirname(os.path.abspath(__file__))
config_root = os.path.dirname(config_path)
m5_root = os.path.dirname(config_root)

parser = argparse.ArgumentParser()
Options.addNoISAOptions(parser)

parser.add_argument("--synthetic", default="uniform_random",
                    choices=['uniform_random', 'tornado', 'bit_complement', \
                             'bit_reverse', 'bit_rotation', 'neighbor', \
                             'shuffle', 'transpose'])

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
parser.add_argument("--router_map_file", type=str, default="configs/topologies/sol_files/kite_small.sol",
                    help=".sol file with n routers/ports and router map.")

parser.add_argument("--num_mems", type=int, default=16,
                         help="Number of memory-like controllers. They are senders")

# not set up yet
parser.add_argument("--inj-vnet", type=int, default=-1,
                    choices=[-3,-2,-1,0,1,2,3],
                    help="Only inject in this vnet (0, 1, 2, or 3).\
                        0/1 is coh req/resp at 1/5-flit.\
                        2/3 is mem req/resp at 1/5-flit.\
                        -1 => inject randomly in all vnets.\
                        -2 => inject randomly vnet 0 or 1.\
                        -3 => inject randomly vnet 2 or 3.")


parser.add_argument("--number_of_virtual_networks", type=int, default=4,
                         help="number of virtual networks")


#
# Add the ruby specific and protocol specific options
#
Ruby.define_options(parser)

args = parser.parse_args()

n_targs_cpus = args.num_cpus + args.num_dirs

n_targs_mems = args.num_cpus

cpus = []

# coh reads and writes
# vnet 0 and 1 = -2
# 64 -> 64
cpus += [ AutoTopSynth(
                     num_packets_max=args.num_packets_max,
                     single_sender=args.single_sender_id,
                     single_dest=args.single_dest_id,
                     sim_cycles=args.sim_cycles,
                     traffic_type=args.synthetic,
                     inj_rate=args.injectionrate,
                     inj_vnet=-2,
                     precision=args.precision,
                     num_dest=args.num_cpus,
                     base_dest=0) \
         for i in range(args.num_cpus) ]



# # cpu to mem reads and writes
# # vnet 2 and 3 = -3
# # 64 -> 16 (count these as "after" the first 64)

cpus += [ AutoTopSynth(
                     num_packets_max=args.num_packets_max,
                     single_sender=args.single_sender_id,
                     single_dest=args.single_dest_id,
                     sim_cycles=args.sim_cycles,
                     traffic_type=args.synthetic,
                     inj_rate=args.injectionrate,
                     inj_vnet=-3,
                     precision=args.precision,
                     num_dest=args.num_mems,
                     base_dest=args.num_cpus) \
         for i in range(args.num_cpus) ]

# # mem to cpu reads and writes
# # vnet 2 and 3 = -3
# # 16 -> 64

cpus += [ AutoTopSynth(
                     num_packets_max=args.num_packets_max,
                     single_sender=args.single_sender_id,
                     single_dest=args.single_dest_id,
                     sim_cycles=args.sim_cycles,
                     traffic_type=args.synthetic,
                     inj_rate=args.injectionrate,
                     inj_vnet=-3,
                     precision=args.precision,
                     num_dest=args.num_cpus,
                     base_dest=0) \
         for i in range(args.num_mems) ]


print(f'cpus({len(cpus)})={cpus})')

# pass this along the ruby chain lol
args.num_cpus = len(cpus)

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

# -----------------------
# run simulation
# -----------------------

print("autotop_synth:: About to run simulation")

root = Root(full_system = False, system = system)
root.system.mem_mode = 'timing'

# Not much point in this being higher than the L1 latency
m5.ticks.setGlobalFrequency('1ps')

# instantiate configuration
m5.instantiate()

# simulate until program terminates
exit_event = m5.simulate(args.abs_max_tick)

print('Exiting @ tick', m5.curTick(), 'because', exit_event.getCause())
