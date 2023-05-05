import sys

benchmark_choices = ["blackscholes", "bodytrack", "canneal", "dedup",
                                          "facesim", "ferret", "fluidanimate", "freqmine",
                                          "raytrace", "streamcluster", "swaptions", "vips", "x264"]

print(f'bench_choices={benchmark_choices}')

if len(sys.argv) < 2:
    print(f'wrong number args')
    print(f'supply desired benchmark')
    quit()

bench = sys.argv[1]

nreps = None
try:
    nreps = int(sys.argv[2])
except:
    pass

system_num = 6

if nreps is not None:
    cmd = f'./build/X86/gem5.fast -d ./parsec_noci_checkpoints/roi_checkpoint/system_5/{bench}_{nreps}reps configs/auto_top/auto_top_fs_readfile_loop.py --num-cpus 64 --num-dirs 16 --mem-size 32GB --kernel parsec_disk_image/vmlinux-5.4.49 --disk-image parsec_disk_image/x86-parsec --cpu-type X86KvmCPU --caches --l2_size 2MB --num-l2caches 64 --sys-clock 1.8GHz --benchmark_parsec {bench} --repeated_multi_prog {nreps} --restore-with-cpu X86KvmCPU -r 1 --checkpoint-dir ./after_boot/system_5/'
else:
    cmd = f'./build/X86/gem5.fast -d ./parsec_noci_checkpoints/roi_checkpoint/system_5/{bench} configs/auto_top/auto_top_fs_readfile_loop.py --num-cpus 64 --num-dirs 16 --mem-size 32GB --kernel parsec_disk_image/vmlinux-5.4.49 --disk-image parsec_disk_image/x86-parsec --cpu-type X86KvmCPU --caches --l2_size 2MB --num-l2caches 64 --sys-clock 1.8GHz --benchmark_parsec {bench} --restore-with-cpu X86KvmCPU -r 1 --checkpoint-dir ./after_boot/system_5/'

print('')
print(f'{cmd}')


# TODO: vips, x264