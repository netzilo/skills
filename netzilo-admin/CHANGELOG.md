# Changelog — netzilo-admin

Versioning: **MAJOR** for a restructure that changes how the skill is loaded or where
files live, **MINOR** for new runbooks or substantive new procedures, **PATCH** for
corrections, clarifications, and command fixes.

An agent reading this to decide whether an update matters: scan the entries newer than
your installed version and look for the area you are working in.

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
