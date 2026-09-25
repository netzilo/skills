---
id: '42'
title: The AI Assistant on a self-hosted Netzilo Server
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 28752
sections:
- id: '1'
  title: What it is made of
  chars: 1743
- id: '2'
  title: Before you start
  chars: 1364
- id: '3'
  title: Configure Management
  chars: 1950
- id: '4'
  title: Configure the worker
  chars: 3470
- id: '5'
  title: The runbooks the agent follows
  chars: 2410
- id: '6'
  title: Compose installs (one-liner, AWS, Azure)
  chars: 6891
- id: '7'
  title: Kubernetes and other orchestrators
  chars: 3253
- id: '8'
  title: Turning it on for people
  chars: 980
- id: '9'
  title: Operating it
  chars: 1787
- id: '10'
  title: Security posture
  chars: 1181
- id: '11'
  title: Troubleshooting
  chars: 3194
---
# The AI Assistant on a self-hosted Netzilo Server

The dashboard's AI Assistant runs on the customer's own server. This file is the one place
that says how it is put together, how to configure and deploy it (compose installs,
Kubernetes and other orchestrators), how to operate it, and how to fix it when it does not
answer. Installing the server itself is `01-server-install.md`; turning the Assistant on
for people is §8 here; what the Assistant may do once it runs is `36-device-tools.md` and
`39-end-user-self-service.md`.

## 1. What it is made of

Three parts, and only one of them is new on a Netzilo Server:

| Part | Where it runs | What it does |
|---|---|---|
| **Management** | the `management` container | Owns the chat: authenticates the person, checks they may use the Assistant, stores sessions, messages and the audit log, assembles each turn and calls the worker. Approvals of writes are decided here, never in the worker. |
| **Support worker** | the `support-worker` container, image `ghcr.io/netzilo/net-support-worker` | The agent. Receives one turn over HTTP, runs the model and its tools, streams the answer back. **Stateless**: nothing survives a turn except what Management stores. |
| **AI provider** | outside the server (or a gateway inside the customer network) | The model. Chosen and approved by the account owner in the dashboard, never configured on the worker. |

How a turn flows:

1. The browser posts a message to Management (`/api/support/sessions/{id}/messages`).
2. Management calls the worker at `SupportConfig.WorkerURL` + `/turn` with the shared
   worker token, the conversation, the caller's own token and the provider settings.
3. The worker calls Management back at `SupportConfig.ManagementURL` for everything it
   does: API reads as the caller, device tools, the API description, and live step
   updates for the audit log. It calls the AI provider directly.
4. The answer streams back through Management to the browser.

The worker has **no ingress**. Nothing outside the server network ever calls it, and
Management is its only client. It never holds an administrator credential of its own: every
API call uses the token of the person in the chat, so the Assistant can do exactly what
that person can do and no more.

## 2. Before you start

- **The server carries the worker.** Compose installs from September 2026 on include
  it; older ones do not and cannot gain it in place (`01-server-install.md` §0 shows the
  check). The quick test on the host: `docker compose ps` lists `support-worker (healthy)`.
- **An AI provider is connected and a model is approved for the Assistant.** Until the
  owner does that under Integrations → Artificial Intelligence
  (`30-activity-reports-and-integrations.md` §4a), the dashboard shows no Assistant button.
  This is the expected state of a fresh install.
- **Outbound network.** The worker needs HTTPS to the provider endpoint. Everything else is
  optional:

| Destination | Needed for | If blocked |
|---|---|---|
| The AI provider endpoint (the vendor, or the gateway URL the owner entered) | every turn | the Assistant cannot answer |
| `github.com` and `codeload.github.com` | refreshing the runbooks the agent follows (§5) | the worker uses the copy baked into its image |
| `docs.netzilo.com`, `netzilo.com`, `www.netzilo.com`, `pkg.netzilo.com`, `github.com`, `raw.githubusercontent.com` | the agent reading a documentation page a runbook links to | those reads fail; the runbooks still work |
| `l3.netzilo.com` | Level 3 escalation, only when a Level 3 token is set (§8) | an approved escalation fails; everything else works |

## 3. Configure Management

The `SupportConfig` block in `management.json`:

