#!/bin/bash           # the shell language when run outside of the job scheduler
#$ -S /bin/bash       # the shell language when run via the job scheduler [IMPORTANT]
#$ -cwd               # job should run in the current working directory
#$ -j y               # STDERR and STDOUT should be joined
#$ -N H1_Prota
#$ -l h_rt=02:00:00   # job requires up to 24 hours of runtime; use small times to dodge the queue
#$ -l compute_cap=86  # require A40- specifies GPU
#$ -l mem_free=2G
#$ -l gpu_mem=10000  #keeps the GPU free from other jobs; keep in MB
#$ -t 1-5
#$ -tc 1

module load Sali
module load cuda/11.0
conda activate python39

export CUDA_VISIBLE_DEVICES=$SGE_GPU

python restart_h1_prota_prod.py

exit_code=$?
pipe="shared_pipe.txt"
echo "$exit_code" > "$pipe"