import os
import re
import argparse
import pandas as pd
from typing import Optional
from pathlib import Path
from openai import OpenAI

def tags_ok(content: str) -> bool:
    return True

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

def process_files(url, key, args):

    count = 0
    concat = "<內容>"

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

        matches = extract(file_content, args.match)
        concat += "\n".join(matches)

        count += 1
        print(f"Processing: {input_path} with: {input_path} count: {count}")

    concat += "</內容>"

    # Prepare the full prompt
    question = prompt.replace("!!FILE!!", concat)

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
            print(f"Story: {output_path} using: {completion.usage.total_tokens} tokens")
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
    parser = argparse.ArgumentParser(description="Prompt to write a story by a toc section")
    parser.add_argument("--model", help="The model name to use for processing files")
    parser.add_argument("--prompt", help="The prompt file to use for processing files")
    parser.add_argument("--match", default="乎合", help="The content to extract from tag")
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

    count = process_files(
        api_url,
        api_key,
        args)

