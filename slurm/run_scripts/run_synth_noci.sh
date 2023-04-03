#!/bin/bash


TLIM="10-00:00:00"

sbatch -t $TLIM slurm/job_scripts/synth_noci_naive_no_lb

# sbatch -t $TLIM slurm/job_scripts/synth_noci_naive_hops_lb