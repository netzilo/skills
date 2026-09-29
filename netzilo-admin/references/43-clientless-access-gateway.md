---
id: '43'
title: Clientless access and the Netzilo gateway
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 65955
sections:
- id: '1'
  title: How it works
  chars: 3035
- id: '2'
  title: Requirements and support
  chars: 1901
- id: '3'
  title: Turning it on for users
  chars: 12445
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '4'
  title: Where the gateway can run
  chars: 3084
- id: '5'
  title: The bundled gateway (compose installs)
  chars: 2386
- id: '6'
  title: Adding the gateway to a server installed without it
  chars: 8411
- id: '7'
  title: Running the gateway on another host
  chars: 4441
- id: '8'
  title: Kubernetes and other orchestrators
  chars: 1514
- id: '9'
  title: Configuration reference
  chars: 2761
- id: '10'
  title: Operating it
  chars: 7860
- id: '11'
  title: Troubleshooting
  chars: 14020
- id: '12'
  title: Introducing it to existing installations
  chars: 2301
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '13'
  title: Limits
  chars: 848
---
# Clientless access and the Netzilo gateway

Clientless access lets a user reach internal resources from a browser that has only the
Netzilo browser extension: no Netzilo client, no VPN adapter, no administrator rights on
the device. The extension sends internal traffic to a **Netzilo gateway**, an
authenticated HTTPS proxy, and the gateway carries it into the network under that user's
own policies. This file is the one place that says how it works, where the gateway can
run, how to install it with a server, add it to a server installed without it, run it
anywhere else, operate it, read its logs and fix it.

