import os
import re
import argparse
from typing import Optional
from pathlib import Path
from openai import OpenAI

def increment(name: str, digits: Optional[int] = None) -> str:
    m = re.search(r'(\d+)(?=\.\w+$)', name)
    if m:
        num = int(m.group(1)) + 1
        width = digits if digits is not None else len(m.group(1))
        return name[:m.start(1)] + f'{num:0{width}d}' + name[m.end(1):]

    base, ext = name.rsplit('.', 1) if '.' in name else (name, '')
    width = digits if digits is not None else 3
    new_num = f'{1:0{width}d}'
    new_name = f"{base}{new_num}.{ext}" if ext else f"{base}{new_num}"
    return new_name

def suffix(filepath, suffix_to_insert):
    p = Path(filepath)
    return p.with_name(p.stem + suffix_to_insert + p.suffix)

def parse_toc_lines(lines):
    parsed = []
    for line in lines:
        line = line.rstrip('\n')
        if not line.strip():
            continue
        # Match leading whitespace (tabs) and section number like "6.1"
        match = re.match(r'^(\t*)([\d.]+)\s+(.*)', line)
        if match:
            indent, num_str, title = match.groups()
            # Convert "6.1" -> (6, 1); "6" -> (6,)
            num_tuple = tuple(map(int, num_str.split('.')))
            level = len(indent)  # number of tabs = hierarchy level
            parsed.append((num_tuple, level, line))
        else:
            # Keep non-matching lines as-is (e.g., comments, but unlikely here)
            parsed.append(((float('inf'),), -1, line))
    return parsed

def extract_new_sections(filepath, delimiter="<新增標題>"):
    # Normalize delimiter to ensure it's a proper XML-like tag
    open_tag = delimiter
    close_tag = "</" + delimiter.lstrip("<").rstrip(">")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build regex pattern dynamically
    pattern = rf"{re.escape(open_tag)}\s*\n(.*?)(?=\n{re.escape(close_tag)}|$)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

    inner_content = match.group(1).strip()
    lines = inner_content.split('\n')

    # Optional: filter out lines that look like tags or are empty
    filtered_lines = [
        line for line in lines
        if line.strip() and not (line.strip().startswith('<') and line.strip().endswith('>'))
    ]

    return filtered_lines

def merge_tocs(toc_path, update_path, output_path):
    # Read original ToC
    with open(toc_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    # Extract new sections
    new_lines = extract_new_sections(update_path)

    # Combine all lines
    all_lines = original_lines + [line + '\n' for line in new_lines]

    # Parse and sort
    parsed = parse_toc_lines(all_lines)
    # Sort by number tuple (natural section order)
    parsed.sort(key=lambda x: x[0])

    # Reconstruct lines
    merged_lines = [line for _, _, line in parsed]

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_lines) + '\n')

def process_files(url, key, args):

    version = 0
    toc_path = args.base
    with open(args.prompt, 'r', encoding='utf-8') as file:
        prompt = file.read()

    # Process each file in the input directory
    for filename in sorted(os.listdir(args.input)):
        input_path = os.path.join(args.input, filename)

        # Skip directories
        if not os.path.isfile(input_path):
            continue

        # Read file content
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
        except UnicodeDecodeError:
            print(f"Skipping non-text file: {input_path}")
            continue

        # Read toc content
        try:
            with open(toc_path, 'r', encoding='utf-8') as file:
                toc_content = file.read()
        except UnicodeDecodeError:
            print(f"Skipping non-text file: {toc_path}")
            continue

        print(f"Processing: {input_path} with: {toc_path} version: {version}")

        # Prepare the full prompt
        question = prompt.replace("!!TOC!!", toc_content).replace("!!FILE!!", file_content)
        print('********')
        print(question)
        print('********')

        client = OpenAI(
            base_url = url,
            api_key = key,
        )

        retry = 0
        while retry < args.retry:
            retry += 1

            completion = client.chat.completions.create(
                model = args.model,
                messages = [{
                    "role": "user",
                    "content": question,
                }],
                timeout = args.timeout,
            )

            if not completion or not completion.choices or not completion.usage or completion.usage.completion_tokens <= 0:
                print(f"Skipping empty response")
                continue

            content = completion.choices[0].message.content
            if not content:
                print(f"Skipping empty content")
                continue

            if content.find(args.skip) >= 0:
                print(f"Skipping no change")
                continue

            version += 1

            output_path = os.path.join(args.output, filename)
            output_path = suffix(output_path, '-LLM')
            try:
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(content)
                print(f"Evolve: {output_path} using: {completion.usage.total_tokens} tokens")
            except IOError as e:
                print(f"Failed to save output for {output_path}: {str(e)}")

            merge_path = output_path.with_name(output_path.name.replace('LLM', 'ToC'))
            merge_tocs(toc_path, output_path, merge_path)
            toc_path = merge_path

            break # retry

    return version

if __name__ == "__main__":
    # Read API url from environment
    api_url = os.environ.get("PLATFORM_API_URL")
    if not api_url:
        print("Error: missing PLATFORM_API_URL environment variable")
        exit(1)

    # Read API key from environment
    api_key = os.environ.get("PLATFORM_API_KEY")
    if not api_key:
        print("Error: missing PLATFORM_API_KEY environment variable")
        exit(1)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Prompt to refine a toc file by a folder of text files")
    parser.add_argument("--model", help="The model name to use for processing files")
    parser.add_argument("--prompt", help="The prompt file to use for processing files")
    parser.add_argument("--base", help="The base toc to use as reference")
    parser.add_argument("--input", default="input", help="The input folder")
    parser.add_argument("--output", default="output", help="The output folder")
    parser.add_argument("--skip", default="NONE", help="No change indicator")
    parser.add_argument("--timeout", default=600, type=int, help="Timeout (in seconds)")
    parser.add_argument("--retry", default=10, type=int, help="Retry of API response (in seconds)")
    args = parser.parse_args()

    # Create output directory if not exists
    os.makedirs(args.output, exist_ok=True)

    # Check if input directory exists
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input directory '{args.input}' not found")

    version = process_files(
        api_url,
        api_key,
        args)

    print(f"Version: {version}")
