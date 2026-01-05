import json
import re

def extract_json(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("LLM returned empty output")

    text = text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = re.sub(r"```$", "", text)
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON from LLM:\n{text}")
