# Netzilo Skills

Agent Skills for operating Netzilo, packaged as a **Claude Code plugin** and its own
marketplace. Every folder under `skills/` is a self-contained skill: a `SKILL.md` entry
point plus supporting reference files. The plugin manifest is
`.claude-plugin/plugin.json`; the marketplace catalog is `.claude-plugin/marketplace.json`.

This repository is the canonical source. Installed copies do not update themselves —
each skill carries its version and tells the agent how to check for a newer one.

## Available skills

| Skill | Version | What it does |
|---|---|---|
| [`netzilo-admin`](skills/netzilo-admin/) | 4.4.0 | Install, configure, run and troubleshoot Netzilo end to end: server (on-prem, AWS, Azure), identity and SSO, clients on every OS (with the full Windows MSI/EXE and macOS installer command lines for the client and the Enterprise Browser), clientless browser access through the Netzilo gateway, published applications (private web apps at an address of their own, opened in any browser through the Netzilo reverse proxy), network policy, AI security (AIDR) on devices, in the browser through the Netzilo browser extension (ChatGPT, Claude, Gemini and other web AI apps, browser filters, browser sessions in the behaviour graph) and through the Netzilo AI Gateway (model grants, limits, MCP servers and bundles, guardrails, Agentic Access, Claude Desktop organization sign-in, AI usage), detection-rule authoring, REST API automation, connectivity diagnosis, Windows hosts, the secure Workspace, log interpretation, bounded remediation workflows, running the AI Assistant on a self-hosted server, onboarding and rollout, incident response and recovery, plan and billing limits, data-handling answers for security reviews, an end-user guide to publish, and support escalation. |

Machine-readable index: [`manifest.json`](manifest.json).

## Installing

- **Claude Code plugin** (recommended) — add this repository as a marketplace, then
  install the `netzilo` plugin; every skill in it loads, and `/plugin update` brings
  new releases.
  ```
  /plugin marketplace add netzilo/skills
  /plugin install netzilo@netzilo
  ```
  The skills are then available as `/netzilo:netzilo-admin` and load on their own when
  a task matches their description.
- **Claude Code, one skill folder** — copy or symlink a folder from `skills/` into
  `~/.claude/skills/<skill>/` (all projects) or `.claude/skills/<skill>/` inside a
  repository (project-scoped).
  ```bash
  git clone https://github.com/netzilo/skills.git
  cp -R skills/skills/netzilo-admin ~/.claude/skills/
  ```
- **Claude Desktop / claude.ai** — zip the skill folder so the archive contains
  `<skill>/SKILL.md` (not `SKILL.md` at the root), then upload it under
  **Settings → Customize → Skills**.
  ```bash
  cd skills && zip -r netzilo-admin.zip netzilo-admin -x '.*'
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
curl -s https://raw.githubusercontent.com/netzilo/skills/main/skills/netzilo-admin/VERSION
```

Update with `/plugin update netzilo` (Claude Code plugin), by pulling this repository
and re-copying (a skill folder), or by re-zipping and re-uploading (Desktop, claude.ai,
API).

## Versioning

`MAJOR` for a restructure that changes how a skill is loaded or where its files live,
`MINOR` for new runbooks or substantive procedures, `PATCH` for corrections and
clarifications. Each skill's `CHANGELOG.md` records what changed.

## Support

support@netzilo.com · documentation at https://doc.netzilo.com
