import re
from collections import Counter
from typing import Optional

STOPWORDS = {
    "the", "and", "to", "of", "in", "a", "for", "with", "on", "is", "are",
    "as", "by", "this", "that", "or", "an", "be", "from", "at", "it", "we",
    "you", "our", "your", "their", "they", "will", "can", "may", "should",
    "must", "not", "but", "if", "into", "out", "up", "down", "across",
    "over", "under", "within", "without", "about", "than", "then",
}

ALIAS_TOKENS = {
    "c++": "cpp",
    "c#": "csharp",
    ".net": "dotnet",
    "ci/cd": "cicd",
}

def normalize_token(token: str) -> str:
    token = token.strip().lower()
    token = ALIAS_TOKENS.get(token, token)
    token = token.strip(".,;:()[]{}")
    return token

def strip_latex(tex: str) -> str:
    # Preserve human-readable text inside common commands
    tex = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", tex)
    # Remove remaining LaTeX commands
    tex = re.sub(r"\\[a-zA-Z]+\*?", " ", tex)
    tex = re.sub(r"[%$&#_^~]", " ", tex)
    return tex

def tokenize(text: str) -> set[str]:
    raw = re.findall(r"[A-Za-z0-9][A-Za-z0-9\+\#\./-]{0,}", text)
    tokens = {normalize_token(t) for t in raw}
    return {t for t in tokens if len(t) >= 2 and t not in STOPWORDS}

def extract_keywords(text: str, max_keywords: int = 80) -> list[str]:
    tokens = tokenize(text)
    if not tokens:
        return []
    counts = Counter(t for t in tokenize(text))
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return [t for t, _ in ranked[:max_keywords]]

def ats_score(jd: str, optimized_tex: str, jd_analysis: Optional[dict] = None) -> int:
    if jd_analysis:
        keywords = jd_analysis.get("core_keywords", []) + jd_analysis.get("secondary_keywords", [])
        jd_tokens = tokenize(" ".join(keywords)) if keywords else set()
    else:
        jd_tokens = set()
    if not jd_tokens:
        jd_tokens = set(extract_keywords(jd))
    resume_text = strip_latex(optimized_tex)
    resume_tokens = tokenize(resume_text)

    if not jd_tokens or not resume_tokens:
        return 0

    overlap = set(jd_tokens) & resume_tokens
    return round((len(overlap) / len(jd_tokens)) * 100)
