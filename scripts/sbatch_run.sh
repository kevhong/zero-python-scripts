#!/bin/bash
#
#SBATCH --mail-user=khong@uchicago.edu
#SBATCH --mail-type=ALL
#SBATCH --output=/home/khong/slurm/slurm_out/%j.%N.stdout
#SBATCH --error=/home/khong/slurm/slurm_out/%j.%N.stderr
#SBATCH --workdir=/home/khong/slurm
#SBATCH --partition=debug
#SBATCH --job-name=python_scripts
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=23:20:00


python xct_to_pid.py
python histogram.py
python toSPMF.py