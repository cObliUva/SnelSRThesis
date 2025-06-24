#!/bin/bash
#SBATCH --job-name=cFerLoT
#SBATCH --output=output_%j.txt
#SBATCH --error=error_%j.txt
#SBATCH --time=010:00:00
#SBATCH --cpus-per-task=64
#SBATCH --mem=32G

module load 2024

# load python module
module load Python/3.12.3-GCCcore-13.3.0

# Activate the virtual environment
source ~/lotlib3-env/bin/activate

# run scripts
python LoT.py 1B
python LoT.py 2B
