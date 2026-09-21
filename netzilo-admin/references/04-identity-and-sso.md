---
id: '04'
title: Netzilo — Identity, Users, SSO and MFA Administration
requires:
- idp-console
- server-shell
executable_on:
- human-operator
chars: 20062
sections:
- id: '1'
  title: How users get into the account
  chars: 2322
- id: '2'
  title: Account-level authentication settings (Dashboard → Settings)
  chars: 1634
- id: '3'
  title: The built-in identity provider (self-hosted Netzilo Server)
  chars: 3028
- id: '4'
  title: Everyday identity tasks (self-hosted)
  chars: 3008
- id: '5'
  title: Login failure messages and what they mean
  chars: 1827
- id: '6'
  title: E-mail (SMTP) — required for invitations and password-reset mails
  chars: 1371
- id: '7'
  title: SSO federation (external identity providers)
  chars: 3282
- id: '8'
  title: Legacy self-hosted path (management talking to a customer IdP directly)
  chars: 2124
- id: '9'
  title: Quick checks
  chars: 413
---
# Netzilo — Identity, Users, SSO and MFA Administration

**Audience:** an AI operator managing who can log in to a customer's Netzilo (self-hosted
or cloud): users, roles, passwords, MFA, lockouts, external SSO federation, SMTP, and
the built-in identity provider (Zitadel) that ships with Netzilo Server.

Two layers exist and it matters which one you touch:

| Layer | Owns | Where |
|---|---|---|
| **Netzilo account** (management server) | user list, roles (owner/admin/user), groups, blocking, service users, access tokens, peer ownership | Dashboard → Team; `/api/users` |
| **Identity provider** (Zitadel on self-hosted; Netzilo-run Zitadel on cloud) | credentials, password policy, MFA factors, lockout, external IdPs, e-mail (SMTP), login branding | Zitadel console `https://<domain>/ui/console`; `/management/v1`, `/admin/v1` |

The dashboard proxies the common identity actions (create user with password, change
password, reset MFA, delete user) to Zitadel, so start in the dashboard; go to the
console only for policy-level settings.

---

## 1. How users get into the account

