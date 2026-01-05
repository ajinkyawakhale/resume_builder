from openai import OpenAI
import json
from llm_utils import extract_json

client = OpenAI()

def load_prompt(path):
    with open(path) as f:
        return f.read()

def analyze_jd(jd_text: str) -> dict:
    prompt = load_prompt("prompts/jd_analyzer.txt")
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": jd_text[:12000]}
        ]
    )
    return extract_json(res.choices[0].message.content)

def optimize_section(bullets: list[str], jd_analysis: dict) -> list[str]:
    prompt = load_prompt("prompts/resume_optimizer.txt")
    payload = {
        "bullets": bullets,
        "jd_analysis": jd_analysis
    }

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(payload)}
        ]
    )

    data = extract_json(res.choices[0].message.content)
    return data["selected_bullets"]
