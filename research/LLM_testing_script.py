import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="auto",
    api_key=os.environ["HF_TOKEN"],
)

completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
    messages=[
        {
            "role": "user",
            "content": "What to do in Xi'an China? I am travelling with my mother and she doesn't like the heat"
        }
    ],
)

print(completion.choices[0].message)