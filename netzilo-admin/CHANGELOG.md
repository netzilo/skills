# Changelog — netzilo-admin

Versioning: **MAJOR** for a restructure that changes how the skill is loaded or where
files live, **MINOR** for new runbooks or substantive new procedures, **PATCH** for
corrections, clarifications, and command fixes.

An agent reading this to decide whether an update matters: scan the entries newer than
your installed version and look for the area you are working in.

## 2.4.0 — 2026-09-21

Machine-readable capabilities, partial loading, and a write doctrine — the release
that makes one runbook set usable by agents with very different reach.

- **Every reference now declares what it needs.** Front matter carries `requires`
  (`api`, `dashboard-ui`, `server-shell`, `client-device`, `idp-console`) and the
  `executable_on` surfaces derived from it, so an agent knows before it reads whether a
  procedure is something it performs or something it explains. SKILL.md's new "What you
  can execute here" defines the three surfaces, and the routing table gained a `Needs`
  column. Sections can override the file when they differ.
- **Long files load in parts.** The same front matter carries a section index with sizes;
  a 178 KB runbook is read one section at a time instead of swallowing an agent's
  context. `references/08-network-administration.md`, previously reachable only by
  guessing, is now in the routing table.
- **A change doctrine.** "Making a change through the API" states the six steps every
  write follows: read the schema, read the current state, say what you will do, apply it,
  read it back, report the difference. Rule 6 now forbids asking anyone for a token and
  says plainly that a 401 or 403 is your own access being refused.
- **Escalating with only the API** (`12` §10): what an API-only agent can collect, what it
  cannot produce and must ask for, how to keep the credential sweep honest on API output,
  and the rule that it composes the summary but never holds a token.
- **Reading without drowning** (`09` §6.1): paginate and filter, never bulk-`GET`
  `/api/events`, verify parameter names against `33`, summarise instead of pasting.
- **Tooling.** `scripts/` gains the metadata contract (`skillmeta.py`,
  `capabilities.json`), its generator (`gen-frontmatter.py`), a validator
  (`check-skills.py`: front matter currency, capability curation against the prose,
  version identity, link and anchor resolution, size budgets) and `build.sh`. CI runs the
  validator on every push. `gen-api-schemas.py` can now rebuild `33` straight from a
  running server's `GET /api/support/openapi.yml`.

## 2.3.1 — 2026-09-21

`33-api-request-schemas.md` regenerated from a reconciled server description: the
OpenAPI file was audited against the handlers and corrected (tenant is `PUT`, not
`POST`; `/api/getclient` is `GET` with an `os` query parameter; `/api/events` returns a
string; `/api/stats` returns an object; countries/cities shapes; ~50 previously
undocumented routes added, e.g. `/api/events/paginated`, `/api/peers/bulk-delete`,
`/api/edge/*`, `/api/support/*`; required fields marked where the server rejects their
absence). The catalogue in `09` §2 stays as the reading guide; `33` is the contract.

## 2.3.0 — 2026-09-21

New reference `33-api-request-schemas.md`: every management API operation with its
parameters, request body (required fields marked, enums listed) and response codes,
generated from Netzilo Server's own OpenAPI description by `scripts/gen-api-schemas.py`.
Operating rule 7 now requires reading the request schema before any API write; `09` §3
points at the generated reference and at the live copy the server serves to admins at
`GET /api/support/openapi.yml`. Background: an agent built a `POST /api/reports` body
from memory, omitted the required `from`/`to` dates, and the write failed. The Netzilo
dashboard's AI assistant enforces the rule with its `netzilo_api_schema` tool.

## 2.2.1 — 2026-09-16

Portability fix in the log-profiling recipe (`13` §3). The step that collapses
twenty-character identifiers used a word-boundary construct that GNU `sed` accepts and
BSD `sed` silently ignores, so on macOS those identifiers were neither grouped nor kept
out of the operator's notes. The step now uses a POSIX boundary and behaves the same on
both. No other recipe in the set used the construct.

## 2.2.0 — 2026-09-16

Two changes to how the operator begins, applied across the index, the playbook, the API
file and every file that tells the operator where a command runs.

**Access is a requirement, not a preference.** The engagement now opens with three
ordered, required steps: establish which management server the customer uses and prove
it answers, obtain an **admin** service-account token for that server, and verify the
token against that server including confirming the tenant with the customer. The
previous model asked for a token only "for anything beyond a single click", recommended
starting with a read-only User-role token, and fell back to walking the customer through
the dashboard. That model could not work: groups, posture checks, DNS, events, reports,
the tenant, integrations and Edge are admin-only in the API, so a User-role token cannot
perform even read-only diagnosis for most of the product. The fallback is now stated
honestly as advising rather than supporting, with an explicit rule not to describe
anything as verified that was not read through the API or observed on the customer's
systems. The Cloud distinction between the dashboard host and the API host is called out
as the most common first mistake.

