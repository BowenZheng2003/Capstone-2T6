import requests
import json

from transcripts import transcripts

LLMS_TO_TEST = ["deepseek/deepseek-r1-0528-qwen3-8b:free", 
        # "deepseek/deepseek-r1-0528:free",
        # "mistralai/devstral-small:free",
        # "deepseek/deepseek-chat-v3-0324:free",
        # "meta-llama/llama-4-maverick:free"
        ]

for llm in LLMS_TO_TEST:
    for transcript, context in transcripts:

        responses = []
        prompt = f"Here is a transcription of someone speaking: {transcript}. You are an evaluator tasked with evaluating and providing helpful feedback on a transcription of someone speaking. The context is {context}. Provide feedback on whether their style of speaking fits the context. Pay attention to their use of language and their tone. Provide feedback on whether the transcription makes sense given the context. Evaluate if they properly cover the correct information to the proper extent given the context. Provide feedback on the clarity of the transcription. Evaluate this based on the coherence and logical flow as well as if there are too many filler words."

        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
            #"HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
            #"X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
        },
        data=json.dumps({
            "model": llm,
            "messages": [
            {
                "role": "user",
                "content": prompt
            }
            ],
            
        })
        )

        if response.status_code == 200:
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            print(message)
            responses.append(message)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

        with open("llm_feedbacks.txt", "a", encoding="utf-8") as f:
            f.write(f"{llm} Responses: ")
            i = 1
            for line in responses:
                f.write(f"# {i}")
                f.write(line)
                i += 1
            f.write("\n")
