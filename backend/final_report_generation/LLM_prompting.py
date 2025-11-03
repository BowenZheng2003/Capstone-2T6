import os
from huggingface_hub import InferenceClient

def call_deepseek(context: str, merged_json: str):
    prompt = (
        f"""Act as a communication coach and generate an evaluation report on how this user’s 
        transcripted speech, audio qualities and body language perform in the context of {context} 
        Provide helpful feedback on the following: whether the tone of voice, 
        words and body language fits the context, whether the information is correct, whether the 
        content spoken is sufficient given the context, and clarity of their message. Provide helpful 
        suggestions where necessary to improve Clarity & Conciseness, Confidence & Presence, Voice & 
        Tone, Body Language, and Storytelling. In addition provide necessary feedback on how the vocal 
        quality, body language and spoken transcript can be utilized at the same time to enhance this 
        speech. Show this as a structured, balanced, and actionable framework that highlights strengths, 
        areas for improvement, and specific next steps. Assume there will be transcription errors in the 
        text so not all the words will be accurate, but they should sound similar to something correct 
        phonetically. Here is the user’s recorded speech as a JSON:"""
    )

    with open(merged_json, "r", encoding="utf-8") as f:
        json_string = f.read()

    client = InferenceClient(
        provider="auto",
        api_key=os.environ["HF_TOKEN"],
    )

    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        messages=[
            {
                "role": "user",
                "content": prompt + json_string
            }
        ],
    )

    print(completion.choices[0].message)

    return completion.choices[0].message.content

#call_deepseek(context="coke rant", merged_json="merged.json")