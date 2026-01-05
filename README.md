# resume_builder
LLM-based resume builder that tailors a LaTeX resume to a job description while keeping a canonical base resume.

## Quick Start
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your API key:
   ```bash
   export OPENAI_API_KEY=...
   ```
4. Run the CLI:
   ```bash
   python3 cli.py
   ```

The output is written to `output/optimized.tex` and `output/Ajinkya_Wakhale_Resume.pdf`.

## How It Works
- `base.tex` is the canonical resume.
- The CLI analyzes the JD and selects relevant bullets from `base.tex`.
- The tool **does not invent new experience**; it only selects and reorders existing content.

## Editing the Base Resume
Update your resume in `base.tex` only.

Key rules:
- Do **not** change formatting; only update content.
- Keep block markers intact (e.g., `BEGIN_DEVOPS` / `END_DEVOPS`).
- The **COMSCORE** and **ACCENTURE** sections are locked. Do not edit or remove them.
- Subsection headings (e.g., Device Management Platform) should stay as subheadings under the primary role.

## JD Input Tips
When pasting a JD, finish with a line containing `END`.

Example:
```
1
<paste job description>
END
```

## Project Structure
- `cli.py` entry point
- `optimizer.py`, `injector.py`, `jd_input.py`, `llm_utils.py`, `ats.py` helpers
- `prompts/` for model prompts
- `base.tex` canonical template
- `output/` generated artifacts

## PDF Generation
The CLI uses `latexmk` or `pdflatex` if available.

If you see a `fullpage.sty` error, ensure `fullpage.sty` exists in the repo root or install it via TeX Live.
