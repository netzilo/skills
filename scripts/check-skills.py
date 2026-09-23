#!/usr/bin/env python3
"""Validate the netzilo-admin skill: metadata, capability curation, versions, links.

    scripts/check-skills.py

Exits non-zero on any error. Warnings are printed but do not fail the build,
because they flag things a human should look at rather than things that are
provably wrong. Everything it checks is something an agent relies on at load
time: front matter that matches the file, a capability map that tells an
API-only agent what it cannot execute, links that resolve, and one version
stated the same way everywhere.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
import skillmeta as sm  # noqa: E402
import importlib.util  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "netzilo-admin"
SCRIPTS = REPO / "scripts"

# A reference over this size must be loadable in parts, so it needs a real
# section index; otherwise an agent has to pull the whole thing into context.
BIG_FILE_BYTES = 60 * 1024
MIN_SECTIONS_FOR_BIG_FILE = 5

# Capabilities whose absence from the curated map actively misleads: an
# API-only agent told "requires: [api]" will try to run a docker command.
SHELL_CAPS = {"server-shell", "client-device"}

REF_LINK_RE = re.compile(r"references/(\d{2}-[a-z0-9-]+\.md)(?:#([A-Za-z0-9._-]+))?")

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_gen_frontmatter():
    """Import gen-frontmatter.py so its --check logic is used, not copied."""
    spec = importlib.util.spec_from_file_location("gen_frontmatter", SCRIPTS / "gen-frontmatter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def as_date(value) -> str:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value).strip().strip('"').strip("'")


def section_bodies(ref: sm.Reference) -> list[tuple[str, str, str]]:
    """(section id, title, text) for every `## ` section of a reference."""
    out = []
    matches = list(sm.HEADING_RE.finditer(ref.body))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(ref.body)
        sid = m.group(1) or sm.slug(m.group(2))
        out.append((sid, m.group(2).strip(), ref.body[m.start():end]))
    return out


# --- (a) front matter present and current -----------------------------------


def check_front_matter() -> None:
    gen = load_gen_frontmatter()
    for path in sm.references(SKILL):
        if not sm.FRONT_MATTER_RE.match(path.read_text(encoding="utf-8")):
            error(f"{path.name}: no YAML front matter (run scripts/gen-frontmatter.py)")
    if gen.main(check=True) != 0:
        error("front matter is stale or unmapped — run scripts/gen-frontmatter.py "
              "(see the gen-frontmatter output above for the file list)")


# --- (b) capabilities.json covers exactly the references --------------------


def check_capability_map(curated_map: dict) -> None:
    on_disk = {p.name for p in sm.references(SKILL)}
    mapped = {k for k in curated_map if not k.startswith("//")}
    for name in sorted(on_disk - mapped):
        error(f"scripts/capabilities.json: no entry for references/{name}")
    for name in sorted(mapped - on_disk):
        error(f"scripts/capabilities.json: stale entry '{name}' — no such reference file")

    for name in sorted(mapped & on_disk):
        entry = curated_map[name]
        requires = entry.get("requires", [])
        if not isinstance(requires, list):
            error(f"scripts/capabilities.json: {name}: 'requires' must be a list")
            continue
        for cap in requires:
            if cap not in sm.CAPABILITIES:
                error(f"scripts/capabilities.json: {name}: unknown capability '{cap}' "
                      f"(known: {', '.join(sorted(sm.CAPABILITIES))})")
        overrides = entry.get("sections", {}) or {}
        ids = {s.id for s in sm.load(SKILL / "references" / name).sections()}
        for sid, caps in overrides.items():
            if sid not in ids:
                error(f"scripts/capabilities.json: {name}: section override '{sid}' "
                      f"matches no `## ` heading in that file")
            for cap in caps:
                if cap not in sm.CAPABILITIES:
                    error(f"scripts/capabilities.json: {name}: section '{sid}': "
                          f"unknown capability '{cap}'")


# --- (c) curation vs prose ---------------------------------------------------


def check_signals(curated_map: dict) -> None:
    """Cross-check the curated `requires` against capability hints in the prose.

    The rule, in one sentence: an undeclared signal is a WARNING, except that
    a server-shell or client-device signal in a file that declares NEITHER of
    them is an ERROR unless the section carrying it has a section-level
    override.

    Why the exception: a file requiring nothing but `api` is executable_on
    `dashboard-assistant`, an agent that has only the REST API. If such a file
    carries docker/systemctl or `netzilo <cmd>` steps, that agent is told it
    can run something it has no way to run. A file that already declares one
    of the two is not executable on an API-only surface anyway, so the same
    prose is only worth a warning. Prose also mentions commands it does not
    ask you to run, which is why nothing else here fails the build.
    """
    for path in sm.references(SKILL):
        entry = curated_map.get(path.name)
        if entry is None:
            continue
        ref = sm.load(path)
        declared = set(entry.get("requires", []))
        overrides = entry.get("sections", {}) or {}
        declared_anywhere = set(declared)
        for caps in overrides.values():
            declared_anywhere |= set(caps)

        api_only = not (declared & SHELL_CAPS)

        for cap in sorted(ref.signals() - declared_anywhere):
            shown = f"[{', '.join(sorted(declared)) or 'none'}]"
            if cap not in SHELL_CAPS or not api_only:
                warn(f"{path.name}: prose shows '{cap}' ({sm.CAPABILITIES[cap]}) "
                     f"but requires is {shown}")
                continue
            rx = sm.SIGNALS[cap]
            hits = [(sid, title) for sid, title, text in section_bodies(ref)
                    if rx.search(text) and cap not in set(overrides.get(sid, []))]
            if hits:
                where = "; ".join(f"§{sid} {title}" for sid, title in hits[:3])
                more = f" (+{len(hits) - 3} more)" if len(hits) > 3 else ""
                error(f"{path.name}: requires is {shown} — no shell capability — yet "
                      f"{where}{more} carries '{cap}' commands with no section-level "
                      f"override, so an API-only agent is told it can execute them. "
                      f"Add '{cap}' to requires in scripts/capabilities.json, or give "
                      f"those sections a 'sections' override.")
            else:
                warn(f"{path.name}: '{cap}' appears only in sections that already "
                     f"override it; file-level requires stays {shown}")


# --- (d) version consistency -------------------------------------------------


def check_versions() -> None:
    import yaml

    version_file = yaml.safe_load((SKILL / "VERSION").read_text(encoding="utf-8")) or {}
    version = str(version_file.get("version", "")).strip()
    released = as_date(version_file.get("released", ""))
    if not version or not released:
        error("netzilo-admin/VERSION: missing 'version:' or 'released:'")
        return

    skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    front = sm.load(SKILL / "SKILL.md").front
    meta = (front.get("metadata") or {}) if isinstance(front, dict) else {}
    if str(meta.get("version", "")).strip() != version:
        error(f"SKILL.md metadata.version is {meta.get('version')!r}, "
              f"VERSION says {version!r}")
    if as_date(meta.get("released", "")) != released:
        error(f"SKILL.md metadata.released is {as_date(meta.get('released', ''))!r}, "
              f"VERSION says {released!r}")

    manifest = json.loads((REPO / "manifest.json").read_text(encoding="utf-8"))
    entry = next((s for s in manifest.get("skills", []) if s.get("name") == "netzilo-admin"), None)
    if entry is None:
        error("manifest.json has no entry for netzilo-admin")
    else:
        if str(entry.get("version", "")).strip() != version:
            error(f"manifest.json version is {entry.get('version')!r}, VERSION says {version!r}")
        if as_date(entry.get("released", "")) != released:
            error(f"manifest.json released is {entry.get('released')!r}, VERSION says {released!r}")

    compare = re.search(r"Compare its `version:` with \*\*([^*]+)\*\*", skill_md)
    if compare is None:
        error("SKILL.md: no \"Compare its `version:` with **X**\" line")
    elif compare.group(1).strip() != version:
        error(f"SKILL.md \"Compare its `version:` with **{compare.group(1).strip()}**\" "
              f"but VERSION says {version}")

    stated = re.search(r"This copy is version ([0-9][^,]*), released ([0-9-]+)", skill_md)
    if stated is None:
        error("SKILL.md: no \"This copy is version X, released Y\" line")
    else:
        if stated.group(1).strip() != version:
            error(f"SKILL.md says \"This copy is version {stated.group(1).strip()}\" "
                  f"but VERSION says {version}")
        if stated.group(2).strip() != released:
            error(f"SKILL.md says \"released {stated.group(2).strip()}\" "
                  f"but VERSION says {released}")

    changelog = (SKILL / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = re.search(rf"^## +{re.escape(version)} +— +(\S+)\s*$", changelog, re.MULTILINE)
    if heading is None:
        error(f"CHANGELOG.md: no '## {version} — {released}' heading")
    elif heading.group(1) != released:
        error(f"CHANGELOG.md: '## {version} — {heading.group(1)}' "
              f"but VERSION says released {released}")

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    for line in readme.splitlines():
        if not line.startswith("|") or "netzilo-admin" not in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        found = [c for c in cells if re.fullmatch(r"\d+\.\d+\.\d+", c)]
        if found and version not in found:
            error(f"README.md table lists netzilo-admin at {found[0]}, VERSION says {version}")


# --- (e) links ---------------------------------------------------------------


def check_links() -> None:
    files = {"SKILL.md": SKILL / "SKILL.md"}
    for p in sm.references(SKILL):
        files[f"references/{p.name}"] = p
    section_ids = {p.name: {s.id for s in sm.load(p).sections()} for p in sm.references(SKILL)}
    existing = set(section_ids)
    linked: set[str] = set()

    for label, path in files.items():
        text = path.read_text(encoding="utf-8")
        for target, anchor in REF_LINK_RE.findall(text):
            if target not in existing:
                error(f"{label}: links to references/{target}, which does not exist")
                continue
            if target != Path(label).name:
                linked.add(target)
            if anchor and anchor not in section_ids[target]:
                error(f"{label}: links to references/{target}#{anchor}, but that file "
                      f"has no section '{anchor}'")

    for name in sorted(existing - linked):
        warn(f"{name}: orphan — no other file links to references/{name}")


# --- (e2) numbered "§n" pointers and device tool names -----------------------

SECTION_POINTER_RE = re.compile(
    r"(?:references/)?(\d{2})-[a-z0-9-]+\.md`?\)?\s*§\s*(\d+)"
    r"|(?<![\w.])(\d{2}) §(\d+)"
)
TOOL_NAME_RE = re.compile(r"(?<![\w.])((?:diag|mod)\.[a-z_]+)")
NEGATION_RE = re.compile(r"not exist|no such|isn't a tool|is not a tool|there is no", re.I)


def check_section_pointers() -> None:
    """A prose pointer like `36-device-tools.md` §11 or "38 §4.2" must name a
    top-level numbered section that exists. The link checker only sees
    #anchors, so these went stale silently."""
    numbered: dict[str, set[str]] = {}
    for p in sm.references(SKILL):
        numbered[p.name[:2]] = {s.id.split(".")[0] for s in sm.load(p).sections()
                                if re.fullmatch(r"\d+(?:\.\d+)*", s.id)}
    files = [SKILL / "SKILL.md"] + sm.references(SKILL)
    for path in files:
        label = "SKILL.md" if path.name == "SKILL.md" else path.name
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for m in SECTION_POINTER_RE.finditer(line):
                ref, sec = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
                if ref not in numbered:
                    continue  # "30 §4" in prose that is not a file number
                if sec not in numbered[ref]:
                    error(f"{label}:{lineno}: points to reference {ref} §{sec}, "
                          f"which has no section {sec}")


