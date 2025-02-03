import os
from openai import OpenAI

api_token = os.environ.get("DEEPSEEK_API_TOKEN")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_token,
)

completion = client.chat.completions.create(
  model="deepseek/deepseek-r1",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life? (answer in plain text without formatting)"
    }
  ]
)

print(completion.choices[0].message.content)
