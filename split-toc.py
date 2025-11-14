import os
import re
import argparse
import pandas as pd
from typing import Optional
from pathlib import Path
from openai import OpenAI

def tags_ok(content: str) -> bool:
    return True

def read_abstract_nos(filename, section):
    # Read the Excel file
    df = pd.read_excel(filename)

    # Strip whitespace from section number column and convert to string
    df['section number'] = df['section number'].astype(str).str.strip()
    # Filter rows where the 'section number' column matches the provided section
    filtered_df = df[df['section number'] == section.strip()]

    # Extract the 'abstract no.' column values from the filtered rows
    abstract_nos = filtered_df['abstract no.'].astype(str).str.strip().tolist()

    return abstract_nos

def process_files(url, key, args):

    count = 0
    toc_path = args.base
    with open(args.prompt, 'r', encoding='utf-8') as file:
        prompt = file.read()

    abstract_nos = read_abstract_nos(args.mapping, args.number)
    if not abstract_nos:
        raise FileNotFoundError(f"Section number '{args.number}' not found in '{args.mapping}'")

    # Process each file in the input directory
    for filename in sorted(os.listdir(args.input)):

        # Skip files not in abstract_nos
        if not any(pattern in filename for pattern in abstract_nos):
            continue

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

        count += 1
        print(f"Processing: {input_path} with: {toc_path} count: {count}")

        # Prepare the full prompt
        section = f"{args.number} {args.remark}"
        question = prompt.replace("!!TOC!!", toc_content).replace("!!FILE!!", file_content).replace("!!SECTION!!", section)

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

            print("QUESTION---")
            print(question)

            print("CONTENT---")
            print(content)

            output_path = os.path.join(args.output, filename)
            try:
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(content)
                print(f"Split: {output_path} using: {completion.usage.total_tokens} tokens")
            except IOError as e:
                print(f"Failed to save output for {output_path}: {str(e)}")

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
    parser = argparse.ArgumentParser(description="Prompt to split content by a toc section")
    parser.add_argument("--model", help="The model name to use for processing files")
    parser.add_argument("--prompt", help="The prompt file to use for processing files")
    parser.add_argument("--mapping", help="Mapping Excel file")
    parser.add_argument("--number", help="Section number in Excel file")
    parser.add_argument("--remark", help="Section remark in Excel file")
    parser.add_argument("--base", help="The base toc to use as reference")
    parser.add_argument("--input", default="input", help="The input folder")
    parser.add_argument("--output", default="output", help="The output folder")
    parser.add_argument("--timeout", default=600, type=int, help="Timeout (in seconds)")
    parser.add_argument("--retry", default=10, type=int, help="Retry of API response (in seconds)")
    args = parser.parse_args()

    # Create output directory if not exists
    os.makedirs(args.output, exist_ok=True)

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

    print(f"Count: {count}")
