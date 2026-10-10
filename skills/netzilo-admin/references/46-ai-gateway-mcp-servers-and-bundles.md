---
id: '46'
title: Admin Skill — MCP Servers, MCP Bundles and Sign-ins (AI Gateway)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 18374
sections:
- id: '1'
  title: MCP server — field reference
  chars: 2323
- id: '2'
  title: Authentication types, and who has to do what
  chars: 3223
- id: '3'
  title: MCP bundles
  chars: 965
- id: '4'
  title: Users' sign-ins and header values
  chars: 2890
- id: '5'
  title: How a tool call is governed
  chars: 1165
- id: '6'
  title: MCP clients that sign in themselves (OAuth 2.1 at the gateway)
  chars: 2038
- id: '7'
  title: API
  chars: 1114
- id: '8'
  title: Diagnosis
  chars: 2634
- id: '9'
  title: Limits to state before a customer discovers them
  chars: 961
---
# Admin Skill — MCP Servers, MCP Bundles and Sign-ins (AI Gateway)

**Dashboard:** Edge → **MCP** (`/ai-edge/mcp`, tabs **MCP Servers** | **MCP Bundles**,
`?tab=bundles`). **API:** `/api/edge/mcp-servers`, `/api/edge/virtual-mcps`,
`/api/edge/mcp-catalog`, `/api/users/current/mcp-connections`. **Who:** admins define
servers and bundles; users connect their own sign-ins at Workplace → **Agentic Access**
(`47-agentic-access-workplace.md`).

An **MCP server** is a definition: how the AI Gateway reaches a server (HTTP, SSE, or a
process it starts) and how it authenticates. Every gateway serves it at
`<gateway>/mcp/<slug>`. An **MCP bundle** serves tools from several servers behind one
endpoint `<gateway>/mcp/<bundle-slug>`. Which servers, bundles and tools a user may call
is a **gateway filter** grant (`29-edge-filters.md` §2.2). Guardrails run on every tool
call and result (`28-edge-guardrails.md`). The device-side MCP gateway of earlier
clients (port 41338, tool catalogue, discovered tools) no longer exists; MCP goes through
the AI Gateway.

---

## 1. MCP server — field reference

Dialog **Add MCP Server** / **Edit MCP Server**, tabs **Connection | Authentication |
Name & Description**. **Add MCP Server ▾** offers **Browse Catalog** (a library of known
servers: columns Server | Category | Connection | Auth | Publisher; picking one pre-fills
the dialog) and **Custom**.

| Tab | Field | Rule |
|---|---|---|
| Connection | Connection | `http`, `sse`, `stdio` ("How the gateway reaches the server: over HTTP, server-sent events, or as a process it starts.") |
| Connection | URL (http/sse) | required, `http(s)://…` ("an http server needs an http(s) URL") |
| Connection | Command, arguments (stdio) | required ("a stdio server needs a command"); **the gateway host runs it**; plus Environment Variables |
| Connection | Extra Headers | sent with every request |
| Connection | Skip TLS Verification | for an internal endpoint with its own CA |
| Authentication | Authentication | `none`, `headers`, `per_user_headers`, `oauth`, `per_user_oauth` (§2); stdio allows only None and Headers |
| Name & Description | Name | required; unique (409 `an MCP server named "…" exists`) |
| Name & Description | Endpoint (`slug`) | `/mcp/<slug>`; derived from the name, `^[a-z0-9]+(-[a-z0-9]+)*$`, unique across servers **and** bundles (409 `the slug "…" is in use`); **cannot change once created** |
| Name & Description | Enable MCP Server | "A disabled server is removed from every gateway; filters that grant it grant nothing from it." |

