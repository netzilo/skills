# Netzilo — Public API and Automation

**Audience:** an AI operator automating Netzilo administration (bulk changes, exports,
CI/IaC enrollment, migrations between servers). Endpoints and fields are from the
management server router and OpenAPI spec; the spec itself is incomplete, so this list is
authoritative for what exists.

Base URL: `https://<domain>/api` (cloud: `https://srv.netzilo.com/api`). All responses
JSON. CORS is open.

---

## 0. Get a token from the customer first

The REST API is the preferred way to administer a Netzilo account: you see the real
configuration, change one thing at a time, and verify immediately. Unless the task is a
single dashboard click, open the engagement by asking for a token.

Ask the customer to create a **service user**, not to hand over their own credentials:
Dashboard → **Team → Agents → Create Agent** (role **User** for read-only diagnosis,
**Admin** once changes are agreed) → open it → **Access Tokens → Create Access Token**
with a 7–30 day expiry. The token is shown once. Say explicitly that it grants API
access to their account and can be deleted at any time.

Verify it before acting, and confirm which role you were actually given:

```bash
nz /accounts | jq '.[0].id'
nz /users | jq '.[] | select(.is_current) | {role, is_service_user}'
```

Keep it in an environment variable for the session; never write it to a file, a script,
or an escalation package. When finished, remind the customer to delete the token and the
agent. Never ask for a password, SSO credentials, or the identity-provider master key.

---

## 1. Authentication

| Header | Token type | How to get |
|---|---|---|
| `Authorization: Token nzl_…` | Personal Access Token (PAT), 40 chars, prefix `nzl_` | Dashboard → Team → your user (or an **Agent** = service user) → **Access Tokens → Create Access Token** (name, 1–365 days). Shown once. |
| `Authorization: Bearer <JWT>` | OIDC access token from the identity provider | what the dashboard uses; useful for scripts that already log in via OIDC |

A PAT sent as `Bearer nzl_…` is accepted too. Errors: `token invalid`,
`no valid authentication provided`, `token expired`,
`the user has no access to the API or is blocked`,
`only users with admin power can perform this operation`.

Permissions follow the token owner's role. Regular users can only read (and manage their
own tokens); admins/owners and admin-role service users can write. Admin-only paths:
`/reports`, `/posture-checks`, `/events`, `/dns/*`, `/stats`, `/summary`, `/edge/*`
(except `GET /edge/filters`), `/tenant`, `/integrations`, `/event-streaming`, `/mfa`,
`/groups`, `/templates`.

Recommended: create a dedicated **Agent** (service user) with role **admin** for
automation so tokens don't die with an employee's account.

```bash
export NZ_URL=https://<domain>/api
export NZ_TOKEN=nzl_...
nz() { curl -sS -H "Authorization: Token $NZ_TOKEN" -H 'Accept: application/json' -H 'Content-Type: application/json' "$NZ_URL$1" "${@:2}"; }
nz /users | jq '.[] | {id,email,role,is_service_user}'
```

---

## 2. Endpoint catalogue

