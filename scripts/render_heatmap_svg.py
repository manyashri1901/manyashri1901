"""Render data/contributions.json as an animated 53x7 heatmap SVG."""
import json
import os
from datetime import date

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP = 13, 3
STEP = CELL + GAP
LEFT, TOP = 40, 56
RIGHT_PAD = 24


def level_for(day):
    """GitHub gives levels 0-4; promote the very top days to level 5 (neon)."""
    lv = day["level"]
    return 5 if lv == 4 and day["count"] >= 15 else lv


def main():
    with open(DATA) as f:
        data = json.load(f)
    days, stats, user = data["days"], data["stats"], data["username"]

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday-first rows

    # FIX: size the canvas from the real number of week columns so the newest
    # weeks are never clipped (53 columns need more than the old fixed 860px).
    ncols = (len(days) + offset + 6) // 7
    W = LEFT + ncols * STEP + RIGHT_PAD

    rects, months = [], []
    last_month = None
    for i, d in enumerate(days):
        idx = i + offset
        col, row = idx // 7, idx % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        delay = round((col + row) * 0.018, 3)  # diagonal reveal
        fill = PALETTE[level_for(d)]
        rects.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{fill}" style="animation-delay:{delay}s">'
            f'<title>{d["count"]} on {d["date"]}</title></rect>'
        )
        m = d["date"][5:7]
        if row == 0 and m != last_month:
            label = date.fromisoformat(d["date"]).strftime("%b")
            # FIX: if the first (partial) month label sits right next to the
            # second one ("OctNov"), drop the first so they don't overlap.
            if len(months) == 1 and x - months[0][0] < 3 * STEP:
                months.pop()
            months.append((x, label))
            last_month = m

    month_labels = "".join(
        f'<text x="{x}" y="{TOP - 10}" class="t">{label}</text>' for x, label in months
    )

    day_labels = "".join(
        f'<text x="8" y="{TOP + r * STEP + 11}" class="t">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    grid_bottom = TOP + 7 * STEP
    legend_x = W - 40 - len(PALETTE) * STEP - 70
    legend = f'<text x="{legend_x}" y="{grid_bottom + 24}" class="t">Less</text>'
    for i, c in enumerate(PALETTE):
        legend += (f'<rect x="{legend_x + 32 + i * STEP}" y="{grid_bottom + 13}" '
                   f'width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
    legend += (f'<text x="{legend_x + 36 + len(PALETTE) * STEP}" '
               f'y="{grid_bottom + 24}" class="t">More</text>')

    footer = (f'{stats["total"]:,} contributions in the last year  ·  '
              f'current streak {stats["current_streak"]}d  ·  '
              f'longest {stats["longest_streak"]}d')
    H = grid_bottom + 40

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .t {{ font: 11px ui-monospace, SFMono-Regular, Menlo, monospace; fill: #8b949e; }}
  .h {{ font: 13px ui-monospace, SFMono-Regular, Menlo, monospace; fill: #c9d1d9; }}
  .c {{ opacity: 0; transform-box: fill-box; animation: in .5s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(-8px); }}
                  to   {{ opacity: 1; transform: translateY(0); }} }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="{LEFT}" y="24" class="h">{user}@github ~ $ contributions --last-year</text>
{month_labels}
{day_labels}
{''.join(rects)}
<text x="{LEFT}" y="{grid_bottom + 24}" class="t">{footer}</text>
{legend}
</svg>
'''
    with open(OUT, "w") as f:
        f.write(svg)
    print("wrote", os.path.normpath(OUT), len(svg), "bytes")


if __name__ == "__main__":
    main()
