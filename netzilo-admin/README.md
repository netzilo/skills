# Netzilo Administration Skill

An installable **Agent Skill** that lets Claude install, configure, run, and
troubleshoot Netzilo end to end — server, identity, clients, network policy, AI
security — without contacting Netzilo support.

## Installing this skill

This folder is a self-contained Agent Skill: `SKILL.md` at the root plus supporting
runbooks in `references/`.

- **Claude Code** — copy or symlink the whole `netzilo-admin/` folder to
  `~/.claude/skills/netzilo-admin/` (personal, all projects) or `.claude/skills/netzilo-admin/`
  inside a project repo (project-scoped). Claude discovers it automatically; no restart
  needed for a new session.
- **Claude Desktop / claude.ai** — zip this folder (the zip must contain
  `netzilo-admin/SKILL.md`, not `SKILL.md` at the zip root) and upload it via
  **Settings → Customize → Skills → Upload** (claude.ai) or **Preferences → Customize →
  Skills → Upload** (Desktop app).
  ```bash
  cd .. && zip -r netzilo-admin.zip netzilo-admin -x '.*'
  ```
- **Claude API / Agent SDK** — upload with the Skills API
  (`client.skills.create(files=files_from_dir("netzilo-admin"))`) or the `ant skills create`
  CLI, then attach the returned `skill_id` to an agent. In a mounted repo, placing this
  folder at `.claude/skills/netzilo-admin/` is discovered automatically with no upload step.
- **Plugin marketplace** (to distribute to a team) — wrap this folder as a plugin
  (`.claude-plugin/plugin.json` + this directory under `skills/netzilo-admin/`) and list
  it in a `marketplace.json`; users run `/plugin marketplace add <repo>` then
  `/plugin install netzilo-admin@<marketplace>`.

Load `SKILL.md` first — it is the index: rules of engagement, a one-paragraph model of
the product, and a table routing every task to the right file in `references/`.

## What's inside `references/`

| File | Covers |
|---|---|
| `00-operator-playbook.md` | how to operate, triage table, canonical facts, known product gaps |
| `01-server-install.md` | on-prem one-liner, AWS Marketplace, Azure Marketplace, external DB, air-gapped, provided TLS, legacy compose path, install failure table |
| `02-server-operations.md` | layouts, health gates, logs, start/stop, upgrades (incl. digest-pinned images), config changes, backup & restore, TLS rotation, domain constraints, destructive re-run warning, firewall, metering, sizing, decommission |
| `03-server-troubleshooting.md` | symptom → fix for TLS, containers, login, client connectivity, performance, disk, reboot, failed upgrades, metering, escalation |
| `04-identity-and-sso.md` | users/roles/blocking, account auth settings, bundled Zitadel objects and console, everyday identity tasks, login errors, SMTP, SSO federation (Entra/Okta/Google/SAML), legacy direct-IdP mode |
| `05-client-install-and-deploy.md` | per-OS install/uninstall/upgrade, enrollment methods, containers/Kubernetes, fleet patterns, verification |
| `06-client-cli-reference.md` | every command, flag, env var, file path, status field, tray menu |
| `07-client-troubleshooting.md` | daemon, login, peer connectivity, relays, interfaces, DNS, routes, SSH, TLS inspection side effects, upgrades, verbose diagnostics |
| `08-network-administration.md` | peers, setup keys, groups, policies (multi-rule, direction semantics), routes/exit nodes, DNS, posture checks, activity/reports/integrations, tenants/plans |
| `09-api-and-automation.md` | auth, full endpoint catalogue, request bodies, recipes (keys, policies, export/import, cleanup, audits, token rotation) |
| `10-ai-security-aidr.md` | AIDR architecture, rollout runbook, client mechanics, coding-agent hooks, SDK, browser extension & Enterprise Browser, Edge Tools/MCP, rule authoring/testing, troubleshooting |
| `11-connectivity-diagnosis.md` | end-to-end "host X unreachable" procedure: classify target, verify both ends, resolve policy via API, validate routes, inspect the routing peer (forwarding, Netzilo firewall chains, NAT, tcpdump, cloud security groups), DNS, server checks, report template |
| `12-escalation-package.md` | when escalation is justified (and when it isn't), severity classification, evidence collection for server/client/config/events, secrets that must never be collected, a tested redaction + verification pass, the summary/environment/timeline documents, packaging and sending |
| `13-log-interpretation.md` | reading client, management and signal logs: line anatomy and timestamp traps, a one-minute profiling recipe, healthy start/connect/network-change sequences, message families, noise to rule out, what debug and trace add, client-to-server correlation, worked readings |
| `14-data-handling-and-privacy.md` | every device attribute reported to the server, exactly what AI security events carry, session recordings, server usage statistics and how to disable them, and the answers a security review asks for |
| `15-incident-response-and-recovery.md` | containment order for a compromised device or credential, what each revocation action actually stops, departing-employee sequence, suspicious AI activity, and recovery from self-inflicted lockouts |
| `16-onboarding-and-rollout.md` | day 0 to production in eight phases with an exit test for each, what the admin sees on first sign-in, and the first-week mistakes ranked by frequency |
| `17-end-user-guide.md` | a page the admin can publish for employees, the checks a user should make before raising a ticket, and a table translating what a user reports into what is actually wrong |
| `18-server-install-gated.md` | the on-premises install driven as numbered gates, each with a scripted check that must pass before the next one starts; use it when an install has to be proven step by step rather than run in one pass |
| `19-server-install-handout.md` | the install instructions written for the customer to follow themselves, to hand over rather than to work from |
| `20-policies-access-control.md` | Policies: model, every field, direction semantics, JSON editor, least-privilege migration, rule resolution and diagnosis |
| `21-posture-checks.md` | every check type and platform, attaching to policies/profiles/filters, API body, design guidance, diagnosis |
| `22-network-routes-and-exit-nodes.md` | routes, HA, masquerade, domain routes, exit nodes, policy groups, what the routing peer installs, diagnosis |
| `23-dns-management.md` | peer DNS, nameserver groups, split DNS, search domains, exclusions, diagnosis |
| `24-peers-and-setup-keys.md` | peer lifecycle and controls, setup key design, bulk operations, diagnosis |
| `25-users-groups-and-account-settings.md` | roles, users/agents, groups and membership sources, every account setting, tenant tab, diagnosis |
| `26-profiles-secure-workplace.md` | Enterprise Workspace, Enterprise Browser, Disposable Browser, Browser Extension domain settings, recording, exceptions, diagnosis |
| `27-edge-tools-and-mcp.md` | approved/discovered MCP tools, transports, approval workflow, gateway usage, diagnosis |
| `28-edge-scanners.md` | premium vs account scanners, YAML fields, AI generation, Replay testing, lifecycle, diagnosis |
| `29-edge-filters.md` | binding groups/OS/agents/tools/scanners/posture, design patterns, "filter not applying" checklist |
| `30-activity-reports-and-integrations.md` | events and codes by category, AI Smart Search, CSV/API export, reports, dashboard home, integrations (S3/Min.io, TURN, AI providers) |
| `31-plans-limits-and-billing.md` | every plan gate and hard limit with its exact message, downgrade blockers, what happens when a subscription lapses, and how plans are set on self-hosted |
| `32-detection-rule-authoring.md` | writing and testing detection rules for the AI security engine: the rule format, every field and action, the behaviour graph, the scripting reference, and worked rules |

These runbooks describe the current Netzilo release. Where older public documentation
differs (hostnames, ports, rule syntax), the values here take precedence.
