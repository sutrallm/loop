# loop

- Loop through an input folder of text files
- Prompt with the content of each input file
- Save the response in an output folder

### Preparation
```bash
pip install --upgrade openai
```

### Setup API token
```bash
export DEEPSEEK_API_TOKEN='api-token'
```

### Run with OpenRouter
```bash
python openrouter-files.py \
  --prompt "Translate the following Chinese text into English:" \
  --model "deepseek/deepseek-r1"
```

Example (using OpenRouter `deepseek/deepseek-r1`)
```
python openrouter-files.py \
  --prompt "Translate the following Chinese Buddhism sutra into English and output in plain text, translated content only, no markdown, minimum formatting:" \
  --model "deepseek/deepseek-r1" \
  --input "sutra/grouped-chi" \
  --output "sutra/grouped-eng-r1" \
  --timeout 1800
```

Example (using OpenRouter `deepseek/deepseek-r1:free`)
```
python openrouter-files.py \
  --prompt "Translate the following Chinese Buddhism sutra into English and output in plain text, translated content only, no markdown, minimum formatting:" \
  --model "deepseek/deepseek-r1:free" \
  --input "sutra/grouped-chi" \
  --output "sutra/grouped-eng-r1-free" \
  --timeout 1800
```

&copy;2025 [SturaLLM](https://github.com/sutrallm/)
