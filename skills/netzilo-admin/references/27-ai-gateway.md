---
id: '27'
title: Admin Skill — The Netzilo AI Gateway (`netzilo-aigw`)
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 35633
sections:
- id: '1'
  title: How it works
  chars: 4693
- id: '2'
  title: Requirements
  chars: 1399
- id: '3'
  title: Install
  chars: 4467
- id: '4'
  title: '`netzilo-aigw run` — flag reference'
  chars: 4368
- id: '5'
  title: Exposing the gateway to callers
  chars: 3553
- id: '6'
  title: How a caller authenticates, and what it gets back
  chars: 3271
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
  chars: 1330
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '9'
  title: Operating it
  chars: 3651
- id: '10'
  title: Troubleshooting
  chars: 3838
- id: '11'
  title: Limits to state before a customer discovers them
  chars: 1429
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
   granted, or an ungranted model, is refused with HTTP 403.
2. **Limits** — spend, token and request quotas from the user's filters, enforced by the
   upstream's governance on a per-user virtual key; across filters the lowest limit of
   each kind applies. Exceeded limits answer 429 or 402.
3. **Guardrails** — the rules bound by the user's filters run on the prompt (block,
   redact, or route to another model), on the answer (block, redact), on each tool call
   the model asks for (block, redact arguments) and on each MCP tool call and result.
4. **Usage** — one record per model request and per MCP tool call: who, which model,
   tokens, cost, latency, status. Never the prompt, answer, arguments or results.

**Which API surfaces are governed.** This is the fact customers trip over, so say it
before they ask:

| Surface on the gateway | Model grant and guardrails | Limits (virtual key) | Usage recorded |
|---|---|---|---|
| `/v1/chat/completions` (OpenAI chat shape; what most SDKs, Cursor, LangChain and the Workplace snippets use) | yes | yes | yes |
| `/v1/responses` (OpenAI Responses API, Codex) | **no** — recorded only | yes | yes |
| `/anthropic/v1/messages` (Anthropic Messages API, Claude Code) | **no** — recorded only; served as a Responses request | yes | yes |
| `/v1/embeddings`, `/v1/completions` | no — recorded only | yes | yes |
| `/mcp/<slug>` (MCP servers and bundles) | yes — tool calls and results | yes | yes |
| `/v1/models` | lists what the user may use | — | no |

So a Claude Code user is identified, limited and counted, but a guardrail that blocks a
prompt applies to them only through the OpenAI chat surface. Streamed chat answers are
evaluated once, on the final chunk: a block ends the stream; a redaction cannot be
applied to a stream.

**Fail-open inside, strict at the door.** Netzilo's own authentication is never
relaxed: a caller the public door cannot identify gets 401 (unless
`--ai-allow-unattributed`). Once a request is inside, an engine or lookup error is an
allow, not a refusal. The one exception admins meet: a user whose filters could not be
fetched at all holds **no** grant and is refused "no model is granted to this user" until
the lookup succeeds (retried after 10 s).

**Sessions.** Requests are grouped per user (`guest/<user>`), or per conversation when the
caller sends `x-bf-session-id`, `x-bf-mcp-session-id`, `Mcp-Session-Id`, or the OpenAI
`user` field.

---

## 2. Requirements

- A **setup key** (or a PAT) for the gateway's own peer, and a **service token**
  (`--service-pat`): a personal access token of a service user (Team → Agents) of the
  account, role **Admin**. The service token binds callers to that account, loads filters,
  providers and MCP servers, and ships usage. Without it the gateway refuses every chat
  request (no filters can be loaded) and cannot identify callers on the tunnel door.
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

```
curl -fsSL https://pkg.netzilo.com/download/linux/install_aig.sh | sh
```

(the same script is published at `…/download/macos/install_aig.sh`). It downloads
`https://pkg.netzilo.com/download/aigateway/<os>/<arch>/netzilo-aigw` into
`/usr/local/bin`, runs it once with `--version` and stops if the binary does not run on
the machine ("the downloaded binary does not run on this machine"), and on macOS removes
the quarantine attribute. Linux is amd64 only ("Linux builds are amd64 only for now").

Environment overrides for the script: `AIG_INSTALL_DIR` (default `/usr/local/bin`),
`AIG_BASE_URL` (default `https://pkg.netzilo.com/download/aigateway`), `AIG_SOURCE` (a
local binary to install instead of downloading), `AIG_NO_SERVICE=1` (Linux: no systemd
unit).

**Linux service.** With systemd and root (or sudo) the script writes:

- `/etc/systemd/system/netzilo-aigw.service` — runs
  `/usr/local/bin/netzilo-aigw run --data-dir /var/lib/netzilo-aigw $AIG_ARGS` as root,
  `Restart=always`, `RestartSec=5`. The unit is written but **not enabled**.
