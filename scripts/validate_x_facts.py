#!/usr/bin/env python3
"""Validate Grok's account facts against candidates/x_facts/schema.json.

Usage:
    python3 scripts/validate_x_facts.py candidates/x_facts/YYYY-MM-DD.jsonl [...]

Requires: pip install jsonschema
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "candidates" / "x_facts" / "schema.json"


def main(paths):
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
                                     format_checker=FormatChecker())
    bad = total = 0
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
            if not validator.is_valid(rec):
                bad += 1
                kind = rec.get("type")
                print(f"{path}:{n} {rec.get('username')} ({kind})")
                # oneOf errors are noisy; show only the branch that matches "type"
                branch = {"account_check": 0, "candidate_proposal": 1}.get(kind)
                for err in validator.iter_errors(rec):
                    subs = [e for e in (err.context or []) if e.schema_path[0] == branch] or [err]
                    for sub in subs:
                        print(f"  - {'/'.join(map(str, sub.path)) or '(root)'}: {sub.message}")
    print(f"{total - bad}/{total} facts valid")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
