"""Generate terminal-style project cards and an open-to banner into assets/.
    python scripts/make_cards.py
Set STATIC=1 to emit frozen frames (no animation) for local previews."""
import os
from html import escape

STATIC = os.environ.get("STATIC") == "1"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

W = 410          # card width (two cards + table padding line up with the 860px heatmap)
PAD = 22
CW = 7.3         # conservative px per character at 12px monospace
LINE_H = 19

# slug, title, subtitle, description lines (<= 50 chars each), tags, accent colour
PROJECTS = [
    ("chainledger", "ChainLedger", "Tokenised fund-share reconciliation",
     ["Permissioned ERC-20 registry on Sepolia with",
      "an event-driven Python indexer. A four-rule",
      "engine flags on-chain vs off-chain drift,",
      "ranked Critical / Warning / OK. 12 contract +",
      "15 pytest tests run on every push (CI)."],
     ["Solidity", "Hardhat", "OpenZeppelin", "Python", "web3.py", "FastAPI", "Streamlit"],
     "#39d353"),
    ("bhoomirakshak", "BhoomiRakshak", "PKI-based land record system (MVP)",
     ["Every registration or transfer is digitally",
      "signed (RSA-2048) and routed Landowner →",
      "Village Officer → Registrar. Chained",
      "signatures give a tamper-evident audit trail."],
     ["Node.js", "Express", "TypeScript", "Prisma", "PostgreSQL", "React", "Tailwind"],
     "#58a6ff"),
    ("finsight", "FinSight", "Personal finance analytics platform",
     ["Normalised PostgreSQL schema behind FastAPI",
      "REST endpoints. Next.js dashboard shows",
      "category-wise spending and budget tracking.",
      "JWT auth + Cloudflare Turnstile protection."],
     ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Next.js", "Recharts"],
     "#d2a8ff"),
    ("portfolio-risk", "Portfolio Risk Analyzer", "Equity portfolio risk insights",
     ["Two years of NSE prices → return, volatility,",
      "Sharpe, max drawdown and correlation, in",
      "Plotly / Streamlit dashboards. Validated vs",
      "published fund data: traced a 15.7% vs 12.9%",
      "volatility gap to sector concentration."],
     ["Python", "Pandas", "NumPy", "yfinance", "Streamlit", "Plotly"],
     "#ffa657"),
]

OPEN_TO = ["Product Management", "Consulting", "Cloud", "Software Engineering",
           "Data & Analytics", "Management"]
ACCENTS = ["#39d353", "#58a6ff", "#d2a8ff", "#ffa657", "#ff7b72", "#79c0ff"]

STYLE = f"""<style>
  text {{ font-family: {FONT}; }}
  .a {{ {'' if STATIC else 'opacity: 0; animation: in .6s ease-out forwards;'} }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(8px); }}
                  to   {{ opacity: 1; transform: translateY(0); }} }}
</style>"""


def layout_chips(labels, x0, y0, max_w, h, gap, cw, pad):
    placed, x, y = [], x0, y0
    for t in labels:
        w = len(t) * cw + pad
        if x + w > x0 + max_w and x > x0:
            x, y = x0, y + h + gap
        placed.append((t, x, y, w))
        x += w + gap
    return placed, y + h


def chip(t, x, y, w, h, color, size):
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h // 2}" '
            f'fill="#161b22" stroke="{color}" stroke-opacity=".55"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + size * 0.35:.1f}" '
            f'text-anchor="middle" font-size="{size}" fill="{color}">{escape(t)}</text>')


def plan_card(p):
    slug, title, sub, lines, tags, color = p
    for ln in lines:
        assert len(ln) * CW <= W - 2 * PAD, f"line too long in {slug}: {ln!r} ({len(ln)})"
    y_desc = 112
    y_chips = y_desc + len(lines) * LINE_H - 6
    chips, bottom = layout_chips(tags, PAD, y_chips, W - 2 * PAD, 22, 8, 6.8, 18)
    return chips, bottom + 20


def render_card(p, idx, height):
    slug, title, sub, lines, tags, color = p
    chips, _ = plan_card(p)
    desc = "".join(
        f'<text x="{PAD}" y="{112 + i * LINE_H}" font-size="12" fill="#c9d1d9">{escape(ln)}</text>'
        for i, ln in enumerate(lines))
    chips_svg = "".join(chip(t, x, y, w, 22, color, 11) for t, x, y, w in chips)
    delay = f' style="animation-delay:{idx * 0.25:.2f}s"' if not STATIC else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}">
{STYLE}
<rect x=".5" y=".5" width="{W - 1}" height="{height - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<g class="a"{delay}>
<circle cx="22" cy="20" r="5" fill="#ff5f56"/><circle cx="40" cy="20" r="5" fill="#ffbd2e"/><circle cx="58" cy="20" r="5" fill="#27c93f"/>
<text x="76" y="24" font-size="11" fill="#8b949e">~/projects/{escape(slug)}</text>
<text x="{PAD}" y="62" font-size="16" font-weight="700" fill="{color}">{escape(title)}</text>
<text x="{PAD}" y="82" font-size="12" fill="#8b949e">{escape(sub)}</text>
{desc}
{chips_svg}
</g>
</svg>
'''


def render_banner():
    BW, h, gap, cw, pad = 860, 30, 12, 8.0, 28
    # split labels into balanced rows that fit the width
    rows, cur, cur_w = [], [], 0
    for t in OPEN_TO:
        w = len(t) * cw + pad
        if cur and cur_w + gap + w > BW - 300:  # ~3 chips per row
            rows.append(cur)
            cur, cur_w = [], 0
        cur_w += (gap if cur else 0) + w
        cur.append((t, w))
    rows.append(cur)

    BH = 24 + len(rows) * (h + 12) + 12
    parts, y, k = [], 24, 0
    for row in rows:
        total = sum(w for _, w in row) + gap * (len(row) - 1)
        x = (BW - total) / 2
        for t, w in row:
            parts.append(chip(t, x, y, w, h, ACCENTS[k % len(ACCENTS)], 13))
            x += w + gap
            k += 1
        y += h + 12
    delay = "" if STATIC else ' style="animation-delay:.2s"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}">
{STYLE}
<rect x=".5" y=".5" width="{BW - 1}" height="{BH - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<g class="a"{delay}>
{''.join(parts)}
</g>
</svg>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    height = max(plan_card(p)[1] for p in PROJECTS)  # same height for a tidy grid
    for i, p in enumerate(PROJECTS):
        path = os.path.join(OUT, f"card-{p[0]}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_card(p, i, height))
        print("wrote", os.path.normpath(path))
    path = os.path.join(OUT, "open-to.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_banner())
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