| Field | Compose installer writes | Meaning |
|---|---|---|
| `WorkerURL` | `http://support-worker:8080` | Where Management reaches the worker. Missing or empty: every message answers `support agent is not configured on this deployment` (HTTP 412). |
| `WorkerToken` | a generated 40-character token | Shared secret. Management sends it to the worker on every turn, and requires it from the worker on the internal step callback. Must equal the worker's `SUPPORT_WORKER_TOKEN`. |
| `ManagementURL` | `http://management:80` | Where the worker reaches Management. Keep it an internal address: left empty, it is derived from the browser's `Host` header, so the worker goes out through the public domain and depends on hairpin routing and on trusting the server's certificate. |
| `TurnTimeoutSec` | `900` | Ceiling on one turn end to end. `0` means 15 minutes. Sized so a Level 3 escalation, which takes minutes, fits inside one turn. |
| `L3URL` | `https://l3.netzilo.com` | Netzilo Level 3 gate. |
| `L3Token` | the `NETZILO_L3_TOKEN` install input, else empty | Netzilo Cloud service-account token for escalation. Empty: the agent's escalate tool answers that escalation is not configured on this deployment and offers to prepare the summary for sending by hand; the Assistant itself works. |

Four environment variables on the `management` container override the file, so secrets can
come from a secret store instead of `management.json`. A set variable always wins; an unset
one leaves the file alone:

| Variable | Overrides |
|---|---|
| `NB_SUPPORT_WORKER_TOKEN` | `WorkerToken` |
| `NB_SUPPORT_L3_TOKEN` | `L3Token` |
| `NB_SUPPORT_L3_URL` | `L3URL` |
| `NB_SUPPORT_MANAGEMENT_URL` | `ManagementURL` |

`WorkerURL` and `TurnTimeoutSec` come from the file only. Management reads both at start,
so any change needs a Management restart (`02-server-operations.md` §3).

## 4. Configure the worker

All settings are environment variables on the worker container. Only the first one is
required.

**Required and safety**

| Variable | Default | Meaning |
|---|---|---|
| `SUPPORT_WORKER_TOKEN` | — | Must equal Management's `WorkerToken`. The worker **refuses to start** without it (`refusing to start: SUPPORT_WORKER_TOKEN is empty`). |
| `SUPPORT_INSECURE_NO_TOKEN` | unset | `1` lets the worker start without a token. A lab switch; never on a server. |
| any `LANGCHAIN_*` or `LANGSMITH_*` | unset | The worker **refuses to start** when one is set (other than `LANGCHAIN_TRACING_V2=false`): tracing would send customer conversations to a third party. |

**How far one turn may go**

| Variable | Default | Meaning |
|---|---|---|
| `SUPPORT_MAX_AGENT_STEPS` | `16` (the compose installer sets `12`) | Model calls per turn. A device diagnosis spends four or five on runbook loads and a plan before its first check; raise to `16` if turns show the status `step limit reached; answering with what I have`. |
| `SUPPORT_TURN_TIMEOUT_SEC` | `900` | The worker's own deadline for a turn. The compose installer sets Management's `TurnTimeoutSec` to the same 900; set Management's a little higher than the worker's so the person sees the worker's plain message rather than a cut stream. |
| `SUPPORT_TOOL_TIMEOUT_SEC` | `30` | One management API call. |
| `SUPPORT_DEVICE_TIMEOUT_SEC` | `150` | One device command, including a two-minute shell command. |
| `SUPPORT_ESCALATION_TIMEOUT_SEC` | `600` | One Level 3 call. Never retried, because a second call starts a second analysis. |
| `SUPPORT_MODEL_RETRIES` / `SUPPORT_MODEL_RETRY_BACKOFF_SEC` | `2` / `2` | Further attempts after a provider rate limit, overload or connection fault, only while nothing has been shown to the person yet. |

**Reasoning.** The worker turns on the provider's extended reasoning where the model
supports it and remembers, per provider, model and endpoint, when it does not: a model that
rejects the parameter costs one retry and is then served without it.

