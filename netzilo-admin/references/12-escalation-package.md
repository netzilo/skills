# Escalation — Building a Diagnostic Package for Code-Level Analysis

Escalation exists for one purpose: **to hand a problem to an analyst who can read the
product's source code.** Everything else is your job.

The package you build is consumed by an engineering analyst working with the private
codebase. That shapes what belongs in it: raw diagnostic material with intact
identifiers and timestamps, a precise statement of the contradiction, and enough
correlation keys to join a client log line to a server log line. It is not a summary,
and it is not a place to speculate about root cause.

Two rules govern the whole procedure:

1. **The customer sends the package, not you.** You build it, show them what is in it,
   and they decide. Never transmit their data anywhere yourself.
2. **Credentials never leave the machine, identifiers must.** §6 lists what to strip;
   §7 explains why over-redacting destroys the evidence you are shipping.

---

## 1. Escalate only when the answer needs the source code

The test: **can this be explained from configuration, documented behaviour, or the
environment?** If yes, it is yours to solve. If the observable facts contradict what the
configuration says should happen, and you have proved that with evidence, the next step
requires reading the implementation — escalate.

Escalate when, after working the relevant runbook to its end, you have one of these:

| Signal | Example |
|---|---|
| **Crash or panic** | management container restart-loops with a stack trace; client daemon dies repeatedly |
| **Enforcement contradicts configuration** | a policy resolved from the API allows TCP 443 between the two peers' groups, both peers are Connected, no posture check is attached, no `peer.access.blocked` event is logged — and the connection is still refused |
| **State machine stuck** | peer shows `Connected` with a WireGuard handshake older than an hour and never recovers; route present in `routes list` but never installed in the routing table |
| **Migration or persistence failure** | `auto migrate` error that a documented rollback does not fix; data present in the API but absent in the dashboard |
| **Documented procedure does not work** | a runbook command fails on a supported platform in a way its error table does not cover |
| **Detection engine disagrees with its own rule** | Replay shows a rule matching a snapshot, the same traffic live produces no verdict, and the filter binding is confirmed correct |

Do **not** escalate — these are solvable, and the runbook says how:

| Not an escalation | Where it is solved |
|---|---|
| Traffic blocked and no policy allows it | `20` §6, `11` §3 |
| Device unreachable, route/routing peer/firewall untested | `11` §4–§5 |
| Certificate, DNS, or port problem on the server | `03` §1–§4 |
| Login, SSO, MFA, or "no e-mail" (SMTP is not configured by the installer) | `04` §5–§6 |
| AI rule not firing, filter not bound, agent path not intercepted | `29` §5, `28` §7 |
| Plan limit, licence state, or an Enterprise-only feature | `25` §4 |
| Behaviour that a newer version of this skill already documents | check first — see below |

