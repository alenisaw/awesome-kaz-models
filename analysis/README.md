# Deep analytics: Awesome Kazakh Models

Snapshot: **2026-08-23** · repository commit: **`893958c`** · analysis unit: **one catalog row / model family**

## Executive findings

The catalog contains **94 verified model-family entries**: 92 have a known release year and two do not. Publication activity has accelerated sharply. The annual count rose from 1 in 2018 to 12 in 2023, 20 in 2025, and **42 in 2026 year-to-date through 23 August**. The 2026 YTD count is already 2.10 times the entire 2025 count and 3.50 times the January–August 2025 count (12). This is growth in publicly released catalog entries, not necessarily growth in research papers, users, or commercial adoption.

| Release year | Text/NLP/LLM | Speech/audio | Vision/multimodal | Total | Cumulative known-year entries |
|---:|---:|---:|---:|---:|---:|
| 2018 | 1 | 0 | 0 | 1 | 1 |
| 2019 | 0 | 0 | 0 | 0 | 1 |
| 2020 | 0 | 1 | 0 | 1 | 2 |
| 2021 | 0 | 3 | 0 | 3 | 5 |
| 2022 | 1 | 1 | 0 | 2 | 7 |
| 2023 | 7 | 4 | 1 | 12 | 19 |
| 2024 | 9 | 2 | 0 | 11 | 30 |
| 2025 | 14 | 4 | 2 | 20 | 50 |
| 2026 YTD | 22 | 16 | 4 | 42 | 92 |

![Model releases by year](figures/01_releases_by_year.png)

The dominant domain is **text/NLP/LLM: 55 of 94 entries (58.5%)**, followed by speech/audio with 32 (34.0%) and vision/multimodal with 7 (7.4%). Text is therefore the cumulative leader, but the mix is broadening. Vision/multimodal grew from one entry before 2025 to six releases in 2025–2026, reaching 9.7% of releases in that recent period. Speech remains structurally important: it accounts for nearly one-third of recent releases and has much better metric coverage than text.

![Domain mix](figures/02_domain_mix.png)

The best proxy for “what society is interested in now” available in this repository is **what model creators are releasing**, not survey or usage evidence. On that proxy, 2025–2026 activity is led by:

1. Automatic speech recognition (ASR): 11 task-labelled families.
2. LLMs and TTS: 7 each.
3. Embeddings/retrieval and machine translation: 5 each.
4. Question answering and OCR: 4 each.
5. Instruction following: 3.

The especially revealing 2026 YTD pattern is eight new ASR families, seven TTS families, six LLM families, three instruction-following families, and three embedding families. This suggests current creator attention is moving from basic language resources toward deployable voice interfaces, generative models, RAG/retrieval, and multimodal/OCR applications.

![Recent task interest](figures/03_recent_task_interest.png)

![Task heatmap](figures/04_task_heatmap.png)

## Which models look stronger or weaker?

There is **no valid global leaderboard** across this repository. Metrics include WER/CER (lower is better), BLEU/chrF and accuracy/F1/recall (higher is better), perplexity/loss, retrieval scores, and subjective MOS. Even identical metric names are not comparable when test sets, text normalization, decoding, or evaluation protocols differ. The plots below group only same-named benchmark families and retain provenance warnings.

### ASR performance through the years

Within the KSC benchmark family, the best reported WER is the 2022 KSC2 system's **6.3% on the KSC subset**, followed by the 2021 multilingual IS2AI system at 7.9% and the 2020 SAIDA model at 8.7%. The 2026 Tulpar report is 10.62%, while the 2021 community Wav2Vec2 model reports 19.65%. These values likely use related KSC test material but may differ in corpus version and normalization, so the ranking is indicative rather than definitive.

Within KSC2-labelled evaluations, **Whisper Turbo KSC2 (2025) reports the lowest WER, 9.16%**. The original 2022 KSC2 system reports 15.6% over its six-source overall test, Whisper Base Kazakh reports 15.36%, VibeVoice reports 22.0%, and AIT-ASR measures 36.05% on a 1,000-utterance sample. The precise subsets are not uniform.