Other stored fields: `code_mode` (the gateway exposes the server's tools through its
upstream's code-mode meta-tools; API only, not shown in the dialog), `icon_url`,
`docs_url`. Header names must match `[A-Za-z0-9-_.]`. Secrets (`headers`, `env`,
`extra_headers`, `oauth.client_secret`) are write-only and masked `••••xxxx` in answers;
sending an empty or masked value keeps the stored one.

A server cannot be deleted while a filter or a bundle references it
(412 `MCP server is used by filter X, MCP bundle Y`). Deleting it deletes every stored
sign-in and header value for it. **Changing the authentication type deletes every
stored credential for that server**, so every user connects again.

Events: **MCP server added / updated / deleted** (`gateway_mcp_server.*`; meta `name,
slug, connection, auth_type, enabled, url`).

---

## 2. Authentication types, and who has to do what

| Type | Dialog text | Who holds the credential | What a user does |
|---|---|---|---|
| None | "The server takes no credential." | nobody | nothing |
| Headers | "One set of headers the admin holds, sent with every request." | the admin, in **Credential Headers** | nothing |
| Per-User Headers | "Each user supplies their own values for the header names declared below, from the Workplace." | each user, for the names in **Header Names Users Supply** (comma separated, e.g. `X-API-Key, X-Tenant-ID`); optional **Static Headers** from the admin | Workplace → the server's card → one input per name → **Connect** (§4) |
| OAuth | "The admin signs in once; every user shares that token." | the admin: **Shared Sign-In** panel in the server's dialog (visible once saved) | nothing; the card says "An admin has not connected this server yet." until the admin signs in |
| Per-User OAuth | "Each user signs in to the server from the Workplace; tokens are kept per user." | each user | Workplace → **Connect** → sign in at the provider in a popup (§4) |

**OAuth fields** (both OAuth types): Client ID, Client Secret, Authorize URL, Token URL,
Registration URL, Scopes (space separated), Resource. "Leave fields empty to let
management discover the server's endpoints and register a client." On the first sign-in
management reads the server's protected-resource metadata and its authorization server's
metadata (RFC 9728, RFC 8414, OpenID), registers a client when none is set (RFC 7591,
public client, `client_name: Netzilo`), runs the authorization-code flow with PKCE, and
writes what it discovered into the empty fields. The redirect URI is always
`<management>/api/mcp/oauth/callback`; there is no field for it.

**When discovery is not enough:** a provider that refuses dynamic registration or refuses
Netzilo's callback (`client registration refused: … invalid_redirect_uri` — the sign-in
fails with HTTP 422 and the toast "Sign-in failed") needs a client registered by hand at
that provider with redirect URI `https://<management-host>/api/mcp/oauth/callback`; enter
its Client ID (and secret) on the server. Management must be reached under its dashboard
host or `api.<dashboard host>` for the sign-in to start (`the request reached management
under an unknown host`).

**Shared Sign-In panel** (OAuth type): states **Not Signed In** → **Sign In**;
**Signed In** + "Signed in {at}" → **Reconnect**, **Disconnect**; **Sign-In Expired** →
**Reconnect**; while waiting, "Complete the sign-in in the window that opened" + Cancel.
The popup times out after 10 minutes ("The sign-in was not completed within 10 minutes.");
a blocked popup says so ("The browser blocked the sign-in window…"). Success: "The shared
sign-in is connected."

