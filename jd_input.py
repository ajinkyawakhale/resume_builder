import sys
import requests
import re
import json
from typing import Optional
from urllib.parse import urlparse

def clean_html(html: str) -> str:
    html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()

def extract_json_ld_description(html: str) -> str:
    matches = re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        flags=re.S | re.I,
    )
    for raw in matches:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            items = data
        else:
            items = [data]
        for item in items:
            if isinstance(item, dict) and "description" in item:
                return clean_html(str(item["description"]))
    return ""

def extract_job_description(html: str) -> str:
    json_ld = extract_json_ld_description(html)
    if json_ld:
        return json_ld
    m = re.search(r'"jobDescription"\s*:\s*"(.*?)"', html, flags=re.S)
    if m:
        return clean_html(m.group(1).encode("utf-8").decode("unicode_escape"))
    return ""

def workday_cxs_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    if "myworkdayjobs.com" not in parsed.netloc:
        return None

    tenant = parsed.netloc.split(".")[0]
    parts = [p for p in parsed.path.split("/") if p]
    if parts and parts[0].lower() in {"en-us", "en_us"}:
        parts = parts[1:]

    if not parts or "job" not in parts:
        return None

    site = parts[0]
    job_index = parts.index("job")
    job_path = "/".join(parts[job_index + 1:])
    if not site or not job_path:
        return None

    return f"{parsed.scheme}://{parsed.netloc}/wday/cxs/{tenant}/{site}/job/{job_path}"

def fetch_workday_jd(url: str) -> str:
    cxs_url = workday_cxs_url(url)
    if not cxs_url:
        return ""

    try:
        data = requests.get(cxs_url, timeout=10).json()
    except Exception:
        return ""

    description = data.get("jobPostingInfo", {}).get("jobDescription", "")
    return clean_html(description)

def get_jd_text():
    print("1) Paste JD")
    print("2) Provide JD URL")
    choice = input("> ").strip()

    if choice == "1":
        print("Paste JD (type END on a new line to finish):")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip().upper() == "END":
                break
            lines.append(line)
        return "\n".join(lines).strip()

    if choice == "2":
        url = input("Enter JD URL: ").strip()
        try:
            if "myworkdayjobs.com" in url:
                jd_text = fetch_workday_jd(url)
                if jd_text:
                    return jd_text

            r = requests.get(url, timeout=10)
            extracted = extract_job_description(r.text)
            cleaned = extracted or clean_html(r.text)
            if cleaned:
                return cleaned
        except Exception:
            pass

        print("Failed to fetch URL. Paste JD instead.")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip().upper() == "END":
                break
            lines.append(line)
        return "\n".join(lines).strip()
