#!/usr/bin/env python3
"""Structural lint for the maintained docs.

Checks the feature-map contract, that the architecture doc carries a diagram,
that the intent doc keeps its sections, that each decision file carries valid
frontmatter, that relative links resolve, and that every flag of each CLI in
CLI_SOURCES is covered by the feature map. Prints one line per problem and
exits 1 if there are any.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".agents/skills/verify-ev-charge-planner"
FEATURES = SKILL / "features"
FEATURE_H2S = [
    "Sub-features",
    "How to get to it (user POV)",
    "Driving it with drive.sh",
    "Gotchas",
]
INTENT_H2S = [
    "Purpose",
    "Users",
    "What success looks like",
    "Principles",
    "Non-goals",
]
DECISIONS = ROOT / "docs/decisions"
DECISION_KEYS = {"id", "title", "date", "status"}
DECISION_STATUSES = {"proposed", "accepted", "superseded"}
# User-facing CLI entry points. Empty until milestone 1 is rebuilt.
CLI_SOURCES: list[Path] = []
LINKED_DOCS = [
    ROOT / "CLAUDE.md",
    ROOT / "AGENTS.md",
    ROOT / "docs/architecture.md",
    ROOT / "docs/intent.md",
    *sorted(DECISIONS.glob("*.md")),
    *sorted((ROOT / "docs/tickets").glob("*.md")),
    SKILL / "SKILL.md",
    *sorted(FEATURES.glob("*.md")),
]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FLAG_RE = re.compile(r"add_argument\(\s*\"(--[a-z0-9-]+)\"")
DECISION_FILE_RE = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

problems: list[str] = []


def problem(path: Path, msg: str) -> None:
    problems.append(f"{path.relative_to(ROOT)}: {msg}")


def headings(text: str, level: int) -> list[str]:
    prefix = "#" * level + " "
    out = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith(prefix):
            out.append(line[len(prefix) :].strip())
    return out


def check_feature_map() -> None:
    readme = FEATURES / "README.md"
    if not readme.exists():
        problem(FEATURES, "missing README.md index")
        return
    index = readme.read_text()
    files = sorted(p for p in FEATURES.glob("*.md") if p.name != "README.md")
    for f in files:
        text = f.read_text()
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if not lines or not lines[0].startswith("# "):
            problem(f, "must start with an H1 title")
        elif len(lines) < 2 or lines[1].startswith("#"):
            problem(f, "H1 must be followed by a one-paragraph description")
        h2s = headings(text, 2)
        if h2s != FEATURE_H2S:
            problem(f, f"H2s must be exactly {FEATURE_H2S}, found {h2s}")
        driving = text.split("## Driving it with drive.sh", 1)
        if len(driving) == 2 and not driving[1].lstrip().startswith("Preconditions:"):
            problem(f, "'Driving it with drive.sh' must start with 'Preconditions:'")
        if f"(./{f.name})" not in index:
            problem(readme, f"does not link feature file {f.name}")
    if not (SKILL / "SKILL.md").read_text().startswith("---\nname: verify-"):
        problem(SKILL / "SKILL.md", "missing YAML frontmatter with name")
    link = ROOT / ".claude/skills" / SKILL.name
    if not (link / "SKILL.md").exists():
        problem(link, "symlink to the verification skill is missing or broken")


def check_cli_flags_covered() -> None:
    corpus = "\n".join(p.read_text() for p in FEATURES.glob("*.md"))
    for src in CLI_SOURCES:
        for flag in FLAG_RE.findall(src.read_text()):
            if flag not in corpus:
                problem(src, f"flag {flag} is not covered by any feature-map file")


def check_architecture() -> None:
    arch = ROOT / "docs/architecture.md"
    if not arch.exists():
        problem(arch, "missing")
        return
    text = arch.read_text()
    if "```mermaid" not in text:
        problem(arch, "must contain at least one mermaid diagram")
    for src in CLI_SOURCES:
        if src.relative_to(ROOT).as_posix() not in text:
            problem(arch, f"does not mention entry point {src.relative_to(ROOT)}")


def check_intent() -> None:
    intent = ROOT / "docs/intent.md"
    if not intent.exists():
        problem(intent, "missing")
        return
    h2s = headings(intent.read_text(), 2)
    missing = [h for h in INTENT_H2S if h not in h2s]
    if missing:
        problem(intent, f"missing sections {missing}")


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    meta = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.split("#", 1)[0].strip()
    return meta


def check_decisions() -> None:
    readme = DECISIONS / "README.md"
    if not readme.exists():
        problem(DECISIONS, "missing README.md")
    files = sorted(p for p in DECISIONS.glob("*.md") if p.name != "README.md")
    metas: dict[str, tuple[Path, dict[str, str]]] = {}
    for f in files:
        m = DECISION_FILE_RE.match(f.name)
        if not m:
            problem(f, "name must be NNNN-short-slug.md")
            continue
        text = f.read_text()
        meta = frontmatter(text)
        if meta is None:
            problem(f, "must start with --- frontmatter ---")
            continue
        missing = sorted(DECISION_KEYS - meta.keys())
        if missing:
            problem(f, f"frontmatter missing {missing}")
            continue
        if meta["id"] != str(int(m.group(1))):
            problem(f, f"id {meta['id']} does not match filename prefix {m.group(1)}")
        if meta["id"] in metas:
            problem(f, f"duplicate id {meta['id']}")
        metas[meta["id"]] = (f, meta)
        if not DATE_RE.match(meta["date"]):
            problem(f, f"date {meta['date']!r} must be YYYY-MM-DD")
        if meta["status"] not in DECISION_STATUSES:
            problem(f, f"status must be one of {sorted(DECISION_STATUSES)}")
        if meta["status"] == "superseded" and not meta.get("superseded_by"):
            problem(f, "superseded decision needs superseded_by")
        if headings(text, 1)[:1] != [meta["title"]]:
            problem(f, "H1 must match the frontmatter title")
    for f, meta in metas.values():
        for key in ("supersedes", "superseded_by"):
            ref = meta.get(key)
            if ref and ref not in metas:
                problem(f, f"{key} {ref} is not a known decision id")


def check_links() -> None:
    for doc in LINKED_DOCS:
        if not doc.exists():
            continue
        for target in LINK_RE.findall(doc.read_text()):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = (doc.parent / target.split("#", 1)[0]).resolve()
            if not path.exists():
                problem(doc, f"broken link {target}")


def main() -> int:
    check_feature_map()
    check_cli_flags_covered()
    check_architecture()
    check_intent()
    check_decisions()
    check_links()
    for p in problems:
        print(p)
    if problems:
        print(f"lint_docs: {len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("lint_docs: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
