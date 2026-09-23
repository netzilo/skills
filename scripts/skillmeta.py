"""Shared helpers for the skill's machine-readable metadata.

Every reference file carries YAML front matter that an agent reads before it
loads the body: which capabilities the procedures need, which agent surfaces
can execute them, and a section index with sizes so a large file can be
loaded one section at a time instead of whole.

The front matter is generated (scripts/gen-frontmatter.py) and validated
(scripts/check-skills.py); it is never hand-edited, except for the curated
capability map in scripts/capabilities.json.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^## +(?:(\d+(?:\.\d+)*)\.? +)?(.+?)\s*$", re.MULTILINE)

# What a procedure needs in order to be EXECUTED (not merely explained).
CAPABILITIES = {
    "api": "Netzilo management REST API with an admin token",
    "dashboard-ui": "a browser session in the Netzilo dashboard",
    "server-shell": "a shell on the Netzilo Server host (docker, systemd, files)",
    "client-device": "a shell or OS access on a device running the Netzilo client",
    "idp-console": "the identity provider's own admin console",
    "device-tools": "the support device tools through management: read a peer's tool catalog and run its tools remotely",
}

# Agent surfaces and the capabilities each one has. A reference is executable
# on a surface when the surface holds every capability the reference requires;
# otherwise the agent explains the procedure and the human performs it.
SURFACES = {
    "dashboard-assistant": {"api", "device-tools"},
    "netzilo-harness": {"api", "server-shell", "client-device", "device-tools"},
    "human-operator": {"api", "dashboard-ui", "server-shell", "client-device", "idp-console", "device-tools"},
}

# Signals used to cross-check the curated map against the prose, so a file
# that grows a docker command stops claiming it is API-only.
SIGNALS = {
    # Command context only: a path mentioned in prose ("never paste management.json")
    # is not a shell requirement, and /etc/netzilo is a client path, not a server one.
    "server-shell": re.compile(
        r"^\s*(sudo )?(docker (compose|run|exec|ps)|systemctl|journalctl)\b"
        r"|^\s*(sudo )?(cat|less|tail|vi|nano|cp|mv|rm|chmod|chown) [^\n]*(zitadel\.env|management\.json)",
        re.I | re.MULTILINE,
    ),
    "client-device": re.compile(r"^\s*(sudo )?netzilo (up|down|status|login|debug|version|service)", re.I | re.MULTILINE),
    "api": re.compile(r"\bnz /|GET /api/|POST /api/|PUT /api/|DELETE /api/|PATCH /api/"),
    "idp-console": re.compile(r"Zitadel console|Entra|Okta|Google Workspace admin", re.I),
    "dashboard-ui": re.compile(r"Dashboard →|dashboard →", re.I),
    "device-tools": re.compile(r"\bdevice_(tools|run)\(|/api/support/devices/"),
}


@dataclass
class Section:
    id: str
    title: str
    chars: int


@dataclass
class Reference:
    path: Path
    front: dict = field(default_factory=dict)
    body: str = ""

    @property
    def ref_id(self) -> str:
        return self.path.name.split("-", 1)[0]

    @property
    def title(self) -> str:
        m = re.search(r"^# +(.+)$", self.body, re.MULTILINE)
        return m.group(1).strip() if m else self.path.stem

    def sections(self) -> list[Section]:
        out: list[Section] = []
        matches = list(HEADING_RE.finditer(self.body))
        seen: dict[str, int] = {}
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.body)
            sid = m.group(1) or slug(m.group(2))
            # Two headings that slug alike (or a repeated number) would give an
            # agent an ambiguous section to load; the later ones get a suffix.
            seen[sid] = seen.get(sid, 0) + 1
            if seen[sid] > 1:
                sid = f"{sid}-{seen[sid]}"
            out.append(Section(id=sid, title=m.group(2).strip(), chars=end - m.start()))
        return out

    def signals(self) -> set[str]:
        return {cap for cap, rx in SIGNALS.items() if rx.search(self.body)}


def slug(title: str) -> str:
    # 48 characters keeps long headings apart that share their first words
    # (e.g. three "Analyze …/Block …/Sanction …" variants), cut on a word
    # boundary so the ID stays readable.
    full = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(full) > 48:
        full = full[:48].rsplit("-", 1)[0]
    return full or "section"


# The device tools the support agents can call, by exact name. The validator
# rejects any other `diag.*` / `mod.*` name in the prose, so a tool that was
# renamed or never existed cannot be recommended.
DEVICE_TOOLS = {
    "diag.catalog", "diag.status", "diag.config", "diag.routes", "diag.route_match",
    "diag.dns", "diag.probe", "diag.posture", "diag.system", "diag.loglevel",
    "diag.logs", "diag.grep", "diag.bundle",
    "mod.refresh", "mod.disconnect", "mod.loglevel",
    "shell.run",
}


def load(path: Path) -> Reference:
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if m:
        return Reference(path=path, front=yaml.safe_load(m.group(1)) or {}, body=text[m.end():])
    return Reference(path=path, front={}, body=text)


def dump(ref: Reference) -> str:
    front = yaml.safe_dump(ref.front, sort_keys=False, allow_unicode=True, width=100).rstrip()
    return f"---\n{front}\n---\n{ref.body}"


def executable_on(requires: list[str]) -> list[str]:
    need = set(requires)
    return [s for s, caps in SURFACES.items() if need <= caps]


def references(root: Path) -> list[Path]:
    return sorted((root / "references").glob("*.md"))
