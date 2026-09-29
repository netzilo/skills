---
id: '44'
title: Published applications and the Netzilo reverse proxy
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 49567
sections:
- id: '1'
  title: How it works
  chars: 3956
- id: '2'
  title: Requirements and support
  chars: 2320
- id: '3'
  title: Turning it on for the tenant
  chars: 3169
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '4'
  title: Publishing an application
  chars: 4142
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '5'
  title: What users see
  chars: 2116
- id: '6'
  title: 'Non-interactive access: scripts and services'
  chars: 2156
- id: '7'
  title: Where the reverse proxy runs
  chars: 1532
- id: '8'
  title: Self-hosted installation
  chars: 7348
- id: '9'
  title: Configuration reference
  chars: 2160
- id: '10'
  title: Operating it
  chars: 6306
- id: '11'
  title: Troubleshooting
  chars: 9618
- id: '12'
  title: Supporting a user who cannot open an application
  chars: 2606
  requires:
  - api
  executable_on:
  - dashboard-assistant
  - netzilo-harness
  - human-operator
- id: '13'
  title: Limits
  chars: 1171
---
# Published applications and the Netzilo reverse proxy

Publish a private web application at an address of its own (`crm.apps.example.com`)
so that users open it in **any browser**, with nothing installed, after signing in at the
Workplace. Every request travels through that user's own private connection: the
application is reached with the user's access, never with the server's. This is the
second way into a private network without the Netzilo client; the first, the browser
extension and the gateway's HTTPS proxy, is `43-clientless-access-gateway.md`.

Not an nginx replacement: one address is one application, no path routing, no caching,
no TCP publishing, and nothing is reachable that the user's own tunnel cannot route.

Read §1 first. Turning it on is §3 and §4 (API). Users' questions are §5 and §12.
Installing the reverse proxy on a self-hosted server is §7 and §8; Netzilo Cloud
customers skip those. Logs and health are §10; symptoms are §11.

---

## 1. How it works

1. An administrator turns publishing on for the tenant (**Settings → Permissions →
   Allow published applications**, §3) and publishes an application (**Edge →
   Applications**, §4): an **address**, a **target** (`http://10.1.2.3:8080`), the
   **groups** that may open it, and whether it is **enabled**.
2. The address points at the **reverse proxy**: a wildcard DNS record for the
   application domain (`*.apps.example.com`) at the reverse proxy's front door. On Netzilo
   Cloud that is `*.netzilo.app`, already provided; on a self-hosted server it is the
   server's own address, and the `reverse-proxy` container behind Caddy (§7).
3. A user opens `https://crm.apps.example.com/`. The reverse proxy has no session for
   that browser on that address, so a page navigation is sent to the **Workplace**
   (`/publish-auth` on the dashboard), and a fetch, XHR or API call gets `401` with a
   JSON body naming the sign-in address.
4. The Workplace signs the user in if needed (the usual identity-provider login), checks
   that the address is one the user may open, and hands the user's sign-in token to the
   application's address (`POST https://crm.apps.example.com/.netzilo/login`, a
   form post bound to a state the reverse proxy set on the browser). The reverse proxy
   verifies the token with management, reads what this user may open
   (`GET /api/users/current/published-apps`), and admits or refuses.
5. Admitted: the reverse proxy sets a **session cookie for that address only**, sends
   the browser back to the Workplace's dialog, which shows *Logging in* while the user's
   tunnel comes up and then opens the application. Refused: the dialog shows **Access
   Denied** with a single **Logout** button.
6. From then on every request on that address is proxied through the user's **tunnel**:
   a virtual peer of the user, named `vp-<n>-RPROXY`, registered in the account as an
   ephemeral peer, with that user's policies, routes and DNS. The target is dialled
   through that tunnel and nowhere else. The application gets two headers naming the user
   (`Nz-User-Id`, `Nz-User-Email`), and the address it was published under in
   `X-Forwarded-Host`; redirects and cookies it sets for its internal name are rewritten
   to the published address. Its certificate is never verified (a private service behind
   an authenticated tunnel; self-signed and internal certificates are the rule).
7. The session lasts 12 hours at most and is re-checked against management every
   10 minutes: an application removed, a group changed or a user blocked takes effect
   within that interval; a token management no longer accepts ends the session at once.
   The next navigation goes through the Workplace again, silently when the Workplace
   session is still alive.
8. The user's tunnel is **one per user, public address and operating system**, shared
   by all of that user's browsers and API clients there on that system. It stops after
   60 minutes without traffic and is started again on the next request, as the same peer
   (§10.3). A second application
   opened from the same browser needs no new sign-in prompt: the Workplace already has
   the session, and only the cookie for the new address is issued.

**Published never means public.** The address answers only signed-in users the
application admits; everyone else gets the sign-in redirect or, for an address nobody
published, `404 There is no application at this address`. What the user can then reach
is exactly what their policies allow: a target the user's tunnel cannot route answers
**Access Failed**, not the page.

**Two different "reverse proxies."** `43-clientless-access-gateway.md` §7.4 talks about
the *server's* reverse proxy, Caddy in front of management. This file is about the
Netzilo **reverse proxy**, the component that publishes applications. Where a sentence
could mean either, this file says *Caddy* or *the ingress* for the front door.

## 2. Requirements and support

