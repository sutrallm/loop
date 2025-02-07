#!/bin/bash

# Set default value to 1 if no parameter is provided
max_runs=${1:-1}

# Validate input is a positive integer
if [[ ! "$max_runs" =~ ^[1-9][0-9]*$ ]]; then
	echo "Error: '$1' is not a valid positive integer" >&2
	exit 1
fi

for ((run=1; run<=max_runs; run++)); do
	python deepseek-files.py \
		--system "You are a professional translator specializing in ancient Chinese Buddhist Sutras. \
			Your task is to translate classical Chinese Sutra texts into modern English while: \
				1. Preserving the original philosophical and religious meaning. \
				2. Using formal, sacred language appropriate for religious texts. \
				3. Maintaining technical terms (e.g., Sanskrit words like "Śūnyatā" or "Bodhisattva") untranslated. \
				4. Keep paragraph numbers in Arabic numerals, do not convert them to words (e.g., 'One', 'Two', 'I', 'II') \
				5. Ensure numbering, punctuation, and terminology match previous chapters (if applicable) \
				6. Output translated content in plain text and translated content only \
			Ensure the translation is faithful to the source text's intent and tone." \
		--prompt "Here is the text to translate:" \
		--model "deepseek-chat" \
		--temperature=0.3 \
		--input "sutra/grouped-chi" \
		--output "sutra/grouped-eng-ds-v3" \
		--timeout 600
done
