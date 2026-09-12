# Netzilo Skills

Agent Skills for operating Netzilo. Each top-level folder is a self-contained,
installable skill: a `SKILL.md` entry point plus supporting reference files.

This repository is the canonical source. Installed copies do not update themselves —
each skill carries its version and tells the agent how to check for a newer one.

## Available skills

| Skill | Version | What it does |
|---|---|---|
| [`netzilo-admin`](netzilo-admin/) | 1.5.0 | Install, configure, run and troubleshoot Netzilo end to end: server (on-prem, AWS, Azure), identity and SSO, clients on every OS, network policy, AI security (AIDR), REST API automation, connectivity diagnosis, log interpretation, onboarding and rollout, incident response and recovery, plan and billing limits, data-handling answers for security reviews, an end-user guide to publish, and support escalation. |

Machine-readable index: [`manifest.json`](manifest.json).

## Installing

- **Claude Code** — copy or symlink the skill folder into `~/.claude/skills/<skill>/`
  (all projects) or `.claude/skills/<skill>/` inside a repository (project-scoped).
  ```bash
  git clone https://github.com/netzilo/skills.git
  cp -R skills/netzilo-admin ~/.claude/skills/
  ```
- **Claude Desktop / claude.ai** — zip the skill folder so the archive contains
  `<skill>/SKILL.md` (not `SKILL.md` at the root), then upload it under
  **Settings → Customize → Skills**.
  ```bash
  zip -r netzilo-admin.zip netzilo-admin -x '.*'
  ```
- **Claude API / Agent SDK** — upload the folder with the Skills API and attach the
  returned skill id to an agent, or place the folder at `.claude/skills/<skill>/` in a
  mounted repository for automatic discovery.

## Staying current

Every skill contains a `VERSION` file and a `CHANGELOG.md`, and states its own version
in `SKILL.md` so the agent knows what it is running without extra reads. Agents are
instructed to compare their local version against this repository at the start of a
session, before escalating an issue to support, and whenever observed behaviour
contradicts the documentation.

Check any skill's current version directly:

```bash
curl -s https://raw.githubusercontent.com/netzilo/skills/main/netzilo-admin/VERSION
```

Update by pulling this repository and re-copying (Claude Code), or re-zipping and
re-uploading (Desktop, claude.ai, API).

## Versioning

`MAJOR` for a restructure that changes how a skill is loaded or where its files live,
`MINOR` for new runbooks or substantive procedures, `PATCH` for corrections and
clarifications. Each skill's `CHANGELOG.md` records what changed.

## Support

support@netzilo.com · documentation at https://doc.netzilo.com