**Before collecting anything, confirm your skill copy is current** (`SKILL.md` → "Check
you are current"). Escalating something a newer runbook already fixes costs the customer
a support cycle.

---

## 2. Classify the impact

| Severity | Meaning |
|---|---|
| **S1** | nobody can work, no workaround — control plane down, all peers disconnected, login broken for everyone |
| **S2** | a group is blocked or a site is isolated; workaround is painful |
| **S3** | single user or device; workaround exists |
| **S4** | suspected defect with no outage, or a documentation contradiction |

Record: how many users and devices, since when, ongoing or intermittent, and what
changed immediately before (upgrade, policy edit, certificate, network change).

---

## 3. What the client debug bundle actually contains

Know this before you rely on it — it is much narrower than the name suggests.

`netzilo debug bundle` produces a zip with exactly two things:

1. `status.txt` — the full `netzilo status --detail` output (`status.anon.txt` with `-A`).
2. **Every file in the daemon's log directory**, copied in wholesale.

It does **not** collect routes, interface state, firewall rules, resolver configuration,
or system information. If the case needs those, collect them separately (§4.2).

What "every file in the log directory" means per platform:

| Platform | Log directory | Consequence |
|---|---|---|
| **Linux** | `/var/log/netzilo/` | also contains the service's stdout/stderr logs, because the installer points them here — good, include them |
| **macOS** | `/var/log/netzilo/` | the launchd logs `/var/log/Netzilo.out.log` and `/var/log/Netzilo.err.log` are **outside** this directory and are **not** in the bundle. Panics can land there — collect them separately (`err.log` is normally thousands of benign `TLS handshake error` lines; grep it for `panic` or `goroutine`). The two system-extension logs `netzilofilter.log` and `netzilosecurity.log` **are** in the directory and ride along in the bundle |
| **Windows** | `%PROGRAMDATA%\Netzilo\` | this is also the **configuration** directory, so the bundle sweeps in `config.json` (contains the WireGuard **private key**), `token.dat`, `pat.dat`, and `netzilo-ca-key.pem` (the TLS-inspection **CA private key**). These must be removed — see §6 |

Also: the tray menu's **Support → Collect Data** produces a bundle with **no
`status.txt` and no anonymization** — it sends an empty request. Always use the CLI so
the status snapshot is included.

---

## 4. Collect

Everything in this section is collected **from the customer's systems**: their affected
device, their routing peer, their server. If the machine you work from has its own Netzilo
client, nothing from it belongs in the package. A bundle from your own device describes
your own enrolment and would send the analyst down the wrong path. When you cannot run a
command on the customer's system yourself, §8 gives them the blocks to run.

Create one directory, fill what you can, and record what you could not.

```bash
STAMP=$(date -u +%Y%m%d-%H%M)
PKG="netzilo-escalation-$STAMP"
mkdir -p "$PKG"/{client,server,config,events}
cd "$PKG"
```

### 4.1 Always — the facts that make logs readable

Without these the analyst cannot locate the event in the logs.

```
- Exact time of an occurrence, with timezone (client and management logs are written in
  local time with a UTC offset; AIDR event payloads are UTC — say which clock you used)
- Client version (`netzilo version`) and server image versions (`docker compose images`)
- The affected peer's WireGuard public key, Netzilo IP, and FQDN (from `status.txt`)
- The user's e-mail / the setup key name the peer enrolled with
- Deployment: cloud or self-hosted, install path, domain
- Reproducibility: every time / intermittent / once; minimal steps to reproduce
```

### 4.2 Client

On the **affected device**. Never on your own machine.

Reproduce with verbose logging in the **same daemon lifetime** — the log level is held
in memory and is lost on restart:

```bash
netzilo debug log level trace     # or: debug
# ... reproduce the problem now ...
sudo netzilo debug bundle          # omit -A unless §7 says otherwise
```

Or capture a fixed window (this takes the client **down**, traces, brings it up, waits,
and takes it down again — warn the customer, and start the service afterwards):

```bash
sudo netzilo debug for 5m
sudo netzilo service start
```

Then add what the bundle does not collect:

```bash
netzilo status -d                > client/status-detail.txt
netzilo routes list              > client/routes.txt
netzilo version                  > client/version.txt
# Linux
ip addr; ip route show table all; ip rule show; sudo nft list ruleset 2>/dev/null || sudo iptables-save
resolvectl status 2>/dev/null || cat /etc/resolv.conf
# macOS — launchd logs are NOT in the bundle
sudo cp /var/log/Netzilo.err.log /var/log/Netzilo.out.log client/ 2>/dev/null
scutil --dns | head -40; netstat -rn | head -40
# Windows (elevated PowerShell)
Get-NetRoute; Get-DnsClientNrptRule; Get-NetAdapter
```

Extra verbosity only when the analyst asks for it, or when the case is clearly in that
subsystem — each needs the daemon restarted unless noted:

| Area | Knob |
|---|---|
| ICE / NAT traversal | `PIONS_LOG_DEBUG=all` (ICE logging is fully suppressed below `debug` level) |
| WireGuard device | `NB_WG_DEBUG=true` |
| gRPC to management/signal | `GRPC_GO_LOG_VERBOSITY_LEVEL=99 GRPC_GO_LOG_SEVERITY_LEVEL=info` |
| Goroutine/heap dumps | `NB_DEBUG=1`, then fetch from `127.0.0.1:6060` |
| AI behaviour graph | `NB_LAB_MODE=true`, then `http://localhost:41336/debug/api/graph` |

### 4.3 Server — the management log (self-hosted only)

**Cloud customers: skip this section entirely.** On Netzilo Cloud the server logs are ours,
already retained, and Level 3 reads them directly. Asking a Cloud customer for server logs
delays the case and gets you nothing we do not already have. Say in the summary that the
deployment is Cloud, give the account and the time window, and move on.

**Self-hosted: the management log is not optional.** Almost every escalation that needs
code-level analysis is decided by joining a client log line to the server line that
answered it. A package with client logs and no management log usually comes straight back
as a data request, which costs the customer another day.

Two different things, often confused, and the analysis needs the first:

| | What it is | Where |
|---|---|---|
| **Management log** | what the server itself wrote while handling the request — the decisions, the errors, the stack traces | the `management` container's stdout, §4.3 below |
| **Events** | the audit feed of what *changed*: who edited a policy, who added a peer | the API, §4.4 |

Events tell you what the configuration became. The management log tells you why a request
was refused. They are not substitutes.

Ask for SSH to the server if you do not already have it — collecting these logs yourself
is faster and less error-prone than talking the customer through it, and you can widen
the window or raise verbosity on the spot. On AWS, `aws ssm start-session --target
<instance-id>` works without opening a port. Fall back to §8 only if access is refused.

There is **no server-side bundle command**. Collect with compose — the shipped
configuration logs to stdout, so `docker compose logs` is the source of truth:

```bash
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo )
cd "$C"
sudo docker compose ps      > "$OLDPWD/server/compose-ps.txt"
sudo docker compose images  > "$OLDPWD/server/compose-images.txt"

# The window that matters: from an hour before the first occurrence to an hour
# after the last. An hour either side is not padding — it catches the startup,
# the token refresh or the sync that set the failure up.
SINCE='2026-09-17T07:00:00Z'   # incident start minus 1h, UTC
UNTIL='2026-09-17T10:00:00Z'   # incident end   plus 1h, UTC
sudo docker compose logs --no-color --timestamps --since "$SINCE" --until "$UNTIL" management \
  > "$OLDPWD/server/management.log" 2>&1

# The rest of the stack, same window — smaller, and they explain the management
# log when the fault is upstream of it.
for s in zitadel caddy signal coturn dashboard db redis; do
  sudo docker compose logs --no-color --timestamps --since "$SINCE" --until "$UNTIL" "$s" \
    > "$OLDPWD/server/logs-$s.txt" 2>&1
done
```

Name the management log `server/management.log` exactly. It is the file the analysis is
built on and it should not have to be hunted for among seven others.

**Say which window you captured, in UTC, in the summary.** A log that does not cover the
incident is worse than no log: it reads as evidence of absence and sends the analysis the
wrong way. If the incident is older than what the server retains, say that explicitly
rather than sending the nearest window you could get.

Check before you send that the log actually covers it:

```bash
head -1 server/management.log; tail -1 server/management.log
``` For a reproducible fault, raise management verbosity first by
setting `--log-level debug` in the management `command:` in `docker-compose.yml`, then
`docker compose up -d --force-recreate management`, reproduce, collect, and restore the
original value afterwards.

Marketplace images also have `/var/log/netzilo-firstboot.log` and
`/var/log/netzilo-metering.log`.

### 4.4 Configuration and events

Export the intent so the analyst can compare configuration against behaviour, using an
API token (`09` §1). Collect only what the case touches.

```bash
nz /policies > config/policies.json ; nz /groups > config/groups.json
nz /peers    > config/peers.json    ; nz /routes > config/routes.json
nz /posture-checks > config/posture-checks.json
nz /edge/filters > config/edge-filters.json   # AI cases
FROM=$(date -u -d '-2 days' +%FT%TZ 2>/dev/null || date -u -v-2d +%FT%TZ)
nz "/events/paginated?limit=1000&date_from=$FROM" > events/events.json
```

For an AI-security case also capture the session snapshot, which is the engine's own
record of what it observed:

```bash
nz "/peers/<peerId>/aidr-snapshot"                 > events/aidr-runs.json
nz "/peers/<peerId>/aidr-snapshot?run_id=<runId>"  > events/aidr-snapshot.json
```

---

## 5. Correlation keys — include these explicitly

An analyst joining client logs to server logs needs the keys below. State them in
`00-SUMMARY.md`; do not make them hunt.

| Key | Client side | Server side |
|---|---|---|
| **WireGuard public key** | in `status.txt`, unanonymized | logged as the peer identifier on peer RPCs — the most reliable join |
| Netzilo IP / FQDN | `status.txt`, log lines | peer record via `GET /api/peers` |
| Peer id / account id | client logs only at `debug` level | API and management logs |
| **AIDR `correlation_id`** | dashboard event metadata | joins AI events across client and server |
| Rule name / filter name | client verdict log lines | `tool.blocked` / `tool.detected` event metadata |
| Timestamp | local time **with UTC offset** | same format; AIDR payloads are UTC |

One practical trick: at `debug` level the client logs every event it sends to the
dashboard verbatim (`Buffered event: {…}`), so a dashboard event can be matched to the
exact client log line that produced it.

---

## 6. Remove credentials before anything leaves the machine

| Remove | Where it appears |
|---|---|
| `config.json` — contains the WireGuard **private key** | inside the Windows debug bundle |
| `netzilo-ca-key.pem` — TLS-inspection **CA private key** | inside the Windows debug bundle |
| `token.dat`, `pat.dat` — session and API credentials | inside the Windows debug bundle |
| `management.json`, `zitadel.env`, `dashboard.env`, `.env`, `turnserver.conf` | server configuration directory — never collect them at all |
| `CREDENTIALS`, `netzilo-state.env` | server state directory — never collect |
| `certs/`, `machinekey/`, any `*.pem` / `*.key` | server configuration directory |
| Database dumps | never needed for code-level analysis |
| API tokens and setup keys in any file or e-mail body | `config/setup-keys.json`, logs, command history |

Open the Windows bundle and delete those four items before including it, then note the
removal in `MANIFEST.txt`. Then run a credential sweep over the package and prove it:

```bash
find . -type f \( -name '*.json' -o -name '*.txt' -o -name '*.log' -o -name '*.md' -o -name '*.yml' \) -print0 \
| xargs -0 perl -0777 -pi -e '
  s/-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----/[PRIVATE KEY REMOVED]/gs;
  s/nzl_[A-Za-z0-9_]{8,}/nzl_REDACTED/g;
  s/("(?:token|plain_token|password|client_secret|secret_key|access_key|api_key|auth_token|masterkey)"\s*:\s*")[^"]*"/${1}REDACTED"/gi;
  s/^([A-Z0-9_]*(?:PASSWORD|SECRET|TOKEN|MASTERKEY)[A-Z0-9_]*)=.*$/$1=REDACTED/gm;
  s/\b(password|secret|api[_-]?key)=[^\s;&"]+/$1=REDACTED/gi;
  s/(Authorization:\s*(?:Bearer|Token)\s+)[^\s"]+/${1}REDACTED/gi;
'
grep -rEi 'nzl_[A-Za-z0-9_]{8,}|BEGIN [A-Z ]*PRIVATE KEY|(MASTERKEY|PASSWORD|SECRET|TOKEN)=[^R]' . \
  && echo "!! CREDENTIALS STILL PRESENT — fix before sending" || echo "credential sweep clean"
```

---

## 7. Do not anonymize by default — decide deliberately

`netzilo debug bundle -A` looks like the safe choice. For code-level analysis it usually
is not, and it is weaker than it appears:

- **It does not hide** WireGuard public keys, peer IDs, group names, LLM prompts, or
  tokens. It rewrites public IP addresses and domain names only.
- **It preserves** the whole `100.64.0.0/10` overlay range, private RFC1918 addresses,
  and `netzilo.*` domains — so most of what identifies a deployment survives anyway.
- **It breaks correlation.** The status file and the log files are anonymized by two
  independent passes, so the same real address becomes *different* placeholders in
  `status.anon.txt` and in the logs. The analyst can no longer follow one address across
  the two.

Guidance: for a normal escalation send the bundle **un-anonymized** and control exposure
through the channel and the credential sweep in §6. Use `-A` only when the customer
requires it for public IPs or internal hostnames — and then say so in `MANIFEST.txt`, so
the analyst knows why addresses do not line up.

---

## 8. If you cannot run the commands yourself

Common: the customer is on the affected machine and you are not. Give them one block to
paste, tell them what it produces, and what to send back. Do not ask them to interpret
anything.

**Linux / macOS client**

```bash
# 1) turn on verbose logging, then reproduce the problem before running step 2
netzilo debug log level trace

# 2) after reproducing, collect
sudo netzilo debug bundle
netzilo status -d > ~/netzilo-status.txt
netzilo version  >> ~/netzilo-status.txt
# macOS only — these are not in the bundle:
sudo cp /var/log/Netzilo.err.log ~/ 2>/dev/null

# 3) send back: the .zip path printed by step 2, plus ~/netzilo-status.txt
#    (and Netzilo.err.log on macOS)
```

**Windows client** (PowerShell as Administrator)

```powershell
netzilo debug log level trace
#  ... reproduce the problem ...
netzilo debug bundle
netzilo status -d | Out-File "$env:USERPROFILE\netzilo-status.txt"
```

Then tell them, in plain words: *"the zip it printed contains your configuration file,
which includes a private key — before sending, open the zip and delete `config.json`,
`token.dat`, `pat.dat` and `netzilo-ca-key.pem`."* If they would rather not edit the
archive, ask them to send it through a private channel and say in the summary that the
bundle is unredacted.

**Self-hosted server** (SSH, as a user with docker access)

```bash
cd /opt/netzilo/run 2>/dev/null || cd /opt/netzilo
sudo docker compose ps > ~/netzilo-server.txt
sudo docker compose images >> ~/netzilo-server.txt
for s in management zitadel caddy signal coturn; do
  sudo docker compose logs --no-color --timestamps --since 24h $s > ~/netzilo-$s.log
done
# send back: ~/netzilo-server.txt and the ~/netzilo-*.log files
```

Ask for the exact wall-clock time and timezone of an occurrence alongside the files — it
is the cheapest thing to get and the most expensive to reconstruct without.

---

## 9. Write the summary

The analyst starts here. Put it in `00-SUMMARY.md` and paste it into the e-mail body.

```markdown
# <one-line problem statement>

**Severity:** S2 — 34 users in `berlin-office` cannot reach 10.20.5.7:5432 since 2026-09-10 09:00 +02:00
**Deployment:** self-hosted, on-prem installer, domain vpn.example.com
**Client:** 4.4.375 (Windows 11)   **Server images:** see server/compose-images.txt
**Reproducible:** yes, every attempt

## Observed
<exact behaviour and error text, and on which side it appears>

## Expected, and the configuration that says so
<the intent, and the specific policy/route/filter that expresses it — cite the file in config/>

## Why this needs code-level analysis
<the contradiction, with the evidence that rules out configuration:
 e.g. "policy X allows TCP 5432 between the peers' groups (config/policies.json),
 both peers Connected with fresh handshakes (client/status-detail.txt),
 no peer.access.blocked events (events/events.json), and the routing peer forwards
 the SYN but no reply returns (server/management.log 09:14:22+02:00)">

## Correlation keys
- peer WireGuard public key: <key>
- peer Netzilo IP / FQDN: 100.64.0.23 / laptop-jane.netzilo.network
- occurrence timestamps: 2026-09-10 09:14:22 +02:00 (client), 09:14:22 +02:00 (server)
- server log window captured: 2026-09-10 08:00–11:00 UTC
- AIDR correlation_id (if applicable): <id>

## Already ruled out
<what you tested and the result — each line saves the analyst a cycle>

## Server-side logs
<For self-hosted: "server/management.log covers 2026-09-17 07:00–10:00 UTC; the incident
occurred 08:14 UTC". If the window could not be covered, say why — retention, log rotation,
access refused — rather than leaving it out.
For Cloud: "Netzilo Cloud, account <id> — server logs not collected; available to Level 3."
>

## Logging state
<log level used, whether the bundle is anonymized, which time window the server logs cover>
```

Add `01-timeline.md` — one row per attempt, in order, with the evidence file for each.
Negative results belong here; they are what stops the analyst repeating your work.

---

## 10. Package and send

```bash
cd ..
find "$PKG" -type f | sort > "$PKG/MANIFEST.txt"
{ echo; echo "## Excluded"
  echo "- config.json, token.dat, pat.dat, netzilo-ca-key.pem removed from the Windows bundle"
  echo "- server configuration files not collected (contain secrets)"
  echo "- bundle is NOT anonymized (preserves correlation)"
} >> "$PKG/MANIFEST.txt"
tar czf "$PKG.tar.gz" "$PKG"; ls -lh "$PKG.tar.gz"
```

Show the customer `MANIFEST.txt` and the credential-sweep result, then **ask for explicit
approval to send**. That approval is about the customer's data leaving their machine, and
it is required whichever route below you take.

Escalation goes to Level 3 over its API, not to a mailbox. Level 3 is an agent with
source access: it reads the code at the exact commit your versions resolve to, traces the
path your evidence implicates, and answers in language you can relay. It needs two things:

| | |
|---|---|
| the endpoint | the gate, `https://l3.netzilo.com` unless this deployment says otherwise |
| the token | this deployment's own Netzilo Cloud service-account token |

Either can be set at install or changed later under **Settings → Plugins → Level 3
escalation**, and the two arrive under different names depending on which: the Settings
page publishes `DSH_L3_PAT` and `DSH_L3_URL`, a launch environment sets `L3_PAT` and
`L3_URL`, and the launch environment wins where both exist. Resolve them once, before
anything else in this section:

```bash
L3_PAT="${L3_PAT:-${DSH_L3_PAT:-}}"
L3_URL="${L3_URL:-${DSH_L3_URL:-https://l3.netzilo.com}}"
```

The token is verified against Netzilo Cloud on every call, so access is granted and
revoked there, per deployment. If it resolves empty, say so plainly — point the customer
at that Settings page — and stop. There is no fallback address to send a package to.

**A question with no package** — the common case, and the one to prefer. Send the summary
inline; `user` is the case id, which is what ties follow-ups to the same case:

```bash
jq -n --arg case "$CASE" --arg body "$(cat "$PKG/00-SUMMARY.md")" '{
  model: "netzilo/l3", user: $case, stream: false,
  messages: [{ role: "user", content: $body }]
}' > /tmp/escalation.json

curl -sS --fail-with-body -X POST "$L3_URL/v1/chat/completions" \
  -H "Authorization: Token $L3_PAT" -H 'Content-Type: application/json' \
  -d @/tmp/escalation.json | jq -r '.choices[0].message.content'
```

A code-level case runs for minutes, not seconds — that is the analysis, not a hang. Do not
set a client timeout below ten minutes, and do not retry a call that is still running: a
second call starts a second analysis and the first one's work is lost.

**When the package itself has to go** — completions carries no files, so use the
conversation API instead, with the same token. Upload, then send the message that refers
to it:

```bash
CONV=$(curl -sS -X POST "$L3_URL/v1/conversations" \
  -H "Authorization: Token $L3_PAT" -H 'Content-Type: application/json' -d '{}' | jq -r .id)

ATT=$(curl -sS -X POST "$L3_URL/v1/conversations/$CONV/attachments" \
  -H "Authorization: Token $L3_PAT" -H "x-filename: $(basename "$PKG.tar.gz")" \
  -H 'Content-Type: application/octet-stream' --data-binary @"$PKG.tar.gz" | jq -r .id)

curl -sS -N -X POST "$L3_URL/v1/conversations/$CONV/messages" \
  -H "Authorization: Token $L3_PAT" -H 'Content-Type: application/json' \
  -d "$(jq -n --arg t "$(cat "$PKG/00-SUMMARY.md")" --arg a "$ATT" \
        '{text: $t, attachmentIds: [$a]}')"
```

That returns a stream: `status` lines while the agent works, `delta` lines carrying the
answer, `done` at the end. The archive is handed to the agent as a file it opens and
searches, so a package of any size costs the few lines that matter rather than being
pasted into a conversation.

**Never** put a token, setup key, password or private key in the text of either call.
The credential sweep in §6 is what makes that true of the package; the summary is yours
to check by eye.

If a server is down and the customer wants it restored before root cause, say so
explicitly in the summary and take a backup (`02` §6) first, so the failure state is
preserved for analysis.

---

## 11. While it is open

- Apply any workaround that reduces impact and record it in the timeline.
- **A follow-up is the same case, not a new one.** Reuse the same `user` value (the case
  id) or the same conversation id. On `/v1/chat/completions` the thread is yours to keep:
  send the previous messages along with the new one, as any OpenAI-compatible client
  does, or the agent starts from nothing. On the conversation API the gate keeps the
  thread for you and replays it — post to the same conversation and it has the history.
- New symptom or clue: a follow-up on the open case, not a rebuilt package.
- If you find the cause yourself, say so on the case and close it.
- When it is fixed, verify against the gate that originally failed — not against the
  absence of complaints.
- Level 3 files its own bug reports. You will get a case id and an answer to relay; you
  will not get an issue link, and the customer never does.
