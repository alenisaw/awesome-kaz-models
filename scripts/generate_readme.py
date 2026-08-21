#!/usr/bin/env python3
"""Regenerate the managed blocks of README.md from data/models.yaml.

Usage:
    python scripts/generate_readme.py            # write README.md
    python scripts/generate_readme.py --check     # exit 1 if README.md would change

Only the content between "<!-- NAME:START -->" / "<!-- NAME:END -->" marker pairs is
replaced. Everything else in an existing README.md (narrative text, headings without
markers) is left untouched. On a first run with no README.md present, an embedded
default skeleton is used. If you edit DEFAULT_SKELETON itself, delete README.md
before regenerating so the new skeleton text actually takes effect.

Mirrors the sister repository's scripts/generate_readme.py (awesome-kaz-datasets)
so the two catalogs share one generation philosophy.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "models.yaml"
README = ROOT / "README.md"

SECTIONS = ["Text, NLP, and LLM", "Speech and audio", "Vision, OCR, and multimodal"]

# Hand-maintained: a short list of candidates independently confirmed to be
# REAL projects/organizations with a genuine, specific reason they aren't in
# the main catalog yet (a dead checkpoint link, no public weights despite a
# real paper, etc.) — not speculative names that merely appeared in research
# without independent confirmation. See CONTRIBUTING.md for the exact
# Watchlist criteria. Kept here (not in models.yaml) because these are
# narrative verification cases, not structured catalog records.
#
# Deliberately short and high-confidence: unconfirmed rumors, names that
# turned out not to correspond to any real resource, and vague "there might
# be more in this account" notes are not tracked here — see the Watchlist
# intro paragraph in DEFAULT_SKELETON below.
WATCHLIST = [
    ("Söyle",
     "The IS2AI GitHub repository and its ICAIIC 2024 paper are real, but the only "
     "pretrained-model link in the README (`dhcppc0/soyle_onnx` on Hugging Face) resolves "
     "to a 404. The official ISSAI project page links the code and a companion dataset but "
     "no model under the `issai` org — currently training-code-only, the same pattern "
     "as the official KazNERD repository."),
    ("AIT-Syn Kazakh TTS",
     "A Qwen3-TTS-12Hz-1.7B-Base fine-tune for Kazakh/Russian/English/Uzbek voice cloning "
     "(`nur-dev/ait-syn-4L`) is real and was indexed with a full model card (confirmed via "
     "third-party search results), but the repository currently returns HTTP 401 for "
     "anonymous access at both the API and page level — unlike the org's other gated repos "
     "(e.g. `nur-dev/ait-asr`), whose cards remain publicly readable. Could not be "
     "independently re-verified this pass."),
]

REPO = "alenisaw/awesome-kaz-models"

# Canonical task name -> short tag shown under the model name in the tables.
# Keep in sync with the task labels actually used in data/models.yaml.
TASK_ABBREV = {
    "Large language model": "LLM",
    "Masked language modelling / encoder": "MLM",
    "Instruction following": "IF",
    "Named entity recognition": "NER",
    "Question answering": "QA",
    "Sentiment classification": "SC",
    "Text classification": "TC",
    "Text generation": "TG",
    "Grammar correction": "GEC",
    "Transliteration": "TR",
    "POS tagging": "POS",
    "Dependency parsing": "DEP",
    "Morphological analysis": "MORPH",
    "Embeddings / dense retrieval": "EMB",
    "Machine translation": "MT",
    "Automatic speech recognition": "ASR",
    "Text-to-speech": "TTS",
    "Keyword spotting": "KWS",
    "Language identification": "LID",
    "Target-speaker ASR": "TS-ASR",
    "Speaker verification": "SV",
    "OCR": "OCR",
    "Handwriting recognition": "HTR",
    "Image captioning": "IC",
    "Vision-language modelling": "VLM",
    "Audio-vision-language modelling": "AVL",
    "Text-to-image": "T2I",
}


def task_tag(task):
    return TASK_ABBREV.get(task, task)


def task_glossary(rows, cols=6, label=True):
    used = sorted(
        {t for m in rows for t in m.get("tasks", [])},
        key=lambda t: (task_tag(t).lower(), t.lower()),
    )
    # <strong>, not **bold** — this table is a multi-line HTML block, which GitHub
    # does not run markdown-inline parsing over (see the earlier badges bug).
    task_expansions = {"OCR": "Optical character recognition"}
    entries = [
        f"<strong>{task_tag(t)}</strong> — {task_expansions.get(t, t)}" for t in used
    ]
    rows_of_cells = [entries[i : i + cols] for i in range(0, len(entries), cols)]
    table_rows = []
    for row_cells in rows_of_cells:
        padded = row_cells + [""] * (cols - len(row_cells))
        table_rows.append("<tr>" + "".join(f'<td align="center" valign="middle">{c}</td>' for c in padded) + "</tr>")
    prefix = "**Abbreviations:**\n\n" if label else ""
    return prefix + '<table width="100%">\n' + "\n".join(table_rows) + "\n</table>"


def picture(alt, base, width="100%"):
    return (
        '<picture>\n'
        f'  <source media="(prefers-color-scheme: dark)" srcset="assets/{base}-dark.svg">\n'
        f'  <img src="assets/{base}.svg" alt="{alt}" width="{width}">\n'
        '</picture>'
    )


DEFAULT_SKELETON = """<h1 align="center">
  <img src="https://emojiassets.saruwakakun.design/a/lg/1f1f0_1f1ff_1o53s.webp" width="34" valign="middle" alt="Kazakhstan flag">
  Awesome Kazakh Models
  <img src="https://emojiassets.saruwakakun.design/a/lg/1f1f0_1f1ff_1o53s.webp" width="34" valign="middle" alt="Kazakhstan flag">