| Variable | Default | Meaning |
|---|---|---|
| `SUPPORT_THINKING_BUDGET_TOKENS` | `4096` | Anthropic models: tokens the model may spend reasoning per call. `0` turns reasoning off. |
| `SUPPORT_ANTHROPIC_BETAS` | `interleaved-thinking-2025-05-14` | Anthropic beta features sent with reasoning on; interleaved thinking lets the model reason again after every tool result. Empty disables. |
| `SUPPORT_OPENAI_REASONING_EFFORT` | `medium` | OpenAI-protocol reasoning models: `low`, `medium` or `high`; empty never sends it. |
| `SUPPORT_OPENAI_REASONING_MODEL_PREFIXES` | `o1,o3,o4,gpt-5` | Which model names get `reasoning_effort`, on the vendor or any compatible gateway. |
| `SUPPORT_MAX_OUTPUT_TOKENS` | `16384` | Output budget per call (Anthropic). |
| `SUPPORT_OPENAI_MAX_TOKENS` | unset | Output budget for OpenAI-protocol endpoints; unset lets the endpoint decide. |

**Long conversations**

| Variable | Default | Meaning |
|---|---|---|
| `SUPPORT_CONTEXT_WINDOW_TOKENS` | `0` | Force a context window; `0` derives it from the model name. |
| `SUPPORT_DEFAULT_CONTEXT_WINDOW_TOKENS` | `200000` | Window assumed for a model the worker does not know. |
| `SUPPORT_COMPACT_THRESHOLD_RATIO` / `SUPPORT_COMPACT_RETAIN_RATIO` | `0.8` / `0.16` | Older messages are summarised once the prompt passes 80% of the window, keeping the newest 16% verbatim. |

**Runbooks and documentation reads** are §5 and §2.

## 5. The runbooks the agent follows

The agent follows this skill set, the public `netzilo/skills` repository. The worker carries
two copies:

- **Baked:** built into the image when the image was built. Always present.
- **Synced:** fetched from GitHub at start and then every 30 minutes, validated, and swapped
  in atomically. A failed or empty fetch never replaces a working copy.

| Variable | Default | Meaning |
|---|---|---|
| `SUPPORT_SKILLS_REPO` | `netzilo/skills` | Repository to sync from. |
| `SUPPORT_SKILLS_REF` | `main` | Branch, tag or commit to sync. Pin a tag or commit for a server whose runbooks must not change under it. |
| `SUPPORT_SKILLS_REFRESH_MINUTES` | `30` | Sync interval. `0` turns syncing off entirely, including at start: the worker serves the baked copy and makes no GitHub request. |
| `SUPPORT_SKILLS_DIR` | `/data/skills` | Where the synced copy lives inside the container. It is rebuilt at start, so it needs no volume. |
| `SUPPORT_SKILLS_BAKED_DIR` | `/opt/netzilo/skills` | The baked copy. |
| `SUPPORT_SKILLS_REFERENCE_MAX_CHARS` | `20000` | Longer references are served section by section. |
| `SUPPORT_SKILLS_SURFACE` | `dashboard-assistant` | Which surface the runbooks are filtered for; leave as is. |
| `SUPPORT_WEB_FETCH_HOSTS` | the documentation hosts in §2 | Hosts the agent may read pages from. |
| `SUPPORT_WEB_FETCH_GITHUB_ORG` | `netzilo` | On GitHub, the only organisation whose repository files may be read. Issues and pull requests are never read. |

**Which copy is serving.** The worker's health endpoint says so:

```bash
cd "$C"   # compose directory, 02-server-operations.md §1
sudo docker compose exec support-worker python -c \
  "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8080/healthz').read().decode())"
# {"status":"ok","skills":1,"skills_source":"synced","skills_revision":"main@1790181690"}
```

`skills_source` is `synced` or `baked`; `skills_revision` is `<ref>@<unix time of the fetch>`.
`skills: 0` means no runbooks at all: the agent still answers but guesses, so treat it as a
fault.

**Air-gapped servers.** Set `SUPPORT_SKILLS_REFRESH_MINUTES=0`. The runbooks are then the
ones in the image, and a newer set arrives with a newer worker image. The AI provider must
still be reachable, typically an OpenAI-compatible gateway inside the network, connected by
the owner in the dashboard like any provider.

## 6. Compose installs (one-liner, AWS, Azure)

