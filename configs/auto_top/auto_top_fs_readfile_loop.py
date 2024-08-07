# Copyright (c) 2010-2013, 2016, 2019-2020 ARM Limited
# Copyright (c) 2020 Barkhausen Institut
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2012-2014 Mark D. Hill and David A. Wood
# Copyright (c) 2009-2011 Advanced Micro Devices, Inc.
# Copyright (c) 2006-2007 The Regents of The University of Michigan
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

import argparse
import sys

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal, warn
from m5.util.fdthelper import *

from os.path import join as joinpath
import time

addToPath('../')

from ruby import Ruby

from common.FSConfig import *
from common.SysPaths import *
from common.Benchmarks import *
from common import Simulation
from common import CacheConfig
from common import CpuConfig
from common import MemConfig
from common import ObjectList
from common.Caches import *
from common import Options

def cmd_line_template():
    if args.command_line and args.command_line_file:
        print("Error: --command-line and --command-line-file are "
              "mutually exclusive")
        sys.exit(1)
    if args.command_line:
        return args.command_line
    if args.command_line_file:
        return open(args.command_line_file).read().strip()
    return None

def writeRepeatedHomogenousMultiProgBenchScript(dir, bench, repetitions, size, ncpus):

    cpus_per_prog = ncpus // repetitions

    assert(ncpus % repetitions == 0)

    file_name = f'{dir}/run_{bench}_repeated{repetitions}'

    cmd = f'cd /home/gem5/parsec-benchmark; source env.sh;'
    
    for rep in range(repetitions):
        cmd += f' parsecmgmt -a run -p {bench} -c gcc-hooks -i {size} -n {cpus_per_prog}'

        # not last rep
        if rep + 1 < repetitions:
            cmd += ' &'

    cmd += '; sleep 5; m5 exit;'

    print(f'writeRepeatedHomogenousMultiProgBenchScript():: cmd = {cmd}')

    with open(file_name, "w+") as bench_file:
        bench_file.write(cmd)
    
    return file_name

def writeReadfileBenchScript(dir, guest_num):

    runscript_file_name = f'{dir}/guest_{guest_num}_runscript'


    # lets call runscript that which runs after boot
    #   and readfile the one that is read and contains directions for parsec

    # runscript cmd
    # cmd = 'm5 exit; m5 readfile;'
    # cmd = 'touch /tmp/execfile; chmod +x /tmp/execfile; m5 exit; m5 readfile | bash'
    cmd = 'm5 exit; m5 readfile | bash'

    with open(runscript_file_name, "w+") as f:
        f.write(cmd)



    return runscript_file_name

def writeBootScript(dir):
    """
    This method creates a script in dir which will be eventually
    passed to the simulated system (to run a specific benchmark
    at bootup).
    """

    # m5 checkpoint;
    cmd = f'm5 exit'

    file_name = f'{dir}/run_boot'
    with open(file_name,"w+") as bench_file:

        bench_file.write(cmd)

    return file_name

def writeMultiProgBenchScript(dir, bench_a, bench_b, size, ncpus):

    file_name = f'{dir}/run_{bench_a}_{bench_b}'

    half_cpus = ncpus // 2
    other_half_cpus = ncpus - half_cpus

    cmd = f'cd /home/gem5/parsec-benchmark; source env.sh; parsecmgmt -a run -p {bench_a} -c gcc-hooks -i simlarge -n {half_cpus} & parsecmgmt -a run -p {bench_b} -c gcc-hooks -i simlarge -n {other_half_cpus}; m5 exit; sleep 5; m5 exit;'

    with open(file_name, "w+") as bench_file:
        bench_file.write(cmd)

    return file_name

def writeBenchScript(dir, bench, size, ncpus):
    """
    This method creates a script in dir which will be eventually
    passed to the simulated system (to run a specific benchmark
    at bootup).
    """
    file_name = '{}/run_{}'.format(dir, bench)
    bench_file = open(file_name,"w+")

    # m5 checkpoint;
    cmd = f'cd /home/gem5/parsec-benchmark; source env.sh; parsecmgmt -a run -p {bench} -c gcc-hooks -i {size} -n {ncpus}; sleep 5; m5 exit;'

    bench_file.write(cmd)

    return file_name

