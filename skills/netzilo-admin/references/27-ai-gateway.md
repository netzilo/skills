---
id: '27'
title: Admin Skill — The Netzilo AI Gateway (`netzilo-aigw`)
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 48705
sections:
- id: '1'
  title: How it works
  chars: 6791
- id: '2'
  title: Requirements
  chars: 1514
- id: '3'
  title: Install
  chars: 6060
- id: '4'
  title: '`netzilo-aigw run` — flag reference'
  chars: 4368
- id: '5'
  title: Exposing the gateway to callers
  chars: 4294
- id: '6'
  title: How a caller authenticates, and what it gets back
  chars: 6191
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '7'
  title: What the gateway pulls from management, and when
  chars: 1773
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '8'
  title: Usage telemetry
  chars: 2846
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '9'
  title: Operating it
  chars: 3702
- id: '10'
  title: Troubleshooting
  chars: 7040
- id: '11'
  title: Limits to state before a customer discovers them
  chars: 2265
---
# Admin Skill — The Netzilo AI Gateway (`netzilo-aigw`)

**Binary:** `netzilo-aigw` (Linux amd64, macOS amd64/arm64, Windows amd64; container image
`ghcr.io/netzilo/net-aigateway`). **Dashboard objects it enforces:** Edge → **Providers**,
**MCP**, **Guardrails**, **Limits**, **Filters** (gateway type). **Peer:** the gateway is an
ordinary peer of the account, named with `--name`. **Users reach it:** at Workplace →
**Agentic Access** (`47-agentic-access-workplace.md`).

The AI Gateway is the second place Netzilo governs AI traffic. The first is the Netzilo
client on a device (`10-ai-security-aidr.md`). The gateway sits in front of the LLM
providers and MCP servers an organisation allows, identifies every caller as a Netzilo
user, applies that user's **gateway filters** (model grants, MCP grants, limits,
guardrails) and records usage. Agents and tools (Claude Code, Cursor, Codex, an SDK, a
script) point at the gateway instead of at a provider, with the user's Netzilo token as
the API key; provider keys never leave the server.

Everything an agent calls goes through one process: a host peer (the gateway's own
WireGuard identity), an LLM/MCP upstream built into the binary, and the Netzilo plugin
between them. The upstream has no user interface of its own; the dashboard is the only
administration surface.

Related files: `45-ai-gateway-providers-and-limits.md` (what the gateway routes to and
how much a user may spend), `46-ai-gateway-mcp-servers-and-bundles.md` (MCP servers,
bundles, sign-ins), `29-edge-filters.md` (the gateway filter that grants all of it),
`28-edge-guardrails.md` (the rules it applies), `47-agentic-access-workplace.md` (what
users see and paste), `44-published-applications.md` §6 (the reverse proxy in front of
it), `30-activity-reports-and-integrations.md` (the Agentic Activity panel and the AI
Usage report).

---

## 1. How it works

```
agent / IDE / script  ──Authorization: Bearer <Netzilo token>──▶ AI door
                                                                  │ who is this user?
                                                                  │ which gateway filters target them?
                                                                  │ model granted? limits? guardrails
                                                                  ▼
                                                      built-in LLM/MCP upstream
                                                                  │ provider keys held on the server
                                                                  ▼
                                               OpenAI / Anthropic / Azure / … and MCP servers
```

**Two doors.** The gateway listens in two places:

| Door | Address | Who can reach it | How the caller is identified |
|---|---|---|---|
| **Tunnel door** | the gateway peer's own tunnel address, port `8447` (`--ai-tunnel-port`) | peers of the account that a **network policy** allows to reach the gateway peer on TCP 8447 | first by the **calling peer** (its tunnel address → peer → user), then by a bearer token if the request carries one |
| **Public door** | `--ai-listen` (for example `:8447` on the host) | anyone who can reach the host | by the bearer token only |

The tunnel door is always on in `netzilo-aigw` (the default `--ai-tunnel-port` is 8447;
`0` would disable it) and is plain HTTP inside the encrypted tunnel. The public door is
off until `--ai-listen` is given.

A published application in front of the gateway (§5.3) delivers requests through the
user's own reverse-proxy session onto the tunnel door, so that path needs no public door
and no certificate on the gateway host.

**What is governed, and where.** Per request the gateway resolves the user, loads the
gateway filters that target the user's groups (cached for `--ai-policy-refresh`,
60 s), and applies them:

1. **Model access** — the request's model must be granted by one of the user's gateway
   filters (`29-edge-filters.md` §2.2). A bare model name is routed to the granted
   provider that serves it; `provider/model` must be granted for that provider. Nothing
   granted, or an ungranted model, is refused with HTTP 400 (`type: netzilo_policy`;
   gateways before October 2026 answered 403).
2. **Limits** — spend, token and request quotas from the user's filters, enforced by the
   upstream's governance on a per-user virtual key; across filters the lowest limit of
   each kind applies. Exceeded limits answer 429 or 402.
3. **Guardrails** — the rules bound by the user's filters run on the prompt (block,
   redact, or route to another model), on the answer (block, redact), on each tool call
   the model asks for (block, redact arguments) and on each MCP tool call and result.
   A rule on a requested tool call sees the agent's name (`agent_name`) and, for a
   scripted judge, the conversation's first prompt and system prompt (`meta["task"]`,
   `meta["instructions"]`), so it can ask System One or an LLM whether the call serves
   the task (`32`, two-tier judging).
4. **Usage** — one record per model request and per MCP tool call: who, which model,
   tokens, cost, latency, status. Usage records carry no prompt, answer, argument or
   result text.
5. **Captured conversations** — the messages of each model call (system prompt, prompts,
   context, thinking, answers, tool calls and results) as the caller sent and received
   them, after the guardrails, sent separately from usage and shown to administrators in
   the session's trajectory (§8.1).

**Which API surfaces are governed.** This is the fact customers trip over, so say it
before they ask:

