import os
import re
import shutil
import subprocess
import typer
from rich import print

from injector import inject, remove_block
from optimizer import analyze_jd, optimize_section
from jd_input import get_jd_text
from ats import ats_score

LOCKED_SECTIONS = {"COMSCORE", "ACCENTURE"}
ALWAYS_KEEP = {"DEVOPS"}

OUTPUT_DIR = "output"
TEX_FILE = "optimized.tex"
PDF_FILE = "optimized.pdf"
MAX_BULLETS = {
    "SYSTEMS_HIGHLIGHTS": 4,
    "DEVOPS": 4,
    "DEVICE_MGMT_BACKEND": 4,
    "METER_DIAGNOSTICS": 3,
    "PROTOCOL_PLATFORM": 3,
    "EDGE_RELIABILITY": 3,
    "ANDROID_PROVISIONING": 2,
}

def run():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        raise typer.Exit(1)

    # --- Load BASE resume (immutable) ---
    with open("base.tex", "r") as f:
        tex = f.read()

    # --- Job Description ---
    jd = get_jd_text()
    jd_analysis = analyze_jd(jd)

    detected = jd_analysis.get("role_type", "")
    print(f"\nDetected role: {detected}")
    print("Override role? (backend / platform / infra / iot or Enter)")
    override = input("> ").strip().lower()
    if override:
        jd_analysis["role_type"] = override

    print(f"Using role: {jd_analysis['role_type']}\n")

    # --- Canonical bullets (input only) ---
    sections = {
        "DEVOPS": [
            "Owned architecture and development of backend services and Android-based industrial gateways for provisioning, telemetry ingestion, diagnostics, and control of IoT assets.",
            "Founded and led DevOps and testing infrastructure, designing Jenkins-based CI/CD pipelines, artifact repositories, and automated testing in an on-prem, air-gapped environment.",
            "Built custom server-side Git hooks in Python for self-hosted Git, enabling end-to-end automation from commit to build, test, and release.",
            "Standardized build and testing workflows across 10--20 engineers, eliminating manual steps and significantly reducing build times for large Android/AOSP applications."
        ],

        "DEVICE_MGMT_BACKEND": [
            "Architected containerized backend services deployed on AWS ECS, handling thousands of API calls and telemetry messages per minute.",
            "Designed event-driven ingestion pipelines where gateways publish telemetry to AWS IoT (MQTT), fan out via SQS, and are processed by backend services.",
            "Implemented service discovery, connection pooling, and horizontal auto-scaling to ensure durability and throughput under load.",
            "Integrated telemetry pipelines with ThingsBoard for real-time visualization and monitoring.",
            "Implemented observability using structured logging, metrics, health checks, and alarms across multiple containerized services.",
            "Reduced cloud infrastructure costs by up to 40\\% through scaling strategies and resource optimization."
        ],

        "METER_DIAGNOSTICS": [],
        "PROTOCOL_PLATFORM": [],
        "EDGE_RELIABILITY": [],
        "ANDROID_PROVISIONING": [],

        "COMSCORE": [],
        "ACCENTURE": []
    }

    all_selected = []

    # --- Inject safely ---
    def rank_bullets(bullets: list[str], keywords: list[str]) -> list[str]:
        if not keywords:
            return bullets
        cleaned = [re.sub(r"[^a-z0-9 ]+", " ", k.lower()).strip() for k in keywords]
        cleaned = [k for k in cleaned if k]

        def score(b: str) -> int:
            text = b.lower()
            return sum(1 for k in cleaned if k in text)

        return sorted(bullets, key=score, reverse=True)

    for marker, bullets in sections.items():

        if marker in LOCKED_SECTIONS:
            if bullets:
                tex = inject(tex, marker, bullets)
                all_selected.extend(bullets)
            continue

        selected = optimize_section(bullets, jd_analysis)

        if marker in ALWAYS_KEEP and not selected:
            selected = bullets

        if not selected or selected == bullets:
            keywords = jd_analysis.get("core_keywords", []) + jd_analysis.get("secondary_keywords", [])
            ranked = rank_bullets(bullets, keywords)
            limit = MAX_BULLETS.get(marker)
            selected = ranked[:limit] if limit else ranked

        if not selected:
            tex = remove_block(tex, marker)
            continue

        tex = inject(tex, marker, selected)
        all_selected.extend(selected)

    # --- WRITE FRESH FILE (OVERWRITE) ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, TEX_FILE)

    with open(out_path, "w") as f:
        f.write(tex)

    print("✔ optimized.tex generated (clean overwrite)")

    pdf_path = os.path.join(OUTPUT_DIR, PDF_FILE)
    latexmk = shutil.which("latexmk")
    pdflatex = shutil.which("pdflatex")

    if latexmk:
        try:
            subprocess.run(
                [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", TEX_FILE],
                cwd=OUTPUT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            print(f"✔ PDF generated: {pdf_path}")
        except subprocess.CalledProcessError:
            print("❌ PDF generation failed (latexmk). Check output/optimized.log.")
    elif pdflatex:
        try:
            subprocess.run(
                [pdflatex, "-interaction=nonstopmode", "-halt-on-error", TEX_FILE],
                cwd=OUTPUT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            print(f"✔ PDF generated: {pdf_path}")
        except subprocess.CalledProcessError:
            print("❌ PDF generation failed (pdflatex). Check output/optimized.log.")
    else:
        print("ℹ️  No LaTeX engine found (latexmk or pdflatex). Use Overleaf or install TeX.")

    # --- ATS Score ---
    score = ats_score(jd, tex)
    print(f"ATS Match Score: {score}%")

if __name__ == "__main__":
    typer.run(run)
