import os
import re
import argparse
import pandas as pd
from typing import Optional
from pathlib import Path
from openai import OpenAI

def process_files(url, key, args):

    count = 0

    with open(args.prompt, 'r', encoding='utf-8') as file:
        prompt = file.read()

    for filename in sorted(os.listdir(args.input)):

        input_file = os.path.join(args.input, filename)
        output_file = os.path.join(args.output, filename)

        # Skip directories
        if not os.path.isfile(input_file):
            continue

        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            print(f"Skipping non-text file: {input_file}")
            continue

        if os.path.exists(output_file):
            print(f"{output_file} already exist")
            continue

        count += 1
        print(f"Processing: {input_file} count: {count}")

        # Prepare the full prompt
        question = prompt.replace("!!CONTENT!!", content)

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

            print("QUESTION---")
            print(question)

            print("CONTENT---")
            print(content)

            with open(output_file, 'w', encoding='utf-8') as out_file:
                out_file.write(content)

            break # retry

        if count >= args.limit:
            break

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
    parser = argparse.ArgumentParser(description="Loop folder with prompt and content")
    parser.add_argument("--model", help="The model name to use for processing files")
    parser.add_argument("--prompt", help="The prompt file to use for processing files")
    parser.add_argument("--input", default="input", help="The input folder")
    parser.add_argument("--output", default="output", help="The output folder")
    parser.add_argument("--limit", default=1000, type=int, help="Limit number of files")
    parser.add_argument("--timeout", default=600, type=int, help="Timeout (in seconds)")
    parser.add_argument("--temperature", default=1.0, type=float, help="Temperature (default 1.0)")
    parser.add_argument("--retry", default=10, type=int, help="Retry of API response (in seconds)")
    args = parser.parse_args()

    # Create output directory if not exists
    os.makedirs(args.output, exist_ok=True)

    # Check if input directory exists
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input directory '{args.input}' not found")

    count = process_files(
        api_url,
        api_key,
        args)

    print(f"Processed: {count}/{args.limit}")