The installer already does everything in §3 and §4: it generates the token, writes it into
`management.json` and into the `support-worker` service, and sets `WorkerURL` and
`ManagementURL` to the compose network names. There is nothing to add for a standard
install. To change a worker setting, edit the `environment:` list of the `support-worker`
service in `$C/docker-compose.yml` and recreate only that service:

```bash
cd "$C"
sudo docker compose up -d --no-deps support-worker
sudo docker compose ps support-worker        # (healthy) within about 30 seconds
```

Recreating the worker interrupts only a turn in flight; the person asks again. Upgrading
the worker image follows the same rules as the other images, including the digest pinning
on AWS and Azure images (`02-server-operations.md` §4).

### 6.1 Adding the worker to a server installed without it

A compose install made from an engine published before the worker existed runs eight
containers and has no `SupportConfig`. The check is `01-server-install.md` §0: zero
`support-worker` lines in `$C/docker-compose.yml`. Re-running the installer is not the
way to add it, because that wipes the server. The worker joins in place: it is a stateless
container that needs only a network name, a shared token and a `SupportConfig` block, and
Management reads that block at start.

What the procedure below does, so it can be checked before it runs: backs up both files
with a timestamp; generates a 40-character token; inserts a `support-worker` service into
`docker-compose.yml` before the top-level `volumes:` or `networks:` section, copying
Management's `extra_hosts` when the install pinned the domain that way; adds the
`SupportConfig` block to `management.json` **in place**, because the file is bind-mounted
into the Management container by path and a rename would leave the container reading the
old inode; validates the compose file; starts the worker; restarts Management. It refuses
to run twice. Management is down for the few seconds of its restart; clients reconnect on
their own.

```bash
if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
cd "$C"
sudo grep -q '^  support-worker:' docker-compose.yml && echo "support-worker is already present; stop here"
stamp=$(date +%s)
sudo cp -a docker-compose.yml "docker-compose.yml.bak-$stamp"
sudo cp -a management.json "management.json.bak-$stamp"
TOKEN="$(openssl rand -base64 32 | tr -d '=+/' | head -c 40)"
sudo TOKEN="$TOKEN" python3 - <<'EOF'
import os, re
tok = os.environ["TOKEN"]
p = "docker-compose.yml"; text = open(p).read()
if re.search(r"^  support-worker:", text, re.M): raise SystemExit("support-worker already present")
mgmt = re.search(r"^  management:\n(?:(?!^  \S).*\n)*", text, re.M)
if not mgmt: raise SystemExit("no management service in docker-compose.yml")
extra = re.search(r"^    extra_hosts:\n(?:^      .*\n)+", mgmt.group(0), re.M)
block = (
    "  # AI Assistant agent, added after install. No ingress: management calls it\n"
    "  # over the compose network with the shared token, and it calls management\n"
    "  # back at http://management:80.\n"
    "  support-worker:\n"
    "    image: ghcr.io/netzilo/net-support-worker:latest\n"
    "    container_name: support-worker\n"
    "    restart: unless-stopped\n"
    "    networks:\n"
    "      - netzilo\n"
    + (extra.group(0) if extra else "")
    + "    environment:\n"
    f"      - SUPPORT_WORKER_TOKEN={tok}\n"
    "      - SUPPORT_MAX_AGENT_STEPS=16\n"
    "      - SUPPORT_TOOL_TIMEOUT_SEC=30\n"
)
top = re.search(r"^(volumes|networks):", text, re.M)
if not top: raise SystemExit("no top-level volumes:/networks: section in docker-compose.yml")
open(p, "w").write(text[:top.start()] + block + text[top.start():])
EOF
sudo TOKEN="$TOKEN" python3 - <<'EOF'
import json, os
p = "management.json"; cfg = json.load(open(p))
if cfg.get("SupportConfig", {}).get("WorkerURL"): raise SystemExit("SupportConfig already set")
cfg["SupportConfig"] = {
    "WorkerURL": "http://support-worker:8080",
    "WorkerToken": os.environ["TOKEN"],
    "ManagementURL": "http://management:80",
    "TurnTimeoutSec": 900,
    "L3URL": "https://l3.netzilo.com",
    "L3Token": "",
}
with open(p, "w") as f:
    json.dump(cfg, f, indent=2); f.write("\n")
EOF
unset TOKEN
sudo docker compose config -q
sudo docker compose pull -q support-worker
sudo docker compose up -d support-worker
sudo docker compose restart management
```