| Surface on the gateway | Model grant | Guardrails | Limits (virtual key) | Usage recorded |
|---|---|---|---|---|
| `/v1/chat/completions` (OpenAI chat shape; what most SDKs, Cursor, LangChain and the Workplace snippets use) | yes (400 with the reason) | yes — prompt, tool results, answer, tool calls | yes | yes |
| `/v1/responses` (OpenAI Responses API, Codex) | yes (400 with the reason) | yes — as chat | yes | yes |
| `/anthropic/v1/messages` (Anthropic Messages API, Claude Code, Claude Desktop) | yes; served as a Responses request | yes — as chat | yes | yes |
| `/v1/embeddings`, `/v1/completions` and other request types | only through the virtual key (the upstream's own refusal) | **no** — counted, not inspected | yes | yes |
| `/mcp/<slug>` (MCP servers and bundles) | the server and tool grants | yes — tool calls and results | yes | yes |
| `/v1/models` | lists what the user may use | — | — | no |

**Streamed answers are governed while they stream**, on the chat and Responses surfaces
alike: the answer text and each thinking block are held back about 1 KB behind the model
and released window by window, so a rule can **redact** a streamed answer, not only end
it. A tool call's arguments are held until the call is complete (on chat, at the
choice's finish) and judged then; a block ends the stream. When the answer ends it is
judged once more whole, and an answer a rule would still change is refused. Where no
bound rule judges answers or tool calls, nothing is held.

**Fail-open inside, strict at the door.** Netzilo's own authentication is never
relaxed: a caller the public door cannot identify gets 401 (unless
`--ai-allow-unattributed`). Once a request is inside, an engine or lookup error is an
allow, not a refusal. The one exception admins meet: a user whose filters could not be
fetched at all holds **no** grant and is refused "no model is granted to this user" until
the lookup succeeds (retried after 10 s).

**Sessions.** Requests are grouped per conversation when the caller sends
`x-claude-code-session-id`, `x-bf-session-id`, `x-bf-mcp-session-id`, `Mcp-Session-Id`, or
the OpenAI `user` field, or continues an earlier answer by its response id. Without any of
these (a model API call from a custom agent), calls that share the agent, system prompt and
first message are one conversation, and a call with nothing answered in it yet starts a new
session, so two runs of the same task are two sessions. Exact sessions: the agent sends its
own ID per task in `x-bf-session-id`. A call with no conversation at all joins the user's run
with that agent, which ends after 30 minutes of quiet. A session always belongs to the user
who made it.

**Which agent.** The agent is the name a Netzilo SDK agent carries in its User-Agent
(`NetziloAgent/<percent-encoded name>`, added by the embedded client; `10` §5), else the
client the User-Agent identifies (Claude Code, Claude Desktop, Codex, Cursor, GitHub
Copilot, the Anthropic and OpenAI SDKs, curl), else the User-Agent's product name.

---

## 2. Requirements

- A **setup key** (or a PAT) for the gateway's own peer, and a **service token**
  (`--service-pat`): a personal access token of a service user (Team → Agents) of the
  account, role **Admin**. The service token binds callers to that account, loads filters,
  providers and MCP servers, and ships usage and captured conversations. Without it the
  gateway refuses every chat request (no filters can be loaded) and cannot identify callers
  on the tunnel door. Management refuses usage and conversations (403) from a token
  without admin rights.
- The gateway peer must be reachable as a **destination**: a network policy from the
  users' device groups to the gateway peer's group on TCP 8447 for the tunnel door. The
  Default All↔All policy covers it; a hardened account needs an explicit rule.
- Outbound from the host: TCP 443 to management, signal and relay; HTTPS to the LLM
  providers and MCP servers the account defines (through the gateway peer's routes first,
  then the host network).
- One account per process. Several gateways in one account are fine; each has its own
  usage counters for limits (a limit is per user **per gateway**, not pooled).
- At least one **Provider** (`45` §1), one **gateway Filter** targeting a group with
  models granted (`29` §2.2), and the users in that group.

Plans: self-hosted servers run as Enterprise. On Netzilo Cloud the AI Edge pages are
available to the account; if a page shows an upgrade prompt, `31-plans-limits-and-billing.md`.

---

## 3. Install

### 3.1 Linux and macOS

Install, then start it as a service — the same two steps as a peer (`curl … | sh`, then
`netzilo up`):

```
curl -fsSL https://pkg.netzilo.com/download/linux/install_aig.sh | sh
sudo netzilo-aigw up --management-url https://srv.netzilo.com \
  --setup-key <SETUP-KEY> --service-pat <SERVICE-TOKEN> --ai-listen :8447
```

(the same script is published at `…/download/macos/install_aig.sh`). The script downloads
`https://pkg.netzilo.com/download/aigateway/<os>/<arch>/netzilo-aigw` into
`/usr/local/bin`, runs it once with `--version` and stops if the binary does not run on
the machine ("the downloaded binary does not run on this machine"), and on macOS removes
the quarantine attribute. Linux downloads are amd64 only ("Linux builds are amd64 only
for now").

**One step:** flags after `sh -s --` (or `NZ_GATEWAY_SETUP_KEY`, `NZ_GATEWAY_PAT`,
`NZ_GATEWAY_SERVICE_PAT` in the environment) make the script run `netzilo-aigw up` with
them: `curl -fsSL …/install_aig.sh | sh -s -- --management-url … --setup-key … --service-pat … --ai-listen :8447`.
Without them it prints the `up` command to run.

Environment overrides for the script: `AIG_INSTALL_DIR` (default `/usr/local/bin`),
`AIG_BASE_URL` (default `https://pkg.netzilo.com/download/aigateway`), `AIG_SOURCE` (a
local binary to install instead of downloading; any architecture), `AIG_NO_SERVICE=1`
(install the binary only).

**The service commands** (also in the plain `gateway` binary, as service `netzilo-gateway`):

| Command | Does | Exit |
|---|---|---|
| `sudo netzilo-aigw up [run flags]` | saves the flags (merged over the saved ones) to `/var/lib/netzilo-gateway/netzilo-aigw.json` (mode 0600; macOS `/Library/Application Support/Netzilo/gateway/`, Windows `%ProgramData%\Netzilo\gateway\`), installs or rewrites the service (systemd unit `netzilo-aigw.service`, `Restart=always`, `RestartSec=5`, enabled; launchd daemon with `RunAtLoad`/`KeepAlive`; Windows service restarting on failure), starts it, and waits up to `--wait` (90 s) for `/readyz` on the admin address, printing `mode`, `peer`, `sessions` | 0 connected; non-zero with the reason and the log command |
| `netzilo-aigw status` | service state plus `/readyz` | 0 ready, 1 running not connected, 3 stopped, 4 not installed |
| `sudo netzilo-aigw down` | stops it (starts again at boot) | |
| `sudo netzilo-aigw uninstall` | stops and removes the service; settings and the peer key stay, so a later `up` returns the same gateway | |

The service runs `netzilo-aigw run --config <settings file>`; a flag on that command line
wins over the file. Without `--data-dir` the gateway keeps its state in the default data
directory (`/var/lib/netzilo-gateway`), the same one a foreground `sudo netzilo-aigw run`
uses, so moving from a foreground run to the service keeps the peer. `up` without root
refuses: "up needs root: sudo netzilo-aigw up …". `--management-url` is required on the
first `up` ("--management-url is required").

**Change a setting:** `sudo netzilo-aigw up --<flag> <value>` (e.g. `--service-pat <new>`);
a bare `sudo netzilo-aigw up` restarts with what is saved. Logs: Linux
`journalctl -u netzilo-aigw`, macOS and Windows `netzilo-aigw.log` in the data directory.

**Earlier installs** (scripts before October 2026 wrote `/etc/systemd/system/netzilo-aigw.service`
reading `/etc/netzilo-aigw/aigw.env`, and never enabled it): the next `up`, or re-running
the script, replaces that unit, takes `AIG_ARGS` and the `NZ_GATEWAY_*` secrets from
`aigw.env` (flags given now win) and keeps `/var/lib/netzilo-aigw` as the data directory
when it holds state, so the gateway stays the same peer; it prints "Replaced the earlier
netzilo-aigw unit…". `aigw.env` is left in place, unused.

A foreground `sudo netzilo-aigw run …` (testing) ends with the SSH session; the service
does not. Never run both at once against the same data directory.

### 3.2 Windows

In an administrator PowerShell:

```
irm https://pkg.netzilo.com/download/windows/install_aig.ps1 | iex
netzilo-aigw up --management-url https://srv.netzilo.com --setup-key <SETUP-KEY> --service-pat <SERVICE-TOKEN> --ai-listen :8447
```

Installs `netzilo-aigw.exe` into `%ProgramFiles%\Netzilo AI Gateway` and adds it to the
machine PATH (`AIG_NO_PATH=1` to skip). `up` installs the `netzilo-aigw` Windows service
(restart on failure), as on Linux. One step: set `$env:AIG_UP_ARGS` to the `up` flags (and/or
the `NZ_GATEWAY_*` secrets) before the `irm … | iex`. Without administrator rights the
script installs into `%LOCALAPPDATA%\Programs\Netzilo AI Gateway` only and says the
service needs an administrator PowerShell. An upgrade stops the service (`down`), replaces
the binary and runs `up`.

### 3.3 Container

`ghcr.io/netzilo/net-aigateway` (`linux/amd64`; tags `<version>.<branch>-<sha>`, and
`:latest`), distroless, runs as user 65532, needs no TUN device and no capabilities,
volume `/var/lib/netzilo-gateway` for the peer key and state, `EXPOSE 8443 8447 9090`.
The image's default command is `run` with no flags, so the flags must be given; the admin
endpoint is on loopback unless `--admin-listen :9090` is passed:

```
docker run -d --name netzilo-aigw --restart unless-stopped \
  -p 8447:8447 -v netzilo-aigw:/var/lib/netzilo-gateway \
  -e NZ_GATEWAY_SETUP_KEY=<SETUP-KEY> -e NZ_GATEWAY_SERVICE_PAT=<SERVICE-TOKEN> \
  ghcr.io/netzilo/net-aigateway:latest run \
  --management-url https://srv.netzilo.com --workplace-url https://go.netzilo.com \
  --name aigw1 --listen 127.0.0.1:8443 --ai-listen :8447 --ai-insecure-plain-http
```

### 3.4 Upgrades

Re-run the install script (Linux/macOS/Windows) or pull a newer image tag. A gateway
service already set up (`status` exit 0, 1 or 3) is restarted on the new binary with its
saved settings (`up`). The data directory carries the peer key, so the gateway returns as
the same peer. The version a
server publishes is at `https://pkg.netzilo.com/download/aigateway/version.txt`
(`<version> <tag> <UTC time>`); `netzilo-aigw --version` prints the installed one.

---

## 4. `netzilo-aigw run` — flag reference

Global: `--log-level` (default `info`), `--log-file` (default `console` = stdout, hence
`journalctl` under systemd). Secrets may come from the environment instead of flags:
`NZ_GATEWAY_SETUP_KEY`, `NZ_GATEWAY_PAT`, `NZ_GATEWAY_SERVICE_PAT` (used only when the flag
is empty).

| Flag | Default | Meaning |
|---|---|---|
| `--management-url` | required | `https://srv.netzilo.com` on Cloud; `https://<domain>` self-hosted. Scheme and host only |
| `--setup-key` / `--pat` | | credential for the gateway's **own** peer; one or the other, never both ("give either a setup key or a PAT for the gateway peer, not both") |
| `--service-pat` | | service-account token that binds callers to this account and loads policy; required unless `--allow-any-account` ("a service PAT is required to bind callers to the gateway's account") |
| `--allow-any-account` | off | let any user of the management server call; without a service PAT the gateway still loads no filters, so chat is refused — not a usable AI-gateway mode |
| `--name` | host name | the gateway peer's name, shown in Peers and in usage (`gateway` column) |
| `--data-dir` | `/var/lib/netzilo-gateway`, `/Library/Application Support/Netzilo/gateway`, `%PROGRAMDATA%\Netzilo\gateway`; the user's config directory when that is not writable | peer key, applied-state file, usage outbox, the upstream's own data under `aigw/` |
| `--ai-data-dir` | `<data-dir>/aigw` | the built-in upstream's configuration and stores |
| `--ai-upstream-log-level` | `warn` | the upstream's own log verbosity |
| `--ai-tunnel-port` | `8447` | tunnel door on the peer's tunnel address; `0` disables |
| `--ai-listen` | off | public door, e.g. `:8447` |
| `--tls-cert` / `--tls-key` | | PEM certificate and key, given together; serve HTTPS on `--listen`, `--ai-listen` and (with `--publish-tls file`) the publish door |
| `--tls-cert-dir` / `--tls-domain` | | take the certificate for `--tls-domain` from a Caddy storage directory, renewals picked up; given together, not with `--tls-cert` |
| `--ai-insecure-plain-http` | off | silence the warning about a plain-HTTP public AI door |
| `--ai-trusted-proxies` | | CIDRs of a TLS-terminating proxy in front of `--ai-listen`; their `X-Forwarded-For`/`-Proto`/`-Host` are believed (also silences the plain-HTTP warning) |
| `--ai-allow-unattributed` | off | public door: pass requests with no identifiable user through ungoverned instead of 401 |
| `--ai-policy-refresh` | `60s` | how long a user's filters are trusted before management is asked again; also the provider and MCP reconcile interval. A policy change reaches the gateway with its next network-map sync and re-checks everyone at once |
| `--workplace-url` | `--management-url` | the Workplace users sign in at (`https://go.netzilo.com` on Cloud): the browser origin allowed to call the gateway (the Workplace's gateway cards probe it), the MCP connect link in refusals, the sign-in for published applications. **Set it on Cloud**, where the Workplace host differs from the management host |
| `--listen` | `:8443` | the browser-access proxy of `43-clientless-access-gateway.md`; always opened, cannot be disabled; bind to `127.0.0.1:8443` when only the AI gateway is wanted |
| `--insecure-plain-http` | off | silence the plain-HTTP warning for `--listen` |
| `--max-connections` | 20000 | accepted connections on each listener |
| `--admin-listen` | `127.0.0.1:9090` | `/healthz`, `/readyz`; empty disables |
| `--egress` / `--egress-allow` | `public` / | where outbound connections may go beyond the tunnel: `public` = the gateway peer's routes, then the host network (private ranges only when listed in `--egress-allow`); `off` = routes only |
| `--ai-upstream` | | only for the plain `gateway` binary: the URL of an LLM/MCP gateway beside it; `netzilo-aigw` has one built in |
| `--publish-listen`, `--publish-http`, `--publish-tls`, `--publish-acme-*`, `--publish-session-max-age`, `--publish-trusted-proxies`, `--revalidate` | | the reverse proxy for published applications, `44-published-applications.md` §9; `--revalidate` (10 m) is also how often a published session re-checks its admission |
| `--idle-timeout`, `--rechallenge`, `--max-sessions`, `--max-devices-per-user`, `--start-concurrency`, `--ready-timeout`, `--login-timeout` | | browser-session tuning, `43` §9 |

---

## 5. Exposing the gateway to callers

### 5.1 Plain HTTP or TLS

The gateway does not refuse to start without a certificate. On a public address without
one it logs a warning per listener and serves plain HTTP; `--insecure-plain-http` and
`--ai-insecure-plain-http` silence the warnings (a second, unconditional line
`gateway: proxy on :8443 without TLS: callers' credentials travel in clear` remains; it
is informational). The installer's defaults are plain HTTP because the common
deployments are a private network, a host behind a TLS-terminating proxy, or the tunnel.

Where callers reach the public door across the Internet, give it a certificate
(`--tls-cert`/`--tls-key`, or `--tls-cert-dir`/`--tls-domain` from a Caddy on the host) or
put a TLS proxy in front and name it in `--ai-trusted-proxies`. The bearer token in every
request is the user's Netzilo credential; on plain HTTP it travels in clear.

### 5.2 Inside the network (tunnel door)

Devices with the Netzilo client reach `http://<gateway-name>.netzilo.network:8447` (or
the peer's `100.x` address) without any certificate, under network policies. The caller
is identified by its peer, so even a client that sends no token is attributed to the
device's user; a token, when sent, must belong to the same account. This is also how a
published application reaches the gateway.

### 5.3 From anywhere, through a published application

The recommended public exposure on Cloud and on self-hosted servers with the reverse
proxy (`44-published-applications.md`):

1. Network → **Applications** → publish: name, address `aigw.<application-domain>`, target
   `http://<gateway-name>.netzilo.network:8447` (the port is required; without it the
   proxy dials port 80 and answers 502 "The application did not answer."), groups of the
   users, **Forward the user's credential** on. Preserve host off.
2. Users call `https://aigw.<application-domain>/v1/chat/completions` with
   `Authorization: Bearer <Netzilo token>`; the reverse proxy admits the token as an API
   session, forwards it to the gateway through the user's own `vp-<n>-RPROXY` tunnel, and
   the gateway identifies the user from it.
3. Put the same address in the gateway filter's **Gateways** list so the Workplace shows
   it (`29` §2.2, `47`).

**Sign-in through the published address.** The reverse proxy answers, on the published
hostname, the sign-in metadata (`https://aigw.<application-domain>/.well-known/oauth-authorization-server`,
and the same under `/anthropic` for Claude Desktop) and the endpoints under
`/.netzilo/oauth2/`, so MCP connectors and Claude Desktop's **Sign in with your
organization** (§6) work through it without a public door. It needs the reverse proxy's
`--workplace-url` (the installers and the Kubernetes chart set it): the sign-in page is a
redirect to `<workplace>/api/mcp/oauth2/…`, so the Workplace host must route `/api/*` to
management (the installers do; `44` §8). Claude Desktop's endpoint is then
`https://aigw.<application-domain>/anthropic`.

A change to the application (target, groups, enabled) reaches running sessions within
about 40 s: the reverse proxy asks management every 10 s whether the application changed
and makes affected sessions re-check on their next request (log: `gateway: application at
<host> changed: N session(s) will ask again`); a session is in any case re-admitted every
`--revalidate` (10 m). Older reverse proxies without the watcher keep a stale target for
up to 10 minutes.

Errors from the reverse proxy on this path: 404 `There is no application at this
address.` (not published, disabled, or not yet known: the name cache refreshes within
30 s), 502 `The application did not answer.` (wrong target port, gateway down, or the
user's device groups have no policy to the gateway peer), 504 `The application took too
long to answer.`, 401 `credential refused`, 403 `not allowed to open this application`
(the user is not in the application's groups). A failed **POST** gets an HTML error
page instead of JSON; test with `GET /v1/models` first.

### 5.4 Direct public door

`--ai-listen :8447` on a host with a public address, TLS as in §5.1, firewall open on
8447. Callers use `https://<host>:8447`. Every caller must present a bearer token; the
public door never identifies by address.

---

## 6. How a caller authenticates, and what it gets back

| Header | Accepted values |
|---|---|
| `Authorization: Bearer <token>` | a user's **personal access token** (`nzl_…`), the signed-in user's identity-provider token (what the Workplace holds), or the token a client obtained by **signing in at the gateway** — an MCP connector by authorization code, Claude Desktop or another device client by device authorization (below; `46` §6) |

The token is checked against management (`GET /api/users` as that token; the entry marked
current is the caller) and cached 60 s (10 s for a refused one; never past a token's
expiry). The gateway's own secret and the caller's token are removed before the request
reaches the upstream; the upstream only ever sees `X-Netzilo-User-*` headers the gateway
sets itself. Anything a caller sends as `X-Netzilo-*`, `Nz-*`, `X-Forwarded-*`,
`Forwarded`, `X-Real-IP`, `X-Request-Id` or `x-bf-*` is dropped, except
`x-bf-mcp-include-clients`, `x-bf-mcp-include-tools`, `x-bf-session-id` and
`x-bf-mcp-session-id`, which narrow a request and are allowed through.

A token of another account on the same management server is refused as unknown
("not a user of the gateway's account"). A revoked token can be honoured for up to a
minute at the door (the cache); management refuses it at once.

**Signing in at the gateway.** A client that cannot carry a token of its own signs in at
the gateway and receives one; management is the authorization server behind the door.
Two flows exist:

| Flow | Clients | How it goes |
|---|---|---|
| **Authorization code** (OAuth 2.1, PKCE) | MCP connectors: Claude Desktop custom connector, claude.ai connector, IDEs | the client registers itself, the browser opens the consent page, Allow sends the browser back to the client with the code (`46` §6.1) |
| **Device authorization** (RFC 8628) | Claude Desktop in gateway mode (**Sign in with your organization**) and other device clients | the client asks for a device code and a user code, shows the user the code and the verification link, and polls for the token; nothing returns through the browser (`46` §6.2) |

Both doors, and the published address (§5.3), serve the authorization-server metadata on
**their own origin**: `GET <gateway>/.well-known/oauth-authorization-server` and, for
Claude Desktop, `GET <gateway>/anthropic/.well-known/oauth-authorization-server`. The
sign-in exists only at the root and under `/anthropic`; `/v1` and `/openai` take tokens
only. The metadata document is authoritative for what a gateway serves — read it before
telling a customer which endpoint exists. A current gateway lists the issuer (the
gateway's origin) and, under `<gateway>/.netzilo/oauth2/`, `authorize`, `token`,
`register`, `revoke`, `device` and a `verify` page, all on that origin: the sign-in and
verification pages are redirects to management (the Workplace host for a published
address), the token, registration, revocation and device calls are forwarded. Claude
requires the issuer, token and device endpoints to be on the same origin as the endpoint
it was given, which is why the gateway serves them itself.

What either flow yields is the user's **own personal access token**, named `<app> (MCP)`
(`Claude (MCP)`), scope `mcp`, valid **1 day**, with a refresh token valid **30 days**
(each refresh rotates both). The user sees it under Profile Settings → **Access Tokens**
and can revoke it there; the app then has to sign in again.

**Refusals, in the order a caller can meet them:**

| HTTP | Body | Cause and fix |
|---|---|---|
| 401 `a Netzilo credential is required` (with `WWW-Authenticate: Bearer realm="netzilo", resource_metadata=…`) | `{"error":{"message":…,"type":"netzilo_gateway"}}` | no token, a malformed token, a token of another account, or an expired one, on the public door. The same body on the tunnel door never appears: there an unidentified caller passes through ungoverned |
| 503 `management is not reachable, try again` (`Retry-After: 5`) | same shape | the gateway could not ask management who the token belongs to; nothing is cached about it |
| 404 `not served by the AI gateway` | same shape | the upstream's own admin or UI paths (`/`, `/api/…`, `/ui`): the gateway never forwards them |
| 405 `Method Not Allowed` on `POST /v1/messages` | — | the Anthropic Messages API is served under `/anthropic`; the caller's base address lacks it (Claude Desktop endpoint, `ANTHROPIC_BASE_URL`) → `<gateway>/anthropic` |
| 502 `the AI gateway upstream is not reachable` | same shape | the built-in upstream is down; the process will have logged why |
| 400, `type: netzilo_policy`, message `no model is granted to this user` / `none of this user's filters grants a model` / `model <m> is not granted to this user` / `model <provider>/<m> is not granted to this user` | the error envelope of the API surface called | no gateway filter grants the user that model (`29` §2.2); also what a user gets while their filters cannot be fetched |
| 400 `type: netzilo_policy`, a guardrail's reason (default `blocked by Netzilo policy`) | same; a block in the middle of a streamed answer ends the stream with this error | a guardrail blocked the prompt, the answer, a requested tool call, an MCP tool call or an MCP result; the event names the rule. A scripted (`execute`) rule's message is the `reason` its script returned — for a judge rule, the judge's own explanation — and a script that failed under `on_error: block` reads `execute script failed (rule <id>): <error>`. Policy refusals are 400, not 401/403, so that clients do not read them as a credential failure; gateways before October 2026 answered 403 |
| 429 / 402 | the upstream's governance error (`budget_exceeded`, `rate_limited`, `token_limited`, `request_limited`) | a limit from the user's filters is exhausted for its window; recorded with status `limited` |
| MCP tool answer `Connect <server> in your Workplace before using its tools: <workplace>/workplace?connect=<server>#gateways` | tool result text | the server needs the user's own sign-in or header values and the user has not connected it (`46` §4) |

Fallback providers are never used to get around a policy refusal.

---

## 7. What the gateway pulls from management, and when

All with the service token:

| Call | When | Purpose |
|---|---|---|
| `GET /api/users` | at start ("bound to an account with N users"), then every 60 s and on demand | which users belong to the account; who a token is |
| `GET /api/peers` | when a tunnel-door caller is seen | which peer and user a tunnel address belongs to |
| `GET /api/edge/filters/effective?type=gateway&user=…` and `GET /api/edge/filters/{id}/expanded` | per user, on first request, then every `--ai-policy-refresh`; everyone re-checked on a policy change | the user's gateway filters, with guardrails inline; only changed filter versions are fetched |
| `GET /api/ai-gateway/providers` | at start, every `--ai-policy-refresh`, on policy change | providers with their enabled models and keys; applied to the upstream |
| `GET /api/ai-gateway/mcp`, `GET /api/ai-gateway/mcp-credentials` | same schedule | MCP servers, bundles and the users' stored sign-ins and header values |
| `POST /api/ai-gateway/usage` | every 15 s, or when 1000 records are waiting | usage facts (§8) |
| `POST /api/edge/events` | on a refused credential | the **Credential refused at gateway** activity |

What was applied to the upstream is remembered in `<data-dir>/ai-applied.json` so a
restart leaves an unchanged upstream and every user's spend counters alone. A provider
that changes is removed and re-added; the first provider of a type keeps the type's own
name in the upstream, further ones become `nz-<id>`; keyless types (`ollama`, `vllm`,
`sgl`) get no key. Each user gets one virtual key (`netzilo:user:<id>`) carrying their
grants, MCP servers and the combined limits; it is replaced when any of those change,
which **restarts that user's counters**.

---

## 8. Usage telemetry

One record per model request (user, gateway name, provider, model asked for and model
served, streamed or not, status `ok`/`error`/`blocked`/`limited`, tokens by kind, cost in
US dollars from the upstream's pricing catalogue, latency, the tool calls the answer asked
for) and one per MCP tool call (server, tool, status `ok`/`error`/`blocked`/`redacted`/
`limited`, latency, argument and result sizes). No prompt, answer, argument or result
content is included.

Records are buffered (cap 50 000; the oldest are dropped past that), posted every 15 s in
batches of 1000 (gzip) to `POST /api/ai-gateway/usage`, kept on disk in
`<data-dir>/ai-usage-outbox.json` across a failed upload or a restart (`gateway ai:
usage: N record(s) recovered from the outbox`), and deduplicated by request id on the
server, so a retried batch never double-counts. A batch the server rejects as malformed
(a 4xx other than 401, 403, 408, 429) is dropped with `gateway ai: usage: N record(s)
dropped: …`; an outage keeps them (`… kept, upload failed: …`). Successful uploads are
logged at debug level only.

Management keeps them as long as the server's AI data retention says (Netzilo Cloud: raw
records 90 days, hourly totals 400 days; self-hosted: the `ai-retention` job,
`02-server-operations.md` §AI data retention). They feed the home page's Agentic Activity
panel (built hourly) and Tokens tile, the Agentic Activity window (built every 15 minutes;
**Refresh** builds both at once), and the **AI Usage** report, which reads them live
(`30-activity-reports-and-integrations.md` §2–3).

### 8.1 Captured conversations

For each model call the gateway also sends the messages the call added to its session —
system prompt, the user's prompts, the agent's context, thinking, answers, tool calls with
their arguments and results — as the caller sent and received them **after the
guardrails**: what a guardrail redacted arrives redacted, and a tool call the guardrails
held back or refused is not sent at all. A message is cut past 32 KB. A message a session
already sent is not sent again with the next call. A refused tool call still appears in the
Trajectory, from its verdict: a row with the tool's name, **Blocked**, the rule and the
reason the rule gave, without the arguments the conversation never carried.

They go to `POST /api/ai-gateway/content` in batches of at most 2 MB and 1 000 calls, and
are held **in memory only**, never on disk: up to 64 MB wait during an outage (the oldest
go first, `gateway ai: content: N call(s) dropped, the buffer is full`), and those waiting
when the gateway stops are lost. Capture is always on. Management stores each text once,
shows it only to administrators, in the session's **Trajectory** in the Agentic Activity
window (`30` §3), and deletes it with the rest of the AI data (`14` §8).

---

## 9. Operating it

### 9.1 Health

`GET http://127.0.0.1:9090/healthz` → `ok` plus `mode=`, `peer=`, `sessions=`.
`GET /readyz` → `ready`, or 503 with `draining`, `gateway peer disconnected from
management`, `management unreachable`, `session limit reached`, `no TLS certificate yet`.
`/readyz` does not reflect the built-in upstream; a 502 at the AI door with a ready
gateway means the upstream failed (§10). The upstream's own `GET /health` is forwarded by
the AI door.

### 9.2 Logs

`journalctl -u netzilo-aigw` (the binary logs to stdout). Lines an admin should recognise:

| Line | Meaning |
|---|---|
| `gateway: data directory <dir>` | which state is in use |
| `gateway: version <v> starting in node mode (management <url>, egress public)` | start |
| `gateway: bound to an account with N users` | the service token resolved the account |
| `gateway: peer <name> connected (…)` | the gateway peer logged in |
| `aigw: agent gateway netzilo-aigw serving on http://127.0.0.1:<port> (data <dir>)` | the built-in upstream is up |
| `aigw: the agent gateway did not become healthy in 15s` | it is not; the process exits |
| `gateway ai: listening on tunnel <ip>:8447 (inside the tunnel, plain) → …` / `gateway ai: listening on http://[::]:8447 → …` | the doors |
| `gateway ai: listener on :8447 serves plain HTTP: callers' tokens travel unencrypted (…)` | no certificate on a public door (§5.1) |
| `gateway ai: no --service-pat: no rules will be loaded and callers on the tunnel cannot be identified` | misconfiguration; chat will be refused |
| `gateway ai: policy ai-<hash>: N user(s) cached, N filter(s) held, N rule(s) loaded, N failed` | filters and guardrails loaded; `failed` names rules that did not parse (fix the guardrail's YAML) |
| `gateway ai: filters for user <id> peer <id>: […]` | which filters a user got |
| `gateway ai: providers <hash>: N provider(s) from management` / `… applied to the upstream as <name> (N model(s))` | provider sync |
| `gateway ai: mcp <hash>: N server(s), N virtual MCP(s) from management` / `… applied to the upstream as /mcp/<slug> (<auth>, generation N)` / `… credential of <user> for /mcp/<slug> written to the upstream` / `… waits for a credential before it can be created` | MCP sync; the last line is normal for a per-user server nobody has connected yet |
| `gateway ai: refused <model> for <user>: <reason>` | a model-access or limit refusal |
| `gateway ai: cannot identify <addr>: <err>` / `… unattributed request from <addr> refused (N so far)` / `… passed through …` | identity at the door |
| `gateway: credential refused at ai <host> for <ip>: <reason>` | a refused bearer (also an activity event) |
| `gateway ai: usage: …` | §8 |
| `gateway: no data dir: the peer key is not persisted, every start registers a new peer` | the data directory is unusable: fix it, or every restart creates a new peer |
| `gateway ai: N request(s) passed through unattributed` | at shutdown |

### 9.3 The gateway peer

It appears under Endpoint → Peers with its `--name`, version and connection state, in the
groups its setup key assigns. If management deletes the peer the process exits so the
service manager restarts it and re-registers (a **new** peer: re-add groups). Two gateways
with the same `--name` are two peers with one name; tell them apart by id.

### 9.4 Rotating the service token

Create a new token for the service user, run `sudo netzilo-aigw up --service-pat <new>`
(it saves the token and restarts the service), then revoke the old token. A restart keeps what was applied to the upstream (providers, keys,
each user's virtual key, in `ai-applied.json`), so users' spend counters survive; filters
and users are fetched afresh.

---

## 10. Troubleshooting

| Symptom | Check | Fix |
|---|---|---|
| Service exits at once, `a service PAT is required…` / `ai mode needs a peer of its own` / `give either a setup key or a PAT` | the saved settings (`netzilo-aigw.json`) | `sudo netzilo-aigw up --service-pat <token> --setup-key <key>` (exactly one of `--setup-key`/`--pat`) |
| `up` ends "running but not connected after 1m30s: <reason>" | the gateway started but `/readyz` never answered 200 (management unreachable, a refused setup key or token) | read the log line it prints (`journalctl -u netzilo-aigw -n 50`), fix the flag with `up --<flag> …` |
| Gateway gone after the SSH session ends | it was started with `run` in the foreground | `sudo netzilo-aigw up` (same flags) installs and starts the service |
| `management-url: not an absolute URL` | the flag | scheme and host only, no path |
| Exits after `aigw: the agent gateway did not become healthy in 15s` | `--ai-data-dir` writable? disk? `--ai-upstream-log-level debug` for the upstream's own error | fix the data directory; escalate with the log if it repeats |
| Workplace card shows the gateway **offline** although `curl` works | the browser's call is refused for its origin: `--workplace-url` missing or wrong (Cloud: `https://go.netzilo.com`) | set `--workplace-url`, restart; the card recovers at its next probe (30 s) |
| 401 `a Netzilo credential is required` from a valid token | token of another account; token expired; typed with a space | `curl -s -o /dev/null -w '%{http_code}' https://<mgmt>/api/users -H "Authorization: Token <t>"` → 200 proves the token; then check the account |
| 400 `no model is granted to this user` / `none of this user's filters grants a model` | the user is in no group an enabled **gateway** filter targets (first text), or the filters that match grant no enabled model (second text: the provider or model was disabled, or the filter was saved without models by an older server) | `GET /api/edge/filters/effective?type=gateway&user=<id>` with an admin token lists what applies; fix the filter (`29` §2.2) |
| 400 `model X is not granted to this user` | the filter grants other models/providers | grant the model (or `provider/*`), or tell the user which models `GET /v1/models` lists for them |
| Every request refused (400 `no model is granted…`) for everyone after a policy change | the filters failed to load (`N failed` in the policy line is about guardrails; a fetch failure shows as `gateway ai: cannot …`) | management reachable from the host? service token still valid (401 in the log)? |
| 429 / 402 before any real use | a limit's window and counters | `45` §3; counters restart when grants or limits change |
| Guardrail does not fire for a user | the request went to `/v1/embeddings`, `/v1/completions` or another surface guardrails do not inspect (§1); or the rule is not bound by one of the user's gateway filters; or it needs an endpoint-only context (process, file) | check which path the client calls; `GET /api/edge/filters/effective?type=gateway&user=<id>`; test the rule in report mode through the gateway (`28` §4) |
| MCP tool answers `Connect <server> in your Workplace…` | the user has no sign-in/header values for that server | `46` §4 and `47` §3 |
| `Tool execution failed: Blocked by rule: <name>` | a guardrail on the tool result or arguments | expected; the event names the rule |
| Claude Desktop: `gateway SSO discovery failed: 401` | the endpoint in Claude is `<gateway>/v1`, `<gateway>/openai` or another path: no sign-in is served there (the bare `<gateway>` signs in but then fails with 405 on `/v1/messages`) | set the endpoint to exactly `<gateway>/anthropic` |
| Claude Desktop: `Gateway returned HTTP 405 … /v1/messages` | the endpoint lacks `/anthropic` (Claude probes `/v1/models` and `/v1/messages` relative to its endpoint) | same |
| Claude Desktop: `gateway SSO metadata invalid: token_endpoint: must be same-origin as inferenceGatewayBaseUrl` | the gateway (or the reverse proxy in front of a published address) is older than the gateway sign-in: its metadata pointed at management | upgrade the gateway (§3.4) or the reverse proxy (`44` §10.4) |
| Claude Desktop: `gateway SSO: server does not advertise device_authorization_endpoint` | `GET <gateway>/anthropic/.well-known/oauth-authorization-server` has no `device_authorization_endpoint`: gateway or management too old | upgrade; re-read the metadata |
| Claude Desktop: `gateway SSO device init failed: HTTP 400` | management is older than the device sign-in (it required a client id) | upgrade management |
| Consent page: "That code was not found or has expired. Check it and try again." | mistyped code (letters only, `XXXX-XXXX`), or more than 10 minutes since Claude showed it | retype; after 10 minutes start the sign-in again in Claude |
| **Allow** pressed, Claude keeps waiting | Claude polls every 5 s and must collect the token within 5 minutes of Allow; a management restart or another replica (§11) lost the pending sign-in | wait a few seconds; else sign in again; single replica or session affinity |
| 429 `too many sign-ins from this address; try again later` | 30 device sign-in starts per address in 10 minutes (a shared egress address counts as one) | wait for the window |
| Through a published application: 502 `The application did not answer.` | target without `:8447`; gateway down; no policy from the user's device groups to the gateway peer; the proxy still on a stale target (≤10 min on old proxies) | fix the target; `44` §11 |
| Through a published application: 404 `There is no application at this address.` | application disabled or unpublished; name cache up to 30 s old | enable; wait; `44` §11 |
| Usage never appears on the dashboard | `gateway ai: usage: … kept, upload failed` (management unreachable or token refused; a 403 means the service token lacks the Admin role) or `… dropped` (server rejected the batch); the panel is built hourly and the window every 15 minutes | fix the cause; click **Refresh** on Agentic Activity; the AI Usage report reads the same data at once |
| A session shows no messages, or **Content not captured for this call** | the call did not go through the gateway; the gateway restarted or its content buffer overflowed before shipping (`gateway ai: content: …` lines) | nothing to recover for those calls; keep the gateway up and management reachable |
| Every restart creates a new peer | `gateway: no data dir: …` | make `--data-dir` writable by the service user, or set it |
| Upstream providers show in the upstream but not the ones defined | the gateway is the only writer: hand-made upstream providers of a type management defines are replaced | define providers in the dashboard only |

**Before escalating** (`12-escalation-package.md`): the exact `run` flags with secrets
removed, `journalctl -u netzilo-aigw --since "-1h"`, the failing request's status and body
(no token), the user's `GET /api/edge/filters/effective?type=gateway&user=<id>` as an
admin, and `netzilo-aigw --version`.

---

## 11. Limits to state before a customer discovers them

- **Governance is per API surface** (§1): model grants and guardrails cover the OpenAI
  chat surface, the Responses API and the Anthropic Messages surface (Claude Code, Claude
  Desktop); embeddings, text completions and other request types are identified, limited
  by the virtual key and recorded, not inspected.
- **Streamed answers arrive held back.** Text and thinking are released about 1 KB behind
  the model so that a match can be redacted; a streamed tool call's arguments arrive once
  the call is judged. Users see a short delay on long answers.
- **A limit is per user per gateway.** Two gateways in one account count separately; a
  group pool shared by users does not exist. Changing a user's grants or limits restarts
  their counters.
- **A revoked token works for up to a minute** at the door; management refuses it
  immediately, so the window is the gateway's cache only.
- **Sign-ins at the gateway live in one management process** for 10 minutes — connector
  and device sign-ins alike: several management replicas need session affinity, and a
  management restart drops sign-ins mid-flight (the user starts again).
- **The device sign-in exists only under `/anthropic`.** Claude Desktop's endpoint must be
  exactly `<gateway>/anthropic`; `/v1` and `/openai` are token-only surfaces.
- **A token from a gateway sign-in lasts 1 day** (refresh token 30 days, rotated on each
  refresh), unlike the 90-day Workplace token; a revoked one makes the app sign in again.
- **Per address:** 30 device sign-in starts and 20 client registrations per 10 minutes;
  a sign-in must be approved within 10 minutes and collected within 5 minutes of Allow.
- **The tunnel door governs by peer.** A request from a peer the gateway cannot map to a
  user passes through ungoverned (counted and logged). Keep the gateway peer reachable
  only from groups that should use it.
- **No Windows service, no Linux arm64 build** today.
- **The browser-access proxy on `:8443` is always on.** Bind it to loopback when it is
  not wanted.
- **Content never leaves the gateway through telemetry**; detections (events with a rule
  name and a short excerpt) do, as on devices — `14-data-handling-and-privacy.md` §3.
