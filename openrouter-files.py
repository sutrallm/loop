import os
import argparse
from openai import OpenAI

def process_files(api_token, prompt, model, input_dir="input", output_dir="output"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Check if input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory '{input_dir}' not found")

    # Process each file in the input directory
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Skip directories
        if not os.path.isfile(input_path):
            continue

        # Read file content
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
        except UnicodeDecodeError:
            print(f"Skipping non-text file: {filename}")
            continue

        # Prepare the full prompt
        full_prompt = f"{prompt}\n\n{file_content}"

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_token,
        )

        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1",
            messages=[{
                "role": "user",
                "content": full_prompt
            }]
        )
        content = completion.choices[0].message.content

        # Save response
        try:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(content)
            print(f"Processed: {filename}")
        except IOError as e:
            print(f"Failed to save output for {filename}: {str(e)}")

if __name__ == "__main__":
    # Read API token from environment
    api_token = os.environ.get("DEEPSEEK_API_TOKEN")
    if not api_token:
        print("Error: DEEPSEEK_API_TOKEN environment variable not set")
        exit(1)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process text files with DeepSeek API")
    parser.add_argument("--prompt", help="The prompt to use for processing files")
    parser.add_argument("--model", help="The model to use for processing files")
    args = parser.parse_args()

    process_files(api_token, args.prompt, args.model)
