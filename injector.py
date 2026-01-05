import re

LATEX_ESCAPE_MAP = {
    "%": r"\%",
    "&": r"\&",
    "_": r"\_",
    "#": r"\#",
    "$": r"\$",
}

def escape_latex(text: str) -> str:
    for char, replacement in LATEX_ESCAPE_MAP.items():
        text = re.sub(rf"(?<!\\){re.escape(char)}", replacement, text)
    return text

def inject(tex: str, marker: str, bullets: list[str]) -> str:
    """
    Safely replace content ONLY between:
      % BEGIN_<MARKER>
      % END_<MARKER>

    Never touches anything else.
    """

    begin = f"% BEGIN_{marker}"
    end = f"% END_{marker}"

    # Fail-safe: if markers missing, do nothing
    if begin not in tex or end not in tex:
        return tex

    rendered = "\n".join(
        f"\\resumeItem{{{escape_latex(b)}}}" for b in bullets
    )

    pattern = rf"{begin}\n.*?\n{end}"

    replacement = (
        f"{begin}\n"
        f"{rendered}\n"
        f"{end}"
    )

    # Use a function to avoid backslash escapes in replacement (e.g., \r).
    return re.sub(pattern, lambda _: replacement, tex, flags=re.S)

def remove_block(tex: str, marker: str) -> str:
    """
    Remove the itemize block for a marker, plus an optional preceding \textit{...} line.
    """
    begin = f"% BEGIN_{marker}"
    end = f"% END_{marker}"

    pattern = (
        rf"\n(?:\\\\textit\\{{[^}}]*\\}}\\n)?"
        rf"\\\\resumeItemListStart\\n"
        rf"{re.escape(begin)}\\n"
        rf".*?\\n"
        rf"{re.escape(end)}\\n"
        rf"\\\\resumeItemListEnd"
    )

    return re.sub(pattern, "", tex, flags=re.S)