| Resource | Endpoints |
|---|---|
| Account | `GET /accounts` (list of one), `PUT /accounts/{id}` `{settings:{…}}`, `DELETE /accounts/{id}` |
| Users | `GET /users[?service_user=true\|false]`, `POST /users`, `GET/PUT/DELETE /users/{id}`, `PUT /users/{id}/password`, `PUT /users/{id}/name`, `POST /users/{id}/invite`, `GET/DELETE /users/{id}/auth-factors` |
| Access tokens | `GET/POST /users/{id}/tokens`, `GET/DELETE /users/{id}/tokens/{tokenId}`, `POST /tokens/revoke` |
| Peers | `GET /peers`, `GET /peers-stream` (SSE), `GET/PUT/DELETE /peers/{id}`, `POST /peers/bulk-delete {peer_ids}` (≤1000), `POST /peers/sync {peer_ids}` |
| Setup keys | `GET/POST /setup-keys`, `GET/PUT/DELETE /setup-keys/{id}` |
| Groups | `GET/POST /groups`, `GET/PUT/DELETE /groups/{id}` |
| Policies | `GET/POST /policies`, `GET/PUT/DELETE /policies/{id}` |
| Posture checks | `GET/POST /posture-checks`, `GET/PUT/DELETE /posture-checks/{id}` |
| Routes | `GET/POST /routes`, `GET/PUT/DELETE /routes/{id}` |
| DNS | `GET/POST /dns/nameservers`, `GET/PUT/DELETE /dns/nameservers/{id}`, `GET/PUT /dns/settings` |
| Events | `GET /events`, `GET /events/paginated?date_from&date_to&limit(≤1000)&offset&order&q&user&code` |
| Geo | `GET /locations/countries`, `GET /locations/countries/{cc}/cities` |
| Stats / dashboard | `GET /stats`, `GET /summary`, `GET /getsecdata` |
| Reports | `GET/POST /reports`, `GET/DELETE /reports/{id}` |
| Profiles (Enterprise) | `GET/POST /profiles`, `PUT/DELETE /profiles/{id}`, `GET /templates`, `GET /templates/{category}` |
| Tenant | `GET/PUT /tenant`, `POST /tenant/subscription`, `POST /tenant/subscription/confirm`, `GET/POST/DELETE /tenant/logo`, `GET /tenant/logo/info` |
| Integrations | `GET/POST /integrations`, `PUT/DELETE /integrations/{id}` (platforms `twilio`, `cloudflare`, `static`, `openai`, `anthropic`) |
| Event streaming | `GET/POST /event-streaming`, `DELETE /event-streaming/{id}`, `GET /event-streaming/getLogVideos`, `POST /event-streaming/sign-urls` |
| MFA | `GET/PUT/POST /mfa` |
| AI Edge | `GET/POST /edge/tools`, `GET /edge/tools/catalog`, `GET/PUT/DELETE /edge/tools/{id}`; `GET/POST /edge/scanners`, `GET /edge/scanners/catalog`, `GET/POST /edge/scanners/generate`, `GET/PUT/DELETE /edge/scanners/{id}`; `GET/POST /edge/filters`, `GET/PUT/DELETE /edge/filters/{id}`; `GET /edge/discovered-tools`, `POST /edge/discovered-tools/{id}/sanction\|block\|analyze`, `DELETE /edge/discovered-tools/{id}`; `POST /edge/events` |
| AIDR | `GET /peers/{id}/aidr-snapshot[?run_id=]`, `GET …/aidr-snapshot/events`, `GET …/aidr-snapshot/search?q&run_id`, `POST …/aidr-snapshot/replay {run_id, rules_yaml}`, `GET /peers?has_aidr_graph=true` |
| Smart search / AI | `GET/POST /smartsearch`, `POST /ai/scanprompt` |
| Unauthenticated | `POST /register`, `POST /verify-recaptcha`, `GET /lookup-account?search=<subdomain>`, `GET /auth/tokens/{sessionId}`, `GET /getclient?os=windows\|macos-amd64\|macos-arm64` (301 to installer — currently redirects to filenames that return 404 on the CDN; use the dashboard download URLs instead) |

Not in this product (do not promise): `/networks`, `/networks/*/resources`, `/routers`,
`allow_extra_dns_labels`, account settings `dns_domain`, `lazy_connection_enabled`,
`routing_peer_dns_resolution_enabled`, `network_traffic_logs`.

---

## 3. Field reference (request bodies)

**Account settings** (`PUT /accounts/{id}`): `{"settings":{peer_login_expiration_enabled, peer_login_expiration (s), peer_inactivity_expiration_enabled, peer_inactivity_expiration (s), regular_users_view_blocked, groups_propagation_enabled, jwt_groups_enabled, jwt_groups_claim_name, jwt_allow_groups:[…], extra:{peer_approval_enabled}}}` — send the full object (read it first).

**User** create: `{email, name, role:"owner|admin|user", auto_groups:[ids], is_service_user, password?, password_change_required?}`. Update: `{role, auto_groups, is_blocked, update_peer_groups}`. Read fields: `id, email, name, role, status (active|disabled|invited), last_login, auto_groups, is_current, is_service_user, is_blocked, issued, permissions.dashboard_view`.

**PAT**: `POST /users/{id}/tokens {name, expires_in (days 1–365)}` → `{plain_token, personal_access_token{id,name,expiration_date,created_by,created_at,last_used}}`.