Gates, in order. Each one must pass before the next:

```bash
sudo docker compose ps                         # every service Up; support-worker (healthy) within ~1 minute
sudo docker compose exec -T support-worker python -c "
import json, os, urllib.request
req = urllib.request.Request('http://management:80/api/internal/support/runs/probe/steps',
    data=json.dumps({'seq': 1, 'text': 'probe'}).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['SUPPORT_WORKER_TOKEN'], 'Content-Type': 'application/json'},
    method='POST')
print('HTTP', urllib.request.urlopen(req, timeout=10).status)"
                                               # HTTP 200: management loaded the token and the worker reaches it
```

A `401` from that probe means Management did not read the new block: check that
`management.json` parses (`sudo python3 -m json.tool management.json > /dev/null`) and that
Management was restarted after the edit. A `404` means Management started from a file
without `SupportConfig`, which on this layout means the edit went to a different file than
the one mounted. Then, in the dashboard, an owner connects a provider and approves a model
(§8); the Assistant button appears and the first question answers.

Rollback, if a gate fails and the cause is not obvious:

```bash
cd "$C"
sudo docker compose rm -sf support-worker
sudo cp -a "$(ls -t docker-compose.yml.bak-* | head -1)" docker-compose.yml
sudo cp -a "$(ls -t management.json.bak-* | head -1)" management.json
sudo docker compose restart management
```

On AWS and Azure images the same procedure applies in `/opt/netzilo/run`, with one
difference: those images pin every image to a digest and the worker is not in the local
image store, so the `pull` step needs outbound access to `ghcr.io`, which the default
security group and NSG allow. Delete the backup files once the Assistant works: they hold
the same secrets as the live files.

**Behind a corporate proxy.** Add `HTTPS_PROXY` to the worker's environment for the
provider and GitHub. The worker's calls to Management use plain HTTP on the compose network
and are not affected by `HTTPS_PROXY`; if you also set `HTTP_PROXY`, or `ManagementURL` is
an `https://` address, add the Management host to `NO_PROXY` or those calls go to the proxy.
If the proxy inspects TLS, mount its CA bundle into the container and point `SSL_CERT_FILE`
at it.

## 7. Kubernetes and other orchestrators

The worker is an ordinary stateless container. What it needs:

| Item | Value |
|---|---|
| Image | `ghcr.io/netzilo/net-support-worker`. Check that your nodes can pull it: if the registry answers 403 to an anonymous pull, create an image pull secret from a GitHub token with `read:packages` and reference it as below |
| Port | `8080`, HTTP |
| Health | `GET /healthz` returns 200; use it for liveness and readiness |
| User | runs as uid `10001`, non-root; writes only under `/data` |
| Ingress | none; a cluster-internal service only |
| Replicas | any number; each turn is one self-contained HTTP stream, so no session affinity |
| Resources | a starting point that has proven enough: request 100m CPU and 256 MiB, limit 1 CPU and 1 GiB |

A minimal set of objects, in the same namespace as Management:

```yaml
apiVersion: v1
kind: Secret
metadata: { name: net-support-worker-secrets }
type: Opaque
stringData:
  SUPPORT_WORKER_TOKEN: "<the same value Management gets as NB_SUPPORT_WORKER_TOKEN>"
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: net-support-worker }
spec:
  replicas: 1
  selector: { matchLabels: { app: net-support-worker } }
  template:
    metadata: { labels: { app: net-support-worker } }
    spec:
      securityContext: { runAsNonRoot: true, runAsUser: 10001 }
      imagePullSecrets: [{ name: ghcr-pull-secret }]   # omit when the image pulls anonymously
      containers:
        - name: worker
          image: ghcr.io/netzilo/net-support-worker:latest
          ports: [{ containerPort: 8080 }]
          envFrom: [{ secretRef: { name: net-support-worker-secrets } }]
          env:
            - { name: SUPPORT_MAX_AGENT_STEPS, value: "16" }
          readinessProbe: { httpGet: { path: /healthz, port: 8080 } }
          livenessProbe:  { httpGet: { path: /healthz, port: 8080 }, initialDelaySeconds: 60 }
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits: { cpu: "1", memory: 1Gi }
          volumeMounts: [{ name: data, mountPath: /data }]
      volumes: [{ name: data, emptyDir: {} }]
---
apiVersion: v1
kind: Service
metadata: { name: net-support-worker }
spec:
  type: ClusterIP
  selector: { app: net-support-worker }
  ports: [{ port: 8080, targetPort: 8080 }]
```