def build_test_system(np, readfile_name, bm):

    # print(f'build_test_system. bm={bm}')
    # quit(-1)

    cmdline = cmd_line_template()
    if buildEnv['TARGET_ISA'] == "x86":
        test_sys = makeLinuxX86System(test_mem_mode, np, bm[0], args.ruby,
                                      cmdline=cmdline)

    else:
        fatal("Incapable of building %s full system!", buildEnv['TARGET_ISA'])

    # Set the cache line size for the entire system
    test_sys.cache_line_size = args.cacheline_size

    # Create a top-level voltage domain
    test_sys.voltage_domain = VoltageDomain(voltage = args.sys_voltage)

    # Create a source clock for the system and set the clock period
    test_sys.clk_domain = SrcClockDomain(clock =  args.sys_clock,
            voltage_domain = test_sys.voltage_domain)

    # Create a CPU voltage domain
    test_sys.cpu_voltage_domain = VoltageDomain()

    # Create a source clock for the CPUs and set the clock period
    test_sys.cpu_clk_domain = SrcClockDomain(clock = args.cpu_clock,
                                             voltage_domain =
                                             test_sys.cpu_voltage_domain)

    if buildEnv['TARGET_ISA'] == 'riscv':
        test_sys.workload.bootloader = args.kernel
    elif args.kernel is not None:
        test_sys.workload.object_file = binary(args.kernel)

    test_sys.readfile = readfile_name
    if args.script is not None:
        test_sys.readfile = args.script


    test_sys.init_param = args.init_param

    # For now, assign all the CPUs to the same clock domain
    test_sys.cpu = [TestCPUClass(clk_domain=test_sys.cpu_clk_domain, cpu_id=i)
                    for i in range(np)]

    if args.ruby:
        bootmem = getattr(test_sys, '_bootmem', None)
        Ruby.create_system(args, True, test_sys, test_sys.iobus,
                           test_sys._dma_ports, bootmem)

        # Create a seperate clock domain for Ruby
        test_sys.ruby.clk_domain = SrcClockDomain(clock = args.ruby_clock,
                                        voltage_domain = test_sys.voltage_domain)

        # Connect the ruby io port to the PIO bus,
        # assuming that there is just one such port.
        test_sys.iobus.mem_side_ports = test_sys.ruby._io_port.in_ports

        for (i, cpu) in enumerate(test_sys.cpu):
            #
            # Tie the cpu ports to the correct ruby system ports
            #
            cpu.clk_domain = test_sys.cpu_clk_domain
            cpu.createThreads()
            cpu.createInterruptController()

            test_sys.ruby._cpu_ports[i].connectCpuPorts(cpu)

    else:
        if args.caches or args.l2cache:
            # By default the IOCache runs at the system clock
            test_sys.iocache = IOCache(addr_ranges = test_sys.mem_ranges)
            test_sys.iocache.cpu_side = test_sys.iobus.mem_side_ports
            test_sys.iocache.mem_side = test_sys.membus.cpu_side_ports
        elif not args.external_memory_system:
            test_sys.iobridge = Bridge(delay='50ns', ranges = test_sys.mem_ranges)
            test_sys.iobridge.cpu_side_port = test_sys.iobus.mem_side_ports
            test_sys.iobridge.mem_side_port = test_sys.membus.cpu_side_ports

        # Sanity check
        if args.simpoint_profile:
            if not ObjectList.is_noncaching_cpu(TestCPUClass):
                fatal("SimPoint generation should be done with atomic cpu")
            if np > 1:
                fatal("SimPoint generation not supported with more than one CPUs")

        for i in range(np):
            if args.simpoint_profile:
                test_sys.cpu[i].addSimPointProbe(args.simpoint_interval)
            if args.checker:
                test_sys.cpu[i].addCheckerCpu()
            if not ObjectList.is_kvm_cpu(TestCPUClass):
                if args.bp_type:
                    bpClass = ObjectList.bp_list.get(args.bp_type)
                    test_sys.cpu[i].branchPred = bpClass()
                if args.indirect_bp_type:
                    IndirectBPClass = ObjectList.indirect_bp_list.get(
                        args.indirect_bp_type)
                    test_sys.cpu[i].branchPred.indirectBranchPred = \
                        IndirectBPClass()
            test_sys.cpu[i].createThreads()

        # If elastic tracing is enabled when not restoring from checkpoint and
        # when not fast forwarding using the atomic cpu, then check that the
        # TestCPUClass is DerivO3CPU or inherits from DerivO3CPU. If the check
        # passes then attach the elastic trace probe.
        # If restoring from checkpoint or fast forwarding, the code that does this for
        # FutureCPUClass is in the Simulation module. If the check passes then the
        # elastic trace probe is attached to the switch CPUs.
        if args.elastic_trace_en and args.checkpoint_restore == None and \
            not args.fast_forward:
            CpuConfig.config_etrace(TestCPUClass, test_sys.cpu, args)

        CacheConfig.config_cache(args, test_sys)

        MemConfig.config_mem(args, test_sys)

    if ObjectList.is_kvm_cpu(TestCPUClass) or \
        ObjectList.is_kvm_cpu(FutureClass):
        # Assign KVM CPUs to their own event queues / threads. This
        # has to be done after creating caches and other child objects
        # since these mustn't inherit the CPU event queue.
        for i,cpu in enumerate(test_sys.cpu):
            # Child objects usually inherit the parent's event
            # queue. Override that and use the same event queue for
            # all devices.
            for obj in cpu.descendants():
                obj.eventq_index = 0
            cpu.eventq_index = i + 1
        test_sys.kvm_vm = KvmVM()

    return test_sys