| Part | Requirement |
|---|---|
| **Management and dashboard** | a release with published applications (September 2026 or later), dashboard from the same release. Check below. |
| **Reverse proxy** | on Netzilo Cloud, provided (`*.netzilo.app`). Self-hosted: the `net-reverse-proxy` container (`ghcr.io/netzilo/net-reverse-proxy`, linux/amd64), installed by the current engine when an application domain is given (§8), or added to an existing server (§8.3). |
| **Browsers** | any current browser, desktop or mobile; no extension, no client. Cookies must be allowed for the application's address and for the Workplace; JavaScript on. A browser that blocks third-party cookies is fine (the cookies are first-party on each address). |
| **DNS** | a **wildcard** record for the application domain pointing at the reverse proxy's front door: `*.netzilo.app` on Cloud (already there); on self-hosted `*.apps.example.com → <server public IP>`. Only the names actually published answer. |
| **TLS** | a certificate for every published name. Cloud: managed. Self-hosted: Caddy obtains one per published name on first use (Let's Encrypt), or the provided certificate must cover `*.<application domain>` (§8.2). Self-signed and internal certificates work only in browsers that trust them. |
| **Network** | browsers reach the front door on `443`; the reverse proxy reaches management like a client and, through each user's tunnel, that user's routing peers. Nothing new to open on a self-hosted server: published applications use the same `443`. |
| **The user** | a user of the tenant, in one of the application's groups, with a policy that lets their peers reach the target's network (a route, and a policy from one of their groups to it; §11.3). |

Does this management server support it? From anywhere, no token needed:

```bash
curl -sS -w ' %{http_code}\n' 'https://<api-host>/api/published-apps/exists?domain=check.example.com'
```

`{"published":false} 200` means published applications exist on this server (the answer
is about that name). `404` means management is older than the feature; upgrade
management and the dashboard first (`02-server-operations.md` §4.2). The Workplace side:
`https://<dashboard>/publish-auth` answers `200` on a dashboard that has it, `404` on an
older one.

## 3. Turning it on for the tenant

**Settings → Permissions**, at the bottom:

- **Allow published applications** (`published_apps_enabled`). Off by default. While it is
  off nothing is published: the Applications page shows a notice, every published
  address answers *There is no application at this address*, and the reverse proxy stops
  serving the tenant's applications within 30 seconds. Existing applications keep their
  settings and come back when the switch is turned on again. **A server upgraded to this
  release starts with the switch off.**
- **Application domains** (`published_app_domains`): the domains the tenant publishes
  under, each with the addresses its wildcard record points at
  (`[{"domain":"apps.example.com","addresses":["203.0.113.10"]}]`). Each row has a
  **Verify** link: management resolves a random name under the domain through public
  resolvers and reports *The wildcard record points to the gateway*, *… points elsewhere:
  <addresses>*, or *No wildcard record found for this domain*. It is a check, not a
  gate: a domain can be saved before its record exists.

Rules on the domains:

- On a **multi-tenant server** (Netzilo Cloud, and any self-hosted server with more
  than one account) every published address must be a name **under one of the tenant's
  application domains**; anything else is refused with `422` and the modal says *Not
  under an application domain*. On a single-account self-hosted server any address is
  allowed.
- An address is unique across the whole server, first come, first served, decided by
  the database the moment the application is saved (two tenants saving the same name at
  once: one wins, the other is told *already published by another account*). On Cloud
  every tenant publishes under the shared `netzilo.app`, so `grafana.netzilo.app` belongs
  to whichever tenant published it first; the availability check says *Unavailable* to
  everyone else. Choose distinctive labels (`grafana-acme.netzilo.app`).
- An application domain is unique across tenants too: a domain another tenant already
  uses, or a name under or above one (`apps.acme.com` next to their `acme.com`), is
  refused when the settings are saved (`412 … is used by another account`). The shared
  Cloud domain is the exception every tenant adds.
- Do not use the server's own domain, nor anything under the peer DNS domain
  (`netzilo.network`): names there are resolved inside every tunnel and would never reach
  the reverse proxy (§11.3).

Netzilo Cloud: add the domain `netzilo.app` with the address the wildcard resolves to
(`dig +short anything.netzilo.app`), and Verify shows the tick. Self-hosted: the
application domain given at install (§8), with the server's public IP, which the
installer prints as the next steps and writes into `CREDENTIALS`.

API: `PUT /api/accounts/{accountId}` carries both fields inside `settings` with every
other setting (`33-api-request-schemas.md`; the dashboard sends the whole settings object,
and so must you). `GET /api/published-apps/domains/check?domain=apps.example.com` is the
Verify link: `{"configured":true,"matches_gateway":true,"resolves_to":["203.0.113.10"]}`.

## 4. Publishing an application

**Edge → Applications** (administrators). The table lists name, **Address**, target,
groups and an **Active** switch per row; filters All / Active / Inactive and by group; a
search box. **Add Application** opens a two-step modal:

**Application**

| Field | Rule |
|---|---|
| **Address** | the label, with a picker of the tenant's application domains as suffix (`crm` + `.apps.example.com`), or **Custom address** for a full hostname. Lowercase FQDN, no `https://`, no path. As you type, the availability check answers: **Available** (and, once the DNS answer is in, *points to the gateway*, *but points elsewhere: <ip>* or *no DNS record yet*, none of which blocks saving), **Unavailable** — *This address is already published* (by this or any other tenant), **Invalid**, or **Not under an application domain** (§3). |
| **Target** | where the reverse proxy forwards to **through the user's private connection**: `http://` or `https://`, a host name or IP, an optional port, **no path**. Loopback, link-local and cloud-metadata addresses are refused; anything else is accepted here and judged at request time by the user's tunnel. A name is resolved by that tunnel (peer DNS, nameserver groups), so an internal name works when the user's DNS settings resolve it. |
| **Groups** | who may open it: the user must be in one of them (auto-groups and **All** count). Empty means nobody. |
| **Send the address as Host header** (`preserve_host`) | off by default: the target sees its own host name. On for applications that compare the `Host` header with the address they were published under. |
| **Enable Application** | an application off is kept but not served (`404` at its address). |

**Name & Description**: a name, unique within the tenant, shown on the Workplace tile
and in the activity log; an optional description.

Activity (`34-event-catalogue.md`, *Administration*): **Application published**,
**Published application updated**, **Application unpublished**.

**How long until it works.** Management answers the reverse proxy's *is this name
published?* from a cache of 30 seconds, and the reverse proxy keeps its own answer for
30 seconds: a new address answers within a minute of saving; a disabled or deleted one
stops within the same window. The certificate is the other delay on self-hosted Let's
Encrypt installs: Caddy obtains it on the **first** visit, a few seconds during which the
first request may fail (§8.2).

API (`33-api-request-schemas.md` for the bodies):

```
GET    /api/published-apps                     the tenant's applications (administrators)
POST   /api/published-apps                     {name, description, domain, target, groups, enabled, preserve_host}
PUT    /api/published-apps/{appId}             same body
DELETE /api/published-apps/{appId}
GET    /api/published-apps/check?domain=crm.apps.example.com[&except=<appId>]
                                               {available, reason: taken|invalid|domain, dns:{resolves_to, matches_gateway, configured}}
GET    /api/users/current/published-apps       what the caller may open: id, name, description, domain, url
                                               (a regular user sees their own list; this is what the Workplace shows)
GET    /api/published-apps/exists?domain=      no token: {"published": bool}; what the reverse proxy asks
```

`except` names the application being edited so its own address counts as available.
Duplicates answer `412`: *an application named "…" already exists* or *… is already
published* (by another tenant: *… by another account*).

**Access is two decisions.** The application's groups decide who may *open* it. The
user's **policies** decide whether their tunnel *reaches* the target: the target's
network must be a route distributed to a group the user is in, allowed by a policy whose
source is one of the user's groups, and the policy's posture checks must pass for the
user's reverse-proxy peer (§10.3). A user admitted to the application whose policies do
not reach the target sees **Access Failed** (§11.3). Nothing about the reverse proxy
widens what a policy allows.

## 5. What users see

- **Workplace → Applications:** every application the user may open appears as a tile
  with its name and address, next to the bookmarks and shortcuts. Opening one goes to
  `https://<address>/` in a new tab.
- **First open, or after 12 hours:** the Workplace's sign-in dialog, the same look as the
  usual login: *Logging in* while the tunnel comes up (a few seconds; 10 to 20 the first
  time in an hour while the user's peer registers), *Login complete*, then the page.
  A user not signed in at the Workplace signs in there first and is brought back.
- **Access Denied** — *Your account is not allowed to open <address>.* — with **Logout**:
  the user is not in the application's groups (§4), or the switch is off. The user's
  administrator decides; nothing on the user's side changes it.
- **Access Failed** — *<address> took too long to answer* or *<address> did not answer* —
  with **Logout**: signed in and admitted, but the application could not be reached
  through the user's connection (§11.3).
- **Sign-in is no longer valid. Open the application again.** — the sign-in link was
  older than 10 minutes or used twice; opening the application again starts a fresh one.
- **Signing out:** the Workplace's **Logout** ends the Workplace session and, in the
  same browser, every published application's session of that user (the reverse proxy is
  told before the token is revoked); the applications ask for a sign-in again at once.
  `https://<address>/.netzilo/logout` ends the session on that one address and returns
  to the Workplace. A session that is not signed out ends at its 12-hour cap, or within
  10 minutes of the token being refused by management.
- A user with the Netzilo client installed uses published applications exactly the same
  way: the browser goes to the published address, and the reverse proxy, not the client,
  carries the request.
- Mobile browsers work the same; nothing is installed.

The Workplace page itself is not required after the sign-in: the cookie on the
application's address carries the session, and a bookmark to the application works.

## 6. Non-interactive access: scripts and services

A script, a monitoring job or a service calls a published application without a browser
by presenting a Netzilo credential on every request:

```bash
curl https://grafana.apps.example.com/api/health \
  -H "X-Netzilo-Bearer: nzl_…"                        # the user's personal access token, or an identity-provider token
  -H "Authorization: Bearer <the application's own token>"   # optional, reaches the application untouched
```

- `X-Netzilo-Bearer` is consumed by the reverse proxy and never reaches the application;
  **`Authorization` and every other header pass through as sent**, so an application that
  expects a bearer of its own gets it. `Proxy-Authorization: Bearer …` is honoured too,
  but a TLS-terminating proxy in front (Caddy on self-hosted, most ingress controllers)
  drops it as hop-by-hop before the reverse proxy sees it: use `X-Netzilo-Bearer`.
- The credential is checked with management like a browser sign-in, and the caller must
  be admitted to the application. The token's owner is the user the application sees.
  Requests share one tunnel with that user's browsers at the same address on the same
  operating system, as far as the client names one (§1).
- Answers are JSON, whatever the `Accept` header says: `401 credential refused`,
  `403 not allowed to open this application`, `404 There is no application at this
  address`, `429 too many attempts` (20 refused credentials from one address in
  5 minutes block that address for 5 minutes, shared with browser sign-ins),
  `503 the credential could not be checked` (management unreachable) or a `503` with
  `Retry-After` while the tunnel is not up yet. Every answer carries `X-Request-Id`
  and the JSON a `request_id`, the value to search the log for (§10.1).
- Create the token as the user who should be seen by the application (**Team → Users**,
  or an **Agent** for a service account; `25-users-groups-and-account-settings.md`), with
  an expiry that matches the job. A token reaches every application its owner is
  admitted to, from anywhere, with no browser posture in the way: treat it like a
  password.

## 7. Where the reverse proxy runs

| Deployment | Front door | Reverse proxy | Sign-in at |
|---|---|---|---|
| **Netzilo Cloud** | `*.netzilo.app`, TLS managed | provided | `https://go.netzilo.com` |
| **Self-hosted, compose** (on-prem one-liner, AWS and Azure images) | Caddy on `443`, a `*.<application domain>` site | the `reverse-proxy` container, plain HTTP on the compose network (`8444`), Caddy trusted as the proxy in front | `https://<server domain>` |
| **Kubernetes** | the ingress controller, a wildcard certificate for the domain | its own Deployment behind a ClusterIP service; the pod network trusted | the dashboard's address |

The reverse proxy is **not the gateway**: two containers, two images, two purposes. The
`gateway` container (`43-clientless-access-gateway.md`) serves browsers that carry the
extension, on `8443`; the `reverse-proxy` container serves published applications behind
the front door on `443`. Both run in the same *shared mode* (no peer of their own; every
session is a guest peer of its user) and both talk to management inside the stack.

Where a proxy terminates TLS in front of it, the reverse proxy believes that proxy's
`X-Forwarded-For` and `X-Forwarded-Proto` (`--publish-trusted-proxies`, §9), so users'
real addresses reach management (§10.3). Give that front proxy a request-body timeout of
its own (Caddy: `servers { timeouts { read_body 30s } }`): the reverse proxy cuts a slow,
unauthenticated body after 30 seconds, but a proxy in front holds the client connection
itself.

## 8. Self-hosted installation

### 8.1 A new install

Give the installer an **application domain**; it installs the `reverse-proxy` container
and Caddy's site for it. The domain must differ from the server's domain (use a subdomain,
`apps.<server domain>`, or any other domain you control) and must not be under
`netzilo.network`.

| Path | Where |
|---|---|
| On-prem one-liner | the prompt *Published applications domain (optional)*, or `NETZILO_APPS_DOMAIN=apps.example.com` in the env file of `01-server-install.md` §1.3; with a provided certificate that lacks `*.apps.example.com`, also `NETZILO_APPS_CERT_FILE` / `NETZILO_APPS_KEY_FILE` |
| AWS CloudFormation | parameter **Published applications domain** (`NetziloAppsDomain`) |
| Azure managed application | **Published applications domain (optional)** on the Basics page |
| Engine directly (`01-server-install.md` §5) | `NETZILO_APPS_DOMAIN`, and for a provided certificate `NETZILO_APPS_CERT_DIR` (a folder with `fullchain.pem` and `privkey.pem` for the wildcard) |

Before or right after the install, create the wildcard record `*.apps.example.com → <the
server's public IP>`. The installer warns when it does not resolve yet and continues.
After the first login: **Settings → Permissions → Allow published applications**, add the
domain with the server's IP, then **Edge → Applications**. The install's `CREDENTIALS`
file ends with these three steps.

The installer refuses the server's own domain and anything under `netzilo.network`, and
installs **without** published applications (a warning, the rest proceeds) when the
`net-reverse-proxy` image cannot be pulled or loaded, or when a provided certificate does
not cover the wildcard and none was given for it. A plain-HTTP install (`use-ip`) never
has them.

Containers: eleven with the reverse proxy (`02-server-operations.md` §2); the offline
image set gains `netzilo-reverse-proxy.tar.gz`, optional. Nothing new in the firewall.

### 8.2 Certificates for the application names

| TLS mode at install | What serves `*.apps.example.com` |
|---|---|
| Let's Encrypt (default) | Caddy **on-demand TLS**: a certificate per published name, obtained on that name's first visit. Before issuing, Caddy asks the reverse proxy (`/tls-ask`) whether management publishes the name, so only real applications ever get one; an unpublished name gets a TLS error, not a certificate. The first visit of a new application can take a few seconds and may fail once while the certificate is being issued. Rate limits are Let's Encrypt's per name; a wildcard is not used (HTTP-01 cannot issue one). |
| Self-signed | the installer adds `*.apps.example.com` to the certificate's names. Browsers trust it only where the certificate is installed (`01-server-install.md`). |
| Provided | used as is when it covers `*.apps.example.com` (the installer checks the names); otherwise a second certificate for the wildcard through `NETZILO_APPS_CERT_FILE` / `NETZILO_APPS_KEY_FILE` (one-liner) or `NETZILO_APPS_CERT_DIR` (engine), mounted for Caddy at `/data/caddy/apps-certificates/`. Rotate it like the main one (`02-server-operations.md` §8.2, the same folder). |

### 8.3 Adding published applications to a server installed without them

For a server installed before September 2026, or installed without an application
domain. Never re-run the installer for this: it wipes the server (`01-server-install.md`
§1.4, §8). Needs a server shell; management and the dashboard must already be a release
with published applications (§2), else upgrade them first (`02-server-operations.md`
§4.2). Let's Encrypt installs only; for a provided certificate the wildcard must be in
it, or add the second certificate as §8.2 and use `tls /data/caddy/apps-certificates/fullchain.pem /data/caddy/apps-certificates/privkey.pem` in place of the `tls { on_demand }` block below.

```bash
C=/opt/netzilo            # /opt/netzilo/run on AWS and Azure images
APPS=apps.example.com     # the application domain; *.apps.example.com -> this server
SRV=$(sudo awk -F= '/^NETBIRD_DOMAIN=/{print $2}' /opt/netzilo/netzilo-state.env)
cd "$C" && sudo cp docker-compose.yml docker-compose.yml.bak-$(date +%F) && sudo cp Caddyfile Caddyfile.bak-$(date +%F)
grep -q 'reverse-proxy:' docker-compose.yml && echo "already present" || echo "adding"
```

Gate 0: the wildcard resolves here, and the image pulls:

```bash
dig +short "nz-check.$APPS" A          # the server's public IP
sudo docker pull ghcr.io/netzilo/net-reverse-proxy:latest
```

Add the service (before the top-level `volumes:` line) and its volume. Keep the
indentation exactly; the network subnet is the installer's `172.20.0.0/24`:

```yaml
  reverse-proxy:
    image: ghcr.io/netzilo/net-reverse-proxy:latest
    container_name: reverse-proxy
    restart: unless-stopped
    cap_drop:
      - ALL
    security_opt:
      - 'no-new-privileges:true'
    networks:
      - netzilo
    depends_on:
      - management
    volumes:
      - /etc/ssl/certs:/etc/ssl/certs:ro
      - netzilo_reverse_proxy:/var/lib/netzilo-reverse-proxy
    command: [
      "run",
      "--management-url", "http://management:80",
      "--listen", "127.0.0.1:8443",
      "--egress", "off",
      "--publish-listen", ":8444",
      "--publish-tls", "none",
      "--publish-trusted-proxies", "172.20.0.0/24",
      "--workplace-url", "https://<server domain>",
      "--admin-listen", ":9090",
      "--idle-timeout", "60m",
      "--data-dir", "/var/lib/netzilo-reverse-proxy",
      "--log-file", "console",
      "--log-level", "info"
    ]
```

```yaml
volumes:
  netzilo_reverse_proxy:
```

If the compose file has an `extra_hosts:` block on the `gateway` service (installs whose
domain resolves to a private address), copy it onto `reverse-proxy` too.

In the `Caddyfile`, add to the global options block (the first `{ … }`):

```
  on_demand_tls {
    ask http://reverse-proxy:9090/tls-ask
  }
```

and a site at the end:

```
*.apps.example.com:443 {
    tls {
        on_demand
    }
    reverse_proxy reverse-proxy:8444
}
```

Apply and gate:

```bash
sudo docker compose config -q && sudo docker compose up -d reverse-proxy && sudo docker compose restart caddy
sudo docker compose logs --tail=20 reverse-proxy | grep 'publishing on'          # Gate 1: "publishing on [::]:8444"
curl -sS -o /dev/null -w '%{http_code}\n' -H 'Accept: application/json' "https://nz-check.$APPS/"   # Gate 2: 404 (a name nobody publishes)
```

Gate 2 proves DNS, the certificate path and Caddy → reverse proxy in one request; `000`
or a TLS error means the wildcard record or the certificate (§11.3). Then **Settings →
Permissions**: the switch and the domain with the server's IP. Rollback: restore the two
`.bak-` files, `sudo docker compose up -d --remove-orphans && sudo docker compose restart caddy`.

### 8.4 Kubernetes

The reverse proxy is its own Deployment with a data volume, a ClusterIP service on its
publish port, an Ingress for `*.<domain>` with a wildcard certificate (DNS-01 through the
DNS provider, since HTTP-01 cannot issue a wildcard), and the arguments of §8.3 with
`--publish-trusted-proxies` set to the pod network and `--workplace-url` to the
dashboard's address. One replica: sessions live in memory. Give the ingress unlimited
request bodies, long read timeouts and no buffering, or uploads and streaming
applications suffer.

## 9. Configuration reference

The binary is the gateway's; these are the reverse-proxy options (the rest as
`43-clientless-access-gateway.md` §9).