The `emptyDir` at `/data` keeps the worker working under `readOnlyRootFilesystem`. The
worker answers `/healthz` only after its start-up runbook sync, which waits up to a minute
when GitHub is slow, hence the liveness delay; with syncing off (§5) it starts in seconds.
Pin the image to a version tag or digest in production rather than `latest`.

On the Management side:

- `SupportConfig.WorkerURL` = `http://net-support-worker.<namespace>.svc.cluster.local:8080`.
- `NB_SUPPORT_WORKER_TOKEN` from the same Secret as the worker's token.
- `NB_SUPPORT_MANAGEMENT_URL` (or `SupportConfig.ManagementURL`) = Management's
  cluster-internal HTTP service address, for example
  `http://<management-service>.<namespace>.svc.cluster.local`. Do not point it at the public
  ingress.

If the cluster enforces network policies: allow ingress to the worker from Management only;
allow egress from the worker to Management, to DNS, and to the destinations in §2.

## 8. Turning it on for people

| Who | What makes it appear |
|---|---|
| Administrators | A provider connected and a model approved for the Assistant (`30-activity-reports-and-integrations.md` §4a). Nothing else. |
| Regular users | Additionally, Settings → Permissions: *Allow regular users to use the AI Assistant* and the allowed groups (`25-users-groups-and-account-settings.md` §4). They get it on the Workplace page, for their own devices only (`39-end-user-self-service.md`). |
| Level 3 escalation | A Netzilo Cloud service-account token in `L3Token` or `NB_SUPPORT_L3_TOKEN`, then a Management restart. Offered to administrators only, and each escalation still needs their approval in the chat (`12-escalation-package.md` §10). |

Every session gets a *Support session created* event in Activity → Events. The eye icon on
it opens the read-only log of that session, for any user's session and after the owner
deletes it; administrators only (`34-event-catalogue.md`).

## 9. Operating it

- **State and backup.** The worker keeps nothing. Sessions, messages, steps and the audit
  trail live in Management's database, so the normal database backup covers them
  (`02-server-operations.md` §6). Nothing to back up on the worker.
- **Logs.** `sudo docker compose logs --tail=200 support-worker`. One line per turn:
  `turn done session=<id> run=<id> steps=<n> answer_chars=<n> in=<tokens> out=<tokens> …`.
  The worker does not log conversation text; a failed turn logs the exception, which for a
  provider error can include the provider's response body.
- **Restart order.** The worker goes last and alone; it depends on nothing but Management
  (`02-server-operations.md` §3).
- **Rotating the shared token.** Both sides change together, and the turn in flight at that
  moment fails:

```bash
cd "$C"
sudo cp -a management.json "management.json.bak-$(date +%s)"
sudo cp -a docker-compose.yml "docker-compose.yml.bak-$(date +%s)"
NEW="$(openssl rand -base64 32 | tr -d '=+/' | head -c 40)"
sudo NEW="$NEW" python3 - <<'EOF'
import json, os, re
new = os.environ["NEW"]
cfg = json.load(open("management.json"))
cfg["SupportConfig"]["WorkerToken"] = new
json.dump(cfg, open("management.json", "w"), indent=2)
text = open("docker-compose.yml").read()
text, n = re.subn(r"(SUPPORT_WORKER_TOKEN=)\S+", lambda m: m.group(1) + new, text)
assert n == 1, "expected exactly one SUPPORT_WORKER_TOKEN line"
open("docker-compose.yml", "w").write(text)
EOF
unset NEW
sudo docker compose up -d --no-deps support-worker
sudo docker compose restart management
```

  On Kubernetes, update the one Secret both sides read, then restart both deployments. If
  Management takes the token from `NB_SUPPORT_WORKER_TOKEN`, that variable wins over the
  file, so change it there.