**Token refresh.** Stored OAuth tokens are refreshed by management shortly before they
expire (when a gateway's pull finds one due within 10 minutes). A refresh that fails marks
the credential **needs re-authentication** and records **MCP server needs a new sign-in**
(`mcp.reauth_required`); the Workplace card turns **Needs Attention** and offers
**Reconnect**; for a shared sign-in the admin reconnects in the server's dialog.

---

## 3. MCP bundles

Dialog **Add MCP Bundle**: Name (unique), Endpoint (`/mcp/<slug>`, locked after create,
same slug namespace as servers), Description, **Servers** ("Each server contributes all
of its tools or the names you type."; **Browse MCP Servers**; per server an **All Tools**
switch, off → "tool names, comma separated"), Enable MCP Bundle ("A disabled MCP bundle
is not served by any gateway."). At least one server ("Add at least one server").

A bundle is one MCP endpoint that lists the chosen tools of its members; a caller
connects to one address instead of several. Members keep their own authentication: a
member with per-user sign-in still needs the user's sign-in, and the bundle's Workplace
card shows **Needs Attention** ("Finish setting up {names} to use all of its tools.")
until every member is set up. A bundle cannot be deleted while a filter grants it.

Events: **MCP bundle created / updated / deleted** (`gateway_virtual_mcp.*`).

---

## 4. Users' sign-ins and header values

Stored on management per server and per user (the shared credential has no user).
The gateway pulls them (`GET /api/ai-gateway/mcp-credentials`, ETag) and writes them into
its upstream's credential store; an OAuth token travels as that server's `Authorization`
header, header values as themselves. A per-user server is created on a gateway only once
a credential exists for someone (`… waits for a credential before it can be created` in
the gateway log is normal before that).

A user's state per server (`GET /api/users/current/mcp-connections`, and the Workplace
card):

| `status` | Meaning | Card |
|---|---|---|
| `none` | the server needs nothing from the user (None, Headers) | Online / Offline by the gateway's answer |
| `shared` | an OAuth server with the admin's sign-in in place | Online / Offline |
| `not_connected` | per-user sign-in or header values missing | **Needs Attention**, **Connect** |
| `connected` | the user's credential is stored and active | Online, **Disconnect** |
| `needs_reauth` | the stored sign-in could not be renewed | **Needs Attention**, **Reconnect** |

What the Workplace calls (any user, their own token):

```
POST   /api/users/current/mcp-connections/{serverId}/oauth    → {authorize_url}   (per_user_oauth)
POST   /api/users/current/mcp-connections/complete {state, code}                  (after the popup)
PUT    /api/users/current/mcp-connections/{serverId}/headers {headers:{…}}        (per_user_headers)
DELETE /api/users/current/mcp-connections/{serverId}                               (disconnect)
```

Header values are tested with an MCP `initialize` before they are stored: a 401/403 from
the server gives `the server refused these values (HTTP 401)`; every declared name is
required (`a value for X-API-Key is required`). The OAuth popup returns to
`<dashboard>/mcp-signin-done`, which completes the sign-in for the user who started it
(`the sign-in expired or was not started here`, `the sign-in was started by someone
else` otherwise; a flow lives 10 minutes in management's memory — with several management
replicas and no session affinity a sign-in can fail this way).

Admin equivalents: `POST /api/edge/mcp-servers/{id}/oauth` (shared sign-in),
`DELETE /api/edge/mcp-servers/{id}/credential` (remove the shared credential;
`only admins can remove a shared credential`, `no credential for this server`).

Events: **MCP server connected** (`mcp.connected`), **MCP server disconnected**
(`mcp.disconnected`), **MCP server needs a new sign-in** (`mcp.reauth_required`), all
Access Control, meta `server, slug, kind (headers|oauth), shared`.

**A tool call before the user connected** answers, as the tool's result text,
`Connect <server> in your Workplace before using its tools: <workplace>/workplace?connect=<server>#gateways`.
That is the user's cue, not an error of the gateway.

---

## 5. How a tool call is governed

1. The caller must be identified at the gateway door (`27` §6) and the server must be
   granted to them by a gateway filter, directly or through a bundle; otherwise the
   endpoint answers as not available to them.
2. The gateway hands the caller's virtual key to its upstream for `/mcp/…`; the
   upstream applies that user's grants (which tools of the server) and credentials.
3. Each `tools/call` runs the user's guardrails on the arguments (block → the call is
   refused with the rule's reason; redact → the arguments are rewritten) and on the
   result (block → the tool answers `Tool execution failed: Blocked by rule: <name>`;
   redact → the result text is rewritten, recorded as `redacted`).
4. Each call is one usage record (server, tool, status, latency, argument and result
   sizes; never the content).
5. Tool names are shown to callers as `<server-slug-with-underscores>-<tool>`; the
   grant and the event use the bare tool name.

MCP tools are **not** injected into chat completions by default: a chat request carries
the gateway's MCP tools only when the caller names them in `x-bf-mcp-include-clients`.

---

## 6. MCP clients that sign in themselves (OAuth 2.1 at the gateway)

An MCP client that cannot carry a token of its own (Claude Desktop "custom connector",
a claude.ai connector) signs in through OAuth 2.1, with management as the authorization
server and the gateway as the resource:

1. The client calls `<gateway>/mcp/<slug>` without a token → 401 with
   `WWW-Authenticate: Bearer realm="netzilo", resource_metadata="<gateway>/.well-known/oauth-protected-resource", scope="mcp"`.
2. It reads that metadata and `<gateway>/.well-known/oauth-authorization-server`; the
   endpoints point at management's `/api/mcp/oauth2/{register,authorize,token,revoke}`
   (both doors of the gateway and a published application in front of it answer these).
3. It registers (RFC 7591; https redirect URIs, or http on localhost; 20 registrations
   per address per 10 minutes), opens the browser at `/api/mcp/oauth2/authorize` (PKCE
   S256 required), and the user lands on the dashboard's **consent page**
   (`/mcp-consent`): "**{client} wants to access your Netzilo account** — This will allow
   {client} to: Use the AI gateway at {host} as you; Call the MCP servers and models your
   filters grant you; Keep an access token in your name until you revoke it." **Allow** /
   **Deny**.
4. On Allow the client exchanges the code for a token: a **personal access token of the
   user**, named `<client> (MCP)`, scope `mcp`, valid **1 day**, plus a refresh token valid
   30 days (one-shot rotation: each refresh mints a new token and deletes the old one).
5. The user sees and revokes that token under Profile Settings → **Access Tokens**;
   revoking it ends the refresh grant too.

An `mcp`-scoped token can call only what a gateway needs on the user's behalf
(`GET /api/users`, the user's AI access and published applications); anything else is
refused (`token scope "mcp" does not allow …`). The gateway honours a revoked token for up
to a minute (its cache).

What a user pastes into each client is in `47-agentic-access-workplace.md` §3.

---

## 7. API

```
GET/POST /api/edge/mcp-servers ; GET/PUT/DELETE /api/edge/mcp-servers/{id}
POST /api/edge/mcp-servers/{id}/oauth ; DELETE /api/edge/mcp-servers/{id}/credential
GET/POST /api/edge/virtual-mcps ; GET/PUT/DELETE /api/edge/virtual-mcps/{id}
GET /api/edge/mcp-catalog
```
```json
{"name":"GitHub","description":"","enabled":true,"slug":"github",
 "connection":"http","url":"https://api.githubcopilot.com/mcp/",
 "auth_type":"per_user_oauth","oauth":{"scopes":["read"]},
 "extra_headers":{},"insecure_skip_verify":false,"code_mode":false}
```
```json
{"name":"Support toolkit","slug":"support-toolkit","enabled":true,
 "tools":[{"server_id":"<id>","tools":["*"]},{"server_id":"<id2>","tools":["search_docs"]}]}
```

`tools: []` or a list containing `"*"` means all tools. A stdio server body uses
`command`, `args`, `env`. `GET /api/edge/mcp-servers` adds `shared_connection {status:
not_connected|shared|needs_reauth, connected_at}` to OAuth servers. The catalogue
(`/api/edge/mcp-catalog`) is fetched from Netzilo's library, cached an hour; it is
reference data, not a list of what is configured.

---

## 8. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Card **Needs Attention** | per-user sign-in/header values missing, shared OAuth not done by an admin, refresh failed, or a bundle member pending | the card's panel says which; Connect / Reconnect; admin: Shared Sign-In |
| Tool answers `Connect <server> in your Workplace before using its tools: …` | same, from an agent | the user connects at the link |
| "Sign-in failed" with `client registration refused … invalid_redirect_uri` | the provider refuses Netzilo's callback or dynamic registration | register a client at the provider with the callback URI; enter the Client ID/secret on the server (§2) |
| "Sign-in failed" with `the server's authorization endpoints could not be discovered` | no discovery metadata at the server | fill Authorize URL / Token URL (and Client ID) by hand |
| `the request reached management under an unknown host` | sign-in started against management at an address that is not the dashboard host or `api.<dashboard host>` | use the dashboard's address |
| `the sign-in expired or was not started here` after the popup | more than 10 minutes, or another management replica | retry; single replica or session affinity |
| `the server refused these values (HTTP 401)` | wrong header values | the user re-enters them |
| Tool call `Tool execution failed: Blocked by rule: <name>` | a guardrail blocked the result | expected; the event names the rule |
| Tools tab "The gateway did not list tools for this server." | server unreachable **from the gateway host**, credential rejected, stdio command failed | gateway log `… applied to the upstream as /mcp/<slug>` then the upstream's error at `--ai-upstream-log-level debug` |
| Card **Offline** while the admin's test works | the Workplace probes through the first reachable gateway; the user's browser cannot reach any gateway address | `47` §2 |
| Stdio server never starts | the command must exist on the **gateway host**; env vars are set in the gateway process | install the command there |
| Cannot delete (412) | referenced by a filter or bundle | edit them first |
| Everyone disconnected after an edit | the authentication type was changed | expected; users connect again |
| `tools/list` through the gateway shows tools the user should not have | the grant is per server (`*` or names); bundles list the chosen tools of their members | narrow the grant in the filter or the bundle |

Before escalating: the server's connection and auth type, `GET /api/users/current/mcp-connections`
for the user, the gateway's `mcp …` log lines (`27` §9.2), and the exact toast or tool
result text.

---

## 9. Limits to state before a customer discovers them

- **No tool listing on management.** Which tools a server has is known only to the
  gateway at runtime (the Workplace Tools tab asks a gateway). A grant names tools by
  the names you type; a typo grants nothing and nothing warns.
- **Secrets are stored on the server unencrypted at the field level** (masked in the
  API, clear to the gateway's service token, as provider keys are).
- **Sign-in flows live in one management process** for 10 minutes; several replicas
  need session affinity.
- **Shared OAuth means one identity at the provider for everyone**; audit at the
  provider will show Netzilo's user, not the end user. Per-user OAuth keeps identities
  apart at the cost of every user signing in.
- **Code mode** is an API-only switch with no dashboard control.
- **`x-api-key` is not a credential at the gateway**; MCP clients send
  `Authorization: Bearer`, which every snippet in `47` uses.
