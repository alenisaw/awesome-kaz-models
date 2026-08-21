#!/usr/bin/env python3
"""Generate all SVG visualizations for the README from data/models.yaml.

Deterministic: same input always produces byte-identical output. No network access.

Every chart is rendered twice — a light variant (`name.svg`) and a dark variant
(`name-dark.svg`) — using the same validated categorical palette. README.md embeds
both via `<picture>`/`prefers-color-scheme` so the chart matches the reader's
browser theme.

Visual system (palette, typography, heatmap layout) is intentionally identical to
the sister repository's scripts/generate_visualizations.py (awesome-kaz-datasets),
so the two catalogs read as one family.
"""

from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "models.yaml"
OUT = ROOT / "assets"

FONT = 'font-family:"Segoe UI",Inter,Arial,sans-serif'

SECTIONS = ["Text, NLP, and LLM", "Speech and audio", "Vision, OCR, and multimodal"]
SECTION_SHORT = {SECTIONS[0]: "Text/NLP", SECTIONS[1]: "Speech", SECTIONS[2]: "Vision"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# --- palette: identical to awesome-kaz-datasets' validated categorical order ---
THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "ink": "#0b0b0b",
        "ink_secondary": "#52514e",
        "ink_muted": "#898781",
        "grid": "#e1e0d9",
        "tile_stroke": "#e1e0d9",
        "blue": "#164a89",
        "orange": "#9a4422",
        "aqua": "#127250",
        "good": "#0ca30c",
        "na_fill": "#f3f2ee",
        "na_stroke": "#e1e0d9",
        # A darker/more saturated 5-step blue ramp (ColorBrewer Blues,
        # palest step dropped) for good step-to-step distinction. The legend
        # doesn't print numbers on top of these fills (see the heatmap
        # legend below), so there's no text-contrast constraint on the
        # palette itself.
        "seq": ["#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"],
    },
    "dark": {
        "surface": "#1a1a19",
        "ink": "#ffffff",
        "ink_secondary": "#c3c2b7",
        "ink_muted": "#898781",
        "grid": "#2c2c2a",
        "tile_stroke": "#383835",
        "blue": "#3987e5",
        "orange": "#d95926",
        "aqua": "#199e70",
        "good": "#0ca30c",
        "na_fill": "#242422",
        "na_stroke": "#383835",
        # Brightest step = most releases — the opposite direction from the
        # light ramp on purpose: on a near-black surface, going *darker*
        # for "more" makes the busiest cells fade into the background
        # instead of standing out. No text-contrast constraint on this
        # palette either (see the light theme's note above).
        "seq": ["#2c5580", "#2f6bab", "#2f83d6", "#3f9df0", "#6dc3ff"],
    },
}


def load_models():
    doc = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    return doc["models"]


def year_of(released):
    if not released or released == "Unknown":
        return None
    return int(str(released)[:4])


def month_of(released):
    if not released or released == "Unknown" or len(str(released)) < 7:
        return None
    return int(str(released)[5:7])


def write_both(basename, render):
    """render(theme_dict) -> list[str] of SVG lines. Writes light + dark variants."""
    stem = basename[:-4] if basename.endswith(".svg") else basename
    for theme_name, palette in THEMES.items():
        lines = render(palette)
        suffix = "" if theme_name == "light" else "-dark"
        (OUT / f"{stem}{suffix}.svg").write_text("\n".join(lines) + "\n", encoding="utf-8")


def svg_header(width, height, t, extra_style=""):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{t["surface"]}"/>',
        f'<style>text{{{FONT};fill:{t["ink"]}}}'
        f'.title{{font-size:22px;font-weight:700}}'
        f'.sub{{font-size:12px;fill:{t["ink_secondary"]}}}'
        f'.muted{{font-size:11px;fill:{t["ink_muted"]}}}'
        f'.axis{{font-size:12px;fill:{t["ink_muted"]}}}'
        f'.grid{{stroke:{t["grid"]};stroke-width:1}}'
        f'.legend{{font-size:12px;fill:{t["ink_secondary"]}}}'
        f'{extra_style}</style>',
    ]


# ---------------------------------------------------------------------------
# Release heatmap (per section) — year x month grid, cell shade = release
# count that month. No model names on the image; a legend below the grid
# maps color steps to counts/month.
# ---------------------------------------------------------------------------