def check_tool_names() -> None:
    files = [SKILL / "SKILL.md"] + sm.references(SKILL)
    for path in files:
        label = "SKILL.md" if path.name == "SKILL.md" else path.name
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for name in TOOL_NAME_RE.findall(line):
                if name in sm.DEVICE_TOOLS or NEGATION_RE.search(line):
                    continue
                error(f"{label}:{lineno}: names device tool '{name}', which does not exist "
                      f"(known: {', '.join(sorted(sm.DEVICE_TOOLS))})")


# --- (f) size budget, (g) H1 title ------------------------------------------


def check_size_and_titles() -> None:
    for path in sm.references(SKILL):
        ref = sm.load(path)
        size = path.stat().st_size
        n = len(ref.sections())
        if size > BIG_FILE_BYTES and n < MIN_SECTIONS_FOR_BIG_FILE:
            warn(f"{path.name}: {size // 1024} KB with only {n} section(s) — "
                 f"a file this large needs at least {MIN_SECTIONS_FOR_BIG_FILE} "
                 f"`## ` sections so it can be loaded in parts")
        declared = (ref.front or {}).get("title")
        if declared and declared != ref.title:
            error(f"{path.name}: H1 is {ref.title!r} but front matter title is {declared!r}")


# --- summary -----------------------------------------------------------------


def print_table() -> None:
    rows = []
    for path in sm.references(SKILL):
        ref = sm.load(path)
        front = ref.front or {}
        rows.append((
            path.name,
            f"{path.stat().st_size / 1024:.0f}K",
            str(len(ref.sections())),
            ",".join(front.get("requires") or []) or "-",
            ",".join(front.get("executable_on") or []) or "-",
        ))
    head = ("reference", "size", "sec", "requires", "executable_on")
    widths = [max(len(r[i]) for r in [head, *rows]) for i in range(5)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*head))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(fmt.format(*r))


def main() -> int:
    curated_map = json.loads((SCRIPTS / "capabilities.json").read_text(encoding="utf-8"))
    check_front_matter()
    check_capability_map(curated_map)
    check_signals(curated_map)
    check_versions()
    check_links()
    check_section_pointers()
    check_tool_names()
    check_size_and_titles()

    print_table()
    print()
    for w in warnings:
        print(f"WARNING  {w}")
    for e in errors:
        print(f"ERROR    {e}", file=sys.stderr)
    print()
    print(f"{len(sm.references(SKILL))} references checked: "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
