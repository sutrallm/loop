#!/bin/bash

usage="Usage: $0 <max_runs> <filename> <model> <input> <output> [timeout]"

max_runs=${1:-1}
file=${2:?$usage}
model=${3:?$usage}
input=${4:?$usage}
output=${5:?$usage}
timeout=${6:-1800}

prompt=$(<"$file")

# Validate input is a positive integer
if [[ ! "$max_runs" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: '$1' is not a valid positive integer" >&2
    exit 1
fi

for ((run=1; run<=max_runs; run++)); do
    python openrouter-files.py \
      --prompt "$prompt" \
      --model $model \
      --input $input \
      --output $output \
      --timeout $timeout
done
