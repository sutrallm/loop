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
      --prompt "Translate the following Chinese Buddhism sutra to English with strict adherence to these rules: \
          Output Format: Plain text only. No markdown, HTML, special formatting, headings, or italics. \
          Paragraph Numbers: Preserve all original paragraph numbers (e.g., 1., 2., 3.) exactly as Arabic numerals. Do not convert them to words (e.g., 'One', 'Two', 'I', 'II'). \
          Whitespace: Avoid extra line breaks, indentation, or spacing. Maintain the original paragraph structure. \
          Consistency: Ensure numbering, punctuation, and terminology match previous chapters (if applicable). \
        Here is the text to translate:" \
      --model "deepseek/deepseek-r1" \
      --input "sutra/grouped-chi" \
      --output "sutra/grouped-eng-r1" \
      --timeout 1800
done
