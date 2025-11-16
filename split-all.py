import os
import re
import argparse
import pandas as pd
import subprocess
from typing import Optional
from pathlib import Path
from openai import OpenAI

def process_files(url, key, args):

    count = 0

    df = pd.read_excel(args.mapping, args.sheet)
    df = df.dropna(subset=['section number'])
    df['section title'] = df['section title'].astype(str).str.strip()
    df['section number'] = df['section number'].astype(str).str.strip()
    rows = df[['section title', 'section number']]

    for title, number in zip(rows['section title'], rows['section number']):
        # make sure they are plain strings/numbers, not NaN
        if pd.isna(title) or pd.isna(number):
            continue

        count += 1
        print(f"{count:02d}: {title} [{number}]")

        command = [
            'python', 'split-toc.py',
            '--model', str(args.model),
            '--prompt', str(args.prompt),
            '--mapping', str(args.mapping),
            '--number', str(number),
            '--remark', str(title),
            '--base', str(args.base),
            '--input', str(args.input),
            '--output', os.path.join(str(args.output), number),
        ]

        subprocess.run(command)

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
    parser = argparse.ArgumentParser(description="Prompt to split content by a toc section")
    parser.add_argument("--model", help="The model name to use for processing files")
    parser.add_argument("--prompt", help="The prompt file to use for processing files")
    parser.add_argument("--mapping", help="Mapping Excel file")
    parser.add_argument("--sheet", help="Mapping Excel sheet")
    parser.add_argument("--base", help="The base toc to use as reference")
    parser.add_argument("--input", default="input", help="The input folder")
    parser.add_argument("--output", default="output", help="The output folder")
    parser.add_argument("--timeout", default=600, type=int, help="Timeout (in seconds)")
    parser.add_argument("--retry", default=10, type=int, help="Retry of API response (in seconds)")
    args = parser.parse_args()

    # Check if input directory exists
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input directory '{args.input}' not found")

    if not os.path.isfile(args.mapping):
        raise FileNotFoundError(f"Mapping Excel file '{args.mapping}' not found")

    if not os.path.isfile(args.base):
        raise FileNotFoundError(f"Base ToC file '{args.base}' not found")

    count = process_files(
        api_url,
        api_key,
        args)

    # print(f"Count: {count}")
