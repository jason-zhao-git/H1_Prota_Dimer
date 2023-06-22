#!/bin/bash

job_name="H1_Prota"
job_file="job.sh"
restart_file="array.sh"
pipe="shared_pipe.txt"

echo 0 > "$pipe"
job_id=$(qsub -q gpu.q "$job_file")
job_id=$(echo $job_id | grep -oE '[0-9]+'| head -n 1)
echo "$job_id"
exit_code=0

while [ $exit_code -ne 73 ]; do
    if qstat -s r | grep -q "$job_id" || qstat | grep qw | grep -q "$job_id"; then
        sleep 20
        #echo "$job_id"
        #echo "checked"
    else
        echo "Old: $job_id"
        job_id=$(qsub -q gpu.q "$restart_file")
        job_id=$(echo $job_id | grep -oE '[0-9]+' | head -n 1)
        echo "New: $job_id"
        echo "changed"
        sleep 20
    fi
    python datalog.py
    exit_code=$(cat "$pipe")
done

echo 0 > "$pipe"