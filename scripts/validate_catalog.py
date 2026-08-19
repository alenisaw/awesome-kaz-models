#!/usr/bin/env python3
"""Validate data/models.yaml structure and taxonomy. Does not check scientific accuracy."""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "models.yaml"

SECTIONS = {"Text, NLP, and LLM", "Speech and audio", "Vision, OCR, and multimodal"}
ACCESS_VALUES = {"open", "gated", "application", "paid", "restricted", "unavailable"}
KIND_VALUES = {
    "foundation", "continued-pretraining", "instruction", "task-finetune",
    "translation", "embedding", "speech", "vision", "multimodal",
}
TIER_VALUES = {"A", "B"}
REQUIRED_FIELDS = [
    "id", "name", "released", "section", "description", "tasks", "tier",
    "kind", "access", "license", "links",
]
DATE_RE = re.compile(r"^\d{4}(-\d{2})?$")
URL_RE = re.compile(r"^https?://\S+$")

# Packaging/quantization/format-only suffixes that usually indicate a deployment
# artifact rather than a substantively distinct trained model. Not an automatic
# ban (a name can legitimately contain one of these as part of a real distinct
# model), just a review flag.
SUSPICIOUS_PATTERNS = re.compile(
    r"\b(gguf|awq|gptq|int8|int4|onnx|quantized|quantised|bnb|mlx|ggml|4bit|8bit)\b",
    re.IGNORECASE,
)


def fail(errors, msg):
    errors.append(msg)


def warn(warnings, msg):
    warnings.append(msg)


def main():
    errors = []
    warnings = []
    if not CATALOG.exists():
        print(f"FATAL: {CATALOG} not found", file=sys.stderr)
        return 1

    doc = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    models = doc.get("models", [])
    if not models:
        fail(errors, "models.yaml has no models")

    ids_seen = {}
    urls_seen = {}

    for i, m in enumerate(models):
        where = f"[{i}] {m.get('id', '<no id>')}"

        for field in REQUIRED_FIELDS:
            if field not in m or m[field] in (None, ""):
                fail(errors, f"{where}: missing required field '{field}'")

        mid = m.get("id")
        if mid:
            if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", mid):
                fail(errors, f"{where}: id '{mid}' is not kebab-case")
            if mid in ids_seen:
                fail(errors, f"{where}: duplicate id '{mid}' (also at index {ids_seen[mid]})")
            ids_seen[mid] = i

        section = m.get("section")
        if section and section not in SECTIONS:
            fail(errors, f"{where}: invalid section '{section}'")

        released = m.get("released")
        if released and released != "Unknown" and not DATE_RE.match(str(released)):
            fail(errors, f"{where}: released '{released}' is not YYYY, YYYY-MM, or 'Unknown'")

        access = m.get("access")
        if access and access not in ACCESS_VALUES:
            fail(errors, f"{where}: invalid access '{access}'")
        if access == "unavailable":
            fail(errors, f"{where}: access='unavailable' models must not appear in the main catalog — move to the Watchlist instead")

        tier = m.get("tier")
        if tier and tier not in TIER_VALUES:
            fail(errors, f"{where}: invalid tier '{tier}' (must be A or B)")

        kind = m.get("kind")
        if kind and kind not in KIND_VALUES:
            fail(errors, f"{where}: invalid kind '{kind}'")

        if not m.get("tasks"):
            fail(errors, f"{where}: tasks must be a non-empty list")

        links = m.get("links") or {}
        model_url = links.get("model")
        if not model_url:
            fail(errors, f"{where}: links.model is required")
        else:
            if not URL_RE.match(model_url):
                fail(errors, f"{where}: links.model '{model_url}' is not a valid URL")
            if model_url in urls_seen:
                fail(errors, f"{where}: duplicate links.model URL, also used by '{urls_seen[model_url]}'")
            else:
                urls_seen[model_url] = mid
        for key, val in links.items():
            if val and not URL_RE.match(val):
                fail(errors, f"{where}: links.{key} '{val}' is not a valid URL")

        params = m.get("params") or {}
        if params and "display" not in params:
            fail(errors, f"{where}: params.display is missing (use null if not reported)")

        derivative_of = m.get("derivative_of")

        # Suspicious packaging/quantization naming — warn, don't fail.
        name = m.get("name") or ""
        desc = m.get("description") or ""
        if SUSPICIOUS_PATTERNS.search(name):
            warn(warnings, f"{where}: name '{name}' matches a packaging/quantization pattern — confirm this is a substantive distinct model, not a format export")

    for mid, idx in ids_seen.items():
        m = models[idx]
        dep = m.get("derivative_of")
        if dep and dep not in ids_seen:
            fail(errors, f"[{idx}] {mid}: derivative_of '{dep}' does not match any known model id")
        base = m.get("base_model_id")
        if base and base not in ids_seen:
            fail(errors, f"[{idx}] {mid}: base_model_id '{base}' does not match any known model id")

    if warnings:
        print(f"{len(warnings)} warning(s):\n")
        for w in warnings:
            print(f"  ! {w}")
        print()

    if errors:
        print(f"FAILED: {len(errors)} error(s)\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {len(models)} models validated, no errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
