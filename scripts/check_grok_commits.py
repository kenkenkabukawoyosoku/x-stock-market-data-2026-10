#!/usr/bin/env python3
"""Check that Grok's commits only ADD new files in the paths Grok owns.

Grok must never modify or delete an existing file (GROK_HANDOFF.md §1).
A commit is treated as Grok's when its message has no "Claude-Session:" line.

Usage:
    python3 scripts/check_grok_commits.py [SINCE]

SINCE defaults to the latest commit whose message has "Claude-Session:".
Prints one line per problem and exits 1 if there are any.
"""
import re
import subprocess
import sys

ALLOWED_NEW = [
    r"posts/\d{4}-\d{2}-\d{2}_(jp|us|task)(_\d+)?\.jsonl",
    r"candidates/x_facts/\d{4}-\d{2}-\d{2}_(jp|us|task)(_\d+)?\.jsonl",
    r"predictions/deletions/\d{4}-\d{2}-\d{2}_(jp|us|task)(_\d+)?\.jsonl",
    r"logs/grok/\d{4}-\d{2}-\d{2}_\d{4}_(jp|us|task)\.md",
]
PLACEHOLDER_LINE = re.compile(r"^\s*(PLACEHOLDER\w*|\$\(.*\))\s*$")


def git(*args):
    return subprocess.check_output(["git", *args], text=True)


def main(argv):
    if argv:
        since = argv[0]
    else:
        since = git("log", "-1", "--format=%H", "--grep=Claude-Session:").strip()
    shas = git("rev-list", "--reverse", f"{since}..HEAD").split()
    problems = []
    for sha in shas:
        body = git("log", "-1", "--format=%B", sha)
        if "Claude-Session:" in body:
            continue
        short, subject = sha[:7], body.splitlines()[0] if body else ""
        for line in git("show", "--name-status", "--format=", sha).splitlines():
            status, *paths = line.split("\t")
            path = paths[-1]
            if status != "A":
                problems.append(f"{short} {status} {path}: changed an existing file ({subject})")
                continue
            if not any(re.fullmatch(p, path) for p in ALLOWED_NEW):
                problems.append(f"{short} A {path}: not a path Grok may create ({subject})")
                continue
            text = git("show", f"{sha}:{path}")
            # A line that is only a placeholder token or an unexpanded $(...) means the
            # real content was never written. Mentioning the word in prose is fine.
            if not text.strip() or any(PLACEHOLDER_LINE.match(l) for l in text.splitlines()):
                problems.append(f"{short} A {path}: empty or placeholder content")
    for p in problems:
        print(p)
    print(f"{len(shas)} commits since {since[:7]}, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