**The operator's own Netzilo client is a tool, not evidence.** The machine an operator
works from may run a client enrolled in someone else's network. The set never said so.
It now does, once in the index and once in the playbook, with the consequences spelled
out: every client command in every file runs on the customer's device, routing peer or
server; a local client showing connected proves nothing about the customer's server;
reachability is tested with `curl` against the customer's URL, not through the
operator's tunnel. The one legitimate deeper use is documented as a deliberate,
consented step: enrol as a test peer in the customer's network with their setup key,
knowing it disconnects the operator from whatever the client was on, and undo it
afterwards. The connectivity procedure now states that "A" is the customer's device, the
client troubleshooting opener says the three starting commands run on the affected
device and not the operator's machine, and the CLI reference carries the same note. The
escalation package, the one place an operator most plausibly runs a bundle command
locally, now opens its collection section by stating that everything in it comes from
the customer's systems and that a bundle from the operator's own device would send the
analyst down the wrong path.

## 2.1.0 — 2026-09-14

Server upgrades rewritten as a complete safe procedure (`02` §4). The previous section
gave the pull-and-recreate commands but not the steps that keep an upgrade from losing
data or taking down components that were not being updated.

- **What an upgrade can and cannot avoid.** The server is one host, so the component being
  replaced stops for the seconds the swap takes; what is achievable is no data loss, no
  dropped tunnels and no effect on untouched components. A table of where every piece of
  state lives shows why container recreation cannot lose it, and names the three
  operations that can. A second table gives the user-visible effect of restarting each
  component, so management and identity-provider restarts get scheduled and dashboard and
  signal do not.
- **Pre-flight, every time**: confirm health before changing anything, record the digest
  of every running image as the rollback anchor, back up, check disk, and understand that
  a pull reporting "up to date" on the moving tag is a correct result.
- **Update one component**: pull and recreate only the named service with `--no-deps`,
  the log line that means each component is up, and the check that proves it. Management
  migrates its schema automatically and that cannot be switched off. The identity
  provider's migrations are forward-only. Management and dashboard are updated together,
  management first, because nothing checks that their versions match.
- **Update the whole stack** in the order identity provider, management, dashboard,
  signal, verifying between. A bare pull-and-recreate on an on-premises host is now
  explicitly forbidden: it also moves the proxy, relay and cache to upstream latest.
- **Pin what you verified** to its digest so the next pull cannot move it, and how to
  move deliberately later. Marketplace images, already digest-pinned, follow the same
  edit, pull, verify, re-pin cycle.
- **Third-party images**: pin proxy, relay and cache on first upgrade; the cache is
  rebuilt from the database on every start so its volume is disposable; the database tag
  names its major version and is never bumped as an upgrade step.
- **Rollback per component** from the recorded digest without network access, with the
  two cases that need more: a management schema migration the old version cannot read
  requires the pre-upgrade dump and the old image together, and an identity provider that
  started cleanly on the new image is left there.
- Clean-up, and the list of things an upgrade does not do, including that re-running the
  installer is not an upgrade.
- The customer handout (`19`) told the customer to pull and recreate everything with no
  backup; it now gives the per-component loop and the two commands that erase a server.
  The failed-upgrade section (`03` §8) and the migration-failure row now point at the
  recorded-digest rollback rather than at a tag.

## 2.0.0 — 2026-09-14

**Breaking: three reference files were renamed.** Their contents are unchanged; only the
file names moved, so the whole set now runs `00` through `32` with no unnumbered strays.
Anything that links to the old names must be updated.

| Was | Now |
|---|---|
| `install-hosted-server.md` | `18-server-install-gated.md` |
| `hosted-server-readme.md` | `19-server-install-handout.md` |
| `aidr-rules.md` | `32-detection-rule-authoring.md` |

Every reference inside the skill set was updated with them: the index, the operator
playbook, the server install file, the AI security file, the scanners file, and the
contents table, where the three rows now sit in numeric order with descriptions that say
what each file is for. Older changelog entries keep the old names, because that is what
the files were called at the time.