## 10. Security posture

- **No ingress** and a shared token on both directions of the Management–worker link.
- **The caller's own permissions.** The worker holds no standing credential; each turn
  carries the token of the person in the chat, and Management enforces what it allows.
- **Writes need approval.** An API write, a change on someone else's device, or an
  escalation is proposed in the chat and executed only after the person approves it, by
  Management, exactly as proposed.
- **Credential fields in results are blanked** before a tool result is stored or replayed:
  JSON fields named like tokens, passwords, API keys, setup keys and the client's own keys.
  A secret printed as plain text by a shell command is not recognised, so the runbooks tell
  the agent not to print one.
- **No tracing.** The worker refuses to start with third-party tracing configured.
- **Non-root, and nothing written outside `/data`.**
- **Runbook integrity.** The synced runbooks come from the public repository over HTTPS and
  are validated before use. Pin `SUPPORT_SKILLS_REF` to a tag or commit where the runbooks
  must be reviewed before they change, or turn syncing off (§5).

## 11. Troubleshooting

Messages as the person in the chat sees them, and as the logs print them:

| Symptom | Cause | Fix |
|---|---|---|
| No Assistant button for anyone | no model approved for the Assistant | `30-activity-reports-and-integrations.md` §4a |
| Button for admins, not for a regular user | the user switch is off, or the user is in none of the allowed groups | §8; `25-users-groups-and-account-settings.md` §4 |
| `support agent is not configured on this deployment` | no `SupportConfig`, or empty `WorkerURL` | §3; on a compose install from before the worker, `01-server-install.md` §0 |
| `support agent is unavailable, try again shortly` | Management cannot reach the worker: container down or still starting, wrong `WorkerURL`, or a network policy | `docker compose ps support-worker`; the health check in §5; `WorkerURL` |
| `support worker returned HTTP 401` | the two tokens differ | make `SUPPORT_WORKER_TOKEN` equal Management's token (§9 rotation does both) |
| Worker log `step push rejected by management: HTTP 401 (check SUPPORT_WORKER_TOKEN)` | same mismatch, seen from the worker; answers still arrive but the audit log has no steps | same fix |
| Worker `Restarting`, log `refusing to start: SUPPORT_WORKER_TOKEN is empty` | token not in the worker's environment | §4; `01-server-install.md` §1.5 |
| Worker `Restarting`, log `refusing to start: LANGCHAIN_… is set` | a tracing variable in the environment | remove it |
| `The AI provider rejected the configured API key` | key wrong, expired or revoked | owner fixes the provider in Integrations → Artificial Intelligence |
| `The configured model was not found at the AI provider` | model id not served by that provider or gateway | approve another model, or correct the id |
| `The AI provider is rate-limiting this deployment` / `… is unavailable right now` | provider limits or outage, after the worker's own retries | wait; raise the provider quota |
| `The AI provider could not be reached (network error or timeout)` | no egress to the provider, proxy not configured, or TLS inspection without the CA | §2; the proxy note in §6 |
| `This turn ran longer than allowed and was stopped` / `the turn timed out` | the worker's or Management's turn deadline | ask a narrower question; review the timeouts in §3 and §4 |
| The status line shows `step limit reached; answering with what I have` and the answer is incomplete | `SUPPORT_MAX_AGENT_STEPS` too low for device diagnoses | raise to `16` (§4) |
| The agent does not follow a runbook fix you expected | the worker serves an older copy | `/healthz` in §5; outbound to `github.com`; or pull a newer worker image |
| `skills: 0` in `/healthz` | the image's baked copy is missing and nothing synced | pull the current worker image; check outbound to `github.com` |
| Worker log `skills refresh failed (keeping current copy)` | GitHub unreachable or the ref does not exist | harmless when intended; otherwise §2 and `SUPPORT_SKILLS_REF` |
| Worker log `provider rejected reasoning for …` | the model or gateway does not support extended reasoning | nothing to do: served without it from then on; set `SUPPORT_THINKING_BUDGET_TOKENS=0` to skip the one retry |