- **Same-domain auto-join:** users whose e-mail domain matches an existing account user
  are added automatically on first sign-in (dashboard text: "Same-domain email users are
  added automatically on first sign-in").
- **Invite by e-mail:** Team → Users → **Add User** → *Email invitation*. Creates the
  Zitadel user and sends the initialization mail. **Requires SMTP** on the identity
  provider (§6). On a self-hosted server SMTP is not configured by the installer, so this
  mail will not arrive until you configure it.
- **Create with password:** Team → Users → **Add User** → *Create password*. Password
  rule enforced by the dashboard: ≥8 chars, upper, lower, digit, one of `@$!%*?&`.
  Credentials are shown once; the user is forced to change the password at first login.
  Works without SMTP.
- **SSO federation:** users authenticate at an external IdP through Zitadel (§7); on
  first login a Zitadel user is auto-created (if provider options allow) and joins the
  account via same-domain rule or an invitation.
- **JWT group gate:** Settings → Groups → *JWT allow group*: when set, only users whose
  token claim (`jwt_groups_claim_name`, e.g. `groups`) contains that group name may access
  Netzilo (`user does not belong to any of the allowed JWT groups`). Warn admins to be in
  the group before saving.

Roles: **Owner** (one per account; full control incl. delete tenant, plan changes;
transferring ownership demotes the previous owner to Admin), **Admin** (everything
except owner-only items), **User** (sees only `/workplace`, own peers; if *Disable portal
access for regular users* is on they are sent to `/install`). Role change: Team → Users →
user → **User Role**.

Blocking: Team → Users → **Block User** toggle (`is_blocked`) — the user's peers lose
access and API calls return `the user has no access to the API or is blocked`.

Deleting a user in the dashboard also deletes the Zitadel user on self-hosted servers
(management runs with `--user-delete-from-idp`) and removes the user's peers. Warn first.

Service users (dashboard label **Agents**): Team → Agents → **Create Agent**; role
`user` (read-only API) or `admin` (write). They have no login; create **Access Tokens**
on their detail page. They are excluded from per-user billing/metering.

---

## 2. Account-level authentication settings (Dashboard → Settings)

| Tab | Setting | API field | Notes |
|---|---|---|---|
| Authentication | **Peer login expiration** + *Expires in* (1–180 days/hours) | `peer_login_expiration_enabled`, `peer_login_expiration` (s) | applies only to SSO-enrolled peers; default enabled, 24 h; setup-key peers exempt |
| Authentication | **Peer inactivity expiration** | `peer_inactivity_expiration_enabled`, `peer_inactivity_expiration` (s) | disconnects idle SSO peers after the period |
| Groups | **Enable user group propagation** | `groups_propagation_enabled` | user's auto-groups copied to their peers (default on) |
| Groups | **Enable JWT group sync** + *JWT claim* + *JWT allow group* | `jwt_groups_enabled`, `jwt_groups_claim_name`, `jwt_allow_groups` | groups are matched by **name** to existing Netzilo groups; never created from tokens; claim-granted membership is revoked when the claim changes |
| Permissions | **Disable portal access for regular users** | `regular_users_view_blocked` | users → `/install` instead of `/workplace` |
| Authentication | peer approval | `extra.peer_approval_enabled` | Cloud feature; no toggle is rendered in the current self-hosted UI, approval is acted on per peer (Peers → **Approve**) |

Saving any tab does `PUT /api/accounts/{id}` with the full `settings` object.

MFA reset for a user: Team → Users → user → **MFA: Reset MFA** (`DELETE /api/users/{id}/auth-factors`).
Password change for a user: user page → **Password → Change Password** (`PUT /api/users/{id}/password`).
Name change: pencil next to the name (`PUT /api/users/{id}/name`).

---

## 3. The built-in identity provider (self-hosted Netzilo Server)

What the installer created in Zitadel:

| Object | Value |
|---|---|
| Instance name / org | `Netzilo` / `Default` |
| Project | `NETZILO` |
| OIDC apps | `Dashboard` (User-Agent, PKCE, JWT access tokens, redirect `https://<d>/nb-auth`, `/nb-silent-auth`, `/nb-auth-x`, post-logout `https://<d>/`, `/nb-logout`); `Cli` (redirects `http://localhost:53000/`, `http://localhost:54000/`, dev mode) |
| Machine user | `netzilo-service-account` (client-credentials secret in `management.json`; roles `ORG_USER_MANAGER`, `IAM_OWNER`, `IAM_OWNER_VIEWER`) — this is how the management server creates/deletes users and imports login events |
| Human admin | the admin e-mail from install; `IAM_OWNER` |
| Removed | Zitadel's default `zitadel-admin` user; bootstrap PAT user demoted |
| Actions (created, **not bound** to flows) | `setEmailVerified`, `addGroupClaim`, `addGroupMeta`, `oktaAuthentication` |
| Defaults | self-registration **off**, password policy ≥8 with upper/lower/digit/symbol, lockout **off** (unlimited attempts), MFA optional, TOTP issuer `Netzilo`, dark theme, Netzilo branding |
| Token lifetimes | access/ID token 12 h, refresh idle 30 d, refresh absolute 90 d |

Console: `https://<domain>/ui/console` — log in with the Netzilo admin (it is an
instance admin). Instance settings live at `/ui/console/instance?id=<panel>` with panels
`login`, `lockout`, `complexity`, `idp`, `smtpprovider`, `branding`, `oidc`, `secrets`,
`messagetexts`, `logintexts`, `privacypolicy`, `verified_domains`, `failedevents`.

Health: `curl -sS https://<domain>/debug/healthz` (`ok`), `/debug/ready` (200, or 412 with
`DB CONNECTION ERROR`).

Never change `ZITADEL_EXTERNALDOMAIN`, `ZITADEL_EXTERNALSECURE`, or the masterkey in
`zitadel.env` on a running system — the domain is permanent and the masterkey is
unrecoverable (`03-server-troubleshooting.md` §2).

### 3.1 Calling the Zitadel API from the server

You need a token with admin rights. Easiest: log in to the console and create a PAT on a
machine user, or reuse the management server's service account credentials from
`management.json` (`IdpManagerConfig.ClientConfig`):

```bash
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo )
D=<domain>
CID=$(sudo jq -r .IdpManagerConfig.ClientConfig.ClientID "$C/management.json")
SEC=$(sudo jq -r .IdpManagerConfig.ClientConfig.ClientSecret "$C/management.json")
TOKEN=$(curl -sS -u "$CID:$SEC" -d 'grant_type=client_credentials' \
  -d 'scope=openid urn:zitadel:iam:org:project:id:zitadel:aud' \
  https://$D/oauth/v2/token | jq -r .access_token)
curl -sS -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  https://$D/management/v1/users/_search -d '{}' | jq '.result[] | {id,userName,state}'
```

Management API (`/management/v1`) is org-scoped (the service account's org is `Default`);
Admin API (`/admin/v1`) is instance-scoped. Add `-H "x-zitadel-orgid: <orgId>"` to target
another org.

---

## 4. Everyday identity tasks (self-hosted)

Prefer the dashboard where it exists; console/API otherwise.

| Task | Dashboard | Zitadel console / API |
|---|---|---|
| Create user with password | Team → Users → Add User → Create password | `POST /management/v1/users/human/_import` `{userName,email:{email,isEmailVerified:true},profile:{firstName,lastName},password,passwordChangeRequired}` |
| Reset a user's password (admin sets it) | user page → Change Password | `POST /management/v1/users/{id}/password` `{"password":"…","noChangeRequired":false}` |
| Send password-reset mail | — | `POST /management/v1/users/{id}/password/_reset` `{"type":"TYPE_EMAIL"}` (needs SMTP); or v2 `POST /v2/users/{id}/password_reset` `{"returnCode":{}}` to get the code without e-mail |
| Force password change at next login | (create-with-password does this) | set password with `noChangeRequired:false` |
| Unlock a locked user | — | console user page → **Unlock**; `POST /management/v1/users/{id}/_unlock` |
| Deactivate / reactivate | Block User (Netzilo level) | `POST /management/v1/users/{id}/_deactivate` / `_reactivate` |
| Reset MFA | user page → Reset MFA | `DELETE /management/v1/users/{id}/auth_factors/otp` (also `/u2f/{tokenId}`, `/otp_sms`, `/otp_email`) |
| Add another instance admin (console access) | — | console → Instance → Members → add with `IAM_OWNER`; `POST /admin/v1/members` `{"userId":"…","roles":["IAM_OWNER"]}` |
| Change admin e-mail/username | user page → name only | `PUT /management/v1/users/{id}/username` / `/email` |
| Force MFA for everyone | — | console `?id=login` → enable a second factor (TOTP: `POST /admin/v1/policies/login/second_factors` `{"type":"SECOND_FACTOR_TYPE_OTP"}`) then `PUT /admin/v1/policies/login` with `"forceMfa":true` |
| Lockout after N failed passwords | — | `PUT /admin/v1/policies/password/lockout` `{"maxPasswordAttempts":10,"maxOtpAttempts":10}` (console `?id=lockout`) |
| Password complexity | — | `PUT /admin/v1/policies/password/complexity` (console `?id=complexity`) |
| Token lifetimes | — | `PUT /admin/v1/settings/oidc` (`accessTokenLifetime`, `idTokenLifetime`, `refreshTokenIdleExpiration`, `refreshTokenExpiration`) — restart Zitadel after changing |
| Login-session lifetimes (how often re-auth is asked) | — | `PUT /admin/v1/policies/login`: `passwordCheckLifetime` (240h), `secondFactorCheckLifetime` (18h), `multiFactorCheckLifetime` (12h), `externalLoginCheckLifetime` (240h), `mfaInitSkipLifetime` (720h) |
| Branding (logo/colors) | Settings → Tenant → Company Logo (dashboard logo) | console `?id=branding` → edit → **Apply** (`PUT /admin/v1/policies/label` then `POST /admin/v1/policies/label/_activate`) |
| Allow self-registration | — | `PUT /admin/v1/policies/login` `"allowRegister":true` (off by default in Netzilo; leave off for corporate deployments) |

User states: `ACTIVE`, `INACTIVE` (deactivated), `LOCKED`, `INITIAL` (never set a
password — resend init mail `POST /management/v1/users/{id}/_resend_initialization`).

---

## 5. Login failure messages and what they mean

| Message (login page / dashboard) | Cause | Fix |
|---|---|---|
| `User could not be found` | wrong login name; user in another org | check Team → Users; try e-mail as username |
| `Password is invalid and user is locked, contact your administrator.` / `User is locked` | lockout threshold hit | unlock (§4) |
| `User is not active` | deactivated | reactivate |
| `Errors.User.NotInitialised` / stuck on "initialize user" | never completed first password | resend initialization or set password via `_import`/`password` |
| Password rejected on change | complexity policy (≥8, upper, lower, digit, symbol) | choose a compliant password |
| `Neither creation of linking is allowed on this provider` | external IdP provider options forbid auto-create/link | enable `is_creation_allowed`/`is_linking_allowed` (§7) |
| `Registration is not allowed` | self-registration off | invite the user instead |
| `The requested redirect_uri is missing in the client configuration.` | Dashboard/Cli app redirect URIs edited, or wrong hostname | restore URIs (§3) |
| `code_challenge required` | Dashboard app auth method changed from None | set to None (PKCE) |
| `Instance not found. Make sure you got the domain right.` | host header ≠ `ZITADEL_EXTERNALDOMAIN` | use the installed domain |
| Dashboard "Oops, something went wrong… Error: …" | token validation failed (issuer/audience) | `03-server-troubleshooting.md` §3 |
| Verification/reset code "expired" | init code valid 72 h, reset code 1 h | resend |
| Device (CLI) login: `Errors.DeviceAuth.NotExisting` | user code expired (5 min) | rerun `netzilo up` |

Login events (`user.login`, `user.failedlogin`, `user.logout`) are imported from Zitadel
into Netzilo Activity every minute; use Activity → Events with the User filter.

---

## 6. E-mail (SMTP) — required for invitations and password-reset mails

The installer configures **no SMTP**. Without it: e-mail invitations, password-reset
mails, and e-mail OTP never arrive (`Errors.SMTPConfig.NotFound` in Zitadel logs).

Console: `https://<domain>/ui/console/instance?id=smtpprovider` → add provider → activate.
API:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  https://$D/admin/v1/email/smtp -d '{
    "senderAddress":"netzilo@example.com","senderName":"Netzilo",
    "tls":true,"host":"smtp.example.com:587","user":"smtp-user","password":"…",
    "replyToAddress":"it@example.com","description":"Corporate relay"}'
# → {"id":"<id>"}; then
curl -sS -X POST -H "Authorization: Bearer $TOKEN" https://$D/admin/v1/email/<id>/_activate
curl -sS -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  https://$D/admin/v1/email/smtp/<id>/_test -d '{"receiverAddress":"you@example.com"}'
```

Rules: `host` must be `host:port`; `tls:true` = implicit TLS (falls back to STARTTLS
automatically on a plaintext port); only one provider can be active. Errors
`Errors.SMTP.CouldNotDial|CouldNotDialTLS|CouldNotStartTLS` = network/TLS to the relay.
Corporate relays often need the sender address whitelisted.

Notification texts (subjects/bodies) are editable at `?id=messagetexts`.

---

## 7. SSO federation (external identity providers)

Zitadel brokers to the corporate IdP; Netzilo keeps using Zitadel as its OIDC issuer, so
nothing changes in `management.json` or the dashboard. Steps (console or API):

1. **Register Zitadel at the external IdP** with callback
   `https://<domain>/ui/login/login/externalidp/callback` (OIDC/OAuth) or SAML ACS
   `https://<domain>/ui/login/login/externalidp/saml/acs`. Collect client id/secret (or
   SAML metadata).
2. **Create the provider** in Zitadel: console `/ui/console/instance/provider/<type>/create`
   (`oidc`, `azure-ad`, `google`, `github`, `gitlab`, `saml`, `ldap`, `jwt`, `oauth`,
   `apple`) — Okta, Auth0, Keycloak, Authentik, JumpCloud, Ping use **Generic OIDC**.
   API examples:
   - Entra ID: `POST /admin/v1/idps/azure` `{"name":"Entra","clientId":"…","clientSecret":"…","tenant":{"tenantId":"<tenant-guid>"},"emailVerified":true,"scopes":["openid","profile","email"],"providerOptions":{"isLinkingAllowed":true,"isCreationAllowed":true,"isAutoCreation":true,"isAutoUpdate":true,"autoLinking":"AUTO_LINKING_OPTION_EMAIL"}}`
   - Generic OIDC (Okta etc.): `POST /admin/v1/idps/generic_oidc` `{"name":"Okta","issuer":"https://<org>.okta.com","clientId":"…","clientSecret":"…","scopes":["openid","profile","email"],"isIdTokenMapping":true,"providerOptions":{…}}`
   - Google: `POST /admin/v1/idps/google` `{"name":"Google","clientId":"…","clientSecret":"…","scopes":["openid","profile","email"],"providerOptions":{…}}`
   - SAML: `POST /admin/v1/idps/saml` `{"name":"ADFS","metadataUrl":"https://…/FederationMetadata.xml","binding":"SAML_BINDING_POST","withSignedRequest":false,"providerOptions":{…}}`
3. **Activate it on the login page** (mandatory, easy to forget):
   `POST /admin/v1/policies/login/idps` `{"idpId":"<id>"}` (console `?id=login` →
   Identity Providers). The login policy must have `allowExternalIdp:true` (default).
4. Provider options: `isAutoCreation` (create the Zitadel user on first SSO login),
   `autoLinking: AUTO_LINKING_OPTION_EMAIL` (link to an existing user by e-mail),
   `isAutoUpdate` (sync profile). Without creation/linking users get
   `Neither creation of linking is allowed on this provider`.
5. Optional: hide username/password login (`allowUsernamePassword:false`) once SSO works
   and at least one admin has tested it. Keep a break-glass local admin.
6. Test at `https://<domain>` → the SSO button appears on the Zitadel login page.

Group claims → Netzilo groups: Netzilo reads groups from the **Zitadel-issued** token.
Zitadel does not forward upstream group claims by default; the installer created (but did
not bind) Actions `addGroupClaim`/`addGroupMeta`/`oktaAuthentication` for this purpose.
Binding them to flows in the console (Actions → Flows → External Authentication /
Complement Token) is required before Settings → Groups → JWT group sync can see a
`role`/`groups` claim. This is an advanced setup: test it with one user before rolling
it out, and keep a local admin account that does not depend on the claim.

Cloud-hosted Netzilo: Okta SSO requires contacting support@netzilo.com to activate;
Google/Microsoft/GitHub personal logins are available by default; IdP sync (SCIM /
Google Workspace / Entra) is a cloud-only feature under Integrations.

---

## 8. Legacy self-hosted path (management talking to a customer IdP directly)

Deployments built from the older `infrastructure_files` templates point the
management server directly at Keycloak/Entra/Okta/Google/Auth0/Authentik/JumpCloud
instead of the bundled Zitadel. Supported `IdpManagerConfig.ManagerType` values:
`zitadel`, `keycloak`, `azure`, `okta`, `google`, `auth0`, `authentik`, `jumpcloud`,
`none`. Required fields per type (startup fails with
`… IdP configuration is incomplete, <field> is missing` otherwise):

| ManagerType | ClientConfig | ExtraConfig |
|---|---|---|
| `zitadel` | ClientID, ClientSecret, TokenEndpoint, GrantType `client_credentials` | `ManagementEndpoint` |
| `keycloak` | ClientID, ClientSecret, TokenEndpoint, GrantType | `AdminEndpoint` (`https://<kc>/admin/realms/netzilo`) |
| `azure` | ClientID, ClientSecret, TokenEndpoint, GrantType | `ObjectId`, `GraphApiEndpoint` (`https://graph.microsoft.com/v1.0`) |
| `okta` | Issuer, TokenEndpoint, GrantType | `ApiToken` |
| `google` | — | `ServiceAccountKey` (base64 JSON), `CustomerId` |
| `auth0` | Issuer, ClientID, ClientSecret, GrantType | `Audience` |
| `authentik` | Issuer, ClientID, TokenEndpoint, GrantType | `Username`, `Password` |
| `jumpcloud` | — | `ApiToken` |

Dashboard-side (`dashboard.env`): `AUTH_AUTHORITY`, `AUTH_CLIENT_ID`, `AUTH_AUDIENCE`,
`AUTH_SUPPORTED_SCOPES`, `USE_AUTH0` (**must be `false` for anything but Auth0** — the
default is `true` and selects Auth0 endpoint paths), `NETBIRD_TOKEN_SOURCE`
(`idToken` for Entra/Okta/Google/JumpCloud). Redirect URIs to register at the IdP:
`https://<domain>/auth`, `https://<domain>/silent-auth`, `http://localhost:53000`
(legacy dashboard paths) — for the current dashboard use `/nb-auth`, `/nb-silent-auth`,
`/nb-auth-x`. The management server fetches `HttpConfig.OIDCConfigEndpoint` at startup
and overrides issuer/JWKS/token endpoints from it.

Note that several Netzilo features (create user with password, change password, MFA
reset, tenant logo, login-event import, self-service registration) call Zitadel
directly and only work when the IdP is Zitadel.

---

## 9. Quick checks

```bash
D=<domain>
curl -sS https://$D/.well-known/openid-configuration | jq '{issuer,authorization_endpoint,token_endpoint,device_authorization_endpoint}'
curl -sS -o /dev/null -w "console %{http_code}\n" https://$D/ui/console/
curl -sS -o /dev/null -w "zitadel ready %{http_code}\n" https://$D/debug/ready
sudo docker compose logs --tail=200 zitadel | grep -iE "smtp|error" | tail -n 20
```
