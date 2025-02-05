#!/bin/bash

# Set default value to 1 if no parameter is provided
max_runs=${1:-1}

# Validate input is a positive integer
if [[ ! "$max_runs" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: '$1' is not a valid positive integer" >&2
    exit 1
fi

for ((run=1; run<=max_runs; run++)); do
    python openrouter-files.py \
      --prompt "Translate the following Chinese Buddhism sutra into English and output in plain text, translated content only, no markdown, minimum formatting:" \
      --model "deepseek/deepseek-r1" \
      --input "sutra/grouped-chi" \
      --output "sutra/grouped-eng-r1" \
      --timeout 1800
done