FLEURS-kk is the cleanest named cross-model group in the catalog: **GigaAM Multilingual Large reports the lowest WER at 4.4%**, followed by Kazakh Whisper Large-v3 Turbo at 11.8%, AIT-ASR at 17.1%, and KRASR Whisper Small at 76.09%. The last model is optimized for Kazakh–Russian code-switching and is much weaker on FLEURS despite improving strongly over its own Whisper-Small baseline, illustrating why intended domain matters. These remain reported results rather than a centrally reproduced evaluation.

![ASR WER over time](figures/05_asr_wer_over_time.png)

Primary evidence: [SAIDA/KSC paper](https://arxiv.org/abs/2009.10334), [2021 multilingual ASR paper](https://arxiv.org/abs/2108.01280), [KSC2 paper](https://www.isca-archive.org/interspeech_2022/mussakhojayeva22_interspeech.pdf), [GigaAM paper](https://arxiv.org/abs/2607.10371) and [model card](https://huggingface.co/ai-sage/GigaAM-Multilingual), [Whisper Turbo KSC2 card](https://huggingface.co/abilmansplus/whisper-turbo-ksc2), [AIT-ASR card](https://huggingface.co/nur-dev/ait-asr), and [Tulpar card](https://huggingface.co/olzhasAl/whisper-large-v3-tulpar). Exact values and comparability notes are in [`data/asr_metric_comparisons.csv`](data/asr_metric_comparisons.csv).

### TTS quality: evidence exists, but no valid shared plot

All five TTS families below are already present in the main catalog. Their quality evidence is now recorded in the structured analysis, but a cross-family comparison plot is intentionally omitted: the studies do not share the same metric, speakers, sentences, listeners, synthesizer task, or evaluation protocol. Plotting the reported numbers together would imply a ranking that the evidence cannot support.

| Model | Reported Kazakh quality evidence | Valid comparison scope |
|---|---|---|
| KazakhTTS (2021) | Tacotron 2 MOS: 4.535 (female F1), 4.144 (male M1); Transformer MOS: 4.436 and 3.907 | Tacotron 2 versus Transformer is comparable only within the original matched listening study. |
| TurkicTTS (2023) | MOS 4.18; comprehensibility 97%; intelligibility 80% | Its multilingual survey and listening tasks differ from the other studies. |
| KazEmoTTS (2024) | Synthesized-speech MOS 3.51–3.57; average MCD 6.02–7.67 across three voices | Emotional synthesis, different voices, stimuli, and listener protocol. |
| Chatterbox Multilingual Kazakh (2026) | Median round-trip CER 7.4%, mean CER 10.2%, using Whisper-large-v3 on 60 synthesized FLEURS-kk samples | ASR-based intelligibility proxy; not human naturalness and not interchangeable with WER. |
| CosyVoice3 Kazakh (2026) | Mean round-trip WER 37.6% at the selected checkpoint, versus 43.6% at the final step | Supports checkpoint selection within this training run only. |

Primary evidence: [KazakhTTS paper, Table 3](https://arxiv.org/abs/2104.08459), [TurkicTTS paper, Table 3](https://arxiv.org/abs/2305.15749), [KazEmoTTS paper, Tables 3–5](https://arxiv.org/abs/2404.01033), [Chatterbox model card](https://huggingface.co/Tohirju/chatterbox-mtl-kazakh), and [CosyVoice3 model card](https://huggingface.co/Tohirju/cosyvoice3-kazakh-499k). The transcribed values, evaluation scopes, and explicit cross-family-comparability flags are in [`data/tts_quality_evidence.csv`](data/tts_quality_evidence.csv).

### Machine translation: Tilmash

The KazParC paper offers a strong same-test-set comparison of NLLB base, KazParC-only fine-tuning, Tilmash (the paper's `parsync` checkpoint), Yandex, and Google. Averaged over the four directions involving Kazakh shown below:

- On FLoRes, Google is first at mean BLEU 0.2225 and **Tilmash is second at 0.2075**.
- On KazParC, Google is first at 0.2850 and **Tilmash is second at 0.2600**.
- Tilmash ties Google on FLoRes EN→KK (0.20) and RU→KK (0.13), but Google is clearly ahead on KazParC EN→KK (0.30 versus 0.21).
- KazParC-only is slightly better than Tilmash on KazParC KK→EN (0.33 versus 0.32), showing that synthetic-data augmentation is not uniformly beneficial in-domain.

![Tilmash comparison](figures/06_tilmash_mt_comparison.png)

Source: [KazParC paper, Table 6](https://arxiv.org/pdf/2403.19399). Transcribed values are in [`data/tilmash_mt_metrics.csv`](data/tilmash_mt_metrics.csv).

### LLM adaptation: ISSAI Qwen3.5 Kazakh

The matched base-versus-adapted comparison is consistently positive. At 4B, Kazakh adaptation improves KazMMLU from 72.5 to 78.5 (+6.0 points) and KazCulture from 42.3 to 55.4 (+13.1). At 35B-A3B, the gains are smaller on KazMMLU, 82.6 to 84.0 (+1.4), but remain large on KazCulture, 60.3 to 68.7 (+8.4). The main signal is that continued Kazakh adaptation adds more cultural knowledge than general multiple-choice ability, especially once the base model is already large.

![Qwen3.5 adaptation](figures/07_qwen35_kazakh_adaptation.png)

Source: [ISSAI Qwen3.5 Kazakh model card](https://huggingface.co/issai/Qwen3.5-35B-A3B-Kazakh). These are self-reported thinking-mode scores; values are in [`data/qwen35_benchmarks.csv`](data/qwen35_benchmarks.csv).

### Other paper/model-card metrics not placed on a shared leaderboard

- TurkicOCR-SVTRv2-B reports Kazakh CER 1.71%, while Kazakh TrOCR reports 3.7%. Their test sets differ, so 1.71 cannot be interpreted as a head-to-head win.
- e5-base-kazakh reports Kazakh SNLI R@1 0.887 versus 0.433 for its base and STS-B Pearson 0.817 versus 0.708. KazEmbed-V5 reports Hits@1 72%, Hits@5 96%, and MRR 0.835 on a different retrieval evaluation; the two embedding models cannot be ranked from those figures.
- SozKZ OmniAudio reports 21.28% WER on only 50 in-domain `kzcalm-tts-kk-v1` samples. This is useful internal evidence but not comparable to the public ASR panels. [Model card](https://huggingface.co/stukenov/sozkz-core-omniaudio-70m-kk-asr-v1).

## Evidence quality and limitations

Only **30 of 94 families (31.9%)** have a numeric metric summary in the structured catalog. Coverage is 19/32 (59%) for speech, 9/55 (16%) for text, and 2/7 (29%) for vision/multimodal. Recording the previously omitted TTS results improves evidence coverage, but not cross-family comparability: missing standardized evaluation remains the main obstacle to a trustworthy ranking.

![Metric coverage](figures/08_metric_coverage.png)

Important interpretation constraints:

- A catalog row can bundle several model sizes or variants. Counts are families, not raw checkpoints.
- Multi-task families count once under every task they list, so task totals exceed 94.
- Release date means public artifact release, not necessarily paper publication.
- Two entries have unknown release years and are excluded from time plots but included in overall totals.
- 2026 is incomplete through 23 August and should not be treated as a full calendar year.
- The repository is curated, so counts measure known qualifying releases and may undercount unlisted, private, deleted, or inaccessible models.
- “Interest” is inferred from release activity. It does not measure users, downloads, funding, or general public preferences.
- Model-card metrics are often self-reported. Some cards provide independently measured results; the CSV records the source type and caveats.

## Reproducing the analysis

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r analysis/requirements.txt
.venv/bin/python analysis/analyze_models.py
```

The script regenerates all CSV/JSON tables under [`analysis/data`](data/) and all PNG/SVG plots under [`analysis/figures`](figures/). The flattened catalog used for audit is [`data/catalog_snapshot.csv`](data/catalog_snapshot.csv), the protocol-aware TTS evidence is [`data/tts_quality_evidence.csv`](data/tts_quality_evidence.csv), and the compact machine-readable summary is [`data/summary.json`](data/summary.json).
