import os
import argparse
from openai import OpenAI

def process_files(api_token, prompt, model, timeout, input_dir, output_dir):
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)

    # Check if input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory '{input_dir}' not found")

    count = 0
    # Process each file in the input directory
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Skip directories
        if not os.path.isfile(input_path):
            continue

        # Skip processed file
        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            print(f"Skipping existing file: {input_path}")
            continue

        # Read file content
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
        except UnicodeDecodeError:
            print(f"Skipping non-text file: {input_path}")
            continue

        print(f"Processing: {input_path}")

        # Prepare the full prompt
        full_prompt = f"{prompt}\n\n{file_content}"

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_token,
        )

        completion = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": full_prompt,
            }],
            timeout=timeout,
        )

        if not completion.choices or completion.usage.completion_tokens <= 0:
            print(f"Skipping empty response by {completion.provider}")
            continue

        content = completion.choices[0].message.content
        if not content:
            print(f"Skipping empty content by {completion.provider}")
            continue

        # Save response
        try:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(content)
            print(f"Processed: {output_path} by {completion.provider}: {completion.usage.total_tokens} tokens")
        except IOError as e:
            print(f"Failed to save output for {filename}: {str(e)}")

        count += 1

    return count

if __name__ == "__main__":
    # Read API token from environment
    api_token = os.environ.get("DEEPSEEK_API_TOKEN")
    if not api_token:
        print("Error: missing DEEPSEEK_API_TOKEN environment variable")
        exit(1)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process text files with DeepSeek API")
    parser.add_argument("--prompt", help="The prompt to use for processing files")
    parser.add_argument("--model", help="The model to use for processing files")
    parser.add_argument("--timeout", default=300, type=int, help="Timeout (in seconds)")
    parser.add_argument("--input", default="input", help="The input folder")
    parser.add_argument("--output", default="output", help="The output folder")
    args = parser.parse_args()

    count = process_files(
        api_token,
        args.prompt,
        args.model,
        args.timeout,
        args.input,
        args.output)

    print(f"Count: {count}")