- `/etc/netzilo-aigw/aigw.env` (mode 0600, created once, never overwritten by a later
  install):

  ```
  AIG_ARGS=--management-url https://srv.netzilo.com --workplace-url https://go.netzilo.com --listen :8443 --insecure-plain-http --ai-listen :8447 --ai-insecure-plain-http
  #NZ_GATEWAY_SETUP_KEY=
  #NZ_GATEWAY_PAT=
  #NZ_GATEWAY_SERVICE_PAT=
  ```

  All flags go on the one `AIG_ARGS` line (one flag per line is not supported); the
  secrets go in the three variables or into `AIG_ARGS` as `--setup-key` /
  `--service-pat`. The defaults serve plain HTTP on both listeners (§5.1); a
  self-hosted server replaces the two URLs with its own.

Then:

```
sudo editor /etc/netzilo-aigw/aigw.env        # URLs, NZ_GATEWAY_SETUP_KEY, NZ_GATEWAY_SERVICE_PAT
sudo systemctl enable --now netzilo-aigw
sudo systemctl status netzilo-aigw --no-pager
sudo journalctl -u netzilo-aigw -f
```

Re-running the install script upgrades the binary in place: an active `netzilo-aigw`
service is stopped and started again around the copy.

**Running it by hand first** (the script prints this): use the service's data directory
so a later switch to the service keeps the same gateway peer:

```
sudo netzilo-aigw run \
  --data-dir /var/lib/netzilo-aigw \
  --management-url https://srv.netzilo.com \
  --workplace-url https://go.netzilo.com \
  --setup-key <SETUP-KEY> --service-pat <SERVICE-TOKEN> \
  --listen :8443 --insecure-plain-http \
  --ai-listen :8447 --ai-insecure-plain-http
```

A foreground run ends with the SSH session; the service does not. Never run both at
once against the same data directory.

### 3.2 Windows

```
irm https://pkg.netzilo.com/download/windows/install_aig.ps1 | iex
```

Installs `netzilo-aigw.exe` into `%ProgramFiles%\Netzilo AI Gateway` (as administrator)
or `%LOCALAPPDATA%\Programs\Netzilo AI Gateway`, and adds that folder to the PATH
(`AIG_NO_PATH=1` to skip). **No Windows service is created**, by the script or by the
binary; a persistent install needs a service wrapper or a scheduled task the admin
provides. If a service named `netzilo-aigw` already exists and is running, the script
stops and restarts it around the upgrade.

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

Re-run the install script (Linux/macOS/Windows) or pull a newer image tag. The data
directory carries the peer key, so the gateway returns as the same peer. The version a
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
| `Authorization: Bearer <token>` | a user's **personal access token** (`nzl_…`), the signed-in user's identity-provider token (what the Workplace holds), or an OAuth access token the gateway issued to an MCP client (`46` §6) |

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

**Refusals, in the order a caller can meet them:**

| HTTP | Body | Cause and fix |
|---|---|---|
| 401 `a Netzilo credential is required` (with `WWW-Authenticate: Bearer realm="netzilo", resource_metadata=…`) | `{"error":{"message":…,"type":"netzilo_gateway"}}` | no token, a malformed token, a token of another account, or an expired one, on the public door. The same body on the tunnel door never appears: there an unidentified caller passes through ungoverned |
| 503 `management is not reachable, try again` (`Retry-After: 5`) | same shape | the gateway could not ask management who the token belongs to; nothing is cached about it |
| 404 `not served by the AI gateway` | same shape | the upstream's own admin or UI paths (`/`, `/api/…`, `/ui`): the gateway never forwards them |
| 502 `the AI gateway upstream is not reachable` | same shape | the built-in upstream is down; the process will have logged why |
| 403, `type: netzilo_policy`, message `no model is granted to this user` / `none of this user's filters grants a model` / `model <m> is not granted to this user` / `model <provider>/<m> is not granted to this user` | the error envelope of the API surface called | no gateway filter grants the user that model (`29` §2.2); also what a user gets while their filters cannot be fetched |
| 403 `type: netzilo_policy`, a guardrail's reason (default `blocked by Netzilo policy`) | same | a guardrail blocked the prompt, the answer, a requested tool call, an MCP tool call or an MCP result; the event names the rule |
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

Management keeps raw rows for 90 days and hourly rollups indefinitely; they feed the home
page's Agentic Activity section and Tokens tile and the **AI Usage** report
(`30-activity-reports-and-integrations.md` §2–3).

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

