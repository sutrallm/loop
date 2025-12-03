> 世尊曰：友！我不住不求以度瀑流。

# Introduction

Based on the Saṃyutta Nikāya (相應部經典 N0006), to process the sutra through a series of steps like a waterfall:

- Splitting the text to fit within the context limitations of large language models;
- Removing redundancies and eliminating noise;
- Creating a table of contents and identifying headings and sub-headings;
- Grouping paragraphs under relevant headings based on thematic coherence;
- Rewriting the scriptural passages in plain, modern language, guided by the headings and referenced paragraphs;
- Translating the rewritten text into English.

### Preparation
```bash
pip install --upgrade openai
```

### Setup API URL and Key
```bash
export PLATFORM_API_URL='https://openrouter.ai/api/v1'
export PLATFORM_API_KEY={KEY}
```

### Denoise
```
./openrouter-loop.sh 10 \
prompt/denoise.txt \
"deepseek/deepseek-v3.2-exp" \
"sutra/N0006c" \
"sutra/N0006c-denoise-20251031-deepseek-v32"
```

### Merge denoised text into a single file
```
python merge-dds.py \
  --input "sutra/N0006c-dds-20251111" \
  --output "sutra/N0006c-merge-20251128" \
  --filename "N0006c-dds-merged.txt" \
  --lines 1 \
  --limit 1000
```

### Build ToC
```
python evolve-toc.py \
  --model "deepseek/deepseek-v3.2-exp" \
  --prompt "prompt/evolve-toc.txt" \
  --base "param/toc.txt" \
  --input "sutra/N0006c" \
  --output "sutra/N0006c-toc-20251105-deepseek-v32"
```

### Write essay from ToC
```
for i in {1..10}; do
  python essay-toc.py \
    --model "openai/gpt-5.1" \
    --prompt "prompt/essay-toc.txt" \
    --base "param/toc-3-only.txt" \
    --merged "input/N0006c-dds-merged.txt" \
    --mapping "param/mapping-2025-12-02.xlsx" \
    --section "ALL" \
    --input "input/N0006c-dds-20251111" \
    --output "output/N0006c-essay-20251203-gpt-5.1" \
    --temperature 0.0
done
```

### Translate to English
```
python content-loop.py \
  --model "openai/gpt-5.1" \
  --prompt "prompt/to-english.txt" \
  --input "output/N0006c-essay-20251203-gpt-5.1-results-chi" \
  --output "output/N0006c-essay-20251203-gpt-5.1-results-eng" \
  --temperature 0.0
```

### Concat sections
```
pip install pandas openpyxl
```
```
python concat.py param/mapping.xlsx 2.2.2 sutra/N0006c-dds-20251111 N0006_ output/N0006c-dds-20251111-concat-2.2.2.txt
```

&copy;2025 [SturaLLM](https://github.com/sutrallm/)