def gen_release_heatmap(models, section, filename):
    section_models = [m for m in models if m["section"] == section]
    counts = Counter()
    for m in section_models:
        y, mo = year_of(m["released"]), month_of(m["released"])
        if y and mo:
            counts[(y, mo)] += 1
    if not counts:
        return

    years = list(range(min(y for y, _ in counts), max(y for y, _ in counts) + 1))
    max_n = max(counts.values())

    def render(t):
        # Cells are wider than tall (not square) so the grid reads as a wide
        # landscape strip — matching the wide README column — rather than a
        # small near-square block. Sized close to a typical rendered README
        # column width (~860-900px) so the width:100% stretch in the README
        # scales it up only slightly instead of blowing sparse sections
        # (fewer years = fewer rows, same fixed width) up into oversized cells.
        cell_w, cell_h, gap = 60, 26, 6
        step_x, step_y = cell_w + gap, cell_h + gap
        left, top, right = 56, 30, 20
        legend_h = 50
        bottom = 20 + legend_h
        width = left + 12 * step_x + right
        height = top + len(years) * step_y + bottom

        parts = svg_header(
            width, height, t,
            ".count{font-size:10px;font-weight:700}"
            f'.axis-strong{{font-size:12px;font-weight:700;fill:{t["ink_secondary"]}}}',
        )

        for col, month in enumerate(range(1, 13)):
            x = left + col * step_x
            parts.append(f'<text x="{x + cell_w/2}" y="{top - 10}" text-anchor="middle" class="axis-strong">{MONTHS[month-1]}</text>')

        for row, year in enumerate(years):
            y = top + row * step_y
            parts.append(f'<text x="{left - 10}" y="{y + cell_h/2 + 4}" text-anchor="end" class="axis-strong">{year}</text>')
            for col, month in enumerate(range(1, 13)):
                x = left + col * step_x
                n = counts.get((year, month), 0)
                if n == 0:
                    parts.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="5" fill="{t["na_fill"]}" stroke="{t["na_stroke"]}" stroke-width="1"/>')
                    continue
                idx = min(n - 1, len(t["seq"]) - 1)
                parts.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="5" fill="{t["seq"][idx]}"/>')

        # Count labels sit below each swatch, in the theme's normal text
        # color on the plain surface — not printed on top of the fill —
        # so there's no per-swatch text-contrast problem to solve at all.
        legend_y = top + len(years) * step_y + 20
        legend_label = "Releases/month:"
        parts.append(f'<text x="{left}" y="{legend_y + 9}" class="legend">{legend_label}</text>')
        lx = left + 11 * 7 + 14
        for i in range(min(max_n, len(t["seq"]))):
            fill = t["seq"][i]
            label = str(i + 1) if i < len(t["seq"]) - 1 or max_n <= len(t["seq"]) else f"{i+1}+"
            parts.append(f'<rect x="{lx}" y="{legend_y - 2}" width="16" height="16" rx="4" fill="{fill}"/>')
            parts.append(f'<text x="{lx+8}" y="{legend_y+30}" text-anchor="middle" class="legend">{label}</text>')
            lx += 24

        parts.append("</svg>")
        return parts

    write_both(filename, render)


# ---------------------------------------------------------------------------
# Model growth (cumulative releases over time, one line per section)
# ---------------------------------------------------------------------------

def gen_model_growth(models):
    by_section = defaultdict(list)
    for m in models:
        y = year_of(m["released"])
        if y:
            by_section[m["section"]].append(y)

    all_years = sorted({y for ys in by_section.values() for y in ys})
    if not all_years:
        return
    year_range = list(range(all_years[0], all_years[-1] + 1))

    series = {}
    for section in SECTIONS:
        counts = Counter(by_section.get(section, []))
        cumulative, running = [], 0
        for y in year_range:
            running += counts.get(y, 0)
            cumulative.append(running)
        series[section] = cumulative

    max_val = max(v for vals in series.values() for v in vals) or 1

    def render(t):
        left, top, right, bottom = 50, 30, 150, 40
        plot_w, plot_h = max(560, 70 * len(year_range)), 260
        width, height = left + plot_w + right, top + plot_h + bottom

        parts = svg_header(width, height, t, ".endlabel{font-size:12px;font-weight:700}")

        baseline = top + plot_h
        for i in range(5):
            v = round(max_val * i / 4)
            y = baseline - (v / max_val) * plot_h
            parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" class="grid"/>')
            parts.append(f'<text x="{left-10}" y="{y+4}" text-anchor="end" class="axis">{v}</text>')

        def px(i):
            return left + (i / max(1, len(year_range) - 1)) * plot_w

        for i, y in enumerate(year_range):
            if i % max(1, len(year_range) // 10) == 0 or i == len(year_range) - 1:
                parts.append(f'<text x="{px(i)}" y="{baseline+22}" text-anchor="middle" class="axis">{y}</text>')

        for section, key in zip(SECTIONS, ("blue", "orange", "aqua")):
            color = t[key]
            vals = series[section]
            points = " ".join(f"{px(i)},{baseline - (v/max_val)*plot_h}" for i, v in enumerate(vals))
            parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
            last_x, last_y = px(len(vals) - 1), baseline - (vals[-1] / max_val) * plot_h
            parts.append(f'<circle cx="{last_x}" cy="{last_y}" r="4" fill="{color}" stroke="{t["surface"]}" stroke-width="2"/>')
            parts.append(f'<text x="{last_x+10}" y="{last_y+4}" class="endlabel" fill="{color}">{SECTION_SHORT[section]} ({vals[-1]})</text>')

        parts.append("</svg>")
        return parts

    write_both("model_growth.svg", render)


def main():
    OUT.mkdir(exist_ok=True)
    models = load_models()

    gen_model_growth(models)

    gen_release_heatmap(models, SECTIONS[0], "nlp_release_heatmap.svg")
    gen_release_heatmap(models, SECTIONS[1], "speech_release_heatmap.svg")
    gen_release_heatmap(models, SECTIONS[2], "cv_release_heatmap.svg")

    print(f"Wrote visualizations (light + dark) to {OUT}")


if __name__ == "__main__":
    main()