Turning it on for users (the account switch and the profile's **Proxy** tab) is §3.
Posture checks for browser sessions are §3.4 here and `21-posture-checks.md`. The
dashboard pages themselves are `25-users-groups-and-account-settings.md` (Settings →
Permissions) and `26-profiles-secure-workplace.md` (the extension's Proxy tab).

## 1. How it works

1. The user signs in with **Login** in the extension popup.
2. The extension asks management how this browser should route
   (`GET /api/users/current/routing`, then `GET /api/users/current/pac`), at login and
   every 5 minutes after.
3. Management computes the answer as if the user had just added a new device: the
   user's groups (plus **All**), the policies those groups are sources of whose posture
   checks the browser passes, the routes and nameserver groups distributed to them, the
   peer DNS zone and the network range. The answer is a PAC script.
4. The extension installs the PAC as the browser's proxy setting. It sends only internal
   names and addresses to the gateway with the `HTTPS <host>:<port>` directive; everything
   else stays `DIRECT` (or goes to the corporate proxy, §3.3).
5. The gateway answers the browser's first request with `407`. The extension answers the
   challenge with the user's sign-in token as the password and the browser's device
   assertion as the user name. The user never sees a prompt.
6. The gateway verifies the token with management's REST API, then starts a **session**
   for that user on that browser: a virtual peer, a *guest*, logged in as the user,
   registered in the user's account as an ephemeral peer named `vp-<n>-PROXY`. The
   request goes through that guest's WireGuard tunnel, so the user reaches exactly what
   their policies allow. The gateway resolves internal names through the guest, so they
   never need public DNS.
7. After 60 minutes without traffic the session stops; the next request starts it again
   in a few seconds (the first request after an idle period is the slow one: about 10 to
   20 seconds while the guest logs in and builds its tunnel).

If a Netzilo client is installed on the device, the extension leaves routing to the client
and installs nothing. A client seen on the device in the last 7 days counts as installed,
even while stopped. A client that starts while the extension is logged in on its own takes
over within about a minute: the extension checks the client's local port once a minute
and, when the client answers, removes the gateway PAC and shows the client's state. The
popup's refresh button makes the same check at once.

**Not the same thing as published applications.** The gateway serves browsers that carry
the extension, on `8443`. A private application published at an address of its own,
opened in any browser with nothing installed, is served by the **Netzilo reverse
proxy**, a separate container behind the front door on `443`
(`44-published-applications.md`); its peers are `vp-<n>-RPROXY` (§10.3).

What the gateway checks on every request: a valid credential of a user of this server
(or of the bound account, §4.3), the per-user device limit, and that the destination is
not the gateway host itself or a link-local address. What it does not do: inspect TLS
content, or reach anything the user's own tunnel cannot, except public addresses from its
own host when `--egress public` (§9).

## 2. Requirements and support

| Part | Requirement |
|---|---|
| **Browsers** | Chromium-based browsers (Google Chrome, Microsoft Edge, and other Chromium browsers that run the extension) and Mozilla Firefox 128 or later. **Safari is not supported**: Safari extensions cannot set a proxy or answer a proxy login; Mac and iPhone users need the Netzilo client. |
| **Extension** | the Netzilo browser extension 5.0.455 or later. Nothing else on the device. |
| **Firefox** | the extension must be allowed in private windows (`about:addons` → Netzilo Secure Browser → **Run in Private Windows: Allow**). Firefox lets an extension change the proxy only then. |
| **Management and dashboard** | a release with clientless access (5.0.455 or later), dashboard from the same release. Check below. |
| **Gateway** | the `net-gateway` container (`ghcr.io/netzilo/net-gateway`), linux/amd64. On Netzilo Cloud it is already provided at `srv.netzilo.com:8443`. |
| **Certificate** | the gateway is an HTTPS proxy: it needs a certificate for the name browsers use, trusted by those browsers (a public CA such as Let's Encrypt, or a corporate CA the browsers trust). A self-signed certificate does not work for browsers. |
| **Network** | browsers reach the gateway on its port (default `8443/tcp`); the gateway reaches management (REST and gRPC), signal and the relay exactly like a Netzilo client, and through its guests the user's routing peers. |

Does this management server support it? From anywhere:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://<api-host>/api/users/current/routing
```

`401` means the endpoint exists (clientless access is supported). `404` means management
is older than clientless access; upgrade management and the dashboard first
(`02-server-operations.md` §4.2). An extension talking to an older server shows
**Private access: unavailable** and never installs a proxy.

## 3. Turning it on for users

### 3.1 The account switch

Dashboard: **Settings → Permissions → Allow clientless access**, and optionally
**Gateway proxy address**. API: the account's `settings.clientless_access_enabled`
(boolean) and `settings.clientless_proxy_address` (`host:port`), written with
`PUT /api/accounts/{accountId}` (read the schema first, `33-api-request-schemas.md`).

- Empty address = the management server's own host on port `8443`. Set it only when the
  gateway runs on another host or port (§6, §7). It is the name browsers connect to, so it
  must match the gateway's certificate.
- The switch gates **automatic** routing only. Off, management serves no computed PAC to
  anyone and browsers remove it at their next refresh (within 5 minutes). A profile set to
  **Custom PAC** keeps being served either way.
- Changing the switch is recorded as the activity *Account clientless access enabled* /
  *disabled*, and changing the address as *Account clientless proxy address updated*
  (`34-event-catalogue.md`).
- The gateway does not read the switch. It authenticates every request and confines each
  user to their own policies whatever the switch says.

### 3.2 The profile's Proxy tab

Dashboard: **Endpoint → Profiles**, a profile with the **Enterprise Browser Extension**,
tab **Proxy**. API: the profile's `components.extension_proxy`:
`{"mode": "disabled" | "auto" | "custom", "pac": "<script>", "upstream": {"type": "none" | "proxy" | "pac", "value": "…"}}`.

| Mode | The browser gets |
|---|---|
| **Disabled (default)** | no proxy; the extension removes anything it installed |
| **Automatic** | the computed PAC, following every change to routes, DNS and policies |
| **Custom PAC** | the admin's script verbatim (must define `FindProxyForURL`, at most 64 KiB); route to the gateway with `"HTTPS <host>:<port>"` |

**Generate** (Custom PAC) fills the editor with what Automatic would serve for chosen user
groups (1 to 200) on a chosen operating system, evaluating posture checks for a current
version of that OS (`POST /api/profiles/pac`, admin only). A custom PAC is a snapshot:
regenerate it after changing routes, DNS or policies.

Which profile applies: among the **enabled** profiles for the browser's operating system
whose groups include one of the user's groups and that have a proxy setting, the first by
name. Avoid overlapping profiles with different proxy settings for the same users.

### 3.3 Corporate proxies

Automatic mode only. **Corporate proxy** = *None (direct)*, *Proxy host:port*, or *PAC
URL*.

- A proxy set in the **browser** (fixed or PAC) is detected by the extension and chained:
  everything the Netzilo PAC does not send to the gateway goes to it. Nothing to
  configure.
- A proxy set only in the **operating system** is invisible to extensions: enter it in the
  profile. Without it the extension notices that public sites stop loading after it
  installs its PAC, removes the PAC again and reports *upstream proxy required: an
  operating-system proxy is in use*.
- A proxy enforced by **browser policy** or owned by **another extension** cannot be
  changed: the extension reports *proxy managed by policy* / *proxy managed by another
  extension* and installs nothing.

### 3.4 Posture checks for browser sessions

Posture checks are evaluated against the browser twice: when management computes the
routing, and when the gateway's guest logs in (the guest reports the browser, never the
gateway host).

| Check | Evaluated against |
|---|---|
| OS version | the OS and version the browser reports. **Approximate for a session**: the gateway reads them from the User-Agent, where Chromium freezes macOS at `10.15.7` and Windows 11 still says `10.0`. Management's routing prefers the version the extension reads from the browser itself, so the PAC and the session can disagree (below) |
| Netzilo version | the extension's version |
| Geolocation, peer network range | the browser's public IP address (§7.4 for a gateway on another host) |
| Process | always fails for browser sessions |
| Netzilo endpoint checks (firewall, antivirus, disk encryption, …) | always fail for browser sessions when enforced |
| **Netzilo Gateway** (Advanced Endpoint Settings) | **passes only for browser sessions**: the guest reports itself as a gateway session; every device with the client reports false |

A browser is not a managed endpoint; this is by design, not a fault. To give browser users
a resource that desktop users reach behind endpoint checks, add a separate policy for the
browser users without those checks. The **Netzilo Gateway** item is how such a policy is
kept to browser users: a posture check with only that item on, attached to the policy,
admits gateway sessions and nothing else. Management applies it when it computes the
routing and when the session's guest logs in; a change to the check or the policy reaches
a running session within about a minute, as any policy change does.

Rules for the **Netzilo Gateway** item (API: `advanced_settings_check.netzilo_gateway_check`):

- **Attach it to network policies only.** On a profile's domain settings, a workspace or an
  MCP filter it is evaluated by the device's client, which is never a gateway session, so
  it blocks every device.
- **Combine it with nothing an endpoint must report.** A check holding the gateway item
  and, say, a firewall item fails for sessions on the firewall item and for devices on the
  gateway item: it admits nobody.
- **It is reported, not attested**, like the Workspace and Browser signals. It
  distinguishes a gateway session from a device; it is not proof against a modified client.
  Its value is segmentation (browser users get their own policy), not device trust.

**OS version checks on sessions.** Because a session's OS version comes from the
User-Agent, a minimum-version rule behaves unexpectedly for browsers: a macOS minimum above
10.15 fails every Mac session, and a Windows 11 build minimum fails every Windows session.
The PAC may still send the resource to the gateway (routing used the browser's real
version), and the session is then refused (`403`/`504`). Give browser users a policy
without OS minimums, or gate them on the Netzilo Gateway item instead.

**Expected "Peer access blocked" events.** Each session evaluates the account's policies
for itself when it starts. Every policy whose posture checks it fails, typically those with
endpoint items, is recorded as *Peer access blocked* with the reason *Endpoint checks
cannot be satisfied by a browser session* (or the failing item's reason). Many browser users
in the source groups of endpoint-gated policies therefore produce many such events; they
record the design working, not a fault.

### 3.4a Several servers: which one the extension follows

The extension follows one Netzilo server at a time: the one the user last signed in on.
A dashboard is a *portal*; the extension keeps a list of portals it knows (`go.netzilo.com`
by default, plus any it was connected to) and the *active* one. Extension 5.0.460 and later.

- **A known portal is opened** (its Workplace loads in the foreground tab, or the user
  logs in through the extension's Login): the extension switches to it — it logs out of
  the previous server (PAC removed, token cleared, policies dropped) and signs in here.
  The previous server's browser session is not touched. Merely focusing an already open
  dashboard tab, a token renewal, or a background tab never switches; the Workplace of
  the other server shows the Connect button instead. A session must name the API the
  portal registered (its descriptor, or its first sign-in); one naming another API is
  refused.
- **An unknown portal** (a self-hosted server the extension has not seen): the Workplace
  shows *Netzilo extension — connect to this server*; the button asks the extension, which
  reads the server's descriptor itself (`https://<portal>/.well-known/netzilo.json`, served
  by every dashboard) and shows **its own confirmation over the page** (an extension
  frame the page can neither read nor click; its buttons arm only once the frame has been
  visible and unobscured for a moment) with the server's name and API; where a page cannot
  show it, a small window centered over the browser instead. Nothing on the web page can
  grant this. *Not now* (clicking outside the card, leaving the page, or closing the window)
  declines that portal for a week; the button asks again regardless (from the active tab,
  at most once a minute per server). A site without the descriptor cannot be connected,
  and the window says so. A page that is not a known portal learns only that the
  extension is installed, never which server it follows.
- **Logout** counts only from the active portal; a logout on another server's tab is ignored.
- **A connected desktop client** owns the login: no portal event switches or signs the
  extension out.
- **Policy** (browser enterprise policy, managed storage of the extension): `portals`
  (origins that need no confirmation), `activePortal`, `lockPortal` (only that server; other
  portals' Workplace says the choice is managed). Chrome/Edge: the extension's
  `3rdparty`/managed policy with `{"portals": ["https://portal.example.com"],
  "activePortal": "https://portal.example.com", "lockPortal": true}`; Firefox: the
  `3rdparty.Extensions.<extension id>` policy with the same keys.
- **Language:** the popup, the Workplace confirmation and the block pages follow the
  language chosen in the Workplace (sent with the login, with every session, and when the
  user switches it there); without one, the browser's UI language. English and Turkish;
  English otherwise. From 5.0.460.
- **Where to look:** the popup shows the active server under the logo; the extension's log
  (`portals` category) records every decision (`session from <origin>: switch`, `prompt`,
  `locked`, …).

### 3.5 What users see

The popup's **Private access** row: the gateway address (the PAC is installed; clicking
shows it, the copy icon copies it with "Settings copied to clipboard"); **off** (logged in,
but no routing for this user); **unavailable** (the PAC could not be installed; hovering
shows the reason, §11.2); **On/Off** (a Netzilo client is installed; the row shows its
state); **Session expired – Login** on the popup's button means the extension's token was
refused and could not be renewed (typically after a long browser shutdown): opening the
Workplace signs the extension in again by itself (extension 5.0.460 and later — the
dashboard hands its current session to the extension on load, after every token renewal
and on request, and a dashboard logout logs the extension out too; a connected desktop
client keeps owning the login instead). Only a *connected* client takes this row; a client that is installed but stopped
or logged out leaves routing to the gateway (extension 5.0.456 and later; before, a client
seen within seven days blocked the PAC). Sessions appear in **Endpoint → Peers** as
`vp-<n>-PROXY` (§10.3).

The dashboard's **Workplace** page shows tabs for what is on the computer: with the
Netzilo client (with or without the extension) **Applications** and **Devices**; without
the client but with the extension routing through a gateway, **Applications** and a
**Private access** status; with neither, **Applications** only. The status is **the
extension's own report**, the way the desktop client reports its own device: the page
asks the Netzilo extension in this browser, and the extension answers with whether its
proxy is installed, through which gateway, the session's peer as the gateway named it on
the last credential probe (name, tunnel address, since when) and its last error. Nothing
is looked up on the server and nothing is inferred from the user's other browsers.
Without an answer (no extension, one older than 5.0.458, or gateway mode off in it)
nothing about private access is shown. **Online** (green) while the extension has its
proxy installed and no error, **Suspended** (amber) otherwise, with the extension's
reason in the hover. Hovering shows the gateway, the session's name and address, since
when it is up, and the extension's version. The page
asks every 30 seconds while it is visible and not at all in a background tab; a new
session can take up to 30 seconds to appear, while online/offline follows at the next
poll. With the client running, the Devices tab is back as before.

## 4. Where the gateway can run

The gateway is a single stateless-enough container (it keeps only a session counter and,
in node mode, its peer key). It does not have to run next to management: it talks to
management over its public URL like any client does.

| Form | When | Section |
|---|---|---|
| **Bundled** next to management in the server's compose stack | a self-hosted server installed with a current installer; the default | §5 |
| **Added later** to an existing compose server | a server installed before the gateway existed | §6 |
| **Another host**, anywhere | the gateway must sit in a DMZ, another region, another cloud, next to the resources, or the customer uses Netzilo Cloud and wants their own gateway | §7 |
| **Kubernetes** or another orchestrator | management runs there, or the customer standardises on it | §8 |

### 4.1 Shared mode and node mode

| | Shared mode (default) | Node mode |
|---|---|---|
| Set by | neither `--setup-key` nor `--pat` | `--setup-key` or `--pat` |
| Own peer | none | the gateway is a peer of its own account |
| Who may start sessions | every user of the management server, or one account with `--service-pat` | users of the account `--service-pat` names (required, unless `--allow-any-account`) |
| Traffic the user's tunnel does not cover | goes out of the gateway host to public addresses (`--egress public`) or nowhere (`--egress off`) | goes through the gateway peer's own routes first, then the host |
| Readiness | management's REST API answers | the gateway peer is connected |

Use **shared mode** in almost every case. Node mode exists for a gateway that should add
its own routes (for example an exit node) for everyone using it.

### 4.2 The management URL

`--management-url` is the management server the gateway verifies credentials with (REST)
and logs its guests into (gRPC):

- **Same compose stack or cluster**: the internal address, `http://management:80` (compose)
  or `http://<management-service>:80` (Kubernetes). Browser addresses reach management
  unchanged this way.
- **Anywhere else**: the public URL, `https://<domain>` (self-hosted) or
  `https://srv.netzilo.com` (Netzilo Cloud). REST and gRPC both use port `443`.

### 4.3 Binding to one account

`--service-pat` (or the environment variable `NZ_GATEWAY_SERVICE_PAT`) binds the gateway
to the account that token belongs to: a verified user outside that account gets `407`.
The token must be able to list the account's users (an **Admin** service user; `Team →
Agents`); the gateway re-reads the member list every minute, so new users work within a
minute.

**Always bind a gateway that points at a multi-tenant management server** (Netzilo Cloud,
or a self-hosted multi-tenant server). Unbound, any user of any account there could use it
and its public egress. A gateway bundled with a single-account server needs no binding.

The token's expiry is the gateway's: when it expires, every new session is refused and the
log says *the gateway's service credential was refused*. Create it with a long expiry and
rotate it before it lapses (§10.5).

## 5. The bundled gateway (compose installs)

A server installed with a current installer (custom one-liner, AWS or Azure image) runs
ten containers; the tenth is `gateway`. Check:

```bash
if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
cd "$C" && sudo grep -c '^  gateway:' docker-compose.yml     # 1 = bundled, 0 = see §6
sudo docker compose ps gateway
```

What the installer writes:

- Shared mode, `--management-url http://management:80`, listening on `:8443`, published on
  host port `8443`; admin endpoints on `:9090` inside the container only.
- **Let's Encrypt** installs: Caddy's data directory is the named volume
  `netzilo_caddy_data`, mounted read-only into the gateway at `/caddy`; the gateway serves
  the certificate Caddy obtains for the domain (`--tls-cert-dir /caddy/caddy/certificates
  --tls-domain <domain>`) and picks up renewals within 30 seconds, without a restart.
- **Provided** or **self-signed** certificate installs: the certificate folder is mounted
  at `/certs` (`--tls-cert /certs/fullchain.pem --tls-key /certs/privkey.pem`); replacing
  the files is picked up the same way. A self-signed certificate works only for browsers
  that trust it (§2).
- **Plain-HTTP** installs (`http://` or an IP without a certificate) get **no gateway**:
  there is no certificate to serve.
- Runs as root only to read the TLS key, with every capability dropped and
  `no-new-privileges`. Session counter in the named volume `netzilo_gateway`.
- Firewall: the cloud templates open `8443/tcp`; on a self-managed host open it yourself
  (`02-server-operations.md` §11).

Verify a bundled gateway:

```bash
cd "$C"
sudo docker compose logs --tail=50 gateway | grep 'gateway:'
# expected: "gateway: version <v> starting in shared mode (management http://management:80, egress public)"
#           "gateway: TLS certificate loaded from …"
#           "gateway: proxy listening on [::]:8443 (https)"
curl -sS -o /dev/null -w 'gateway -> HTTP %{http_code}\n' --proxy "https://<domain>:8443" http://example.com/
# expected: 407 (the gateway wants a credential)
echo | openssl s_client -connect "<domain>:8443" -servername "<domain>" 2>/dev/null | openssl x509 -noout -subject -issuer -enddate
```

The image is distroless (no shell, no curl inside); run checks from the host. For the
admin endpoints from the host, see §10.2.

## 6. Adding the gateway to a server installed without it

A compose server installed before the gateway existed runs nine containers and has no
`gateway` service. **Do not re-run the installer to add it: that wipes the server**
(`02-server-operations.md` §10). The gateway joins in place, like the AI worker does
(`42-ai-assistant-self-hosted.md` §6.1).

### 6.1 Before you start

1. Management and dashboard are a release with clientless access: the `401` check in §2.
   If it answers `404`, update them first (`02-server-operations.md` §4.2), management then
   dashboard.
2. The server has a certificate: `grep -E '^(NETBIRD_DOMAIN|NETBIRD_HTTP_PROTOCOL|TLS_MODE)=' /opt/netzilo/netzilo-state.env`.
   An `http` install cannot host a gateway; run one on another host with its own
   certificate instead (§7).
3. Take a backup (`02-server-operations.md` §6). The procedure also keeps timestamped
   copies of the files it edits.
4. Tell the customer: the **caddy** container is recreated on Let's Encrypt servers, so the
   dashboard and API are unreachable for a few seconds; clients reconnect on their own.
   Nothing else restarts.

### 6.2 The procedure

What it does, so it can be checked before it runs: detects the compose directory and the
domain; on a Let's Encrypt server, copies Caddy's current data (with its certificate) out
of the running container, gives Caddy the named data volume `netzilo_caddy_data` and seeds
it with that copy, so no new certificate is requested; on a provided-certificate server,
mounts the same certificate folder Caddy uses; inserts the `gateway` service before the
top-level `volumes:` section, copying management's `extra_hosts` when the install pinned the
domain that way; adds the volumes; validates the file; starts the gateway (and recreates
caddy only when its volume changed). It refuses to run twice.

```bash
if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
cd "$C"
sudo grep -q '^  gateway:' docker-compose.yml && echo "gateway is already present; stop here"
DOMAIN=$(sudo sed -n 's/^NETBIRD_DOMAIN=//p' /opt/netzilo/netzilo-state.env | tr -d '"')
echo "domain: $DOMAIN"
stamp=$(date +%s)
sudo cp -a docker-compose.yml "docker-compose.yml.bak-$stamp"
# Let's Encrypt servers: keep Caddy's current certificate before its container changes.
sudo docker cp caddy:/data "caddy-data-seed-$stamp"
sudo DOMAIN="$DOMAIN" python3 - <<'EOF'
import os, re
dom = os.environ["DOMAIN"]
if not dom: raise SystemExit("no NETBIRD_DOMAIN in /opt/netzilo/netzilo-state.env")
p = "docker-compose.yml"; text = open(p).read()
if re.search(r"^  gateway:", text, re.M): raise SystemExit("gateway already present")
def block(name):
    m = re.search(r"^  %s:\n(?:(?!^  \S).*\n)*" % name, text, re.M)
    if not m: raise SystemExit("no %s service in docker-compose.yml" % name)
    return m
caddy, mgmt = block("caddy"), block("management")
provided = re.search(r"^      - (\S+):/data/caddy/certificates/?\s*$", caddy.group(0), re.M)
ssl = re.search(r"^      - (\S+):/etc/ssl/certs:ro\s*$", caddy.group(0), re.M)
extra = re.search(r"^    extra_hosts:\n(?:^      .*\n)+", mgmt.group(0), re.M)
vols = ["  netzilo_gateway:\n"]
if provided:
    cert_mount = "      - %s:/certs:ro\n" % provided.group(1)
    tls = '"--tls-cert", "/certs/fullchain.pem", "--tls-key", "/certs/privkey.pem",'
else:
    if not re.search(r"^      - netzilo_caddy_data:/data\s*$", caddy.group(0), re.M):
        cv = re.search(r"^    volumes:\n", caddy.group(0), re.M)
        if not cv: raise SystemExit("caddy has no volumes: list")
        at = caddy.start() + cv.end()
        text = text[:at] + "      - netzilo_caddy_data:/data\n" + text[at:]
        vols.append("  netzilo_caddy_data:\n")
        open(".gateway-caddy-changed", "w").write("1\n")
    cert_mount = "      - netzilo_caddy_data:/caddy:ro\n"
    tls = '"--tls-cert-dir", "/caddy/caddy/certificates", "--tls-domain", "%s",' % dom
svc = (
    "  # Clientless access gateway (browser extension -> HTTPS proxy on :8443), added\n"
    "  # after install. Shared mode: each browser session is a guest peer of its user.\n"
    "  gateway:\n"
    "    image: ghcr.io/netzilo/net-gateway:latest\n"
    "    container_name: gateway\n"
    "    restart: unless-stopped\n"
    "    user: '0:0'\n"
    "    cap_drop:\n"
    "      - ALL\n"
    "    security_opt:\n"
    "      - 'no-new-privileges:true'\n"
    "    networks:\n"
    "      - netzilo\n"
    + (extra.group(0) if extra else "")
    + "    depends_on:\n"
    "      - management\n"
    "    ports:\n"
    "      - '8443:8443'\n"
    "    volumes:\n"
    + ("      - %s:/etc/ssl/certs:ro\n" % ssl.group(1) if ssl else "")
    + "      - netzilo_gateway:/var/lib/netzilo-gateway\n"
    + cert_mount
    + "    command: [\n"
    '      "run",\n'
    '      "--management-url", "http://management:80",\n'
    '      "--listen", ":8443",\n'
    "      " + tls + "\n"
    '      "--admin-listen", ":9090",\n'
    '      "--idle-timeout", "60m",\n'
    '      "--data-dir", "/var/lib/netzilo-gateway",\n'
    '      "--log-file", "console",\n'
    '      "--log-level", "info"\n'
    "    ]\n"
)
top = re.search(r"^volumes:\n", text, re.M)
if not top: raise SystemExit("no top-level volumes: section in docker-compose.yml")
text = text[:top.start()] + svc + "volumes:\n" + "".join(vols) + text[top.end():]
open(p, "w").write(text)
EOF
sudo docker compose config -q && echo "compose file valid"
```

Then start it, **in the same shell** (it reuses `$C` and `$stamp`). On a Let's Encrypt
server whose Caddy just gained its data volume, create the volume, seed it with the copied
data, and only then recreate caddy:

```bash
cd "$C"
sudo docker compose pull gateway
if [ -f .gateway-caddy-changed ]; then
  sudo docker compose up --no-start --no-deps gateway              # creates netzilo_caddy_data, touches nothing running
  VOL=$(sudo docker volume ls -q --filter label=com.docker.compose.volume=netzilo_caddy_data)
  IMG=$(sudo docker inspect caddy --format '{{.Config.Image}}')
  sudo docker run --rm --entrypoint sh -v "$VOL":/to -v "$PWD/caddy-data-seed-$stamp":/from:ro "$IMG" -c 'cp -a /from/. /to/'
  sudo docker compose up -d --no-deps caddy gateway               # caddy: a few seconds of downtime
  sudo rm -f .gateway-caddy-changed
else
  sudo docker compose up -d --no-deps gateway
fi
sudo docker compose logs --since 2m gateway | grep 'gateway:'
```

`caddy-data-seed-<stamp>` holds a private key: delete it once the gateway serves the
certificate (`sudo rm -rf "$C"/caddy-data-seed-*`).

### 6.3 Gates

| Gate | Check | Expected |
|---|---|---|
| G1 | `sudo docker compose ps` | ten services `Up`, including `gateway` |
| G2 | gateway log | `TLS certificate loaded from …` and `proxy listening on [::]:8443 (https)`, no `no TLS certificate yet` after the first minute |
| G3 | `curl -sS -o /dev/null -w '%{http_code}\n' https://<domain>/` | `200`: the dashboard came back after caddy's recreation |
| G4 | `openssl s_client -connect <domain>:8443 -servername <domain>` | the server's certificate, same issuer as on 443 |
| G5 | the proxy test in §11.1 with a real user's token | `200` for an internal URL |

Then open `8443/tcp` inbound (§6.4) and switch clientless access on (§3).

### 6.4 The firewall rule on marketplace servers

Existing AWS and Azure deployments were created without `8443`. Add it to the instance's
security group or network security group; limit the source to the users' networks when
they are known.

```bash
# AWS: the stack's security group
aws ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 8443 --cidr 0.0.0.0/0
# Azure: the deployment's NSG (pick a free priority)
az network nsg rule create -g <resource-group> --nsg-name <nsg> -n Allow-Gateway-8443 \
  --priority 1010 --direction Inbound --access Allow --protocol Tcp --destination-port-ranges 8443
```

A host firewall (`ufw`, `firewalld`) does not see Docker-published ports; the cloud rule is
what matters there.

### 6.5 Rollback

```bash
cd "$C"
sudo docker compose stop gateway && sudo docker compose rm -f gateway
sudo cp -a "docker-compose.yml.bak-<stamp>" docker-compose.yml
sudo docker compose up -d --no-deps caddy        # only if caddy's volume was added
```

Switch clientless access off first (§3.1) so browsers remove the PAC. The
`netzilo_caddy_data` volume can stay; it only holds Caddy's certificates.

## 7. Running the gateway on another host

Any Linux host with Docker (linux/amd64), anywhere browsers can reach and that can reach
management, works: a DMZ, another region or cloud, a site next to the resources, or the
customer's own network when they use Netzilo Cloud.

### 7.1 What the host needs

- A DNS name for the gateway (for example `gw.example.com`) and a certificate for it that
  the browsers trust.
- Inbound `8443/tcp` (or the port you choose) from the browsers.
- Outbound like a Netzilo client: `443/tcp` to management (REST and gRPC), signal and the
  identity provider; `3478/udp` and the relay ports to the relay; UDP to peers for direct
  connections. The guests reach the user's routing peers through WireGuard; nothing is
  opened towards them.

### 7.2 Run it

Keep the service token out of the command line: put it in an environment file readable
only by root.

```bash
sudo install -d -m 700 /etc/netzilo-gateway
sudo sh -c 'umask 077; printf "NZ_GATEWAY_SERVICE_PAT=%s\n" "<admin service token>" > /etc/netzilo-gateway/env'
sudo docker volume create netzilo_gateway
sudo docker run -d --name netzilo-gateway --restart unless-stopped \
  --user 0:0 --cap-drop ALL --security-opt no-new-privileges \
  -p 8443:8443 -p 127.0.0.1:9090:9090 \
  --env-file /etc/netzilo-gateway/env \
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
  -v netzilo_gateway:/var/lib/netzilo-gateway \
  ghcr.io/netzilo/net-gateway:latest \
  run --management-url https://<domain-or-srv.netzilo.com> \
      --listen :8443 \
      --tls-cert /etc/letsencrypt/live/gw.example.com/fullchain.pem \
      --tls-key /etc/letsencrypt/live/gw.example.com/privkey.pem \
      --admin-listen :9090 --idle-timeout 60m \
      --data-dir /var/lib/netzilo-gateway --log-file console --log-level info
sudo docker logs --tail=30 netzilo-gateway | grep 'gateway:'
```

- **Certificate files**: mount the whole `/etc/letsencrypt` directory, not only `live/…`:
  the files in `live/` are links into `archive/`. Renewals by certbot are picked up within
  30 seconds. With a Caddy on that host, use `--tls-cert-dir <caddy data>/caddy/certificates
  --tls-domain gw.example.com` instead. Any other PEM pair works with `--tls-cert/--tls-key`.
- **Binding**: `NZ_GATEWAY_SERVICE_PAT` binds the gateway to one account (§4.3). Required
  against Netzilo Cloud; recommended whenever the gateway is not on the server itself.
  Expected log: `gateway: bound to an account with <n> users`.
- **Egress**: `--egress public` (default) lets the gateway fetch public addresses from its
  own host for requests the user's tunnel does not cover; `--egress off` allows only the
  tunnel. Private ranges on the gateway host's side are refused unless listed in
  `--egress-allow`.

### 7.3 Point the account at it

Set **Settings → Permissions → Gateway proxy address** to `gw.example.com:8443`. Every
browser of the account then uses this gateway (§3.1). One account uses one gateway
address; to spread users over several gateways, use Custom PAC profiles per group, each
pointing at its gateway.

### 7.4 Browser addresses through a self-hosted server's reverse proxy

A gateway sends each browser's public address to management as `X-Forwarded-For` when its
guests log in; management records it as the session peer's connection address (the
public IP and location shown in Peers, and the input of geolocation and network-range
posture checks, §3.4).

- In the same compose stack or cluster (§5, §8) the gateway talks to management directly
  and the address arrives as sent.
- A gateway **on another host** reaches a self-hosted server through its Caddy. Caddy
  replaces a forwarded address from a source it does not trust, so management records the
  gateway host's address for every session, and geolocation checks judge the gateway's
  location instead of the browser's. Trust the gateway host in the server's `Caddyfile`
  (global options, the existing `servers` block), then reload Caddy:

  ```
  {
    servers :80,:443 {
      protocols h1 h2c
      trusted_proxies static <gateway-public-ip>/32
    }
  }
  ```

  ```bash
  cd "$C" && sudo docker compose restart caddy      # a few seconds of dashboard downtime
  ```

  Trust only the gateway's own address: any host listed there may state a browser address.
- On Netzilo Cloud nothing is needed.

Verify: a session from a known browser appears in **Endpoint → Peers** with that browser's
public IP, not the gateway's.

## 8. Kubernetes and other orchestrators

The container contract, whatever runs it:

| Item | Value |
|---|---|
| Image | `ghcr.io/netzilo/net-gateway:<tag>`, linux/amd64, distroless |
| Arguments | `run --management-url http://<management-service>:80 --listen :8443 --tls-cert /tls/tls.crt --tls-key /tls/tls.key --admin-listen :9090 --data-dir /var/lib/netzilo-gateway --idle-timeout 60m --revalidate 10m --max-sessions 2000 --max-devices-per-user 5 --log-file console --log-level info` |
| TLS | a `kubernetes.io/tls` Secret mounted at `/tls` (mode `0440`, readable by the container's group); a renewed Secret (cert-manager) is picked up within 30 seconds |
| Writable paths | `/var/lib/netzilo-gateway` (an `emptyDir`, or a PersistentVolumeClaim to keep the session counter across restarts) and `/tmp` |
| Security | runs non-root with a read-only root filesystem when the key is readable by its group; no capabilities |
| Probes | liveness `GET /healthz` on `9090`; readiness `GET /readyz` on `9090` |
| Service | `LoadBalancer` (or NodePort) exposing `8443/tcp`; `externalTrafficPolicy: Local` keeps browser addresses visible |
| Replicas | one. Each replica keeps its own sessions; with more, use client-IP session affinity so a browser keeps hitting the same one |
| Secrets | `NZ_GATEWAY_SERVICE_PAT` from a Secret when binding (§4.3) |

Logs: `kubectl logs deploy/<gateway-deployment> --since=1h`. The gateway can share the
ingress's public IP on another port where the cloud load balancer supports it.

## 9. Configuration reference

All settings are command-line options of `gateway run`; three can come from the
environment instead. Compose passes them as the service's `command:`, Kubernetes as the
container's `args`. Change them there and recreate the container
(`sudo docker compose up -d --no-deps gateway`).

| Option | Default | Meaning |
|---|---|---|
| `--management-url` | (required) | management server, `http(s)://host[:port]` (§4.2) |
| `--listen` | `:8443` | proxy address |
| `--tls-cert`, `--tls-key` | — | PEM certificate and key; reloaded when the files change |
| `--tls-cert-dir`, `--tls-domain` | — | take the certificate for a domain from a Caddy storage directory (`…/caddy/certificates`) |
| `--insecure-plain-http` | off | serve without TLS on a non-loopback address; credentials travel in clear. Never for browsers |
| `--admin-listen` | `127.0.0.1:9090` | `/healthz` and `/readyz`; empty disables |
| `--idle-timeout` | `60m` | stop a session's tunnel after this long without traffic |
| `--revalidate` | `10m` | re-present each session's credential to management this often |
| `--rechallenge` | `2m` | make each browser present its proxy credential afresh this often (one `407` per session per interval, answered by the extension), so an extension whose device seed changed after a reinstall gets a session under its current device id; the old session is stopped once silent for two minutes |
| `--max-sessions` | `2000` | concurrent sessions in total |
| `--max-devices-per-user` | `5` | concurrent browser sessions per user |
| `--max-connections` | `20000` | accepted proxy connections |
| `--start-concurrency` | `10` | sessions starting at once |
| `--ready-timeout` | `30s` | how long a request waits for its session's tunnel |
| `--login-timeout` | `90s` | how long a session's first login may take |
| `--egress` | `public` | `public` or `off` (§7.2) |
| `--egress-allow` | — | private CIDRs the gateway host may reach for traffic outside the tunnel |
| `--service-pat` / `NZ_GATEWAY_SERVICE_PAT` | — | bind to one account (§4.3) |
| `--setup-key` / `NZ_GATEWAY_SETUP_KEY`, `--pat` / `NZ_GATEWAY_PAT` | — | node mode (§4.1) |
| `--allow-any-account` | off | node mode without binding |
| `--name` | host name | node mode: the gateway peer's name |
| `--data-dir` | `/var/lib/netzilo-gateway` | session counter (`vp.seq`), node-mode peer key |
| `--log-level` | `info` | `trace`, `debug`, `info`, `warn`, `error` |
| `--log-file` | `console` | a path, or `console` |

Fixed behaviour, not configurable: 256 open connections per session; 20 failed logins
from one address within 5 minutes block that address for 5 minutes (a user whose
credential the gateway already accepted is not blocked); dials time out after 20 seconds.

## 10. Operating it

### 10.1 Logs

```bash
cd "$C" && sudo docker compose logs --tail=200 gateway          # compose, bundled or added
sudo docker compose logs -f --since 10m gateway | grep 'gateway:'
sudo docker logs --tail=200 netzilo-gateway                      # another host (§7)
kubectl logs deploy/<gateway-deployment> --since=1h              # Kubernetes
```

The gateway logs its own lines with the prefix `gateway:`; the other lines come from the
guests (the same engine as the Netzilo client: management and signal connections, network
map, posture evaluation) and read like a client log (`13-log-interpretation.md`). For a
per-request trace (every dial and its outcome), set `--log-level debug` and recreate the
container; put it back to `info` afterwards. Logs never contain a credential.

Key lines:

| Line | Meaning |
|---|---|
| `gateway: version <v> starting in shared mode (management <url>, egress public)` | start; the version and mode in use |
| `gateway: <what>: management not reachable yet, retrying in <d>` | management down or still starting; the gateway waits up to 5 minutes, then exits (and restarts under `restart: unless-stopped`) |
| `gateway: bound to an account with <n> users` / `any user of <url> may start a session (no account binding)` | binding state (§4.3) |
| `gateway: TLS certificate loaded from <file>` / `reloaded from <file>` | certificate in use / renewal picked up |
| `gateway: no TLS certificate yet (<source>): <reason>` | nothing to serve yet (Caddy still obtaining it, wrong domain, wrong mount); handshakes fail and `/readyz` says so |
| `gateway: proxy listening on [::]:8443 (https)` | serving |
| `gateway: session vp-<n>-PROXY (<email>) ready: peer <ip> <fqdn>, device <public-ip> <os>, <browser>, extension <v>, device <id>` | a browser session is up |
| `gateway: session vp-<n>-PROXY (<email>) now from <public-ip> <os>, <browser>` | the same session's browser details changed |
| `gateway: session vp-<n>-PROXY (<email>) stopped: <reason>` | `idle`, `access token expired`, `credential no longer accepted: …`, `re-login refused: …`, `guest exited`, `gateway shutting down` |
| `gateway: session … tunnel not ready: …` / `start failed: …` / `login refused: …` | the guest could not log in or connect (§11.3) |
| `gateway: credential refused for "<user>" from <ip>: …` | a wrong, expired or foreign token |
| `gateway: <ip> blocked for 5m0s after 20 failed logins` | an address is guessing tokens, or a misconfigured client retries |
| `gateway: <email> already has 5 browser sessions; a new device from <ip> refused` | the device limit |
| `Posture check '<name>' FAILED at <check>` (guest line) | a policy's posture check fails for that browser (§3.4) |

### 10.2 Health

The admin endpoints listen inside the container on `9090` (compose does not publish them).
From a compose host, through a throwaway container on the same network:

```bash
cd "$C"; NET=$(sudo docker inspect gateway --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')
IMG=$(sudo docker inspect caddy --format '{{.Config.Image}}')
sudo docker run --rm --network "$NET" --entrypoint wget "$IMG" -qO- http://gateway:9090/readyz
```

`/healthz` answers `ok` with `mode=`, `sessions=`; `/readyz` answers `ready` (HTTP 200) or,
with HTTP 503, one of: `management unreachable`, `gateway peer disconnected from
management` (node mode), `session limit reached`, `no TLS certificate yet`, `draining`.

### 10.3 Sessions in the Peers list

- Each browser session is a peer named `vp-<n>-PROXY` in the user's account, platform
  *browser*, showing the browser's OS, the extension version as its client version, the
  browser's public IP and location. The number is the gateway's own counter; two gateways
  can each have a `vp-1-PROXY` (their DNS labels differ); identify a session by its peer
  id, user and device.
- They are **ephemeral**: management deletes them once offline for a while. Only a peer
  named exactly `vp-<digits>-PROXY` and reporting the browser platform is treated that
  way; any other device, whatever its name, is an ordinary peer.
- One session per user per browser (a stable device identity per browser profile); logging
  in again reuses it. Five per user at most.
- Blocking or deleting a user, or revoking their token, ends their sessions within the
  revalidation interval (10 minutes).
- **What the peer page shows for a session:** a **Browser** row under Operating System
  (for example `Edge 154.0.0.0`; Chrome, Edge, Opera, Firefox and Safari are told apart),
  and the **Netzilo Gateway** indicator lit in the Security Score row. API: `browser` and
  `browser_version` on the peer (set only for sessions), `meta.netzilo_meta.is_netzilo_gateway`.
  Chrome and Edge report only their major version (`154.0.0.0`); Firefox its full one.
- **Security score:** a session scores 50 on Windows, macOS and Linux (grade C), the
  gateway signal being the only one it reports, and 100 on Android and iOS
  (`24-peers-and-setup-keys.md` §2).
- **`vp-<n>-RPROXY` is a reverse-proxy tunnel, not a browser's session.** It is a
  user's tunnel for published applications (`44-published-applications.md` §10.3): one
  per user, public address and operating system, kept across restarts, reporting every
  browser it has served. It carries the Netzilo Gateway posture item like an
  extension session, but it is not a browser's session: `gateway-sessions` leaves it
  out and it never makes the Workplace's Private access status Online.
- **No device tools.** A session runs no device-tool executor: every tool request returns
  `unsupported` with *remote support tools are not available on this client*. Diagnose a
  session with §11, never with `36-device-tools.md`.
- **A browser whose extension was reinstalled** keeps using its cached proxy credential,
  so its old session stays online under the old device id for up to `--rechallenge`
  (2 minutes); then the gateway makes the browser present its credential afresh, a
  session under the new device id appears, and the old one is stopped two minutes
  later. Two connected sessions of one browser for a few minutes after a reinstall are
  expected.
- **Online or not, per user:** `GET /api/users/{userId}/gateway-sessions` lists a user's
  sessions: `id`, `name`, `connected`, `connected_since`, `last_seen`, `browser`,
  `browser_version`, `os`, `connection_ip`, `device_id`, and `matches_request` (the session
  with the caller's public IP and browser). A user may read their own; an administrator any
  user of the account (another user's answers 403 for a regular user, 404 across accounts).
  It takes a user's token or a dashboard login. This is what the Workplace page polls
  (§3.5); it is built to be polled and never slows the account down. `connected` is live;
  a new or deleted session shows within 30 seconds, a role or token change within a minute.

### 10.4 Upgrades

Update the gateway with management and the dashboard, from the same release
(`02-server-operations.md` §4.2 with `S=gateway`). Recreating the container drops every
session; browsers restart theirs on the next request (a few seconds each). Pin the tag you
verified (`02-server-operations.md` §4.4). The first log line shows the version running.

### 10.5 Rotating the service token

Create the new token (**Team → Agents**, the gateway's service user → **Access Tokens**),
replace it in the environment file or Secret, recreate the container, check for `bound to
an account with <n> users`, then delete the old token.

### 10.6 Capacity

A session is a userspace WireGuard peer inside the gateway process: memory grows with
active sessions, CPU with traffic. Size from measurement: watch `sessions=` in `/healthz`
and the container's usage (`sudo docker stats gateway`) during the pilot (§12.2). The
defaults cap one gateway at 2000 sessions and 5 per user.

## 11. Troubleshooting

### 11.1 Test the path without a browser

From any machine that can reach the gateway, with a real user's token (a personal access
token works; the user name is free text):

```bash
export TOKEN=nzl_...     # the user's token; never paste it into a ticket
curl -sS -o /dev/null -w 'internal -> HTTP %{http_code} in %{time_total}s\n' \
  --proxy "https://gw.example.com:8443" --proxy-user "test:$TOKEN" http://<internal-name-or-ip>/
curl -sS -o /dev/null -w 'wrong token -> HTTP %{http_code}\n' \
  --proxy "https://gw.example.com:8443" --proxy-user "test:nzl_wrong" http://<internal-name-or-ip>/
unset TOKEN
```

Expected: `200` (the first call after idle takes 10 to 20 seconds), then `407`. Add
`--proxy-insecure` only to test a gateway whose certificate your machine does not trust;
browsers will still refuse it.

The routing management computes for that user, as a browser would see it:

```bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
curl -sS -A "$UA" -H "Authorization: Token $TOKEN" https://<api-host>/api/users/current/routing | jq '{mode, gateway, zones, match_domains, route_domains, networks}'
curl -sS -A "$UA" -H "Authorization: Token $TOKEN" https://<api-host>/api/users/current/pac | head -20
```

`mode` is `disabled` when the account switch is off, no profile applies for that OS, or the
profile is Disabled. The user agent matters: the profile is chosen by the browser's OS, and
a request without a browser user agent matches no profile.

### 11.2 The popup says "unavailable"

Hovering over **unavailable** shows the reason.

| Reason | Cause | Fix |
|---|---|---|
| `allow Netzilo in private windows (Firefox requires it to set a proxy)` | Firefox, extension not allowed in private windows | `about:addons` → the extension → Run in Private Windows: Allow |
| `proxy managed by policy` / `proxy managed by another extension` | a browser policy or another extension owns the proxy setting | remove the policy or extension, or use the Netzilo client |
| `upstream proxy required: an operating-system proxy is in use` | public sites need an OS-level proxy the extension cannot see | set **Corporate proxy** in the profile (§3.3) |
| `routing: HTTP 404` | management predates clientless access | upgrade management and dashboard (§2) |
| `routing: HTTP <5xx>` or a network error | management unreachable from the browser | check the server (`03-server-troubleshooting.md`); the last installed PAC stays meanwhile |
| `credential refused` / `credential refused by the gateway` | the sign-in expired or the user was blocked | log out and in again in the popup; check the user in Team → Users |
| `no gateway address` | the account has no usable gateway address | set Gateway proxy address (§3.1) |
| `custom mode without a PAC` | Custom PAC profile with an empty script | fill or Generate the script |
| `corporate PAC: HTTP <code>`, `corporate PAC unavailable`, `corporate PAC has no FindProxyForURL` | the corporate PAC URL cannot be fetched or is not a PAC | fix the URL in the profile, or the browser's own PAC setting |

**off** is not an error: the user is logged in but gets no routing (account switch off, no
matching enabled profile for the OS, or the profile is Disabled).

### 11.3 Symptoms

| Symptom | Check | Cause and fix |
|---|---|---|
| `gateway` container restarting | `docker compose logs --tail=50 gateway` | `management URL …: want http(s)://host[:port]` or another start error: fix the command; `management not reachable yet` for 5 minutes, then exit: management is down (`03-server-troubleshooting.md`) |
| `/readyz` says `no TLS certificate yet` | the log's source line | Let's Encrypt: Caddy has no certificate for exactly `--tls-domain` yet (first boot, or the domain differs from the Caddyfile's); provided: wrong mount or file names (`fullchain.pem`, `privkey.pem`) |
| browser: "proxy connection failed" / `ERR_PROXY_CONNECTION_FAILED` / `ERR_TUNNEL_CONNECTION_FAILED` | `openssl s_client -connect <gw>:8443` from the user's network | port 8443 blocked (cloud rule, §6.4), wrong Gateway proxy address, or a certificate the browser does not trust or for another name |
| browser: `ERR_EMPTY_RESPONSE` for internal sites | the PAC's proxy line | a custom PAC uses `PROXY host:8443`; the gateway speaks TLS, use `HTTPS host:8443` |
| a password prompt for the proxy | the popup | the extension is not logged in or not the one answering: log in; a second proxy extension may be interfering |
| `407` repeatedly with a correct token | gateway log `credential refused …` | token for another server, expired, or the user is outside the bound account (§4.3) |
| `429 too many devices for this user` | log `already has 5 browser sessions` | idle sessions end after 60 minutes; or raise `--max-devices-per-user` |
| `429 too many failed logins` | log `blocked for 5m0s` | wait 5 minutes; find what keeps presenting a wrong token |
| `503` with `Retry-After` | `/readyz` | management unreachable, session limit, or the session's tunnel was not ready in 30 s; the browser retries |
| `403` for one internal site, others work | the user's policies, guest line `Posture check … FAILED` | the policy excludes that resource for this user, or a posture check fails for browsers (§3.4) |
| `403` for the gateway host or a link-local address | — | refused by design; reach that service another way |
| `504` / `502` | debug log for that destination | the resource did not answer through the tunnel within 20 s, or refused; check the routing peer and the resource (`11-connectivity-diagnosis.md`) |
| internal site loads for some users only | §11.1 routing for each user | different groups or profiles; the PAC only sends what the user may reach |
| public sites broke after enabling | popup reason | an OS-level proxy (§3.3) |
| Peers show the gateway's IP for sessions | §7.4 | remote gateway behind the server's Caddy without `trusted_proxies` |
| Mac or Windows browser users refused a resource that the PAC does send to the gateway | the policy's OS version check | the session's OS version comes from the User-Agent (macOS `10.15.7`, Windows `10.0`); remove OS minimums from browser users' policy or gate it on the Netzilo Gateway item (§3.4) |
| a policy with the Netzilo Gateway item admits nobody | the posture check's other items | an endpoint item in the same check fails every session; keep the gateway item alone in its check (§3.4) |
| desktop or mobile clients lose a domain, a workspace or MCP tools after a posture check was attached | whether it carries the Netzilo Gateway item | clients evaluate profile and filter checks themselves and are never gateway sessions; attach the gateway item to network policies only (§3.4) |
| the activity log fills with *Peer access blocked* for `vp-<n>-PROXY` peers | the reasons | expected for policies with endpoint checks (§3.4); scope those policies' source groups, or leave it |
| Workplace shows **Private access · Suspended** | the hover (the extension's own reason); the popup's Private access row; §10.3 for the user | the extension has no proxy installed or its last gateway probe failed: it is off, logged out or paused, its proxy setting is blocked (the reason says so), or the gateway is down (`/readyz`); it turns Online within 15 s of the gateway answering the extension |
| Workplace still shows **Devices** on a browser-only computer | the popup | the user's routing is off for this browser (§3.2), so no private access is expected; or a Netzilo client answers on this computer |
| Workplace shows *Netzilo extension — connect to this server* although the user is signed in | the popup's server line | the extension follows another server (§3.4a); press the button, confirm in the extension's window |
| the Connect window says the site is not a Netzilo server | `curl -s https://<portal>/.well-known/netzilo.json` | the dashboard is older than the descriptor, or a proxy blocks `/.well-known/`; update the dashboard, allow the path |
| private access stopped after visiting another customer's portal | the popup's server line | the extension switched to the portal that signed in last (§3.4a); sign in again on the intended one, or set `lockPortal` by policy |
| popup button says **Session expired – Login**; Workplace shows Applications only | the popup row's hover text ("credential refused") | the token lapsed while the browser was closed and the renewal failed; open the Workplace (5.0.460+ signs the extension in from the dashboard's session) or click Login |
| popup says **Off** and no PAC although the client is not running | the extension version | before 5.0.456 a client seen within seven days blocked the gateway PAC; update the extension, or wait for the marker to expire |
| every new session refused, log `the gateway's service credential was refused` | the service token | expired or revoked: rotate (§10.5) |
| **one browser** cannot open an internal `http://` name while the same user reaches it by IP, from another browser, or from another device; the guest log shows only `failed to dial … <name>:443 … connection was refused` | the browser's address bar or history shows `https://<name>` although `http://` was typed | the browser pinned the name to HTTPS (HSTS, or a cached permanent redirect) after something answered for that name over HTTPS outside the tunnel; reset that site in the browser and remove what served it (§11.6) |

### 11.3a One browser pinned an internal name to HTTPS: the cache reset

The one browser-side reset worth doing, and only under these conditions, all of them:

1. **One browser, one computer.** The same name works for the same user from another
   browser on that computer, from another device, or by the resource's IP address in the
   failing browser. (The IP working rules out policy, route and posture.)
2. **The resource is plain HTTP.** From somewhere that works, `curl -sI http://<name>/`
   answers and `https://<name>/` is refused or times out. The application itself sends
   no `Location: https://…` redirect (if it does, that is the application's base URL,
   §11.3 "links go to its internal name", not the browser).
3. **The failing browser goes to HTTPS.** Its address bar or history shows
   `https://<name>/` although `http://` was typed; the error page says *Secure
   Connection Failed*, *The proxy server is refusing connections* or
   `ERR_CONNECTION_REFUSED`; the gateway's guest log for that browser's session (§10.1)
   shows `failed to dial via Netzilo route <name>:443: … connection was refused` and
   no dial on the real port. With the Netzilo client instead of the extension, the
   client log shows the same `:443` dials.
4. **The name resolves correctly where it is resolved.** The `:443` line names the
   tunnel address, or `diag.dns` on a client returns it.

Then the cause is the browser: it stored an HSTS pin for the name, or a cached
permanent redirect, because something once answered for that name **over HTTPS outside
the tunnel**: a public wildcard record for the internal domain pointing at a public
server (a staging server, a reverse proxy whose application domain overlaps the peer
DNS zone), a captive portal, or a Netzilo reverse proxy older than the September 2026
release, which sent `Strict-Transport-Security` on its *There is no application at this
address* page. Firefox does not upgrade a typed `http://` name by itself; without the
pin, look at the application.

**The reset.** It removes that one site's stored data in that browser (cookies and
logins for the site included), nothing else. Say so and get a "yes" first
(`41-remediation-workflows.md` §13).

| Browser | Steps |
|---|---|
| Firefox | Library (Ctrl/Cmd+Shift+H) → search the name → right-click the entry → **Forget About This Site**. Removes the HSTS pin, the cache and the cookies for that host. No restart. |
| Chrome, Edge | `chrome://net-internals/#hsts` (`edge://net-internals/#hsts`) → **Delete domain security policies** → the host name → Delete. Then Settings → Privacy → Clear browsing data → **Cached images and files**, last hour (the cached redirect). |
| Safari | Settings → Privacy → **Manage Website Data** → the site → Remove (Safari keeps HSTS with site data); then History → Clear History, last hour. |

Then open `http://<name>/` again. Verified when the page loads, the address bar stays
`http://`, and the guest or client log shows the dial on the real port. Never reset
the whole browser, reinstall the extension or the client, or change the server or DNS
for this symptom.

**Then the cause, for the administrator:** `dig +short <name> @1.1.1.1`. An internal
name that resolves publicly points at what served it over HTTPS; remove that record (a
reverse proxy's application domain must never be the peer DNS zone,
`44-published-applications.md` §3), and update a reverse proxy that sends HSTS on its
404 (§11.3 of `44`). Until that is gone, every user who resolves the name outside the
tunnel is pinned again.

### 11.4 Debugging the extension

Chromium: `chrome://extensions` (or `edge://extensions`) → Developer mode → the Netzilo
extension → **service worker** → Console. Firefox: `about:debugging#/runtime/this-firefox`
→ the extension → **Inspect**. In that console:

```js
chrome.storage.local.get('nz_gw_state', r => console.log(r.nz_gw_state))
```

shows `enabled`, `installed`, `mode`, `gateway`, `version`, `chain` and `error` (the
reason §11.2 lists); `pac` is the installed script. The browser's view of its proxy:
`chrome://net-internals/#proxy` (Chromium) or `about:preferences` → Network Settings
(Firefox). Never copy the extension's storage into a ticket: it holds the sign-in token.

### 11.5 Before escalating

Collect: the gateway version (first log line), mode, and management URL scheme; the last
200 gateway log lines around the failure; `/readyz`; the §11.1 results; the popup reason;
the browser and extension version. Redact user e-mails if the customer asks. Then follow
`12-escalation-package.md`.

## 12. Introducing it to existing installations

Clientless access needs three things an existing installation may lack: a management and
dashboard release that has it, a gateway, and the extension version that uses it. Take them
in this order.

### 12.1 By delivery path

| Installation | Management and dashboard | Gateway | Firewall |
|---|---|---|---|
| Netzilo Cloud | already current | provided at `srv.netzilo.com:8443`; optional own gateway (§7, bound) | — |
| Custom one-liner, current installer | current | bundled (§5) | open `8443/tcp` on a self-managed host |
| Custom one-liner, older | update both (`02-server-operations.md` §4.2) | add in place (§6), never re-run the installer | open `8443/tcp` |
| AWS or Azure image, current | current | bundled | template opens `8443` |
| AWS or Azure image, older | update both (`02-server-operations.md` §4.5) | add in place (§6) | add the rule (§6.4) |
| Kubernetes | update both | deploy the container (§8) | expose the Service |
| Plain-HTTP server | update both | only on another host with its own certificate (§7) | — |

### 12.2 Rollout

1. **Server ready**: the `401` check (§2); the gateway gates (§6.3) or the proxy test (§11.1)
   with an admin's own token.
2. **Pilot group**: create a group for a few users, and a profile for that group and each
   OS they use, with the Enterprise Browser Extension and **Proxy → Automatic**. Leave
   every other profile Disabled.
3. **Extension**: deploy version 5.0.455 or later to the pilot (browser policy or store). On
   Firefox, allow it in private windows as part of the deployment.
4. **Switch on**: Settings → Permissions → Allow clientless access.
5. **Verify with the pilot**: the popup shows the gateway address; an internal site loads;
   the user's `vp-<n>-PROXY` session appears in Peers with their public IP. Check posture:
   resources behind endpoint checks will not be reachable from browsers (§3.4) — decide per
   resource whether browser users need a separate policy.
6. **Expand** group by group. Users who also have the Netzilo client keep using it; the
   extension steps aside for them automatically.
7. **Tell users** what to expect: sign in from the popup; the first internal page after a
   break takes a few seconds; Safari is not supported (`17-end-user-guide.md`).

## 13. Limits

- Safari cannot use clientless access (§2).
- Browser sessions never pass process checks or Netzilo endpoint checks (§3.4).
- Only TCP through the browser: HTTP and HTTPS sites, and anything the browser opens through
  its proxy. Other protocols need the Netzilo client.
- A custom PAC does not follow later changes to routes, DNS or policies (§3.2).
- Sessions stop after 60 minutes idle; the first request after that is slow (§1).
- One gateway address per account through the account setting; several gateways need
  custom PACs per group (§7.3).
- A gateway on another host behind a self-hosted server's Caddy needs `trusted_proxies`
  for browser addresses to be recorded (§7.4).
- Published applications (an address of their own, no extension) are the reverse proxy's
  job, not the gateway's (`44-published-applications.md`).
