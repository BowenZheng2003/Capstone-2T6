# backend/final_report_generation/LLM_prompting.py
from __future__ import annotations
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
if not HF_TOKEN:
    raise RuntimeError(
        "Missing HF token. Set HF_TOKEN or HUGGING_FACE_HUB_TOKEN in your environment or .env file."
    )

# Default DeepSeek model; override with env HF_MODEL if desired
HF_MODEL = os.getenv("HF_MODEL", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B")


def _read_json_as_string(path: str | os.PathLike, max_chars: int = 120_000) -> str:
    """Read JSON file and return (possibly truncated) pretty string to keep prompt size manageable."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    try:
        data = json.loads(text)
        if isinstance(data, list):
            data = data[:50]  # keep first 50 segments if it's a list
        text = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        text = text[:max_chars]
    return text

def _strip_think(s: str) -> str:
    start = s.find("<think>")
    end = s.rfind("</think>")
    if start != -1 and end != -1 and end > start:
        return s[end+8:].strip()
    if start != -1 and end == -1:
        return s[:start].strip()
    return s.strip()

def call_deepseek(merged_json: str, context: str = "") -> str:
    """
    Generate an evaluation report using a DeepSeek model hosted on Hugging Face.
    - merged_json: path to your merged features JSON (string path)
    - context: short description of scenario (e.g., 'tech interview', 'class presentation')
    """
    prompt = (
        f"Act as a communication coach and generate an evaluation report on how this user’s "
        f"transcripted speech, audio qualities and body language perform in the context of {context}. "
        f"Provide helpful feedback on the following: whether the tone of voice, words and body language "
        f"fits the context, whether the information is correct, whether the content spoken is sufficient "
        f"given the context, and clarity of their message. Provide helpful suggestions where necessary to "
        f"improve Clarity & Conciseness, Confidence & Presence, Voice & Tone, Body Language, and "
        f"Storytelling. In addition provide necessary feedback on how the vocal quality, body language and "
        f"spoken transcript can be utilized at the same time to enhance this speech. Show this as a structured, "
        f"balanced, and actionable framework that highlights strengths, areas for improvement, and specific next steps. "
        f"Assume there will be transcription errors in the text so not all the words will be accurate, but they should "
        f"sound similar to something correct phonetically. Here is the user’s recorded speech as a JSON:\n\n"
    )

    payload = prompt + _read_json_as_string(merged_json)

    # Build the client *without* forcing provider; use chat.completions (works with this model)
    client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)

    try:
        resp = client.chat.completions.create(
            model=HF_MODEL,
            messages=[{"role": "user", "content": payload}],
            max_tokens=900,
            temperature=0.6,
            top_p=0.9,
        )
        text = resp.choices[0].message.content
        return _strip_think(text) or "(empty after stripping)"
    except HfHubHTTPError:
        # Fallback: try classic text_generation (some deployments wire only this)
        out = client.text_generation(
            payload,
            max_new_tokens=900,
            temperature=0.6,
            top_p=0.9,
            repetition_penalty=1.05,
            return_full_text=False,
        )
        return out.strip()
    