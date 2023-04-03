#!/bin/bash
TLIM="20-00:00:00"
sbatch --exclude=mnemosyne -t $TLIM slurm/job_scripts/parsec_noci_largemem_18GHz_500kB/100m/blackscholes_kite_large_noci