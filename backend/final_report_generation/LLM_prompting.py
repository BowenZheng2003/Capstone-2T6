import os
from huggingface_hub import InferenceClient
from backend.final_report_generation.string_cleaning import extract_and_save_json
import json
import json_repair

def call_deepseek(context: str, merged_json: str):
    prompt = f"""
    Act as a communication coach and generate an evaluation report on how this user’s 
transcribed speech, audio qualities and body language perform in the context of {context}.
Provide helpful feedback on the following: whether the tone of voice, 
words and body language fits the context, whether the information is correct, whether the 
content spoken is sufficient given the context, and clarity of their message. Provide helpful 
suggestions where necessary to improve Clarity & Conciseness, Confidence & Presence, Voice & 
Tone, Body Language, and Storytelling. In addition provide necessary feedback on how the vocal 
quality, body language and spoken transcript can be utilized at the same time to enhance this 
speech. Show this as a structured, balanced, and actionable framework that highlights strengths, 
areas for improvement, and specific next steps. Assume there will be transcription errors in the 
text so not all the words will be accurate, but they should sound similar to something correct 
phonetically. 

You MUST return your response in the following JSON format:

{{
    "context": "{context}",
    "summary": "high-level summary of feedback, strengths, weaknesses and suggestions",
    "score": 0,
    "strengths": [
        {{
            "description": "",
            "evidence": [
                {{
                    "ts_start": 0,
                    "ts_end": 15
                }}
            ]
        }}
    ],
    "problems": [
        {{
            "description": "",
            "evidence": [
                {{
                    "ts_start": 0,
                    "ts_end": 15,
                    "suggestion": ""
                }}
            ]
        }}
    ]
}}

The score must be out of 10. Where 10 is the best score and 0 is the worst.
"""


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
    llm_response = completion.choices[0].message.content

    #json_obj = extract_and_save_json(completion.choices[0].message.content, "deepseek_output.json")

    start_index = llm_response.find('{')
    end_index = llm_response.rfind('}') + 1 # +1 to include the closing brace

    if start_index != -1 and end_index != -1:
        json_str = llm_response[start_index:end_index]
        try:
            json_obj = json_repair.loads(json_str)
        except Exception as e:
            print(f"Failed to parse JSON even with repair: {e}")
            # Handle failure (e.g., return empty dict or retry)
            return {}
        # json_obj = json.loads(json_str)

        print(f"Score: {json_obj['score']}")
        print(f"Summary: {json_obj['summary']}")
    else:
        print("No JSON object found in response")

    return json_obj

# call_deepseek(context="coke rant", merged_json="merged.json")