Why the numbering matters: the three were the only files without a numeric prefix, so
they sorted away from the runbooks they belong with and read as strays. The install pair
now sits directly after the core operator band it extends, and rule authoring sits after
the per-page administration band it supports.

This is a major version because the repository's versioning policy reserves it for a
restructure that changes where files live, which a rename is. Nothing about how the skill
loads has changed, and no procedure was altered.

## 1.5.0 — 2026-09-12

Gap-closing release. The skill set was audited against the product surface — dashboard,
management API, client platforms, entitlements, deployment topologies, AI security and the
published documentation — and the gaps that would still have forced a support call are now
covered. Five new files, eight extended, two corrections.

**Corrections (these produced wrong answers before)**

- Edge Filters are **not** an Enterprise feature. Any plan can create and use them; only
  premium catalogue scanner rules bound inside a filter require Enterprise. The previous
  blanket claim would have told a paying customer to upgrade for no reason (`29`).
- The routing description is now within the 500-character limit some hosts apply to the
  skill catalogue, so the trigger list survives instead of being cut mid-sentence.
- Server sizing now reconciles the numbers the marketplace images run on with the higher
  published minimum, instead of quoting only the lower figure (`01`).
- The skill's own file listing was missing six files, so `13` through `17` and `31` were
  present on disk but absent from the contents table. All files are now listed.
- Two headings carried internal framing rather than a customer-facing title: the
  gate-driven install runbook was titled after a filename, and the rule-authoring
  reference was titled as a system prompt. Both now say what the document is.

**New**

- `14-data-handling-and-privacy.md` — every device attribute reported to the server,
  including the two that surprise reviewers, and exactly what AI security events carry:
  normal prompts stay on the device, but a rule that fires sends the content that
  triggered it. Server usage statistics and how to switch them off. Prepared answers for
  a security review.
- `15-incident-response-and-recovery.md` — containment order for a compromised device or
  credential, a table of what each revocation actually stops (deleting a setup key does
  not disconnect devices already enrolled with it), the departing-employee sequence, and
  recovery from self-inflicted lockouts including a login-group restriction that locks out
  the admin who set it.
- `16-onboarding-and-rollout.md` — day 0 to production in eight phases, each with an exit
  test, plus the first-week mistakes ranked by frequency. Covers the first-run onboarding
  form and the dashboard status widget, so a red indicator later is not a surprise.
- `17-end-user-guide.md` — a page the admin can publish for employees, the four checks a
  user should make before raising a ticket, and a table translating what a user reports
  into what is actually wrong.
- `31-plans-limits-and-billing.md` — every plan gate and hard limit with its exact
  message, the traps (service users consume a Free seat; filters are not gated), what a
  blocked downgrade means, what actually happens when a subscription lapses, and how plans
  are set on self-hosted.

**Extended**

- API (`09`): the status-code table, including that field validation returns 422 rather
  than 400; every authentication failure collapsing to one message; group deletion
  returning an unhelpful 500 when the group is still referenced; tokens being role-scoped
  only; no versioning and no idempotency; and the silent limits that under-fetch instead
  of erroring.
- Operations (`02`): no high availability for the server and no Kubernetes path, stated
  plainly; uncapped relay bandwidth; clients need not be upgraded with the server; database
  engine migration; keeping the geolocation database current; and the wildcard certificate
  failures that are expected noise rather than an incident.
- Client deployment (`05`): macOS needs three approvals and pre-approving extensions does
  not cover the third; the installer package versus the executable installer for managed
  deployment; the separate Linux tray application; no managed configuration for mobile;
  hardened Kubernetes needing an exemption; and the outbound allow-list for hosted
  customers.
- Client troubleshooting (`07`): a competing VPN, a wrong clock, an unfinished captive
  portal and an intercepting proxy — four environment causes that look like product faults.
- Users (`25`): the guard rails that refuse a change by design, why a role selector is
  disabled with no on-screen explanation, and everything that blocks a group deletion.
- Peers (`24`): accepted ranges for login expiration and setup-key lifetime, why login
  expiration cannot be set on a setup-key peer, and that deleting a network deletes every
  route inside it.
- Scanners (`28`): there is no version history and no rollback, so fetch and keep a rule
  before editing; premium rule sensitivity is fixed and cannot be tuned; performance is
  not instrumented, so do not quote a number.
- AI security (`10`): excluding a domain from inspection is not self-service; certificate
  trust varies by runtime; provider coverage is broader than the named list; and how to
  read the behaviour graph, whose colours and clustering were previously unexplained.

## 1.4.0 — 2026-09-12

