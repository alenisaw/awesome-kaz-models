# Changelog

This changelog starts from the repository's initial curated release.

## 2026-08-20 — Watchlist verification pass + license

### Added

- **AIT-ASR** (`nur-dev/ait-asr`) — Whisper-small fine-tune for Kazakh ASR,
  trained on farabi-lab/kazakh-stt (≈204k pairs); 17.10% WER on Kazakh FLEURS,
  36.05% WER on ISSAI KSC2 in-domain. Moved from Watchlist after confirming
  the gated repo has real weights, a stated base model, training dataset, and
  reported metrics.
- **MMS-TTS Kazakh** (`facebook/mms-tts-kaz`) — per-language Kazakh VITS
  checkpoint from Meta's MMS project. Moved from Watchlist after confirming
  the repo is public (non-gated) with real weights, a CC-BY-NC-4.0 license,
  and a linked paper (arXiv:2305.13516). Classified tier B, not A: MMS's
  1,000+-language scope means Kazakh-specific training-data volume isn't
  independently isolated from the shared pipeline.

### Watchlist

- **AIT-Syn Kazakh TTS** (`nur-dev/ait-syn-4L`) reason sharpened: the model is
  real (indexed with a full technical README via third-party search), but
  unlike the org's other gated repos, it currently returns HTTP 401 for
  anonymous access at both the API and page level, so it could not be
  independently re-verified this pass and stays in the Watchlist.
- Söyle and the Tencent Kazakh 7B Adapter retained unchanged — their issue is
  the absence of public weights, not unverified metadata.

### Infrastructure

- Added a top-level `LICENSE` badge, nav link, and closing README section
  pointing to the existing MIT `LICENSE` file (catalog content only; linked
  models keep their own licenses).

## 2026-08-19 — Initial curated release

### Added

70 curated model families, built from a large research pass and follow-up gap audit
(≈100 audited candidates across Text/NLP/LLM, Speech, and Vision/OCR/multimodal)
that was independently re-verified against primary sources — mostly the
Hugging Face API (`createdAt`, `cardData.license`, tags) and official GitHub
repository READMEs — rather than accepted at face value.

By section:

- **Text, NLP, and LLM** — 43 models (foundation encoders/LLMs, task
  fine-tunes for NER/QA/sentiment/classification/transliteration/GEC,
  embeddings/retrieval models, and machine translation).
- **Speech and audio** — 20 models (ASR, TTS, keyword spotting/language ID,
  target-speaker ASR).
- **Vision, OCR, and multimodal** — 7 models (OCR, image captioning,
  vision-language, audio-vision-language, text-to-image).

Candidates were moved to the [Watchlist](README.md#watchlist--announced-resources)
only where real projects exist without a currently downloadable model (e.g. Söyle,
whose only linked Hugging Face model returns 404) or where primary-source
verification is pending (e.g. AIT-ASR, Tencent LoRA, facebook/mms-tts-kaz).
Helsinki-NLP/OPUS was confirmed as a general 23-language Turkic mixture failing
the Tier B dedicated threshold and excluded per policy.

### Major normalization decisions

- **Family-level deduplication.** Quantizations, GGUF/AWQ/GPTQ conversions,
  and ONNX exports of an already-listed checkpoint are not separate entries
  (e.g. TurkicOCR-SVTRv2-B's ONNX FP32/INT8 mirrors, KazLLM's GGUF mirrors,
  FogGen's GGUF mirrors). Base/instruct and base/task-finetune pairs *are*
  kept as separate entries when the additional training creates a real new
  capability (e.g. RoBERTa Large KazQAD → RoBERTa Large KazQAD Informatics).
- **Generic multilingual exclusion.** No entries for mBERT, XLM-R, mT5,
  vanilla Whisper, NLLB-200, or similar foundations on their own; they appear
  only as `base_model` metadata on Kazakh-specific adaptations already in the
  catalog (e.g. mBERT under several sentiment/QA fine-tunes).
- **Corrected release dates.** Several entries' `released` date was moved off
  a Hugging Face "last modified" timestamp or a paper submission date onto
  the actual first-artifact-availability date where verifiable (e.g.
  Wav2Vec2-Large-XLSR-53 Kazakh's `createdAt` reads 2022-03, implausibly late
  for a 2021 XLSR Fine-Tuning Week model — recorded as year-only "2021"
  rather than a specific, unverifiable month).
- **Split vs. merged variants.** Darmm Text Generation v1 (mT5) and v2
  (Qwen2.5-Coder) are kept as two entries because they use genuinely
  different base architectures. HPLT's Kazakh-English MT and HPLT+OPUS
  Kazakh-English MT are kept separate because they use different training
  data recipes on the same architecture. Qolda-AVL's 5B/9B/34B checkpoints
  are one entry (same architecture and training recipe at different scales).
- **KSC2 dual role.** The KSC2 speech corpus (in the sister
  `awesome-kaz-datasets` repository) and the KSC2 best-performing ASR
  checkpoint (in this repository) are correctly two different catalog
  entries in two different repositories — a dataset and a trained model built
  from it are different artifacts.

### Infrastructure

- Added `data/models.yaml` as the canonical, machine-readable model registry —
  the README tables, badges, dashboard, and charts are generated from it.
- Added `scripts/validate_catalog.py`, `scripts/generate_readme.py`,
  `scripts/generate_visualizations.py`, `scripts/check_links.py` — mirroring
  the architecture and visual system of the sister `awesome-kaz-datasets`
  repository.
- Added `CONTRIBUTING.md`, this `CHANGELOG.md`, and
  `.github/ISSUE_TEMPLATE/model-submission.yml`.
- Added `.github/workflows/validate.yml` — CI validates the catalog and
  checks that committed `README.md`/`assets/*.svg` match what the generators
  produce from `data/models.yaml`.

### Notes on this pass

Model discovery for this release started from a single large research pass
rather than an exhaustive, independently repeated sweep of every possible
source (Hugging Face search, GitHub, institutional pages, and Turkic-NLP
literature). Coverage is strong for ISSAI/IS2AI's published model inventory,
the SozKZ/EkiTil/TilQazyna family of independent researcher projects, and
well-known community fine-tunes (Whisper, wav2vec2, RoBERTa/BERT variants).
Explicitly flagged as incomplete for a future pass: Helsinki-NLP/OPUS Kazakh
MT model canonicalization, `facebook/mms-tts-kaz`'s current release metadata,
and a properly scoped verification of the `nur-dev/ait-*` model family
discovered incidentally during this release's research.