</h1>

<p align="center">
  A curated, research-grade catalog of public AI models with substantial support for the Kazakh language.
</p>

<!-- BADGES:START -->
<!-- BADGES:END -->

<p align="center">
  <a href="#about">About</a> ·
  <a href="#text-nlp-and-llm">Text &amp; NLP</a> ·
  <a href="#speech-and-audio">Speech</a> ·
  <a href="#vision-ocr-and-multimodal">Vision &amp; OCR</a> ·
  <a href="#watchlist--announced-resources">Watchlist</a> ·
  <a href="#contributing">Contributing</a> ·
  <a href="#license">License</a>
</p>

> ### ✨ Explore Kazakh datasets across every domain — [awesome-kaz-datasets](https://github.com/Allessyer/awesome-kaz-datasets)

---

## About

Public Kazakh-capable models are scattered across Hugging Face, GitHub, and
institutional pages, with no reliable map of what's actually obtainable
today. A search for "Kazakh" mixes genuinely Kazakh-trained models with
generic multilingual foundations, packaging clones of the same checkpoint,
and paper-only experiments with no published weights.

Every entry below is checked against its primary source, with release date,
license, access terms, and evidence of Kazakh training recorded rather than
assumed. Resources that are announced or not yet independently verifiable go
in the [Watchlist](#watchlist--announced-resources) instead of the main
tables. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full inclusion policy
and [CHANGELOG.md](CHANGELOG.md) for what's new.

<!-- LANDSCAPE:START -->
<!-- LANDSCAPE:END -->

## Text, NLP, and LLM

<!-- NLP_SECTION:START -->
<!-- NLP_SECTION:END -->

## Speech and audio

<!-- SPEECH_SECTION:START -->
<!-- SPEECH_SECTION:END -->

## Vision, OCR, and multimodal

<!-- VISION_SECTION:START -->
<!-- VISION_SECTION:END -->

## Watchlist / announced resources

Resources below are announced, described in a paper without a public artifact,
of unclear provenance, or not yet independently verifiable as substantively
Kazakh-trained models. They are intentionally **not** part of the main catalog
above, but could plausibly still qualify once verification succeeds.

<!-- WATCHLIST:START -->
<!-- WATCHLIST:END -->

## Abbreviations

<!-- ABBREVIATIONS:START -->
<!-- ABBREVIATIONS:END -->

## Contributing

Missing a Kazakh model, or spotted outdated metadata? Contributions are welcome:

- **Add a model** — [open a submission issue](../../issues/new?template=model-submission.yml)
  or send a PR directly.
- **Fix or update an entry** — edit `data/models.yaml` and open a PR.
- **Report a stale number** — Hugging Face download/like counts drift; flag it
  with the current value, though note the catalog does not treat these as
  intrinsic model properties.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full inclusion criteria, required
metadata, and PR format.

## Contributors

<p align="center">
  <a href="https://github.com/REPO_PLACEHOLDER/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=REPO_PLACEHOLDER" alt="Contributors to awesome-kaz-models">
  </a>
</p>

## License

This catalog's own content — the repository structure, documentation, generated
tables, and scripts — is released under the [MIT License](LICENSE). Models
linked from this catalog remain under their own respective licenses (recorded
per entry above); this MIT license does not extend to their contents.
"""

DEFAULT_SKELETON = DEFAULT_SKELETON.replace("REPO_PLACEHOLDER", REPO)


def load_models():
    doc = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    return doc["models"]


def released_sort_key(m):
    r = m.get("released")
    if not r or r == "Unknown":
        return (0, 0, 0)
    parts = str(r).split("-")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 0
    return (1, year, month)


def last_name(name):
    return name.strip().split()[-1] if name else name


def author_and_org(m):
    authors = [a["name"] for a in (m.get("authors") or []) if a.get("name")]
    orgs = [o["name"] for o in (m.get("organization") or []) if o.get("name")]
    author_str = None
    if len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{last_name(authors[0])} & {last_name(authors[1])}"
    elif len(authors) >= 3:
        author_str = f"{last_name(authors[0])} et al."
    org_str = " · ".join(orgs) if orgs else None
    return author_str, org_str


def author_line(m):
    # Individual/group author when known; falls back to the organization name
    # only when no author is recorded at all (e.g. an org-attributed release
    # like the HPLT project or MMS project team). Affiliation is not shown
    # alongside a named author — keeps the Model cell to name + one
    # attribution line, not name + author + affiliation.
    author_str, org_str = author_and_org(m)
    name = author_str or org_str
    if not name:
        return None
    author_link = (m.get("links") or {}).get("paper") or (m.get("links") or {}).get("project")
    display = f"[{name}]({author_link})" if author_link and author_str else name
    return f"<sub>{display}</sub>"


def format_access(m):
    # License is intentionally not surfaced in the table — it stays in
    # data/models.yaml rather than in the display.
    return (m.get("access") or "unavailable").capitalize()


def format_storage(m):
    storage = m.get("storage") or {}
    value = storage.get("value")
    if value is None:
        return "Not reported"
    unit = storage.get("unit") or ""
    return f"{value} {unit}".strip()


def format_parameters(m):
    # Parameter count first, then architecture/base — stacked, dash-prefixed.
    params = m.get("params") or {}
    pieces = []
    p_display = params.get("display")
    if p_display and p_display != "Not reported":
        pieces.append(str(p_display))
    arch = m.get("architecture")
    base = m.get("base_model")
    if arch and base and arch != base:
        pieces.append(f"{arch} (base: {base})")
    elif arch:
        pieces.append(arch)
    elif base:
        pieces.append(f"base: {base}")
    if not pieces:
        return "Not reported"
    return "<br>".join(f"– {p}" for p in pieces)


def model_row(m, idx):
    tags = " · ".join(task_tag(t) for t in (m.get("tasks") or [])) or "Not reported"
    model_url = (m.get("links") or {}).get("model")
    display_name = f"[{m['name']}]({model_url})" if model_url else m["name"]

    name_lines = [f"**{display_name}**"]
    al = author_line(m)
    if al:
        name_lines.append(al)
    name_lines.append(f"<sub>{format_access(m)}</sub>")
    name_cell = "<br>".join(name_lines)

    released = m.get("released") or "Unknown"
    return "| {idx} | {released} | {name} | {task} | {desc} | {storage} | {params} |".format(
        idx=idx,
        released=released,
        name=name_cell,
        task=tags,
        desc=m.get("description") or "",
        storage=format_storage(m),
        params=format_parameters(m),
    )


def model_table(rows):
    header = (
        "| ID | Released | Model | Task | Description | Storage | Parameters |\n"
        "|---:|---|---|---|---|---|---|"
    )
    ordered = sorted(rows, key=released_sort_key, reverse=True)
    body = "\n".join(model_row(m, i + 1) for i, m in enumerate(ordered))
    return header + "\n" + body


def build_section(models, section):
    rows = [m for m in models if m["section"] == section]
    return model_table(rows)


def build_landscape(models):
    caption = "<sub>Cumulative Kazakh model-family releases over time, by section.</sub>"
    return picture("Cumulative Kazakh model-family releases over time, by section", "model_growth") + "\n\n" + caption


def build_abbreviations(models):
    return task_glossary(models, cols=6, label=False)


def build_badges(models):
    # Markdown image syntax is not parsed inside a multi-line HTML block, so these
    # are plain <img> tags rather than ![]() — otherwise GitHub renders the literal
    # "![Models](...)" text instead of the badge.
    n = len(models)
    open_n = sum(1 for m in models if m["access"] == "open")
    open_pct = round(100 * open_n / n)
    stars = (
        f'<img alt="GitHub Repo stars" '
        f'src="https://img.shields.io/github/stars/{REPO}?style=flat&color=eda100">'
    )
    badges = [
        ("Models", str(n), "2a78d6"),
        ("Open weights", f"{open_pct}%25", "2ea44f"),
        ("Last verified", "2026--08--21", "1baf7a"),
    ]
    parts = [stars] + [
        f'<img alt="{label}" src="https://img.shields.io/badge/{label.replace(" ", "_")}-{value}-{color}">'
        for label, value, color in badges
    ]
    return '<p align="center">\n  ' + "\n  ".join(parts) + "\n</p>"


def build_watchlist():
    return "\n".join(f"- **{name}** — {reason}" for name, reason in WATCHLIST)


BLOCKS = {
    "BADGES": build_badges,
    "LANDSCAPE": build_landscape,
    "NLP_SECTION": lambda models: build_section(models, "Text, NLP, and LLM"),
    "SPEECH_SECTION": lambda models: build_section(models, "Speech and audio"),
    "VISION_SECTION": lambda models: build_section(models, "Vision, OCR, and multimodal"),
    "WATCHLIST": lambda models: build_watchlist(),
    "ABBREVIATIONS": lambda models: build_abbreviations(models),
}


def apply_blocks(content, models):
    for name, builder in BLOCKS.items():
        start = f"<!-- {name}:START -->"
        end = f"<!-- {name}:END -->"
        si = content.find(start)
        ei = content.find(end)
        if si == -1 or ei == -1:
            raise ValueError(f"Marker pair {name} not found in README skeleton")
        replacement = builder(models)
        content = content[: si + len(start)] + "\n" + replacement + "\n" + content[ei:]
    return content


def main():
    check = "--check" in sys.argv
    models = load_models()

    base = README.read_text(encoding="utf-8") if README.exists() else DEFAULT_SKELETON
    # If the existing file predates this marker set (e.g. the pre-redesign layout
    # with DASHBOARD/per-section overview cards), fall back to the skeleton.
    if "<!-- ABBREVIATIONS:START -->" not in base:
        base = DEFAULT_SKELETON

    new_content = apply_blocks(base, models)

    if check:
        if README.exists() and README.read_text(encoding="utf-8") == new_content:
            print("OK: README.md is up to date.")
            return 0
        print("STALE: README.md does not match generated output. Run scripts/generate_readme.py.")
        return 1

    README.write_text(new_content, encoding="utf-8")
    print(f"Wrote {README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
