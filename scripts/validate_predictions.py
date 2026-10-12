#!/usr/bin/env python3
"""Validate prediction records against predictions/prediction.schema.json.

Usage:
    python3 scripts/validate_predictions.py FILE [FILE ...]

FILE may be .jsonl (one record per line) or .json (a list of records, or an
object with a "predictions" list). Exits 1 if any record is invalid.
Requires: pip install jsonschema
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "predictions" / "prediction.schema.json"
BACKFILL_HOURS = 36


def load_records(path):
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".jsonl"):
        return [(i, json.loads(line)) for i, line in enumerate(text.splitlines(), 1) if line.strip()]
    data = json.loads(text)
    records = data["predictions"] if isinstance(data, dict) else data
    return list(enumerate(records, 1))


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def extra_checks(rec):
    """Rules that JSON Schema cannot express."""
    errors = []
    expected_id = f"{rec.get('post_id')}-{rec.get('ticker')}-{rec.get('direction')}"
    if rec.get("id") != expected_id:
        errors.append(f"id should be {expected_id!r}")
    if rec.get("post_id") and not str(rec.get("post_url", "")).endswith("/" + rec["post_id"]):
        errors.append("post_url does not end with post_id")
    try:
        lag = parse_ts(rec["collected_at"]) - parse_ts(rec["posted_at"])
        if lag < timedelta(0):
            errors.append("collected_at is before posted_at")
        elif (lag > timedelta(hours=BACKFILL_HOURS)) != rec.get("backfill"):
            errors.append(f"backfill should be {lag > timedelta(hours=BACKFILL_HOURS)} (lag {lag})")
    except (KeyError, ValueError, AttributeError):
        pass  # reported by the schema
    if rec.get("status") == "open" and rec.get("evaluation") is not None:
        errors.append("evaluation must be null while status is open")
    return errors


def main(paths):
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
                                     format_checker=FormatChecker())
    bad = total = 0
    seen = {}
    for path in paths:
        for n, rec in load_records(path):
            total += 1
            errors = [f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}"
                      for e in validator.iter_errors(rec)]
            errors += extra_checks(rec)
            rid = rec.get("id")
            if rid in seen:
                errors.append(f"duplicate id (also at {seen[rid]})")
            seen[rid] = f"{path}:{n}"
            if errors:
                bad += 1
                print(f"{path}:{n} {rid}")
                for e in errors:
                    print(f"  - {e}")
    print(f"{total - bad}/{total} records valid")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
