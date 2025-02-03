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

### Run with OpenRouter (DeepSeek R1)
```bash
python openrouter-files.py \
  --prompt "Translate the following Chinese Buddhism sutra into English:" \
  --model "deepseek/deepseek-r1"
```

&copy;2025 [SturaLLM](https://github.com/sutrallm/)
