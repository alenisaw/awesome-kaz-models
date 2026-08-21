# Contributing

Thanks for helping grow this catalog. This document is the policy the generator
and reviewers hold every submission to. Read it before opening a PR that adds or
edits `data/models.yaml` — most review feedback traces back to one of the rules
below. This repository is the sister project of
[awesome-kaz-datasets](https://github.com/alenisaw/awesome-kaz-datasets) and
follows the same generation philosophy.

## How the repository works

`data/models.yaml` is the single source of truth. `README.md`'s tables, stats,
and images are generated from it — never hand-edit a table row or a stat line
inside the `<!-- NAME:START -->` / `<!-- NAME:END -->` markers; your edit will be
silently overwritten the next time someone runs the generator. Edit the YAML,
then run:

```bash
python scripts/validate_catalog.py
python scripts/generate_visualizations.py
python scripts/generate_readme.py
```

CI (`.github/workflows/validate.yml`) reruns all three in check mode and fails the
PR if the committed README/assets don't match what the YAML generates.

## Adding a model

1. Verify the model from a **primary source** in this order of preference:
   1. official model repository/card (Hugging Face, GitHub release, official project download, ...)
   2. official project repository
   3. the associated peer-reviewed paper
   4. official institutional page (e.g. an ISSAI or IS2AI project page)
   5. a trusted archive/release page
   6. a secondary source, only when a primary one is genuinely unavailable
2. Confirm there is an **actual, currently obtainable trained artifact** — not
   just a paper, an architecture description, training code, or a demo API. If
   you can't download or request the weights today, it belongs in the
   Watchlist, not the main tables.
3. Confirm the **Kazakh scope** is real and identifiable — see Tiers below. A
   tokenizer that happens to include `kk`, or a "supports 100 languages" claim,
   is not sufficient.
4. Check it isn't a **packaging duplicate** of a model already listed — see
   Model families and variants below.
5. Fill in `data/models.yaml` using the schema below. **Never guess a missing
   fact.** Use `null`, `"Not reported"`, or `"Unknown"` (for `released`)
   instead of inventing a date, author, license, or number.
6. Run the three commands above and commit the regenerated `README.md` and
   `assets/*.svg` alongside your YAML change.

### Inclusion tiers

**Tier A — Kazakh-specific.** At least one applies: trained from scratch
substantially on Kazakh; continued-pretrained substantially on Kazakh;
fine-tuned specifically for a Kazakh task; a dedicated Kazakh checkpoint within
a wider research project.

**Tier B — strong Kazakh support.** A multilingual model qualifies only when
Kazakh is explicitly part of training/adaptation, there is dedicated Kazakh
evaluation, Kazakh is one of a small number of central target languages, or a
dedicated Kazakh artifact/config/checkpoint exists within the model family.

**Not included (Tier C — generic multilingual).** A model does not qualify
merely because its tokenizer supports `kk`, its README says "100 languages," a
benchmark happened to include Kazakh, or it can zero-shot Kazakh. Generic
multilingual foundations (mBERT, XLM-R, mT5, vanilla Whisper, NLLB-200,
MADLAD, SeamlessM4T, and similar) may appear only as `base_model` metadata on
a Kazakh-specific adaptation — never as their own catalog row.

### What does NOT belong in the main catalog

- Generic multilingual baselines with only incidental Kazakh support (Tier C).
- Quantizations, GGUF/AWQ/GPTQ conversions, ONNX/TensorRT exports, or other
  format-only duplicates of a model already listed.
- Tokenizer-only adaptations with no retraining.
- Training-code-only projects with no public checkpoint (see the KazNERD case
  below).
- API-only proprietary services with no downloadable weights.
- Hugging Face Space wrappers with no underlying downloadable model.
- Dataset-only repositories — those belong in
  [awesome-kaz-datasets](https://github.com/alenisaw/awesome-kaz-datasets).
- Tiny personal test/demo repositories with no independent research or
  practical utility.
- Models whose "Kazakh" relevance is geographical/cultural branding (e.g. a
  Kazakhstan-themed image LoRA) rather than Kazakh-*language* capability.
- Unreleased or announced-only resources — these go in the Watchlist section.

A useful worked example: the official KazNERD project repository documents
CRF/BiLSTM-CNN-CRF/BERT/XLM-R training code and reports benchmark results, but
does not publish a canonical trained checkpoint — the README instructs users to
train their own model. That makes the official KazNERD experiment models
`training-scripts-only`, excluded from the main catalog, even though the
*dataset* is real and useful. An independent public Hugging Face fine-tune
trained on KazNERD with real published weights is a separate, includable
model. This distinction — a model described in a paper/repo vs. a model whose
weights you can actually obtain — is the single most common reason an
otherwise-legitimate-looking candidate ends up in the Watchlist instead of the
main table.

### Model families and variants

The catalog counts **learned model families**, not deployment packaging. A
base checkpoint and its AWQ/GPTQ/GGUF/ONNX/bitsandbytes conversions are one
entry — link the primary weights and mention notable quantized mirrors in
`notes` if useful, don't add them as separate rows. The same applies to a
PyTorch checkpoint and its ONNX FP32/INT8 exports of the same recognizer.

A new row **is** warranted when new training creates a genuinely new
capability: base vs. instruction-tuned, base vs. a task-specific fine-tune
(NER, GEC, sentiment, ...), a general MT model vs. a domain-adapted one, or a
monolingual base vs. an explicitly bilingual continued-pretrained model. Use
`derivative_of` (or `base_model` / `base_model_id`, for a foundation model
elsewhere in the catalog) to record the lineage rather than duplicating
metadata. Use judgment: the test is whether the new training step creates a
new useful research/inference capability, not whether the upload has a
different file format.

### Multilingual models

A multilingual model is added only when Kazakh support is substantive and
identifiable per the Tier B criteria above — never merely because Kazakh is
"one of N languages" in marketing copy. When in doubt, check whether the
model card documents Kazakh-specific training data volume or a Kazakh-specific
evaluation result; if it doesn't, the model likely belongs in the Watchlist or
should be excluded entirely.

## The `released` field

`released` is the date the specific model artifact/version **became publicly
obtainable** — a real person could have downloaded or requested those weights
on that date. It is explicitly **not**:

- a Hugging Face "last modified" timestamp (repos get re-uploaded/mirrored long
  after the true release — verify against `createdAt` via the HF API, and
  cross-check against the paper/original host if `createdAt` looks
  implausibly late),
- the date a paper was submitted or accepted,
- the date of the latest commit to a companion GitHub repo,
- the date the model was added to *this* catalog (that's `added_to_catalog`).

Use `YYYY-MM` when the month is known, `YYYY` when only the year is known, and
the literal string `Unknown` when even the year can't be established reliably.
Never upgrade a year-only date to a specific month by guessing. Entries with
`released: Unknown` are excluded from the release-calendar visualizations
rather than guessed into a chart.

## Access classification

| Value | Meaning |
|---|---|
| `open` | Directly downloadable, or requires only normal service authentication (a free account) with no special approval step. |
| `gated` | Free, but requires accepting terms, requesting access, or Hugging Face-style gating. |
| `application` | An explicit request/application to an institution or the authors is required. |
| `paid` | Commercial or licensed purchase required. |
| `restricted` | Special institutional or usage restrictions beyond a simple application. |
| `unavailable` | Described/announced but no usable artifact can currently be verified — belongs in the Watchlist, not the main table. `validate_catalog.py` rejects any main-catalog entry with this value. |

Never mark a model `open` merely because its code or paper is open access —
check the weights' own access terms.

## `kind` and `tier`

`kind` (pick one): `foundation`, `continued-pretraining`, `instruction`,
`task-finetune`, `translation`, `embedding`, `speech`, `vision`, `multimodal`.

`tier` (pick one): `A` or `B`, per the Inclusion tiers above.

## Canonical task labels

Use an existing task label from `data/models.yaml` whenever your model's task
matches one already in use (check "Models per task" in the README's Model
landscape section) instead of inventing a near-synonym. If you must introduce
a new label, keep it short and sentence-case, and add its abbreviation to
`TASK_ABBREV` in `scripts/generate_readme.py` if it's likely to recur.

## Required / optional metadata

Required: `id`, `name`, `released`, `section`, `description`, `tasks`, `tier`,
`kind`, `access`, `license`, `links.model`.

Strongly encouraged when available: `authors`, `organization`, `architecture`,
`base_model`, `params`, `storage`, `languages`, `links.paper`, `links.code`,
`links.project`, `kazakh_evidence`, `training.summary`.

`storage` (`value` + `unit`, e.g. `{value: 15.7, unit: GB}`) records the
checkpoint/weights download size from the primary source (Hugging Face's
"Files and versions" size total, or a GitHub release asset size) — never
estimated. Leave `value: null` when it can't be independently confirmed.

`id` must be a stable, kebab-case slug (`kazllm-1-0-8b`, not
`KazLLM_1.0_8B`) — it is used as the join key for `derivative_of` /
`base_model_id` and must never be reused for a different model.

## Metrics policy

This catalog is **not a leaderboard**. WER, CER, F1, and aggregate benchmark
scores are not comparable across different test sets, normalization
protocols, and evaluation harnesses. A metric may appear in `metrics.summary`
or a model's `description` when it adds real context, but never present it in
a way that implies ranking against other catalog entries. Hugging Face
download/like counts are volatile snapshots, not intrinsic model properties —
they are not used as an inclusion criterion and do not appear in the main
README table.

## Updating an existing entry

If you're correcting metadata rather than adding a model, edit the relevant
entry in place, update `last_verified` to today's date, and add a one-line
`notes` field explaining what changed and why (this feeds the CHANGELOG
process). Don't silently replace a value you're unsure about — if you can't
verify a correction, open an issue describing the discrepancy instead.

## Watchlist entries

A resource goes in the README's Watchlist (not `models.yaml`) when it's
announced but unreleased, described in a paper with no downloadable artifact,
of unclear provenance, temporarily inaccessible, license-conflicted, or its
Kazakh training/evaluation relevance isn't yet sufficiently verified.
Watchlist entries are hand-maintained in `scripts/generate_readme.py` (the
`WATCHLIST` list) — add a short, factual reason a real person could act on,
not a guess about when it might become available. Watchlist status is not a
rejection: it means "potentially qualifies later if verification succeeds."
An entry that clearly fails the inclusion criteria (a format conversion, a
generic multilingual baseline, an API-only service) is excluded outright, not
added to the Watchlist.

## PR format

- One model addition/correction per PR where practical (easier to review).
- Include the primary source URL(s) you verified against in the PR description.
- Run the three generator commands and commit the resulting diff to
  `README.md`/`assets/` — don't leave the repo in a state where
  `generate_readme.py --check` would fail.
- If you're unsure about a field, use `"Not reported"`/`"Unknown"`/`null` and
  say so in the PR description rather than guessing.

## Repository license

The repository's own top-level license (as opposed to each model's license,
recorded per-entry in `models.yaml`) is an open decision reserved for the repo
owner. Don't add a `LICENSE` file in a PR unless the owner has explicitly
asked for one.