New: log-first interpretation of client and management logs (`13`), built from real
client and production management logs cross-checked against the software's behaviour.

- **Line anatomy** shared by client and management: RFC 3339 local time with UTC offset
  (offset can change inside one client file; containers print `Z`; dashboard event
  times are UTC), four-letter levels, optional `[context/requestID/accountID/peerID]`
  bracket, a source-location field to ignore, and truncated key prefixes in messages.
- **A one-minute profiling recipe** with a sanitiser that collapses identifiers so
  identical events group together, plus an anchor-and-window read with the noise
  families filtered out.
- **Client**: file layout including the macOS system-extension logs that ride along in
  the bundle and the launchd `err.log` that is mostly benign TLS-handshake noise; the
  healthy daemon start order; the healthy connect order with the `connection
  established … direct=/relayed=/ice=` verdict line; the network-change restart cycle
  and why its `context canceled` errors are expected; message families for management,
  signal, peers, DNS and the AI-security stack; a noise list; what `debug`/`trace` add.
- **Management**: where it logs and how lines are attributed; the healthy start order
  from OIDC discovery to `running HTTP server and gRPC server`; steady-state families
  (`NOOP`, `Peer has no userID`, `FILTER_DIAG` as the direct answer to "why is the
  filter not applying", tenant resolution, token revocation, ephemeral cleanup, relay
  credential issuance); `WARN`/`ERRO` families including the fact that only non-success
  API responses are logged; what `debug`/`trace` add (REST access log only at trace).
- **Signal**: start lines and the two steady-state warnings, and their pairing with the
  client's `wrongly addressed message`.
- **Correlation**: WireGuard public key as the primary join (prefix-truncated on the
  client), overlay IP/FQDN, server-only `requestID`, UTC conversion, the ~30 s dashboard
  lag, AIDR identifiers via debug-level `Buffered event` lines, and a step-by-step
  procedure.
- **Six worked readings** from real logs: laptop reconnect cycles, DNS loss during a
  network change, duplicate identity (`wrongly addressed` + `already registered`),
  posture-gated connectivity, a local port conflict, and stale-client login noise on the
  server.
- Routing description shortened below 500 characters so the trigger list survives
  harnesses that truncate it in the skill catalogue; wording and triggers unchanged.
- Escalation (`12`) now notes the system-extension logs and how to grep `err.log` for a
  panic; client (`07`) and server (`03`) troubleshooting route log-first questions to `13`.

## 1.3.0 — 2026-09-12

Signal and relay (STUN/TURN) get a dedicated diagnosis section (`03` §4a).

- **Component model**: what management, signal and the relay each do, and how each
  fails differently — signal down blocks *new* peer connections only; relay down affects
  peers behind restrictive NAT only; management down stops updates but keeps tunnels.
- **Shipped relay configuration** stated explicitly: coturn on host network, ports
  3478/5349 plus the `49152–65535/udp` allocation range, static `self` credential that
  must match between `management.json` and `turnserver.conf`, no certificate mounted
  in Let's Encrypt mode (so `turns:5349` is expected to fail), no `external-ip`, and the
  Integrations → Networking override that bypasses coturn entirely.
- **Client-first triage table** mapping `netzilo status -d` output (`Signal:`,
  `Relays: n/m`, `Relayed`, handshake state) to the responsible component.
- **Server verification**: signal container and Caddy route; coturn listeners; a
  credential-consistency check that compares hashes without printing the secret; a
  functional STUN and TURN self-test using `turnutils_stunclient` and
  `turnutils_uclient`, which ship in the coturn image (verified), including the TLS
  variant.
- **Client-site verification** with the WebRTC trickle-ICE page and the same image run
  externally, and how to read `host` / `srflx` / `relay` candidates.
- **Failure table** covering port conflicts, security groups, the relay range, cloud
  1:1 NAT, TLS relay, ICE failure when both sites block UDP, integration overrides,
  `401` floods and relay CPU.
- Client troubleshooting (`07` §4) and connectivity diagnosis (`11` §7) now route to it.

## 1.2.0 — 2026-09-12

Server access for self-hosted diagnosis.

- **Ask for SSH.** The operator is now told to request shell access to the server
  whenever a self-hosted task touches server logs, container state, certificates,
  upgrades or backups, instead of working from screenshots — with wording to ask for it,
  and the AWS Systems Manager and Azure Serial Console / Bastion alternatives when SSH
  is closed (`SKILL.md`, `00` §4).
- **Conduct once granted**: read-only first, announce state-changing commands before
  running them, and do not open the configuration files that hold the master key,
  database passwords and identity-provider secrets.
