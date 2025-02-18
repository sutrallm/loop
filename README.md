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

### Run with DeepSeek V3
```bash
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
```

### Run with DeepSeek R1
```bash
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
  --model "deepseek-reasoner" \
  --temperature=0.3 \
  --input "sutra/grouped-chi" \
  --output "sutra/grouped-eng-ds-r1" \
  --timeout 600
```

### Run with Nvidia
```bash
python nvidia-files.py \
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
  --model "deepseek-ai/deepseek-r1" \
  --temperature=0.3 \
  --input "input" \
  --output "output" \
  --timeout 1800
```

- DeepSeek API [uptime](https://status.deepseek.com/uptime/)

### Run with OpenRouter
```bash
python openrouter-files.py \
  --prompt "Translate the following Chinese text into English:" \
  --model "deepseek/deepseek-r1"
```

Example (using OpenRouter `deepseek/deepseek-r1`)
```bash
python openrouter-files.py \
  --prompt "Translate the following Chinese Buddhism sutra into English and output in plain text, translated content only, no markdown, minimum formatting:" \
  --model "deepseek/deepseek-r1" \
  --input "sutra/grouped-chi" \
  --output "sutra/grouped-eng-or-r1" \
  --timeout 1800
```

Example (using OpenRouter `deepseek/deepseek-r1:free`)
```bash
python openrouter-files.py \
  --prompt "Translate the following Chinese Buddhism sutra into English and output in plain text, translated content only, no markdown, minimum formatting:" \
  --model "deepseek/deepseek-r1:free" \
  --input "sutra/grouped-chi" \
  --output "sutra/grouped-eng-or-r1-free" \
  --timeout 1800
```

Example (loop above prompt for 100 times)
```bash
chmod a+x ./openrouter-loop.sh
./openrouter-loop.sh 100
```

Note about [free](https://openrouter.ai/deepseek/deepseek-r1:free) and [paid](https://openrouter.ai/deepseek/deepseek-r1) DeepSeek R1 models on OpenRouter:
<details>
  <summary>Free model providers return lots of empty response:</summary>
  <img src="https://raw.githubusercontent.com/SutraAI/loop/refs/heads/master/image/openrouter-free-vs-paid.png?token=GHSAT0AAAAAACM2J25GVQ2CP5OKJHNMK3RIZ5BYBQQ">
</details>

### Run with SiliconFlow
```bash
python siliconflow-files.py \
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
  --model "deepseek-ai/DeepSeek-R1" \
  --temperature=0.3 \
  --input "sutra/grouped-chi" \
  --output "sutra/grouped-eng-sf-r1" \
  --timeout 1800
```

&copy;2025 [SturaLLM](https://github.com/sutrallm/)
