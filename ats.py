import re

STOPWORDS = {
    "the", "and", "to", "of", "in", "a", "for", "with", "on",
    "is", "are", "as", "by", "this", "that", "or"
}

def strip_latex(tex: str) -> str:
    # Preserve human-readable text inside common commands
    tex = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", tex)
    # Remove remaining LaTeX commands
    tex = re.sub(r"\\[a-zA-Z]+\*?", " ", tex)
    tex = re.sub(r"[%$&#_^~]", " ", tex)
    return tex

def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return {w for w in words if w not in STOPWORDS}

def ats_score(jd: str, optimized_tex: str) -> int:
    jd_tokens = tokenize(jd)
    resume_text = strip_latex(optimized_tex)
    resume_tokens = tokenize(resume_text)

    if not jd_tokens or not resume_tokens:
        return 0

    overlap = jd_tokens & resume_tokens
    return round((len(overlap) / len(jd_tokens)) * 100)
