#!/usr/bin/env python3
"""Render the activity event catalogue as a runbook reference.

    scripts/gen-event-codes.py path/to/codes.go > netzilo-admin/references/34-event-catalogue.md

Netzilo Server names every audited activity three ways: a display name ("Code
injection detected"), a stable code ("workspace.injection.detected") and a
category ("Suspicious"). The API returns all three on every event, and an
operator should be reading the display name back to an admin, not the code.
This renders the full table from the server's activity code map so the
catalogue is available offline and stays in step with the product.
"""

from __future__ import annotations

import re
import sys
from collections import OrderedDict
from datetime import date

ENTRY_RE = re.compile(
    r'^\s*[A-Za-z0-9_]+:\s*\{\s*"(?P<name>(?:[^"\\]|\\.)*)"\s*,\s*"(?P<code>[^"]+)"\s*,\s*"(?P<category>[^"]+)"\s*\},',
    re.MULTILINE,
)
CATEGORY_ORDER = [
    "Administration", "Authentication", "Access Control", "Policy Violation",
    "Data Exfiltration", "Suspicious", "System",
]


def main(path: str) -> None:
    source = open(path, encoding="utf-8").read()
    start = source.find("activityMap = map[Activity]Code{")
    if start == -1:
        sys.exit("no activityMap found; is this the server's activity code table?")
    entries = [m.groupdict() for m in ENTRY_RE.finditer(source[start:])]
    if not entries:
        sys.exit("activityMap found but no entries parsed")

    by_category: "OrderedDict[str, list[dict]]" = OrderedDict()
    for category in CATEGORY_ORDER:
        by_category[category] = []
    for e in entries:
        by_category.setdefault(e["category"], []).append(e)

    out = [
        "# Event catalogue — what each activity is called",
        "",
        f"Generated from Netzilo Server's activity table on {date.today().isoformat()} by",
        "`scripts/gen-event-codes.py`. {} activities.".format(len(entries)),
        "",
        "Every event the API returns carries all three columns: `activity` (the display",
        "name), `activity_code` (the stable identifier) and `activity_category`. **Say the",
        "display name.** The code is a filter value and a machine identifier — put it in a",
        "`GET /api/events/paginated?code=…` call, not in a sentence to an admin, unless they",
        "asked for it or you are telling them what to search for themselves.",
        "",
        "Codes are also the vocabulary of `references/32-detection-rule-authoring.md` and the",
        "Activity page filters in `references/30-activity-reports-and-integrations.md`.",
        "",
    ]
    for category, rows in by_category.items():
        if not rows:
            continue
        out += [f"## {category}", "", "| Say this | Code |", "|---|---|"]
        seen = set()
        for r in sorted(rows, key=lambda x: x["code"]):
            if r["code"] in seen:
                continue
            seen.add(r["code"])
            out.append(f'| {r["name"]} | `{r["code"]}` |')
        out.append("")
    print("\n".join(out))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