Create a new token for the service user, put it in `aigw.env`, restart the service, then
revoke the old token. A restart keeps what was applied to the upstream (providers, keys,
each user's virtual key, in `ai-applied.json`), so users' spend counters survive; filters
and users are fetched afresh.

---

## 10. Troubleshooting

| Symptom | Check | Fix |
|---|---|---|
| Service exits at once, `a service PAT is required…` / `ai mode needs a peer of its own` / `give either a setup key or a PAT` | `aigw.env` | supply `--service-pat` and exactly one of `--setup-key`/`--pat` |
| `management-url: not an absolute URL` | the flag | scheme and host only, no path |
| Exits after `aigw: the agent gateway did not become healthy in 15s` | `--ai-data-dir` writable? disk? `--ai-upstream-log-level debug` for the upstream's own error | fix the data directory; escalate with the log if it repeats |
| Workplace card shows the gateway **offline** although `curl` works | the browser's call is refused for its origin: `--workplace-url` missing or wrong (Cloud: `https://go.netzilo.com`) | set `--workplace-url`, restart; the card recovers at its next probe (30 s) |
| 401 `a Netzilo credential is required` from a valid token | token of another account; token expired; typed with a space | `curl -s -o /dev/null -w '%{http_code}' https://<mgmt>/api/users -H "Authorization: Token <t>"` → 200 proves the token; then check the account |
| 403 `no model is granted to this user` | the user is in no group a **gateway** filter targets, or the filter grants no model, or is disabled, or is of type endpoint | `GET /api/edge/filters/effective?type=gateway&user=<id>` with an admin token lists what applies; fix the filter (`29` §2.2) |
| 403 `model X is not granted to this user` | the filter grants other models/providers | grant the model (or `provider/*`), or tell the user which models `GET /v1/models` lists for them |
| Every request 403 for everyone after a policy change | the filters failed to load (`N failed` in the policy line is about guardrails; a fetch failure shows as `gateway ai: cannot …`) | management reachable from the host? service token still valid (401 in the log)? |
| 429 / 402 before any real use | a limit's window and counters | `45` §3; counters restart when grants or limits change |
| Guardrail does not fire for Claude Code / Codex users | by design: prompt guardrails and model grants apply to `/v1/chat/completions` only (§1) | state it; limits and usage still apply |
| MCP tool answers `Connect <server> in your Workplace…` | the user has no sign-in/header values for that server | `46` §4 and `47` §3 |
| `Tool execution failed: Blocked by rule: <name>` | a guardrail on the tool result or arguments | expected; the event names the rule |
| Through a published application: 502 `The application did not answer.` | target without `:8447`; gateway down; no policy from the user's device groups to the gateway peer; the proxy still on a stale target (≤10 min on old proxies) | fix the target; `44` §11 |
| Through a published application: 404 `There is no application at this address.` | application disabled or unpublished; name cache up to 30 s old | enable; wait; `44` §11 |
| Usage never appears on the dashboard | `gateway ai: usage: … kept, upload failed` (management unreachable or token refused) or `… dropped` (server rejected the batch); the dashboard snapshot is hourly | fix the cause; wait for the next hourly snapshot; the AI Usage report reads the same data |
| Every restart creates a new peer | `gateway: no data dir: …` | make `--data-dir` writable by the service user, or set it |
| Upstream providers show in the upstream but not the ones defined | the gateway is the only writer: hand-made upstream providers of a type management defines are replaced | define providers in the dashboard only |

**Before escalating** (`12-escalation-package.md`): the exact `run` flags with secrets
removed, `journalctl -u netzilo-aigw --since "-1h"`, the failing request's status and body
(no token), the user's `GET /api/edge/filters/effective?type=gateway&user=<id>` as an
admin, and `netzilo-aigw --version`.

---

## 11. Limits to state before a customer discovers them

- **Governance is per API surface** (§1): prompt and answer guardrails and Netzilo's own
  model-grant refusal cover the OpenAI chat surface; the Responses API, the Anthropic
  Messages surface, embeddings and completions are identified, limited by the virtual key
  and recorded, nothing more. Do not promise a prompt block for a Claude Code user.
- **Streams are block-only.** A streamed chat answer or a streamed tool call is evaluated
  on its final chunk and can be ended, not rewritten.
- **A limit is per user per gateway.** Two gateways in one account count separately; a
  group pool shared by users does not exist. Changing a user's grants or limits restarts
  their counters.
- **A revoked token works for up to a minute** at the door; management refuses it
  immediately, so the window is the gateway's cache only.
- **The tunnel door governs by peer.** A request from a peer the gateway cannot map to a
  user passes through ungoverned (counted and logged). Keep the gateway peer reachable
  only from groups that should use it.
- **No Windows service, no Linux arm64 build** today.
- **The browser-access proxy on `:8443` is always on.** Bind it to loopback when it is
  not wanted.
- **Content never leaves the gateway through telemetry**; detections (events with a rule
  name and a short excerpt) do, as on devices — `14-data-handling-and-privacy.md` §3.