| Option | Default | Meaning |
|---|---|---|
| `--publish-listen` | off | the address serving published applications; empty disables the mode |
| `--publish-tls` | `acme` | `acme`: obtains a certificate per published name itself; `file`: the proxy's own `--tls-cert`/`--tls-cert-dir`; `none`: a TLS-terminating proxy in front (the compose and Kubernetes layouts) |
| `--publish-http` | off | with `acme`: a plain-HTTP address for ACME challenges and the redirect to HTTPS |
| `--publish-acme-email`, `--publish-acme-directory` | — | ACME account and directory with `acme` |
| `--publish-trusted-proxies` | none | CIDRs of the proxy in front whose `X-Forwarded-For`/`-Proto` are believed. Only that proxy: any host listed may state a browser address |
| `--workplace-url` | the management URL | where users sign in; on a self-hosted server the server's own domain, on Cloud the dashboard. A wrong value refuses every sign-in with *The sign-in did not come from the Workplace* |
| `--publish-session-max-age` | `12h` | longest a sign-in on one address lasts before the user signs in again |
| `--revalidate` | `10m` | how often a session's admission is re-read from management |
| `--idle-timeout` | `60m` | a user's tunnel stops after this long without traffic |
| `--max-sessions` | `2000` | sessions (tunnels) at once |
| `--listen 127.0.0.1:8443 --egress off` | — | the forward-proxy listener the binary always has, parked on loopback with no egress: the reverse proxy serves nothing else |
| `--data-dir` | | keeps each user's peer identity (§10.3) and the peer-name counter across restarts; on a volume |
| `--admin-listen` | `127.0.0.1:9090` | `/healthz`, `/readyz`, and `/tls-ask?domain=` (200 for a published name, 404 otherwise; Caddy's on-demand TLS asks it) |

Fixed: 32 web sessions per user (the oldest goes), 256 connections per client address
(a proxy in front is exempt), 30 seconds to send a request body before sign-in, 20 refused
credentials per address in 5 minutes, then 5 minutes blocked.

## 10. Operating it

### 10.1 Logs

```bash
cd "$C" && sudo docker compose logs --tail=200 reverse-proxy
sudo docker compose logs -f --since 10m reverse-proxy | grep 'gateway:'
kubectl logs deploy/<reverse-proxy-deployment> --since=1h          # Kubernetes
```

The reverse proxy's own lines carry the prefix `gateway:` (it is the gateway binary); the
other lines come from the users' tunnels and read like a client log
(`13-log-interpretation.md`). Every request writes one **access line**; the `id=` at its
end is the `X-Request-Id` the browser or API client received, so a user's *request_id*
finds the line.

| Line | Meaning |
|---|---|
| `gateway: publishing on [::]:8444 (tls none, sign-in at https://…)` | the mode is on; the sign-in address in use |
| `gateway: access GET crm.apps.example.com/path 200 12345B 8ms user=a@example.com app=<app id> ip=<public ip> id=<request id>` | one request: method, address and path, status, bytes, duration, user (empty before sign-in), application, the client's address |
| `gateway: <email> signed in at <address> from <ip> (<id>)` | a browser sign-in accepted |
| `gateway: <email> refused at <address>: not admitted (<id>)` | signed in at the Workplace, but not in the application's groups: the user saw *Access Denied* |
| `gateway: publish login for <address>: …` | the sign-in could not be checked (management unreachable, token refused): *Sign-in unavailable* / *Sign-in refused* |
| `gateway: <email>: API access at <address> from <ip> (<id>)` | a non-interactive session started (§6) |
| `gateway: API access at <address>: …` | a non-interactive credential could not be checked |
| `gateway: session vp-<n>-RPROXY (<email>) ready: peer <ip> <fqdn>, device <public ip> …` | the user's tunnel is up |
| `gateway: session vp-<n>-RPROXY (<email>) stopped: idle` / `gateway shutting down` | the tunnel ended; the next request starts it again |
| `gateway: <email> at <address>: session: … (<id>)` | the tunnel could not start for that request: the user saw *Access Failed* or a `503` |
| `gateway: <email> signed out at <address>` | `/.netzilo/logout` |
| `gateway: <email> at <address>: oldest sign-in dropped, 32 web sessions` | the per-user session cap |
| `gateway: <ip> blocked for 5m0s after 20 failed logins` | an address guessing credentials, or a job with a stale token |
| `Posture check '<name>' FAILED at <check>` (tunnel line) | a policy's posture check fails for this user's reverse-proxy peer (§10.3) |

`--log-level debug` adds every dial and its outcome; put it back to `info` afterwards.
Logs never contain a credential.

### 10.2 Health

`/healthz` and `/readyz` on the admin port, inside the container (`43` §10.2 shows the
throwaway-container recipe; the service name here is `reverse-proxy`). `/readyz` answers
`ready`, or `503` with `management unreachable`, `session limit reached` or `draining`.
From outside, the one-line check of §8.3 Gate 2: a name nobody publishes must answer
`404` with `There is no application at this address` over a valid certificate.

Certificates: on Caddy installs `sudo docker compose logs caddy | grep -i 'apps\.'` shows
on-demand issuance and its errors; on Kubernetes the Certificate resource's status.

### 10.3 Reverse-proxy peers in the Peers list

- One peer per **user, public address and operating system** (name and version), named
  `vp-<n>-RPROXY`, platform *browser*, ephemeral (management deletes it once offline for
  a while). All of that user's browsers and API clients at that address on that system
  share it. The same user from home and from the office is two peers, each judged by its
  own location; a Mac and a Windows laptop behind one address are two peers, each judged
  by its own operating system.
- **The peer comes back.** Its key and name are kept on the reverse proxy's data volume
  per user, address and system: after the idle stop or a restart the same
  `vp-<n>-RPROXY` reconnects instead of a new number appearing. Unused for 30 days, the
  identity is dropped (at most 16 are kept per user, and a user has at most 16 tunnels
  at once: a 17th address or system is refused until one idles out); management's
  ephemeral cleanup
  removes the peer meanwhile and it registers again under the same name on the next use.
- **What it reports:** the user's public IP as its connection address (so **Country &
  Region** and **Peer Network Range** checks judge the user's location), the operating
  system and version the session was signed in from (the **Operating System** check
  judges it like any peer, `21-posture-checks.md` §1), every browser it has served with
  its version (*Chrome 154.0.0.0, Firefox 156.0*), the reverse proxy's version as its
  client version, and the **Netzilo
  Gateway** posture item, like an extension session. The OS version comes from the
  browser's client hints where it sends them (Chrome, Edge), else from the User-Agent,
  which Firefox and Safari freeze at macOS `10.15` and Windows `10.0`: a minimum-version
  rule above those blocks such browsers.
- **What it is not:** it passes no Endpoint or Advanced endpoint check. Write the policy
  that reaches the application's network for the user's group without those, or with
  location, network-range and operating-system checks only.
- **No device tools** (`36-device-tools.md`): diagnose with §11.
- Blocking or deleting the user, or revoking the token, ends the sessions within the
  revalidation interval (10 minutes); stopping the container ends them at once.

### 10.4 Upgrades and restarts

Update with management and the dashboard, from the same release
(`02-server-operations.md` §4.2 with `S=reverse-proxy`). A restart drops the browser
sessions (they live in memory): users are sent through the Workplace again on their next
navigation, silently while their Workplace session is alive; API clients see one `401`
and continue. The peers come back under their names (§10.3). Behind an ingress the
address answers `503` for a few seconds while the pod is replaced.

### 10.5 Capacity

A tunnel is a userspace WireGuard peer inside the process: memory grows with users online
at once, CPU with traffic. Watch `sessions=` in `/healthz` and `sudo docker stats
reverse-proxy` during the pilot. One tunnel serves all of a user's browsers at an address
on one operating system.

## 11. Troubleshooting

### 11.1 Test the path without a browser

From any machine, no token:

```bash
A=crm.apps.example.com
curl -sS -o /dev/null -w 'navigation -> %{http_code} %{redirect_url}\n' -H 'Accept: text/html' -H 'Sec-Fetch-Mode: navigate' "https://$A/"
curl -sS -w '\nfetch -> %{http_code}\n' -H 'Accept: application/json' "https://$A/"
curl -sS -w '\nunpublished -> %{http_code}\n' -H 'Accept: application/json' "https://nz-check.apps.example.com/"
```

Expected: `302` to `https://<workplace>/publish-auth?host=…&rd=…&state=…`; `401` with
`{"error":"sign in required","login":"…"}`; `404` with `{"error":"There is no application
at this address"…}`. All three over a valid certificate.

With a user's token (§6; never paste it into a ticket):

```bash
export TOKEN=nzl_...
curl -sS -o /dev/null -w 'api -> HTTP %{http_code} in %{time_total}s\n' -H "X-Netzilo-Bearer: $TOKEN" "https://$A/"
unset TOKEN
```

`200` proves sign-in, admission, the tunnel and the target end to end (the first call
after an idle hour takes 10 to 20 seconds); `403` is admission (§4); `503` is the tunnel
(§11.3); `502`/`504` is the target.

What management publishes, and for whom:

```bash
curl -sS 'https://<api-host>/api/published-apps/exists?domain='"$A"          # {"published":true}
curl -sS -H "Authorization: Token $ADMIN_TOKEN" https://<api-host>/api/published-apps | jq '.[] | {name, domain, target, enabled, groups}'
curl -sS -H "Authorization: Token $USER_TOKEN" https://<api-host>/api/users/current/published-apps | jq '.[].domain'
```

### 11.2 Symptoms

| Symptom | Check | Cause and fix |
|---|---|---|
| **There is no application at this address** (page or JSON `404`) | `exists?domain=` (§11.1) | `false`: the switch is off (§3), the application is disabled or deleted, the address differs (case, a trailing dot, a typo), or another tenant's server. `true` but still 404: the reverse proxy's 30-second cache; wait a minute |
| the address does not resolve, or a certificate error | `dig +short` the address; `openssl s_client -servername <address> -connect <front door>:443` | the wildcard record is missing or points elsewhere (**Settings → Permissions → Verify** says so); on Let's Encrypt installs the first visit is issuing the certificate (retry), or Caddy could not: `logs caddy` (§10.2) — `/tls-ask` answered 404 because management does not publish the name yet; a provided certificate without the wildcard (§8.2) |
| the page shows *Not published* or a Netzilo error page with a **request id** | the access line with that `id=` (§10.1) | the line's status and user say which case below |
| **Access Denied** | `refused at <address>: not admitted` in the log; the application's groups | the user is in none of the application's groups; add the group, or the switch is off. Take effect within 10 minutes for an existing session, at once for a new sign-in |
| **Access Failed — took too long to answer / did not answer** | `session: …` line with the request id; the `vp-<n>-RPROXY` peer in Peers: connected? its groups; the tunnel line `Posture check … FAILED`; the routes and policies of the user's groups | the target is not reachable **through the user's tunnel**: no route to its network for the user's groups, a policy that does not include them, a posture check the reverse-proxy peer fails (§10.3), a wrong target address or port, the target down, or its name unresolved by the user's DNS. `11-connectivity-diagnosis.md` from the peer's point of view; the same user with the Netzilo client reaching the target proves the policy, not the reverse proxy |
| stuck at **Logging in** | `sudo docker compose logs -f reverse-proxy` while the user retries; `/readyz` | management unreachable from the reverse proxy; the user's tunnel cannot connect (signal, relay: `03-server-troubleshooting.md`); on a self-hosted server whose Caddy sets a strict `Content-Security-Policy` for the dashboard, the dialog's status polling and form post to the application's address are blocked — allow `https:` in `connect-src` and `form-action` for `/publish-auth` |
| **Sign-in refused — The sign-in did not come from the Workplace** | `--workplace-url` in the container's command | it does not match the dashboard's origin the user signed in at (`https://` scheme and host exactly); fix it and recreate the container |
| **Sign-in expired — Open the application again** | — | the state was older than 10 minutes, already used, or the browser dropped the cookie set at the first visit (cookies blocked for the address); open the application again from the Workplace |
| **Sign-in unavailable** | `publish login …` line | management did not answer the token check; the server (`03-server-troubleshooting.md`) |
| **Too many attempts** (`429`) | `blocked for 5m0s` | 20 refused credentials from that address: a script with a stale token, or someone guessing; wait 5 minutes, fix the script |
| **Connecting** (`503`, retries by itself) | the peer's `ready` line | the tunnel or its route is not up yet (the first request after an idle hour); it clears within seconds. Persisting: as *Access Failed* |
| **Not reachable** (`502`) / **Timed out** (`504`) | debug log for the target | the target refused or did not answer within 20 seconds through the tunnel: the application itself, or the wrong port |
| the application loads but links, redirects or logins go to its internal name | the application's configuration | it builds absolute URLs from its configured base address: set that to the published address, or turn on **Send the address as Host header** (§4) |
| the application works for some users only | §11.1 with each user's token; their groups and policies | groups admit them differently, or their policies reach the target differently (§4) |
| **Peers** show the server's or the ingress's IP for `vp-<n>-RPROXY` | the container's `--publish-trusted-proxies` | it does not cover the proxy in front (compose: `172.20.0.0/24`; Kubernetes: the pod network) |
| a policy with a posture check never admits the reverse-proxy peer | the check's items | Endpoint items can never pass for it; an OS minimum above what the browser reports (Firefox and Safari freeze the version) blocks it (§10.3) |
| API client gets `401 credential refused` with a valid token | the token's owner in **Team → Users** | expired, revoked, for another server, or the user is blocked; through a proxy that strips headers, `Proxy-Authorization` was dropped: use `X-Netzilo-Bearer` (§6) |
| API client gets `403 not allowed to open this application` | the token owner's groups | the owner is not admitted (§4) |
| the modal says **Not under an application domain** | **Settings → Permissions → Application domains** | multi-tenant server: add the domain first (§3), or pick a label under an existing one |
| **Unavailable — already published** for a name nobody in this tenant uses | — | another tenant on the same server holds it (Cloud: the shared `netzilo.app`); choose another label |
| Verify says **No wildcard record found** | `dig +short nz-check.<domain> @1.1.1.1` | the record is missing at the DNS provider, or a proxy-style DNS record (Cloudflare "proxied") hides the address; use a plain record |
| Verify says **points elsewhere** | the addresses shown | the record points at another server or an old IP; fix the record or the addresses in the row |
| after a restart every user is sent through the Workplace again | expected (§10.4) | sessions live in memory; nothing to fix |
| users of **another** name under the application domain (a peer name, an internal site) lose plain-HTTP access in one browser: it insists on `https://` | `dig +short <name> @1.1.1.1` shows the reverse proxy's address; the browser's history shows `https://` | the application domain overlaps a name space that is resolved inside tunnels (never use the peer DNS zone, §3), and a reverse proxy older than the September 2026 release sent `Strict-Transport-Security` on its 404, pinning the name in that browser; upgrade, fix the domain, and reset the site in the browser (`43-clientless-access-gateway.md` §11.3a) |
| the `reverse-proxy` container restarts | `logs --tail=50 reverse-proxy` | a start error in the command (`management URL …: want http(s)://host[:port]`), or `management not reachable yet` for 5 minutes, then exit: management is down |

### 11.3 Reading *Access Failed* correctly

Sign-in and admission are management's decisions and pass before the dialog says
*Logging in*; *Access Failed* is always the **tunnel**: the user's reverse-proxy peer
could not reach the target. Work it like any peer that cannot reach a host
(`11-connectivity-diagnosis.md`) with the peer being `vp-<n>-RPROXY`, and remember three
things about that peer: it has the user's groups and nothing else, it reports no
endpoint posture, and the target's name is resolved by the user's DNS settings, not by
the server. The commonest cause is a policy on the target's network that carries a
posture check (an endpoint item, or an OS minimum above what the browser reports) which
the reverse-proxy peer cannot satisfy: give browser users a policy without one, or with
location, network-range and operating-system checks only.

### 11.4 Before escalating

Collect: the reverse proxy's version (first log line), the `publishing on` line, `/readyz`,
the §11.1 results, the access line and session lines for the failing request id, the
peer's status in Peers, the application's settings (address, target, groups, enabled)
and the Permissions settings; the user's e-mail and the time. Never the token, the
cookie or the Workplace's session. Then `12-escalation-package.md`.

## 12. Supporting a user who cannot open an application

For the assistant in a regular user's session (`39-end-user-self-service.md`), and for an
administrator answering a user's ticket.

What a regular user can see through the API: `GET /api/users/current/published-apps`, the
applications they may open (the Workplace tiles), and their own `vp-<n>-RPROXY` peers in
`GET /api/peers` (`connected`, `connection_ip`, `last_seen`). There are no device tools for
a browser; nothing on the user's machine is Netzilo's.

| They say | Check first | Where it usually ends |
|---|---|---|
| "The tile is not there" / "I don't see the application" | `GET /api/users/current/published-apps` | not admitted: **administrator** (groups, §4) or the switch is off (§3). An application the user opened yesterday that is gone today was disabled or its groups changed |
| "Access Denied" | the same list: the address is not in it | **administrator**: the user is in none of the application's groups |
| "Access Failed — took too long / did not answer" | their reverse-proxy peer in `GET /api/peers`: connected? | **administrator**: the target is not reachable for this user's groups (§11.3). Nothing on the user's side |
| "It keeps asking me to log in" / "Sign-in expired" | which browser; cookies allowed for the address? private window? | user's side: cookies blocked for the application's address or the Workplace, a browser extension that strips cookies, or a link older than 10 minutes; open the application from the Workplace tile again. Every 12 hours a fresh sign-in is normal |
| "There is no application at this address" | `exists?domain=` (§11.1); the exact address they typed | a typo or an old bookmark; if the address is right, **administrator** (§3, §4) |
| "The certificate is not trusted" / browser warning | the front door's certificate for that name | **administrator** (§8.2); a self-signed certificate only in browsers that trust it |
| "It opens but looks broken / logs me out of the app / goes to an internal name" | the application's own configuration (§11.2) | **administrator**: the application's base URL or the Host header option |
| "Slow the first time" | — | expected: the user's tunnel starts on the first request after an hour (§1) |
| "Does this work on my phone / without the Netzilo app?" | — | yes, any browser; the application still opens only for signed-in, admitted users |

The message to the administrator follows `39-end-user-self-service.md` §4: the
application's address, what the dialog said (*Access Denied* or *Access Failed* and its
line), the time, and the user's e-mail.

## 13. Limits

- Web applications over HTTP and HTTPS only: one address is one target, no path routing,
  no TCP or UDP publishing; other protocols need the Netzilo client.
- Nothing is reachable that the user's tunnel cannot route: a target must be inside a
  route and a policy for the user's groups (§4).
- The target's certificate is never verified.
- Sessions live in the reverse proxy's memory: one replica per address; a restart sends
  browsers through the Workplace again (§10.4).
- A sign-in lasts 12 hours per address; the Workplace session makes renewals silent.
- Reverse-proxy peers pass no endpoint posture check; the operating system they report
  is what the browser says about itself (§10.3).
- Addresses are unique across the server; on Cloud the application domain is shared
  between tenants (§3).
- On self-hosted Let's Encrypt installs each published name gets its own certificate on
  first use; a provided certificate must be a wildcard (§8.2).
- The reverse proxy trusts the proxy in front of it for client addresses and nothing
  else; behind a proxy that does not forward `Proxy-Authorization`, API clients must use
  `X-Netzilo-Bearer` (§6).