**Peer** update: `{name, ssh_enabled, login_expiration_enabled, inactivity_expiration_enabled, approval_required}`. Read: `id, name, ip, connection_ip, connected, last_seen, os, kernel_version, version, ui_version, groups[], ssh_enabled, user_id, hostname, dns_label, login_expiration_enabled, login_expired, last_login, approval_required, country_code, city_name, serial_number, geoname_id, meta.netzilo_meta{device_id, domain_name, is_firewall_enabled, is_disk_encryption_enabled, is_av_enabled, is_av_updated, is_screen_locked, is_os_updated, is_virtual_device, is_being_debugged, is_netzilo_container, is_netzilo_browser}`.

**Setup key**: `{name, type:"reusable|one-off", expirable, expires_in (s, 86400–31536000), revoked, auto_groups, usage_limit, ephemeral}` → read adds `key, valid, used_times, last_used, state (valid|overused|expired|revoked), updated_at`.

**Group**: `{name, peers:[peerIds]}` → `id, name, peers_count, issued (api|jwt|integration), peers[{id,name}]`.

**Policy**: `{name, description, enabled, any_check_must_pass, source_posture_checks:[ids], rules:[{id?, name, description, enabled, action:"accept", protocol:"all|tcp|udp|icmp", bidirectional, sources:[groupIds], destinations:[groupIds], ports:["443"], port_ranges:[{start,end}], allowed_routes:[cidr]}]}`.

**Route**: `{network_id (≤40), description, enabled, peer | peer_groups:[id], network (cidr) | domains:[…], keep_route, metric (1–9999), masquerade, groups:[dist], access_control_groups:[…]}`.

**Nameserver group**: `{name, description, nameservers:[{ip, ns_type:"udp", port}] (1–3), enabled, groups, primary (true iff domains empty), domains:[…], search_domains_enabled}`. **DNS settings**: `{disabled_management_groups:[ids]}`.

**Posture check**: `{name, description, checks:{nb_version_check{min_version}, os_version_check{android|ios|darwin{min_version}, linux|windows{min_kernel_version}}, geo_location_check{locations[{country_code, city_name}], action}, peer_network_range_check{ranges, action}, date_time_checks{rules}, netzilo_check{peer_domain_check, security_settings_check, advanced_settings_check}}}`.

**Integration**: `{platform, enabled, config:{…}}` — `openai|anthropic: {api_key, usage}`, `twilio: {accountSid, authToken}`, `cloudflare: {tokenId, apiToken}`, `static: {stun_servers: "<json array string>", turn_servers: "<json array string>"}`.

**Event streaming**: `{platform:"s3"|"min.io", enabled, config:{bucket, access_key, secret_key, region, endpoint?}}`.

**Edge tool**: `{name, transport:"stdio|sse|streamable_http", description, url?, command?, args?, env?, categories:[…], icon, enabled}`. **Edge scanner**: `{name, description, severity:"low|medium|high|critical", context:[…], rule_yaml, enabled}`. **Edge filter**: `{name, description, enabled, os:["Windows","Darwin","Linux","Android","iOS"], groups:[ids], posture_checks:[ids], tools:[toolIds or "*"], scanners:[ids], agents:[process path globs], any_check_must_pass}`.

Events: `{id, timestamp, activity, activity_code, initiator_id, initiator_name, initiator_email, target_id, meta{…}}`.

---

## 4. Recipes

### 4.1 Create a setup key for an autoscaling group
```bash
GID=$(nz /groups | jq -r '.[] | select(.name=="servers") | .id')
[ -z "$GID" ] && GID=$(nz /groups -X POST -d '{"name":"servers","peers":[]}' | jq -r .id)
nz /setup-keys -X POST -d "{\"name\":\"asg-web\",\"type\":\"reusable\",\"expirable\":true,\"expires_in\":2592000,\"revoked\":false,\"auto_groups\":[\"$GID\"],\"usage_limit\":0,\"ephemeral\":true}" | jq -r .key
```

