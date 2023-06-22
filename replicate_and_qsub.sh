#!/bin/bash

source_dir="h1_prota_sim"
num_copies=10
test_job_file="job.sh"

if [ ! -d "$source_dir" ]; then
  echo "Error: '$source_dir' is not a valid directory."
  exit 1
fi

original_dir_name=$(basename "$source_dir")

for i in $(seq 1 $num_copies); do
  new_dir_name="${original_dir_name}_${i}"
  cp -r "$source_dir" "$new_dir_name"
  cd "$new_dir_name" || exit 1
  chmod +x job_coord.sh
  ./job_coord.sh &
  cd .. || exit 1
  sleep 1

done