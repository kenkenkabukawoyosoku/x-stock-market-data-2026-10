#!/usr/bin/env python3
"""Validate Grok's post snapshots against posts/post.schema.json.

Usage:
    python3 scripts/validate_posts.py posts/YYYY-MM-DD.jsonl [...]

Exits 1 if any line is invalid. Requires: pip install jsonschema
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "posts" / "post.schema.json"


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main(paths):
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
                                     format_checker=FormatChecker())
    bad = total = 0
    seen = {}
    for path in paths:
        for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            total += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                bad += 1
                print(f"{path}:{n} invalid JSON: {e}")
                continue
            errors = [f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}"
                      for e in validator.iter_errors(rec)]
            if rec.get("post_id") and not str(rec.get("post_url", "")).endswith("/" + rec["post_id"]):
                errors.append("post_url does not end with post_id")
            try:
                if parse_ts(rec["collected_at"]) < parse_ts(rec["posted_at"]):
                    errors.append("collected_at is before posted_at")
            except (KeyError, ValueError, AttributeError):
                pass
            pid = rec.get("post_id")
            if pid in seen:
                errors.append(f"duplicate post_id (also at {seen[pid]})")
            seen[pid] = f"{path}:{n}"
            if errors:
                bad += 1
                print(f"{path}:{n} {pid}")
                for e in errors:
                    print(f"  - {e}")
    print(f"{total - bad}/{total} posts valid")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
