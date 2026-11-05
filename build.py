#!/usr/bin/env python3
"""Build droneseal-tech GitHub Pages site from DJI/XAG briefing markdowns.
Strips internal-only sections (경계·확인 메모, 논문 연관 메모) before publishing.
"""
import re, html, os

SRC = os.path.expanduser("~/workspace/goals/dji/briefs")
OUT = os.path.expanduser("~/workspace/github/droneseal-tech")
BRIEFS = [
    ("2026-11-05-mavic3e-mapping.md", "2026-11-05-mavic3e-mapping.html",
     "2026-11-05", "DJI 기술 브리핑"),
    ("2026-11-03-matrice4-sensing.md", "2026-11-03-matrice4-sensing.html",
     "2026-11-03", "DJI 기술 브리핑"),
    ("2026-11-04-xag-realterra.md", "2026-11-04-xag-realterra.html",
     "2026-11-04", "DJI 기술 브리핑"),
]

PAGE_CSS = """
:root{--green:#2D7A4F;--green-dark:#1E5C38;--pale:#E7F4ED;--ink:#222;--muted:#5a6b60;--line:#dce8df}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,'Segoe UI','Noto Sans KR',sans-serif;color:var(--ink);line-height:1.75;background:#fff}
header{background:var(--green);color:#fff;padding:2.2rem 1.2rem 1.6rem}
.wrap{max-width:860px;margin:0 auto;padding:0 1.2rem}
header h1{margin:0;font-size:1.7rem;letter-spacing:.02em}
header p{margin:.5rem 0 0;opacity:.92}
nav{margin-top:1rem}
nav a{color:#fff;opacity:.9;margin-right:1.1rem;text-decoration:none;font-size:.95rem}
nav a:hover{opacity:1;text-decoration:underline}
main{padding:2rem 0 3rem}
h2{color:var(--green-dark);border-bottom:2px solid var(--green);padding-bottom:.35rem;margin-top:2.4rem}
h3{color:var(--green-dark);margin-top:1.8rem}
a{color:var(--green-dark)}
.meta{color:var(--muted);font-size:.9rem}
.card{border:1px solid var(--line);border-radius:10px;padding:1rem 1.2rem;margin:.8rem 0;background:#fbfdfc}
.card h3{margin:.1rem 0 .3rem}
.card h3 a{text-decoration:none}
.card h3 a:hover{text-decoration:underline}
.card p{margin:.2rem 0}
.badge{display:inline-block;background:var(--pale);color:var(--green-dark);border-radius:999px;padding:.05rem .6rem;font-size:.8rem;margin-right:.4rem}
.full{font-size:.9rem}
footer{border-top:1px solid var(--line);padding:1.6rem 0 2.4rem;color:var(--muted);font-size:.92rem}
footer a{color:var(--green-dark)}
blockquote{border-left:3px solid var(--green);margin:1rem 0;padding:.4rem 1rem;background:var(--pale)}
ul{padding-left:1.3rem}
"""

PAGE_TMPL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — DRONE SEAL 기술 브리핑 아카이브</title>
<style>{css}</style>
</head>
<body>
<header><div class="wrap">
<h1>DRONE SEAL · 무인항공AI 교육센터</h1>
<p>DJI·XAG 기술 브리핑 아카이브</p>
<nav><a href="../index.html">← 아카이브 목록</a> <a href="../index.html#portfolio">회사 소개</a></nav>
</div></header>
<main><div class="wrap">
<p class="meta">{date} · {kind}</p>
{body}
<p style="margin-top:2.5rem"><a href="../index.html">← 아카이브 목록으로 돌아가기</a></p>
</div></main>
<footer><div class="wrap">
DRONE SEAL · 무인항공AI 교육센터<br>
W. <a href="https://droneseal.kr">droneseal.kr</a> · T. 055-345-8231 · M. <a href="mailto:amen@droneseal.kr">amen@droneseal.kr</a>
</div></footer>
</body>
</html>
"""

def strip_internal(text: str) -> str:
    """Remove internal-only sections: 경계·확인 메모 block and 논문 연관 메모 line."""
    lines = text.split("\n")
    out = []
    skipping = False
    for ln in lines:
        if ln.startswith("**경계·확인 메모.**"):
            skipping = True
            continue
        if skipping:
            if ln.startswith("**출처·참고문헌:**"):
                skipping = False
                out.append(ln)
            continue
        if "논문 연관 메모" in ln:
            continue
        out.append(ln)
    return "\n".join(out)

def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(https?://[^\s\)\]]+)", r'<a href="\1">\1</a>', s)
    return s

def md_to_html(text: str) -> str:
    lines = text.split("\n")
    parts = []
    in_ul = False
    para = []
    def flush_para():
        nonlocal para
        if para:
            parts.append("<p>" + " ".join(inline(p) for p in para) + "</p>")
            para = []
    def close_ul():
        nonlocal in_ul
        if in_ul:
            parts.append("</ul>")
            in_ul = False
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            flush_para(); close_ul(); continue
        if s.startswith("# "):
            flush_para(); close_ul()
            parts.append("<h1>" + inline(s[2:].strip()) + "</h1>"); continue
        if s.startswith("## "):
            flush_para(); close_ul()
            parts.append("<h2>" + inline(s[3:].strip()) + "</h2>"); continue
        if s.startswith("- "):
            flush_para()
            if not in_ul:
                parts.append("<ul>"); in_ul = True
            parts.append("<li>" + inline(s[2:].strip()) + "</li>"); continue
        para.append(s.strip())
    flush_para(); close_ul()
    return "\n".join(parts)

os.makedirs(os.path.join(OUT, "briefs"), exist_ok=True)
for src, dst, date, kind in BRIEFS:
    with open(os.path.join(SRC, src), encoding="utf-8") as f:
        raw = f.read()
    cleaned = strip_internal(raw)
    assert "경계·확인 메모" not in cleaned, f"strip failed: {src}"
    assert "논문 연관 메모" not in cleaned, f"strip failed: {src}"
    assert "Groq" not in cleaned and "NVIDIA" not in cleaned, f"internal tool mention left: {src}"
    title = re.search(r"^## (.+)$", cleaned, re.M).group(1)
    body = md_to_html(cleaned)
    page = PAGE_TMPL.format(title=html.escape(title), css=PAGE_CSS,
                            date=date, kind=kind, body=body)
    with open(os.path.join(OUT, "briefs", dst), "w", encoding="utf-8") as f:
        f.write(page)
    print("built", dst, "title:", title[:60])
print("done")