# Add args
parser = argparse.ArgumentParser()
Options.addCommonOptions(parser)
Options.addFSOptions(parser)



# for auto top
parser.add_argument("--router_map_file", type=str, default="configs/topologies/sol_files/kite_small.sol",
                    help=".sol file with router map.")

parser.add_argument("--flat_nr_map_file", type=str,
                    default="configs/topologies/nr_list/kite_large_naive.nrl",
                    help=".")

parser.add_argument("--flat_vn_map_file", type=str,
                    default="configs/topologies/vn_maps/kite_large_naive_hops.vn",
                    help=".")

parser.add_argument("--inj-vnet", type=int, default=-1,
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

parser.add_argument('--synth_traffic',action='store_true')

# ##
parser.add_argument('--boot_w_kvm',action='store_true')

parser.add_argument('--benchmark_parsec',type=str)

parser.add_argument('--first_parsec',type=str,default='bodytrack')

parser.add_argument('--second_parsec',type=str,default='dedup')

parser.add_argument('--multi_prog',action='store_true')

parser.add_argument('--max_insts_after_boot',type=int,default=1000000000)

# {AtomicSimpleCPU,BaseAtomicSimpleCPU,BaseMinorCPU,BaseNonCachingSimpleCPU,BaseO3CPU,BaseTimingSimpleCPU,DerivO3CPU,NonCachingSimpleCPU,O3CPU,TimingSimpleCPU,X86AtomicSimpleCPU,X86KvmCPU,X86NonCachingSimpleCPU,X86O3CPU,X86TimingSimpleCPU}
parser.add_argument('--switch_cpu',type=str)

parser.add_argument('--timing_insts',type=int,default=100000)

parser.add_argument('--repeated_multi_prog',type=int)


# Add the ruby specific and protocol specific args
if '--ruby' in sys.argv:
    Ruby.define_options(parser)

args = parser.parse_args()

# TODO: unhardcode
args.use_escape_vns = True


# system under test can be any CPU
(TestCPUClass, test_mem_mode, FutureClass) = Simulation.setCPUClass(args)

if args.switch_cpu is not None:
    FutureClass, _future_mem_type = Simulation.getCPUClass(args.switch_cpu)

# Match the memories with the CPUs, based on the options for the test system
TestMemClass = Simulation.setMemClass(args)

bm = [SysConfig(disks=args.disk_image, rootdev=args.root_device,
                mem=args.mem_size, os_type=args.os_type)]


np = args.num_cpus

command_file_name = writeBootScript('configs/auto_top/runscripts')

# def writeBenchScript(dir, bench, size, ncpus):
if args.benchmark_parsec is not None:
    bench = args.benchmark_parsec
    size = 'simlarge'
    # size = 'native'
    command_file_name = writeBenchScript('configs/auto_top/runscripts',bench, size, np )

if args.repeated_multi_prog is not None:
    bench = args.benchmark_parsec
    size = 'simlarge'
    # size = 'native'
    nreps = args.repeated_multi_prog
    # def writeRepeatedHomogenousMultiProgBenchScript(dir, bench, repetitions, size, ncpus):
    command_file_name = writeRepeatedHomogenousMultiProgBenchScript('configs/auto_top/runscripts',bench,nreps ,size, np )


if args.script:
    command_file_name = args.script

test_sys = build_test_system(np, command_file_name , bm)



# avoid running out of host memory
test_sys.mmap_using_noreserve = True


root = Root(full_system=True, system=test_sys)


if ObjectList.is_kvm_cpu(TestCPUClass) or \
    ObjectList.is_kvm_cpu(FutureClass):
    # Required for running kvm on multiple host cores.
    # Uses gem5's parallel event queue feature
    # Note: The simulator is quite picky about this number!
    root.sim_quantum = int(1e9) # 1 ms


if args.maxinsts:
    for i in range(np):
        test_sys.cpu[i].max_insts_any_thread = args.maxinsts


switch_cpus = None
if FutureClass:
    print(f'there is FutureClass={FutureClass}')
    # quit(-1)
    switch_cpus = [FutureClass(switched_out=True, cpu_id=(i))
                    for i in range(np)]

    for i in range(np):
        # not for now
        # if options.fast_forward:
        #     testsys.cpu[i].max_insts_any_thread = int(options.fast_forward)
        switch_cpus[i].system = test_sys
        switch_cpus[i].workload = test_sys.cpu[i].workload
        switch_cpus[i].clk_domain = test_sys.cpu[i].clk_domain
        switch_cpus[i].progress_interval = \
            test_sys.cpu[i].progress_interval
        switch_cpus[i].isa = test_sys.cpu[i].isa

        # not for now
        # simulation period
        if args.maxinsts:
            switch_cpus[i].max_insts_any_thread = args.maxinsts

        switch_cpus[i].createThreads()


    test_sys.switch_cpus = switch_cpus

    switch_cpu_list = [(test_sys.cpu[i], switch_cpus[i]) for i in range(np)]



if args.wait_gdb:
    test_sys.workload.wait_for_remote_gdb = True


# Exit from guest on workbegin/workend
test_sys.exit_on_work_items = True


Simulation.setWorkCountOptions(test_sys, args)

print("Running the simulation")

print(f'Beginning {TestCPUClass} simulation')
print(f'Later, {FutureClass} simulation')

print(f'Running: {command_file_name}')

print(f'1st cpu will run for {test_sys.cpu[0].max_insts_any_thread} insts')
if switch_cpus is not None:
    print(f'2nd cpu will run for {switch_cpus[0].max_insts_any_thread} insts')



if args.checkpoint_dir:
    in_cptdir = args.checkpoint_dir
else:
    in_cptdir = getcwd()

checkpoint_dir = None
if args.checkpoint_restore:
    cpt_starttick, checkpoint_dir = Simulation.findCptDir(args, in_cptdir, test_sys)
root.apply_config(args.param)

print(f'Will restore from {checkpoint_dir}')

# cont = input('continue?')
# if 'n' in cont:
#    quit(-1)


m5.instantiate(checkpoint_dir)

print(f'Instantiatied')
print(f'If applicable, restored from {checkpoint_dir}')

# now cptdir should be redefined to be the OUTPUT dir
cptdir = m5.options.outdir

print(f'Will output checkpoints to {cptdir}')


keep_going = True

n_to_skip = 0
# if args.repeated_multi_prog is not None:
#     n_to_skip = args.repeated_multi_prog - 1

abs_start = -1

n_exits = 0

while keep_going:


    cont = input('continue?')
    if 'n' in cont:
        quit(-1)

    start_time = time.time()
    start_tick = m5.curTick()
    if abs_start == -1:
        abs_start = start_time


    exit_event = m5.simulate()

    end_tick = m5.curTick()
    end_time = time.time()
    n_exits += 1

    print("Exiting @ tick {} because {} ({}).".format(
            m5.curTick(),
            exit_event.getCause(),
            n_exits ))



    # Simulation is over at this point. We acknowledge that all the simulation
    # events were successful.
    print("All simulation events were successful.")

    # We print the final simulation statistics.

    print(f"Done with the simulation of {command_file_name}")
    print()
    print("Performance statistics:")

    print("Simulated time: %.2fs" % ((end_tick-start_tick)/1e12))
    print("Ran a total of ", m5.curTick()/1e12, " simulated seconds")
    print(f'Real time: {end_time-start_time:.2f}s')
    print(f'Total real time: {end_time-abs_start:.2f}s')

    print(f'Dumping and resetting stats...')

    # m5.stats.dump()
    m5.stats.reset()


    do_chkpt = input('USER INPUT: checkpoint?')

    if 'y' in do_chkpt:
        m5.checkpoint(joinpath(cptdir, f"cpt.{m5.curTick()}"))

        print(f'Wrote checkpoint to : {joinpath(cptdir, f"cpt.{m5.curTick()}")}')

    # if n_to_skip <= 0:
        # m5.checkpoint(joinpath(cptdir, f"cpt.{m5.curTick()}"))


        # print(f'Wrote checkpoint to : {joinpath(cptdir, f"cpt.{m5.curTick()}")}')


        # cont = input('continue?')
        # if 'n' in cont:
        #     quit(-1)

    # else:
    #     n_to_skip -= 1


    if switch_cpus is not None:
        do_chkpt = input('USER INPUT: switch cpus?')

        if 'y' in do_chkpt:
            print("Switched CPUS @ tick %s" % (m5.curTick()))

            m5.switchCpus(test_sys, switch_cpu_list)
