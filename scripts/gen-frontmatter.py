#!/usr/bin/env python3
"""Write the machine-readable front matter of every reference file.

    scripts/gen-frontmatter.py [--check]

Front matter is derived from the file itself (title, section index, sizes)
plus the curated capability map in scripts/capabilities.json. `--check`
exits non-zero when a file's front matter is stale, so CI catches an edit
that changed the sections without regenerating.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import skillmeta as sm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "netzilo-admin"


def build(ref: sm.Reference, curated: dict) -> dict:
    requires = list(curated.get("requires", []))
    overrides = curated.get("sections", {})
    sections = []
    for s in ref.sections():
        entry = {"id": s.id, "title": s.title, "chars": s.chars}
        if s.id in overrides:
            # A section that differs from its file carries the derived surface
            # list too, so a consumer never has to know the capability table.
            entry["requires"] = overrides[s.id]
            entry["executable_on"] = sm.executable_on(overrides[s.id])
        sections.append(entry)
    front = {
        "id": ref.ref_id,
        "title": ref.title,
        "requires": requires,
        "executable_on": sm.executable_on(requires),
        "chars": len(ref.body),
        "sections": sections,
    }
    return front


def main(check: bool) -> int:
    curated_map = json.loads((Path(__file__).parent / "capabilities.json").read_text())
    stale, missing = [], []
    for path in sm.references(ROOT):
        curated = curated_map.get(path.name)
        if curated is None:
            missing.append(path.name)
            continue
        ref = sm.load(path)
        front = build(ref, curated)
        if ref.front == front:
            continue
        stale.append(path.name)
        if not check:
            ref.front = front
            path.write_text(sm.dump(ref), encoding="utf-8")
    if missing:
        print("not in scripts/capabilities.json: " + ", ".join(missing), file=sys.stderr)
    if check:
        if stale:
            print("stale front matter (run scripts/gen-frontmatter.py): " + ", ".join(stale), file=sys.stderr)
        return 1 if stale or missing else 0
    print(f"front matter written for {len(stale)} file(s); {len(sm.references(ROOT)) - len(stale)} already current")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main("--check" in sys.argv))
