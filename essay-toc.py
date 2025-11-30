import os
import re
import argparse
import pandas as pd
from collections import defaultdict
from typing import Optional
from pathlib import Path
from openai import OpenAI

def group_cn_by_dn(filename):
    df = pd.read_excel(filename)
    df = df.dropna(subset=['dn', 'cn'])

    grouped = defaultdict(list)
    for _, row in df.iterrows():
        key = str(row['dn']).strip().rstrip('.')
        value = str(row['cn']).strip().rstrip('.')

        parts = re.findall(r'\d+', value)
        if len(parts) >= 3:
            upper = '.'.join(parts[:-1])

            if (key, upper) not in grouped:
                grouped[key].append(upper)

        grouped[key].append(value)

    return dict(grouped)

def breakby(content):
    splitter = re.compile(r'^(?=\d+(?:\.\d+)*\.?\s)', re.MULTILINE)
    pieces = [b for b in splitter.split(content) if b.strip()]

    result = []
    for piece in pieces:
        # grab the number at the very beginning
        m = re.match(r'(\d+(?:\.\d+)*\.?)\s*', piece)
        key = m.group(1).rstrip('.') if m else ''
        result.append((key, piece))

    return result

def parse_tocs(text: str):
    pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$', re.MULTILINE)
    return pattern.findall(text.strip())

def process_files(url, key, args):

    concat = ""
    count = 0

    with open(args.prompt, 'r', encoding='utf-8') as file:
        prompt = file.read()

    with open(args.merged, 'r', encoding='utf-8') as file:
        merged = file.read()

    with open(args.base, 'r', encoding='utf-8') as file:
        base_toc = file.read()

    mappings = group_cn_by_dn(args.mapping)
    values = dict(breakby(merged))

    tocs = parse_tocs(base_toc)
    for number, title in tocs:

        if args.section.upper() != 'ALL' and number != args.section:
            continue

        if number not in mappings:
            print(f"{number} not in mappings")
            continue

        question_file = os.path.join(args.output, f"{number}-question.txt")
        answer_file = os.path.join(args.output, f"{number}-answer.txt")

        if os.path.exists(answer_file):
            print(f"{number} already exist")
            continue

        count += 1
        print(f"{number} -> {title}")

        for linking in mappings[number]:
            concat += values[linking]

        question = prompt.replace("!!CONTENT!!", concat)
        # print(f"{number} -> {question}")

        retry = 0
        while retry < args.retry:

            with open(question_file, 'w', encoding='utf-8') as out_file:
                out_file.write(question)

            print("QUESTION---")
            print(question)

            client = OpenAI(
                base_url = url,
                api_key = key,
            )

            completion = client.chat.completions.create(
                model = args.model,
                messages = [{
                    "role": "user",
                    "content": question,
                }],
                temperature = args.temperature,
                timeout = args.timeout,
            )

            if not completion or not completion.choices or not completion.usage or completion.usage.completion_tokens <= 0:
                print(f"Skipping empty response")
                continue

            content = completion.choices[0].message.content
            if not content:
                print(f"Skipping empty content")
                continue

            print("CONTENT---")
            print(content)

            with open(answer_file, 'w', encoding='utf-8') as out_file:
                out_file.write(content)

            break # retry

    return count

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
    parser = argparse.ArgumentParser(description="Prompt to write an essay by a toc section")
    parser.add_argument("--model", help="The model name to use for processing files")
    parser.add_argument("--prompt", help="The prompt file to use for processing files")
    parser.add_argument("--base", help="The base toc to use as reference")
    parser.add_argument("--merged", help="The merged file to use for processing files")
    parser.add_argument("--mapping", help="Mapping Excel file")
    parser.add_argument("--section", default="1.2.1", help="Base on the section to write a story, or ALL")
    parser.add_argument("--input", default="input", help="The input folder")
    parser.add_argument("--output", default="output", help="The output folder")
    parser.add_argument("--timeout", default=600, type=int, help="Timeout (in seconds)")
    parser.add_argument("--temperature", default=1.0, type=float, help="Temperature (default 1.0)")
    parser.add_argument("--retry", default=10, type=int, help="Retry of API response (in seconds)")
    args = parser.parse_args()

    # Create output directory if not exists
    os.makedirs(args.output, exist_ok=True)

    # Check if input directory exists
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input directory '{args.input}' not found")

    if not os.path.isfile(args.base):
        raise FileNotFoundError(f"Base ToC file '{args.base}' not found")

    if not os.path.isfile(args.mapping):
        raise FileNotFoundError(f"Mapping Excel file '{args.mapping}' not found")

    count = process_files(
        api_url,
        api_key,
        args)

    print(f"Count: {count}")
