import os
import re
import argparse
import pandas as pd
from typing import Optional
from pathlib import Path
from openai import OpenAI

def extract(content, tag):
    start_tag=f"<{tag}>"
    end_tag=f"</{tag}>"
    # Create the regular expression pattern
    # re.DOTALL allows '.' to match newlines as well
    escaped_start = re.escape(start_tag)
    escaped_end = re.escape(end_tag)
    pattern = f"{escaped_start}(.*?){escaped_end}"

    # Find all non-overlapping matches
    matches = re.findall(pattern, content, re.DOTALL)

    return matches

def breakby(content, lines):

    splitter = re.compile(r'^(?=\d+(?:\.\d+)*\.?\s)', re.MULTILINE)
    blocks = [b for b in splitter.split(content) if b.strip()]

    return [block for block in blocks if block.count('\n') >= lines]

def process_files(args):

    count = 0
    toc_path = args.base

    folder = args.input
    for filename in sorted(os.listdir(folder)):

        input_path = os.path.join(folder, filename)

        # Skip directories
        if not os.path.isfile(input_path):
            continue

        # Read file content
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                content = '\n'.join(extract(file_content, '內容'))
                blocks = breakby(content, args.lines)
        except UnicodeDecodeError:
            print(f"Skipping non-text file: {input_path}")
            continue

        # Read toc content
        try:
            with open(toc_path, 'r', encoding='utf-8') as file:
                toc = file.read()
        except UnicodeDecodeError:
            print(f"Skipping non-text file: {toc_path}")
            continue

        for block in blocks:
            first = block.splitlines()[0]   # or .partition('\n')[0]
            print(first)

        count += 1
        # print(f"Checking: {input_path}/{filename} with: {toc_path} count: {count}")

        if count >= args.limit:
            break

    return count

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="To check content to a toc section")
    parser.add_argument("--base", help="The base toc to use as reference")
    parser.add_argument("--input", default="input", help="The input folder")
    parser.add_argument("--output", default="output", help="The output folder")
    parser.add_argument("--lines", default=2, type=int, help="Match only blocks with minimum n lines")
    parser.add_argument("--limit", default=1000, type=int, help="Limit number of files")
    args = parser.parse_args()

    # Create output directory if not exists
    os.makedirs(args.output, exist_ok=True)

    # Check if input directory exists
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input directory '{args.input}' not found")

    if not os.path.isfile(args.base):
        raise FileNotFoundError(f"Base ToC file '{args.base}' not found")

    count = process_files(args)

    print(f"Checked: {count}/{args.limit}")