- **Fallback is explicit**: if access is refused or impossible, use the customer-run
  collection blocks (`12` §8) rather than stalling.
- Server troubleshooting (`03`) and escalation server collection (`12` §4.3) now open
  with the same instruction.

## 1.1.0 — 2026-09-12

Escalation reworked around code-level analysis and real log collection (`12`).

- **Scope narrowed.** Escalation is now defined as "the answer requires reading the
  product's source code", with a decision test, six qualifying signals (crash,
  enforcement contradicting configuration, stuck state machine, migration failure,
  documented procedure failing, detection engine disagreeing with its own rule) and an
  explicit table of what is *not* an escalation.
- **What the debug bundle actually contains**, documented precisely: `status.txt` plus
  every file in the daemon log directory — no routes, interfaces, firewall rules or
  system information, so those are now collected separately.
- **Platform hazards.** On Windows the bundle sweeps in the configuration directory:
  `config.json` (WireGuard private key), `token.dat`, `pat.dat` and `netzilo-ca-key.pem`
  (TLS-inspection CA private key) must be removed before sending. On macOS the launchd
  logs `/var/log/Netzilo.err.log` and `.out.log` sit outside the collected directory and
  are not in the bundle. On Linux the service stdout/stderr logs are included.
- **Tray caveat**: Support → Collect Data produces a bundle with no status snapshot and
  no anonymization; use the CLI.
- **Anonymization guidance reversed.** `-A` does not hide WireGuard public keys, peer
  IDs, group names or prompts, and anonymizes the status file and the logs with
  independent passes, so addresses no longer match across files. Default is now
  un-anonymized, with the trade-off documented.
- **Correlation keys** section: which identifiers join a client log line to a server log
  line, plus the debug-level `Buffered event:` trick for matching dashboard events.
- **Verbose reproduction**: log level is in-memory only, so the level must be raised and
  the fault reproduced within one daemon lifetime; subsystem knobs for ICE, WireGuard,
  gRPC, pprof and the AI behaviour graph.
- **Server collection** via `docker compose logs` (management logs to stdout in the
  shipped configuration); there is no server-side bundle command.
- **Customer-run instructions** for Linux/macOS, Windows and the server, for when the
  agent has no shell on the affected machine.
- Credential sweep retained and retargeted: strip credentials, preserve the identifiers
  the analyst needs.

## 1.0.0 — 2026-09-12

First release.

- **Operating model** — `SKILL.md` index with rules of engagement, the preferred access
  path (ask the customer for a service-user API token and work through the REST API),
  and a task-to-reference routing table.
- **Server** — install across on-prem, AWS Marketplace and Azure Marketplace including
  external database, air-gapped and provided-TLS variants (`01`); day-2 operations
  covering both on-disk layouts, upgrades for tag- and digest-pinned images, backup and
  restore, certificate rotation, metering and decommission (`02`); symptom-driven
  troubleshooting (`03`).
- **Identity** — users, roles, account authentication settings, the bundled identity
  provider, SMTP, SSO federation, and the legacy direct-IdP path (`04`).
- **Client** — install, enrolment and fleet deployment per OS including containers and
  Kubernetes (`05`); complete CLI, environment-variable and file-path reference (`06`);
  troubleshooting with exact error strings (`07`).
- **Network administration** — peers, setup keys, groups, policies, routes, DNS,
  posture checks, activity and integrations (`08`), with per-page deep dives for
  policies (`20`), posture checks (`21`), routes and exit nodes (`22`), DNS (`23`),
  peers and setup keys (`24`), users and account settings (`25`), and profiles (`26`).
- **AI security** — AIDR architecture and rollout, coding-agent hooks, the SDK, the
  browser extension and Enterprise Browser (`10`); Edge Tools and MCP (`27`); Edge
  Scanners with Replay testing (`28`); Edge Filters (`29`).
- **Evidence** — activity events and codes, reports, dashboard home, integrations (`30`).
- **Automation** — REST API authentication, endpoint catalogue, request bodies and
  recipes (`09`).
- **Diagnosis** — end-to-end "host X unreachable" procedure spanning the source device,
  routing peer, policies, routes, firewalls and DNS (`11`).
- **Escalation** — when escalation is justified, severity classification, evidence
  collection, a verified redaction pass, and the support package the customer sends
  (`12`).
- **Rule authoring** — the AI-security rule-author reference (`aidr-rules.md`) and the
  gate-driven on-prem install runbook (`install-hosted-server.md`).
