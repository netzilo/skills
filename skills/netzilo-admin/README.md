# Netzilo Administration Skill

An installable **Agent Skill** that lets Claude install, configure, run, and
troubleshoot Netzilo end to end — server, identity, clients, network policy, AI
security — without contacting Netzilo support.

## Installing this skill

This folder is a self-contained Agent Skill: `SKILL.md` at the root plus supporting
runbooks in `references/`. It ships inside the `netzilo` Claude Code plugin, whose
manifest and marketplace catalog live two levels up in `.claude-plugin/`.

- **Claude Code plugin** (recommended) — in Claude Code run
  `/plugin marketplace add netzilo/skills`, then `/plugin install netzilo@netzilo`.
  The skill is then `/netzilo:netzilo-admin`, loads on its own when a task matches its
  description, and `/plugin update netzilo` brings new releases.
- **Claude Code, this folder alone** — copy or symlink the whole `netzilo-admin/` folder to
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
- **Your own marketplace** (to distribute a fork to a team) — this repository already
  is one: `.claude-plugin/marketplace.json` lists the `netzilo` plugin with
  `"source": "./"`. Fork it, keep the layout, and point users at your fork with
  `/plugin marketplace add <owner>/<repo>`.

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
| `10-ai-security-aidr.md` | the two enforcement points (devices and the AI Gateway), rollout for each, client mechanics, coding-agent hooks, SDK 5.0.0, browser extension & Enterprise Browser, guardrails, troubleshooting and old-client behaviour |
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
| `21-posture-checks.md` | every check type and platform, attaching to policies/profiles/published applications, old-client behaviour for gateway and extension checks, API body, design guidance, diagnosis |
| `22-network-routes-and-exit-nodes.md` | routes, HA, masquerade, domain routes, exit nodes, policy groups, what the routing peer installs, diagnosis |
| `23-dns-management.md` | peer DNS, nameserver groups, split DNS, search domains, exclusions, diagnosis |
| `24-peers-and-setup-keys.md` | peer lifecycle and controls, setup key design, bulk operations, diagnosis |
| `25-users-groups-and-account-settings.md` | roles, users/agents, groups and membership sources, every account setting, tenant tab, diagnosis |
| `26-profiles-secure-workplace.md` | Enterprise Workspace, Enterprise Browser, Disposable Browser, Browser Extension domain settings, recording, exceptions, diagnosis |
| `27-ai-gateway.md` | the Netzilo AI Gateway (`netzilo-aigw`): requirements, install on Linux/macOS/Windows/containers, every flag, plain HTTP vs TLS, exposure (tunnel, public, published application), authentication and every refusal, what it pulls from management, usage telemetry, logs, troubleshooting |
| `28-edge-guardrails.md` | Edge → Guardrails: the model, every field, contexts, AI generation, Replay against real sessions, lifecycle, diagnosis |
| `29-edge-filters.md` | endpoint filters (groups, OS, agents, guardrails) and gateway filters (models, limits, MCP, gateways, guardrails), effective filters, design patterns, diagnosis for a device and for a gateway user |
| `30-activity-reports-and-integrations.md` | events and codes by category, AI Smart Search, CSV/API export, reports (incl. AI Agent Activity and AI Usage), the dashboard home and Agentic Activity, integrations (S3/Min.io, TURN, Artificial Intelligence) |
| `31-plans-limits-and-billing.md` | every plan gate and hard limit with its exact message, downgrade blockers, what happens when a subscription lapses, and how plans are set on self-hosted |
| `32-detection-rule-authoring.md` | writing and testing detection rules for the AI security engine: the rule format, `requires:` capabilities, every field and action, sessions and the observation log, the behaviour graph, the scripting reference, evaluation order, replay, fixtures, migration from the process-keyed engine, and worked rules |
| `33-api-request-schemas.md` | every REST request body and parameter, generated from the server's OpenAPI description |
| `34-event-catalogue.md` | every activity code with its display name and category |
| `35-plain-language.md` | what to call pages, objects and events when talking to an admin, and the AI Edge terms |
| `36-device-tools.md` | diagnosing and repairing a peer from the support agent |
| `37-device-tool-reference.md` | one card per device tool: arguments, outputs, OS notes, failure modes |
| `38-device-diagnosis-method.md` | the root-cause method for device problems and the OS matrix |
| `39-end-user-self-service.md` | what a regular user can see and do, and which side of the admin's boundary each symptom ends on |
| `40-windows-hosts.md` | Windows install, services, drivers, DNS, the AI network filter, posture |
| `41-remediation-workflows.md` | bounded remediation workflows for changes |
| `42-ai-assistant-self-hosted.md` | the AI Assistant on a self-hosted server |
| `43-clientless-access-gateway.md` | clientless browser access through the Netzilo gateway |
| `44-published-applications.md` | published applications through the Netzilo reverse proxy, incl. forwarding the user's credential to an AI gateway |
| `45-ai-gateway-providers-and-limits.md` | Edge → Providers and Edge → Limits: providers, keys, model catalogue, grants, budgets, how the gateway applies them |
| `46-ai-gateway-mcp-servers-and-bundles.md` | Edge → MCP: MCP servers (HTTP, SSE, stdio), every authentication type, bundles, users' sign-ins, OAuth for MCP clients |
| `47-agentic-access-workplace.md` | Workplace → Agentic Access: what users see, the Connect dialogs and snippets, the gateway token, diagnosis |
| `48-installer-command-lines.md` | every installer and parameter: Windows client MSI / offline EXE / pack / online EXE, Enterprise Browser MSI and EXE, tenant-named installers, `CONFIGFILE` pre-enrolment, Intune/SCCM/GPO/Jamf, return codes, upgrade, uninstall, macOS and Linux, known installer limitations |

These runbooks describe the current Netzilo release. Where older public documentation
differs (hostnames, ports, rule syntax), the values here take precedence.
