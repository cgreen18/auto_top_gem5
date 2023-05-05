
# simple misaligned: 20r, 64 cpu, 64 dir. Read topo from file
./build/Garnet_standalone/gem5.opt configs/auto_top/synth_fromfile_normal.py --num-cpus=64 --num-dirs=64 --network=garnet --topology=Simple_Misaligned --sim-cycles=10000 --synthetic=uniform_random --injectionrate=0.01