### 4.2 Least-privilege policy: developers → servers on 22/443
```bash
DEV=$(nz /groups | jq -r '.[] | select(.name=="developers") | .id')
SRV=$(nz /groups | jq -r '.[] | select(.name=="servers") | .id')
nz /policies -X POST -d "$(jq -n --arg d "$DEV" --arg s "$SRV" '{name:"dev-to-servers",description:"",enabled:true,any_check_must_pass:false,source_posture_checks:[],rules:[{name:"ssh-https",description:"",enabled:true,action:"accept",protocol:"tcp",bidirectional:false,sources:[$d],destinations:[$s],ports:["22","443"],port_ranges:[],allowed_routes:[]}]}')"
# then disable the Default policy
DEF=$(nz /policies | jq -r '.[] | select(.name=="Default") | .id')
nz /policies/$DEF | jq '.enabled=false | .rules |= map(.enabled=false)' > /tmp/def.json && nz /policies/$DEF -X PUT -d @/tmp/def.json
```

### 4.3 Export everything (for backup or migration to a new server)
```bash
mkdir -p export && for r in accounts users groups setup-keys policies posture-checks routes dns/nameservers dns/settings profiles edge/tools edge/scanners edge/filters integrations event-streaming; do
  nz /$r > "export/$(echo $r | tr / _).json"; done
nz "/events/paginated?limit=1000&offset=0" > export/events_page0.json
```
Import order on the target: groups → posture-checks → policies → routes → dns → setup-keys
→ edge tools → scanners → filters. Strip `id`/timestamps and remap group IDs by name.
Users are recreated via the identity provider (`04-identity-and-sso.md`); peers must
re-enrol (keys live on devices).

### 4.4 Find and clean stale peers
```bash
nz /peers | jq -r --arg cutoff "$(date -u -d '-30 days' +%FT%TZ 2>/dev/null || date -u -v-30d +%FT%TZ)" '.[] | select(.connected==false and .last_seen < $cutoff) | .id' > stale.txt
jq -Rn '{peer_ids:[inputs]}' stale.txt | nz /peers/bulk-delete -X POST -d @-
```

### 4.5 Audit who accessed what
```bash
nz "/events/paginated?limit=500&code=peer.access.blocked&date_from=$(date -u -d '-7 days' +%FT%TZ)" | jq '.events[] | {timestamp, user:.initiator_email, target:.target_id, meta}'
```

### 4.6 Rotate an automation token
```bash
SVC=$(nz "/users?service_user=true" | jq -r '.[] | select(.name=="automation") | .id')
nz /users/$SVC/tokens -X POST -d '{"name":"ci-'$(date +%Y%m)'","expires_in":90}' | jq -r .plain_token
nz /users/$SVC/tokens | jq '.[] | {id,name,expiration_date,last_used}'   # then DELETE the old id
```

### 4.7 Live peer status stream
`GET /peers-stream` (SSE): first `data:` line is the full peer array; subsequent lines are
comma-separated peer IDs that just connected.

---

## 5. Client-side automation

- **Enrollment in IaC:** `netzilo up --setup-key "$KEY" --management-url https://<domain> --hostname "$NAME"` in cloud-init/Ansible; idempotent (`Already connected`).
- **Headless as a user:** `NETZILOPAT=nzl_… netzilo up`, or `netzilo deploy-user` to
  create user+PAT in one step (`05-client-install-and-deploy.md` §8.3).
- **Health check:** `netzilo status --json | jq '.management.connected and .signal.connected'`.
- **Force map refresh after policy changes:** `netzilo refresh`.
- **PowerShell:** `Invoke-RestMethod -Uri "$Base/api/users" -Headers @{Authorization="Token $Pat"}`
  works the same way as the `curl` examples above for bulk user and group provisioning.

---

## 6. Rate limits, pagination, gotchas

- No documented rate limiting; be polite (the server buffers `GET /accounts` requests).
- `GET /events` returns everything — use `/events/paginated` (`limit` ≤ 1000).
- `PUT` endpoints replace the object; always `GET` first, modify, `PUT` back.
- Group deletion fails while the group is referenced anywhere (policies, routes, DNS,
  setup keys, users, profiles, filters).
- Deleting a user deletes their peers, and on self-hosted also the IdP user.
- Free-plan servers return `maximum number of users reached` (>4 users) and
  `maximum number of personal peers reached` (>99 peers); Enterprise/MSP have no limits.
- The API is labelled Beta in the docs; test destructive scripts against a small group
  first.
