"""Generate a neofetch-style info-card.svg. Edit the CARD dict below, then run:
    python scripts/make_info_card.py
Set STATIC=1 to emit a frozen frame (no animation) for local previews."""
import os
from html import escape

# ---- EDIT THESE -----------------------------------------------------------
USER = "manyashri1901"
CARD = [
    ("Now", "Your current role / what you're studying"),
    ("Prev", "Previous role, internship or education"),
    ("Stack", "Python, JavaScript, SQL, Git"),
    ("Focus", "What you're learning or building"),
    ("Highlight", "One project or achievement you're proud of"),
    ("Reach", "your@email.com"),
]
# ---------------------------------------------------------------------------

STATIC = os.environ.get("STATIC") == "1"
W, ROW, TOP = 490, 26, 70
H = TOP + len(CARD) * ROW + 30
KEY_COLORS = ["#58a6ff", "#d2a8ff", "#39d353", "#ffa657", "#ff7b72", "#79c0ff"]

rows = []
for i, (k, v) in enumerate(CARD):
    y = TOP + i * ROW
    delay = 0.4 + i * 0.25
    anim = "" if STATIC else f' style="animation-delay:{delay}s"'
    cls = "r" if STATIC else "r a"
    rows.append(
        f'<g class="{cls}"{anim}>'
        f'<text x="24" y="{y}" class="k" fill="{KEY_COLORS[i % len(KEY_COLORS)]}">{escape(k)}</text>'
        f'<text x="110" y="{y}" class="v">{escape(v)}</text></g>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font: 14px ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .k {{ font-weight: 700; }}
  .v {{ fill: #c9d1d9; }}
  .a {{ opacity: 0; animation: in .45s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-8px); }}
                  to   {{ opacity: 1; transform: translateX(0); }} }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="22" cy="20" r="6" fill="#ff5f56"/><circle cx="42" cy="20" r="6" fill="#ffbd2e"/><circle cx="62" cy="20" r="6" fill="#27c93f"/>
<text x="24" y="50" fill="#39d353" style="font-weight:700">{escape(USER)}@github</text>
{''.join(rows)}
</svg>
'''

out = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", os.path.normpath(out))
