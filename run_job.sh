#!/bin/bash
#SBATCH --job-name=cFerLoT
#SBATCH --output=output_%j.txt
#SBATCH --error=error_%j.txt
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=64
#SBATCH --mem=32G

# load python module
module load Python/3.10.4-GCCcore-11.3.0

# Activate the virtual environment
source ~/lotlib3-env/bin/activate

# run scripts
python your_script.py 1B
python your_script.py 2B