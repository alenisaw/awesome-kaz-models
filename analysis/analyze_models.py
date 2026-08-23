#!/usr/bin/env python3
"""Reproducible descriptive and benchmark analysis for awesome-kaz-models.

The catalog row is the unit of analysis. A row can represent a model family with
multiple checkpoint sizes, so counts are model-family releases, not checkpoints.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODELS_YAML = ROOT / "data" / "models.yaml"
OUT = ROOT / "analysis"
DATA_OUT = OUT / "data"
FIG_OUT = OUT / "figures"
SNAPSHOT_DATE = "2026-08-23"

SECTIONS = [
    "Text, NLP, and LLM",
    "Speech and audio",
    "Vision, OCR, and multimodal",
]
SECTION_SHORT = {
    "Text, NLP, and LLM": "Text / NLP / LLM",
    "Speech and audio": "Speech / audio",
    "Vision, OCR, and multimodal": "Vision / multimodal",
}
COLORS = {
    "Text, NLP, and LLM": "#2563eb",
    "Speech and audio": "#f97316",
    "Vision, OCR, and multimodal": "#10b981",
}


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIG_OUT / f"{stem}.png", dpi=220, bbox_inches="tight", facecolor="white")
    svg_path = FIG_OUT / f"{stem}.svg"
    fig.savefig(
        svg_path,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Date": SNAPSHOT_DATE},
    )
    # Matplotlib writes trailing spaces in multiline SVG path data. Normalize
    # generated text so repository whitespace checks remain clean.
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


def released_year(value: str) -> int | None:
    if not value or value == "Unknown":
        return None
    return int(str(value)[:4])


def released_month(value: str) -> int | None:
    if not value or value == "Unknown" or len(str(value)) < 7:
        return None
    return int(str(value)[5:7])


def load_catalog() -> tuple[list[dict], pd.DataFrame, pd.DataFrame]:
    models = yaml.safe_load(MODELS_YAML.read_text(encoding="utf-8"))["models"]
    rows = []
    task_rows = []
    for m in models:
        year = released_year(m["released"])
        month = released_month(m["released"])
        metric_summary = (m.get("metrics") or {}).get("summary")
        rows.append(
            {
                "id": m["id"],
                "name": m["name"],
                "released": m["released"],
                "year": year,
                "month": month,
                "section": m["section"],
                "kind": m["kind"],
                "access": m["access"],
                "tier": m["tier"],
                "tasks": " | ".join(m["tasks"]),
                "task_count": len(m["tasks"]),
                "has_numeric_metric_summary": bool(metric_summary),
                "metric_summary": metric_summary,
                "model_url": (m.get("links") or {}).get("model"),
                "paper_url": (m.get("links") or {}).get("paper"),
            }
        )
        for task in m["tasks"]:
            task_rows.append(
                {
                    "id": m["id"],
                    "name": m["name"],
                    "year": year,
                    "month": month,
                    "section": m["section"],
                    "task": task,
                }
            )
    return models, pd.DataFrame(rows), pd.DataFrame(task_rows)


def write_descriptive_tables(models_df: pd.DataFrame, tasks_df: pd.DataFrame) -> dict:
    models_df.to_csv(DATA_OUT / "catalog_snapshot.csv", index=False)

    dated = models_df.dropna(subset=["year"]).copy()
    dated["year"] = dated["year"].astype(int)
    years = range(int(dated.year.min()), int(dated.year.max()) + 1)
    yearly = (
        dated.groupby(["year", "section"]).size().unstack(fill_value=0).reindex(years, fill_value=0)
    )
    yearly = yearly.reindex(columns=SECTIONS, fill_value=0)
    yearly["total"] = yearly.sum(axis=1)
    yearly["cumulative"] = yearly["total"].cumsum()
    yearly.to_csv(DATA_OUT / "releases_by_year.csv", index_label="year")

    task_trends = (
        tasks_df.dropna(subset=["year"])
        .assign(year=lambda x: x.year.astype(int))
        .groupby(["task", "year"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=years, fill_value=0)
    )
    task_trends["lifetime"] = task_trends.sum(axis=1)
    task_trends["recent_2025_2026"] = task_trends.get(2025, 0) + task_trends.get(2026, 0)
    task_trends["recent_share"] = task_trends["recent_2025_2026"] / task_trends["lifetime"]
    task_trends.sort_values(["recent_2025_2026", "lifetime"], ascending=False).to_csv(
        DATA_OUT / "task_trends.csv", index_label="task"
    )

    sections = models_df.groupby("section").size().reindex(SECTIONS, fill_value=0)
    access = models_df.groupby("access").size().sort_values(ascending=False)
    summary = {
        "snapshot_date": SNAPSHOT_DATE,
        "catalog_rows_model_families": int(len(models_df)),
        "known_release_year": int(models_df.year.notna().sum()),
        "unknown_release_year": int(models_df.year.isna().sum()),
        "metric_summary_available": int(models_df.has_numeric_metric_summary.sum()),
        "metric_summary_coverage_percent": round(
            100 * models_df.has_numeric_metric_summary.mean(), 1
        ),
        "sections": {SECTION_SHORT[k]: int(v) for k, v in sections.items()},
        "access": {str(k): int(v) for k, v in access.items()},
        "year_counts": {str(int(k)): int(v) for k, v in dated.groupby("year").size().items()},
        "recent_2025_2026": int(dated.year.isin([2025, 2026]).sum()),
        "recent_share_percent": round(100 * dated.year.isin([2025, 2026]).mean(), 1),
    }
    (DATA_OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def plot_release_history(models_df: pd.DataFrame) -> None:
    dated = models_df.dropna(subset=["year"]).copy()
    dated["year"] = dated.year.astype(int)
    years = np.arange(int(dated.year.min()), int(dated.year.max()) + 1)
    table = dated.groupby(["year", "section"]).size().unstack(fill_value=0).reindex(years, fill_value=0)
    table = table.reindex(columns=SECTIONS, fill_value=0)
    totals = table.sum(axis=1)
    cumulative = totals.cumsum()

    fig, ax = plt.subplots(figsize=(12, 6.4))
    bottom = np.zeros(len(years))
    for section in SECTIONS:
        vals = table[section].to_numpy()
        ax.bar(years, vals, bottom=bottom, color=COLORS[section], label=SECTION_SHORT[section], width=0.72)
        bottom += vals
    ax2 = ax.twinx()
    ax2.plot(years, cumulative, color="#111827", marker="o", linewidth=2.2, label="Cumulative")
    for x, total in zip(years, totals):
        if total:
            ax.text(x, total + 0.7, str(int(total)), ha="center", va="bottom", fontsize=9)
    ax.axvspan(2025.65, 2026.35, color="#fde68a", alpha=0.22, zorder=0)
    ax.text(2026, max(totals) * 0.88, "2026 YTD\n(to Aug 23)", ha="center", fontsize=9, color="#92400e")
    ax.set_title("Kazakh model-family releases accelerated sharply after 2023", loc="left", weight="bold", fontsize=16)
    ax.set_ylabel("New catalog entries released")
    ax2.set_ylabel("Cumulative entries with known year")
    ax.set_xticks(years)
    ax.set_ylim(0, max(totals) * 1.18)
    ax2.set_ylim(0, max(cumulative) * 1.12)
    ax.grid(axis="y", alpha=0.22)
    handles, labels = ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(handles + handles2, labels + labels2, frameon=False, ncol=4, loc="upper left")
    fig.text(0.01, 0.01, "Unit: catalog rows (model families), not individual checkpoints. Unknown-year entries excluded.", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save_figure(fig, "01_releases_by_year")


def plot_domain_mix(models_df: pd.DataFrame) -> None:
    dated = models_df.dropna(subset=["year"]).copy()
    dated["year"] = dated.year.astype(int)
    dated["period"] = pd.cut(
        dated.year,
        bins=[2017, 2022, 2024, 2026],
        labels=["2018–2022", "2023–2024", "2025–2026 YTD"],
    )
    counts = dated.groupby(["period", "section"], observed=False).size().unstack(fill_value=0)
    counts = counts.reindex(columns=SECTIONS, fill_value=0)
    shares = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.3), gridspec_kw={"width_ratios": [1, 1.55], "wspace": 0.28})
    overall = models_df.groupby("section").size().reindex(SECTIONS, fill_value=0)
    axes[0].barh([SECTION_SHORT[x] for x in SECTIONS][::-1], overall.to_numpy()[::-1], color=[COLORS[x] for x in SECTIONS][::-1])
    for i, value in enumerate(overall.to_numpy()[::-1]):
        if value >= 15:
            axes[0].text(value - 0.8, i, f"{value} ({100*value/len(models_df):.1f}%)", va="center", ha="right", color="white", fontsize=9.5, weight="bold")
        else:
            axes[0].text(value + 0.7, i, f"{value} ({100*value/len(models_df):.1f}%)", va="center", fontsize=10)
    axes[0].set_title("Overall catalog", loc="left", weight="bold")
    axes[0].set_xlabel("Model-family entries")
    axes[0].grid(axis="x", alpha=0.2)

    left = np.zeros(len(shares))
    for section in SECTIONS:
        vals = shares[section].to_numpy()
        bars = axes[1].barh(shares.index.astype(str), vals, left=left, color=COLORS[section], label=SECTION_SHORT[section])
        for bar, pct, n in zip(bars, vals, counts[section].to_numpy()):
            if pct >= 8:
                axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_y()+bar.get_height()/2, f"{n}\n{pct:.0f}%", ha="center", va="center", color="white", fontsize=9, weight="bold")
        left += vals
    for i, period in enumerate(shares.index.astype(str)):
        axes[1].text(-0.02, i, period, transform=axes[1].get_yaxis_transform(), va="center", ha="right", fontsize=9.5)
    axes[1].set_yticklabels([])
    axes[1].set_ylabel("")
    axes[1].set_title("Domain mix by release era", loc="left", weight="bold")
    axes[1].set_xlabel("Share of releases in era")
    axes[1].set_xlim(0, 100)
    axes[1].legend(frameon=False, ncol=3, bbox_to_anchor=(1, -0.12), loc="upper right")
    fig.suptitle("Text dominates, but vision/multimodal broadened after 2024", x=0.01, ha="left", weight="bold", fontsize=16)
    fig.subplots_adjust(left=0.14, right=0.98, bottom=0.18, top=0.80, wspace=0.46)
    save_figure(fig, "02_domain_mix")


def plot_task_interest(tasks_df: pd.DataFrame) -> None:
    recent = tasks_df[tasks_df.year.isin([2025, 2026])].copy()
    table = recent.groupby(["task", "year"]).size().unstack(fill_value=0).reindex(columns=[2025, 2026], fill_value=0)
    table["total"] = table.sum(axis=1)
    table = table.sort_values(["total", 2026], ascending=True).tail(15)

    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    ax.barh(table.index, table[2025], color="#93c5fd", label="2025 (full year)")
    ax.barh(table.index, table[2026], left=table[2025], color="#1d4ed8", label="2026 YTD (to Aug 23)")
    for i, (_, row) in enumerate(table.iterrows()):
        ax.text(row.total + 0.18, i, str(int(row.total)), va="center", fontsize=9)
    ax.set_title("Recent publication activity concentrates on ASR, LLMs, TTS, embeddings, and MT", loc="left", weight="bold", fontsize=15)
    ax.set_xlabel("Task labels attached to 2025–2026 model-family releases")
    ax.grid(axis="x", alpha=0.22)
    ax.legend(frameon=False, loc="lower right")
    fig.text(0.01, 0.01, "Multi-task families contribute once to each listed task; totals therefore exceed the number of model families. Counts proxy creator/research activity, not population demand.", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    save_figure(fig, "03_recent_task_interest")


def plot_task_heatmap(tasks_df: pd.DataFrame) -> None:
    dated = tasks_df.dropna(subset=["year"]).copy()
    dated["year"] = dated.year.astype(int)
    top = dated.groupby("task").size().nlargest(15).index
    heat = dated[dated.task.isin(top)].groupby(["task", "year"]).size().unstack(fill_value=0)
    heat = heat.reindex(columns=range(2018, 2027), fill_value=0)
    heat = heat.loc[heat.sum(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(11.8, 7.2))
    sns.heatmap(heat, cmap="Blues", annot=True, fmt="g", linewidths=0.5, linecolor="white", cbar_kws={"label": "Releases"}, ax=ax)
    ax.set_title("Task landscape: specialization broadened after 2023", loc="left", weight="bold", fontsize=15)
    ax.set_xlabel("Release year (2026 is YTD)")
    ax.set_ylabel("")
    fig.tight_layout()
    save_figure(fig, "04_task_heatmap")


def metric_rows() -> pd.DataFrame:
    rows = [
        # KSC benchmark family. Standard split/version differences are retained in notes.
        (2020, "SAIDA Kazakh ASR", "KSC", "WER", 8.70, "benchmark-family", "paper", "https://arxiv.org/abs/2009.10334", "Original KSC test; paper reports 2.8 CER / 8.7 WER."),
        (2021, "Wav2Vec2 XLSR-53 Kazakh", "KSC", "WER", 19.65, "benchmark-family", "model card", "https://huggingface.co/aismlv/wav2vec2-large-xlsr-kazakh", "KSC v1.1 test partition."),
        (2021, "IS2AI Multilingual ASR", "KSC", "WER", 7.90, "benchmark-family", "paper", "https://arxiv.org/abs/2108.01280", "Best multilingual result on the standard KSC test split; best monolingual was 8.0."),
        (2022, "KSC2 ASR", "KSC", "WER", 6.30, "benchmark-family", "paper", "https://www.isca-archive.org/interspeech_2022/mussakhojayeva22_interspeech.pdf", "KSC subset test, model trained on full KSC2; not the KSC2 overall result."),
        (2026, "Whisper Large v3 Tulpar", "KSC", "WER", 10.62, "benchmark-family", "model card", "https://huggingface.co/olzhasAl/whisper-large-v3-tulpar", "Card calls this ISSAI KSC test; decoding/normalization may differ from papers."),
        # KSC2 family. Public cards do not always pin identical sampled subsets/normalization.
        (2022, "KSC2 ASR", "KSC2", "WER", 15.60, "benchmark-family", "paper", "https://www.isca-archive.org/interspeech_2022/mussakhojayeva22_interspeech.pdf", "Overall six-source KSC2 test set."),
        (2024, "Whisper Base Kazakh", "KSC2", "WER", 15.36, "benchmark-family", "model card", "https://huggingface.co/akuzdeuov/whisper-base.kk", "Reported KSC2 test."),
        (2025, "Whisper Turbo KSC2", "KSC2", "WER", 9.16, "benchmark-family", "model card", "https://huggingface.co/abilmansplus/whisper-turbo-ksc2", "Official issai/Kazakh_Speech_Corpus_2 test partition."),
        (2025, "AIT-ASR", "KSC2", "WER", 36.05, "benchmark-family", "model card", "https://huggingface.co/nur-dev/ait-asr", "Independently measured 1,000-utterance KSC2 sample with uniform Whisper normalization."),
        (2026, "VibeVoice ASR Kazakh", "KSC2", "WER", 22.00, "benchmark-family", "model card", "https://huggingface.co/InflexionLab/VibeVoice-ASR-Kazakh", "Self-reported ISSAI_KSC2 test."),
        # FLEURS kk test is the cleanest cross-card comparison in the catalog.
        (2025, "AIT-ASR", "FLEURS kk", "WER", 17.10, "same-named-benchmark", "model card", "https://huggingface.co/nur-dev/ait-asr", "Independently measured FLEURS kk_kz test, 500 utterances."),
        (2026, "GigaAM Multilingual Large", "FLEURS kk", "WER", 4.40, "same-named-benchmark", "paper/model card", "https://huggingface.co/ai-sage/GigaAM-Multilingual", "Reported for the 600M Large CTC model on the FLEURS Kazakh test set."),
        (2026, "Kazakh Whisper Large-v3 Turbo", "FLEURS kk", "WER", 11.80, "same-named-benchmark", "model card", "https://huggingface.co/shyngys879/kazakh-whisper-large-v3-turbo", "Reported FLEURS Kazakh test."),
        (2026, "KRASR Whisper Small", "FLEURS kk", "WER", 76.09, "same-named-benchmark", "model card", "https://huggingface.co/KRASR/kazakh-russian-asr-whisper-small-full-ft", "Self-reported FLEURS kk test."),
    ]
    cols = ["year", "model", "benchmark", "metric", "value", "comparability", "source_type", "source_url", "notes"]
    df = pd.DataFrame(rows, columns=cols)
    df["lower_is_better"] = True
    return df


def plot_asr_metrics(metrics: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 6.6), sharey=False)
    for ax, benchmark in zip(axes, ["KSC", "KSC2", "FLEURS kk"]):
        d = metrics[metrics.benchmark == benchmark].sort_values(["year", "value"])
        x = np.arange(len(d))
        colors = ["#16a34a" if v == d.value.min() else "#60a5fa" for v in d.value]
        ax.bar(x, d.value, color=colors)
        ax.set_xticks(x, [f"{y}\n{m}" for y, m in zip(d.year, d.model)], rotation=52, ha="right", fontsize=8.5)
        ax.set_title(benchmark, weight="bold")
        ax.set_ylabel("Reported WER % (lower is better)")
        ax.grid(axis="y", alpha=0.22)
        ax.set_ylim(0, max(d.value) * 1.18)
        for i, v in enumerate(d.value):
            ax.text(i, v + max(d.value)*0.025, f"{v:.2f}", ha="center", fontsize=9)
    fig.suptitle("Reported Kazakh ASR quality over time — only within benchmark families", x=0.01, ha="left", weight="bold", fontsize=16)
    fig.text(0.01, 0.01, "Green marks the lowest reported WER in each panel. Test subsets, normalization, decoding and reporting provenance still differ; bars are not a universal leaderboard.", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    save_figure(fig, "05_asr_wer_over_time")


def mt_rows() -> pd.DataFrame:
    # Values transcribed from KazParC paper Table 6. "parsync" is the released Tilmash model.
    directions = ["EN→KK", "KK→EN", "KK→RU", "RU→KK"]
    models = ["NLLB base", "KazParC-only", "Tilmash", "Yandex", "Google"]
    flores = {
        "EN→KK": [0.11, 0.14, 0.20, 0.18, 0.20],
        "KK→EN": [0.28, 0.32, 0.32, 0.30, 0.36],
        "KK→RU": [0.15, 0.17, 0.18, 0.18, 0.20],
        "RU→KK": [0.08, 0.10, 0.13, 0.12, 0.13],
    }
    kazparc = {
        "EN→KK": [0.12, 0.18, 0.21, 0.18, 0.30],
        "KK→EN": [0.24, 0.33, 0.32, 0.28, 0.31],
        "KK→RU": [0.22, 0.29, 0.29, 0.29, 0.29],
        "RU→KK": [0.15, 0.21, 0.22, 0.23, 0.24],
    }
    rows = []
    for benchmark, values in [("FLoRes", flores), ("KazParC", kazparc)]:
        for direction in directions:
            for model, value in zip(models, values[direction]):
                rows.append((benchmark, direction, model, "BLEU", value))
    return pd.DataFrame(rows, columns=["benchmark", "direction", "model", "metric", "value"])


def plot_mt_metrics(mt: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 6.1), sharey=True)
    palette = {"NLLB base": "#94a3b8", "KazParC-only": "#60a5fa", "Tilmash": "#2563eb", "Yandex": "#f59e0b", "Google": "#dc2626"}
    for ax, benchmark in zip(axes, ["FLoRes", "KazParC"]):
        d = mt[mt.benchmark == benchmark]
        sns.barplot(data=d, x="direction", y="value", hue="model", palette=palette, ax=ax)
        ax.set_title(f"{benchmark} test", weight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("BLEU (higher is better)" if benchmark == "FLoRes" else "")
        ax.grid(axis="y", alpha=0.22)
        ax.legend_.remove()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=5, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 0.045))
    fig.suptitle("Tilmash is competitive, but not uniformly strongest across Kazakh MT directions", x=0.01, ha="left", weight="bold", fontsize=16)
    fig.text(0.01, 0.015, "Same test sets and metric within each panel. Values from KazParC paper Table 6; Tilmash is the paper's parsync checkpoint.", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.13, 1, 0.93))
    save_figure(fig, "06_tilmash_mt_comparison")


def plot_qwen_metrics() -> None:
    rows = [
        ("4B", "KazMMLU", "Base", 72.5), ("4B", "KazMMLU", "Kazakh-adapted", 78.5),
        ("4B", "KazCulture", "Base", 42.3), ("4B", "KazCulture", "Kazakh-adapted", 55.4),
        ("35B-A3B", "KazMMLU", "Base", 82.6), ("35B-A3B", "KazMMLU", "Kazakh-adapted", 84.0),
        ("35B-A3B", "KazCulture", "Base", 60.3), ("35B-A3B", "KazCulture", "Kazakh-adapted", 68.7),
    ]
    df = pd.DataFrame(rows, columns=["size", "benchmark", "variant", "score"])
    df.to_csv(DATA_OUT / "qwen35_benchmarks.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), sharey=True)
    for ax, size in zip(axes, ["4B", "35B-A3B"]):
        d = df[df["size"] == size]
        sns.barplot(data=d, x="benchmark", y="score", hue="variant", palette={"Base":"#94a3b8", "Kazakh-adapted":"#2563eb"}, ax=ax)
        ax.set_title(size, weight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("Accuracy / score (higher is better)" if size == "4B" else "")
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.22)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f", padding=2, fontsize=9)
        if size == "35B-A3B":
            ax.legend_.remove()
    axes[0].legend(frameon=False, loc="upper left")
    fig.suptitle("Kazakh adaptation helps cultural knowledge more than KazMMLU at larger scale", x=0.01, ha="left", weight="bold", fontsize=16)
    fig.text(0.01, 0.01, "Self-reported model-card results in thinking mode; base and adapted variants are matched by size and benchmark.", fontsize=9, color="#4b5563")
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    save_figure(fig, "07_qwen35_kazakh_adaptation")


def plot_metric_coverage(models_df: pd.DataFrame) -> None:
    table = models_df.groupby("section").has_numeric_metric_summary.agg(["sum", "count"]).reindex(SECTIONS)
    table["missing"] = table["count"] - table["sum"]
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    labels = [SECTION_SHORT[x] for x in table.index]
    ax.barh(labels, table["sum"], color="#16a34a", label="Numeric metric summary")
    ax.barh(labels, table["missing"], left=table["sum"], color="#e5e7eb", label="No numeric metric summary")
    for i, row in enumerate(table.itertuples()):
        ax.text(row.count + 0.5, i, f"{int(row.sum)}/{int(row.count)} ({100*row.sum/row.count:.0f}%)", va="center", fontsize=10)
    ax.set_title("Comparable evidence is the bottleneck: most catalog entries lack numeric metrics", loc="left", weight="bold", fontsize=14)
    ax.set_xlabel("Model-family entries")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    save_figure(fig, "08_metric_coverage")


def main() -> None:
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=1.0)
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.hashsalt": SNAPSHOT_DATE,
        }
    )

    _, models_df, tasks_df = load_catalog()
    summary = write_descriptive_tables(models_df, tasks_df)
    metrics = metric_rows()
    metrics.to_csv(DATA_OUT / "asr_metric_comparisons.csv", index=False)
    mt = mt_rows()
    mt.to_csv(DATA_OUT / "tilmash_mt_metrics.csv", index=False)

    plot_release_history(models_df)
    plot_domain_mix(models_df)
    plot_task_interest(tasks_df)
    plot_task_heatmap(tasks_df)
    plot_asr_metrics(metrics)
    plot_mt_metrics(mt)
    plot_qwen_metrics()
    plot_metric_coverage(models_df)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
