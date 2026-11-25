---
id: '26'
title: Admin Skill — Profiles (Enterprise Workspace, Enterprise Browser, Disposable Browser, Browser Extension)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 43736
sections:
- id: '1'
  title: Model
  chars: 5216
- id: '2'
  title: Enterprise Workspace — reference
  chars: 5456
- id: '3'
  title: Enterprise Browser — reference
  chars: 994
- id: '4'
  title: Disposable Browser — reference
  chars: 636
- id: '5'
  title: Domain Settings (Browser Extension and Enterprise Browser)
  chars: 5159
- id: 5a-proxy-clientless-access
  title: 5a. Proxy (clientless access)
  chars: 1305
- id: 5b-modify-headers-header-rules
  title: 5b. Modify Headers (header rules)
  chars: 4753
- id: 5c-variables-netzilo-name
  title: 5c. Variables (`%netzilo.<name>%`)
  chars: 3543
- id: '6'
  title: API
  chars: 1450
- id: '7'
  title: Procedures
  chars: 1358
- id: '8'
  title: Diagnosis
  chars: 2932
- id: '9'
  title: Troubleshooting the Workspace
  chars: 10397
---
# Admin Skill — Profiles (Enterprise Workspace, Enterprise Browser, Disposable Browser, Browser Extension)

**Dashboard:** Endpoint → **Profiles** (`/profiles`). **API:** `/api/profiles`,
`/api/templates/{category}`. **Licence:** saving a profile requires the **Enterprise**
plan (other plans see **Upgrade Plan**); self-hosted servers qualify.

A profile binds data-in-use controls to **groups** and **operating systems** and is
delivered to the Netzilo client on matching devices. Four components can be combined in
one profile.

---

## 1. Model

| Component | What it controls | Where it runs |
|---|---|---|
| **Enterprise Workspace** | native Windows applications ("work apps") run inside an isolated, optionally encrypted enclave with restrictions (clipboard, printing, screen sharing, keylogging, watermark, recording, integrity) and optional posture checks | Windows x64, full (admin) install only |
| **Enterprise Browser** | Netzilo's own Chromium-based browser: bookmarks, per-domain restrictions, extension allow/block list, encrypted profile, wipe on close | Windows, macOS (mobile apps exist) |
| **Disposable Browser** | isolated throw-away browser sessions; everything is destroyed on close | Windows x64, full (admin) install only |
| **Enterprise Browser Extension** | per-domain DLP inside the user's normal browser (Chrome/Edge/Firefox/Safari): downloads, URL blocking, redaction, watermark, clipboard, printing, source-code controls, classified content; the client force-installs the extension in Chrome/Edge when such a profile applies. Its **Proxy** tab turns on clientless access for the profile's users (§5a) | any OS with a supported browser (Proxy: Chromium-based browsers and Firefox, not Safari) |

**Add Profile** opens the dialog of that name; an existing profile opens **Edit
Profile**. Profile fields: **Groups** (required), **OS** (Windows, Darwin, Linux, Android, iOS;
default Windows), components, **Enable Profile**, Name, Description. A device gets a
profile when it is in one of the groups and runs one of the OSs. Posture checks can gate
the workspace and each domain setting (All/Any evaluation).

Table: Name (enabled dot), Active toggle, OS icons, Groups, Components icons, Delete.

**Platform scope — read before promising a workspace to anyone.** The Enterprise
Workspace and the Disposable Browser exist only on Windows x64 devices with the full
(administrator) install. An ARM64 Windows device and a non-admin install get the network
client only: no workspace, no Disposable Browser, whatever the profile says. macOS and
Linux have neither. Selecting Darwin or Linux in a profile's OS list still delivers the
profile's Browser Extension and Enterprise Browser parts there, never a workspace.

**The "Enterprise Workspace" and "Enterprise Browser" posture signals** (Advanced
Endpoint Settings, `21-posture-checks.md`) describe the peer, not the person. On Windows
the workspace signal is true only on a workspace's own peer (name ending `-WORKSPACE`,
§9) and the browser signal only on the Enterprise Browser's own peer (`-BROWSER`), never
on the ordinary Windows host peer. On macOS the workspace signal is true when the Mac is
MDM- or DEP-enrolled, and such a Mac's peer name can end in `-WORKSPACE` too: that is the
Mac itself, not a workspace. On Linux it is never true. Putting either check on an
ordinary network policy therefore blocks every normal host in its source groups; attach
it only to policies whose sources are workspace or browser peers. The third signal of
that card, **Netzilo Gateway**, is true only for a clientless-access browser session
(`43-clientless-access-gateway.md` §3.4) and false on every device with the client; it
is the way to write a policy that admits browser users and nobody else. When a customer
says "everyone lost access after we added a posture check", ask which check first (§9).

**How a workspace comes to exist on a device.** When a profile with an Enterprise
Workspace reaches a Windows x64 admin-installed device, the client service creates the
workspace and places shortcuts for the work apps on the user's Desktop and under Start
Menu → Programs → Netzilo → *<folder name>*. Shortcuts appear only when **Create Desktop
Shortcut for Work Apps** has a folder name *and* the application exists at its configured
path (Chrome and Edge are located automatically for the Disposable Browser). A workspace
with an **Encryption Key** is backed by an encrypted disk image `C:\Netzilo\<name>.box`,
sized once at creation to the smaller of 4 GB and half the free space on the system drive;
with **Use Workspace Filesystem** it is instead an encrypted folder under the user's
`AppData\LocalLow\Containers\<name>`. A workspace without a key isolates the work apps
without a separate disk. The Disposable Browser is a separate sandboxed browser. A
per-session engine process supervises the work apps; if that process exits, the work apps
close with it.

**Extension bookmarks** (`extension_bookmarks`) are not shown inside the browser
extension. They appear on the **Workplace** (the dashboard's `/workplace`, the desktop
app's window and the extension's Workplace page, `47-agentic-access-workplace.md` §9), which lists
the bookmarks of every enabled profile whose groups include one of the signed-in
**user's** groups (or All) and whose OS list includes the OS of the browser viewing the
page; opened in the Enterprise Browser, it adds that browser's bookmarks. Each web tile
carries an **Online** / **Offline** pill from the browser's own check, none for an `http://`
address (`47-agentic-access-workplace.md` §8.1). The account
setting **Disable portal access for regular users** hides the page from regular users
(`25-users-groups-and-account-settings.md`).

---

## 2. Enterprise Workspace — reference

Card text: "Creates a secure and isolated enclave on endpoints to protect data accessed by
work applications". Tabs **Work Apps**, **Restrictions**, **Posture Checks**.

**Work Apps**: rows of application paths (regex/wildcards allowed; suggestions from a
template list), e.g. `c:\windows\system32\notepad.exe`. ⋯ opens **Application
Settings**: path, command line arguments, friendly name, allowed **hashes**, allowed
**signers**. The application must already exist on the device — profiles do not
distribute software.

**Restrictions**:

| Setting | Help text | Value |
|---|---|---|
| Enforce Isolation | "Creates an isolated enclave on the endpoint for work apps" | opens Settings (below) |
| Add Watermark | "Adds a watermark to the graphical user interface of work apps" | text, Dense / Sparse. Any `%netzilo.<name>%` variable of §5c is filled in per user and device, e.g. `%netzilo.username% - CONFIDENTIAL`. Older `[USERNAME] - [DATE]` placeholders are printed literally — replace them |
| Restrict Clipboard Access | "Restrict copying and pasting data from work apps to non-work apps" | **from** workspace = users cannot copy out of work apps; **to** workspace = users cannot paste into them; **to and from** = both |
| Restrict Printing | "Prevents work apps from printing sensitive data" | toggle |
| Restrict Screen Sharing | "Prevents screen capturing or sharing apps to grab the screens of work apps" | toggle; mutually exclusive with Record Desktop Activity — turning one on turns the other off |
| Record Desktop Activity | "Video records the desktop of users while they use workspace apps" | requires an **Amazon S3 or Min.io** event-streaming integration and a **privacy policy link** the user must accept before the first work app opens; the recorder runs as its own process and pauses while the user is idle; if it cannot start (declined consent, missing storage) the work app does not open and the workspace closes; recordings appear in Activity as `session.recorded` once the first chunk has uploaded |
| Restrict Key-logging | "Prevents key-logging applications to record key strokes of work apps" | toggle; protects keystrokes typed into work-app windows |
| Verify Workspace Integrity | "Hardens work apps against advanced attacks such as device rooting, debugging or memory injection attacks" | toggle; detections are recorded as `workspace.injection.detected` / `workspace.selfdefense.activated` events for the admin to act on |
| Create Desktop Shortcut for Work Apps | "Choose a folder name where users can find shortcuts for work apps" | folder name; created on the Desktop **and** under Start Menu → Programs → Netzilo. Every profile sync deletes and recreates that Desktop folder — never point it at a folder that already holds the user's own files |
| Show Border | "Draws a border around work apps to identify them visually" | colour or None |

**Enforce Isolation → Settings**:

| Setting | Help text | Notes |
|---|---|---|
| Encryption Key | "Optional. Encryption key used for encrypting the virtual disk created for secure enclave." | generate/copy; creates the fixed-size disk image `C:\Netzilo\<name>.box` (§1); changing the key once the disk exists **resets the workspace and wipes its data** (confirm dialog) |
| Use Workspace Filesystem | "Optional. Use encrypted container file system for better compatibility and performance." | toggle + **Allowed Apps** paths that may access it; data lives in an encrypted folder under the user's `AppData\LocalLow\Containers\<name>` instead of the disk image |
| Setup Key for Netzilo Network | "Optional. A setup key that is used to authenticate work apps to a Netzilo Network." | the workspace runs **its own Netzilo instance**, enrolled with this key as a separate peer named `<host>-WORKSPACE` (config `%ProgramData%\Netzilo\<workspace>.json`, log `%ProgramData%\Netzilo\client.<workspace>.log`). All work-app traffic leaves through that peer and reaches only what *its* groups and policies allow. Use a reusable key: a one-off, expired, revoked or exhausted key leaves the workspace with no network (§9). Without a key, work apps use the host's network and tunnel |
| Use Workspace VPN | "Define VPN adapters exclusively for workspace." | adapters + allowed apps |
| Create Document Shortcuts | "Creates outside shortcuts for documents(e.g. .pdf, .ppt) downloaded inside isolated enclave for easy access" | toggle |
| Wipe Data When Closed | "Disposes all data e.g. files downloaded created inside enclave when all work apps are closed" | toggle |
| Trusted Certificates | "Define X.509 certificates to be trusted by applications running in workspace" | name + certificate (+ key) uploads |

**Posture Checks** tab: browse/new; **All** / **Any** evaluation. The workspace
re-evaluates its checks continuously (about every 15 seconds). A failing check **blurs the
work-app windows** and records a `workspace.posture.check` event; it does not stop the
workspace from opening. The blur clears on its own once the check passes again.

**Changing a live workspace.** When an administrator saves a change to the profile's
Workspace component (work apps, restrictions, isolation settings, posture checks), open
workspaces show "**Your workspace will be restarted in N seconds.**" and restart. Tell
users to save their work before the admin saves. Changing the encryption key is the one
change that also wipes the workspace's data.

---

## 3. Enterprise Browser — reference

Card text: "Configures Netzilo enterprise browser to protect data delivered through web
applications". Tabs **Shortcuts** (bookmarks: URL, name, drag to order), **Restrictions**
(domain rows → **Domain Settings**, §5), **Security**:

| Setting | Help text |
|---|---|
| Extension Control | "Restrict browser extensions by defining allowed or blocked ones" — Allow / Block + extension IDs |
| Encryption Key | as in Workspace; encrypts the browser's on-disk data |
| Wipe Data When Closed | disposes downloaded data when the browser closes |

The Enterprise Browser is installed separately (`10-ai-security-aidr.md` §6; every installer switch and MSI property in `48-installer-command-lines.md` §13–16); the
profile only configures it. Its new tab is the Workplace, where the **Shortcuts** join
the Applications; signed out, the new tab shows the workplace picker, which lists only the tenant
when the browser is locked to it (`48` §13.5, `47` §9.2).

---

## 4. Disposable Browser — reference

Card text: "Creates a secure and isolated browsing environment on endpoints to protect
them against infections and web borne threats". Single setting: **Desktop Folder Name**
where users find the disposable browser shortcuts. Turn off by clearing the name. All
session data (history, cookies, cache, passwords, storage) is destroyed on close; tell
users to save work externally.

Windows x64 admin install only (§1). The shortcuts ("Disposable Google Chrome",
"Disposable Microsoft Edge") are created for whichever of Chrome and Edge is installed;
nothing is created when neither is present.

---

## 5. Domain Settings (Browser Extension and Enterprise Browser)

Header: "Configure protection settings for the web domain". Domain field: e.g.
`.netzilo.com` (leading dot = domain and subdomains). Tabs **Restrictions** / **Posture Checks**.

| Setting | Help text | Notes |
|---|---|---|
| Use Enterprise Workspace | "Enforces use of Enterprise Workspace while visiting matching web domains" | only when the profile has a Workspace; exclusive with Disposable Browser. On a Windows device with a workspace, the extension replaces the page with **Browse in Netzilo Workspace**, which hands the URL to the workspace (an `nz://` link). On macOS, Linux, ARM64 or non-admin installs the page is simply blocked — there is no workspace to open |
| Use Disposable Browser | "Enforces use of disposable browser while visiting matching web domains" | only when Disposable Browser is configured; same pattern — **Browse with Disposable Browser** on Windows, blocked elsewhere |
| Restrict Downloads | "Restrict files that could be downloaded from matching web domains" | `all`, or regex matching file content; templates offered |
| Restrict Uploads (Enterprise Browser only) | "Restrict files that could be uploaded to matching web domains" | same |
| Block URLs | "Define URL patterns that should be blocked from being accessed" | patterns/regex |
| Restrict Content → Redact Data | "Define sensitive data patterns and mask them before displaying" | rows: Pattern (regex; templates for cards, SSNs…), Mask with, Last N visible |
| Restrict Content → Add Watermark | "Adds a watermark to web site while visiting" | text, Dense/Sparse |
| Restrict Content → Restrict Clipboard | "Restrict copying and pasting data from matching web domains" | toggle; Enterprise Browser variant adds allowed paste domains |
| Restrict Content → Restrict Printing | "Prevents browser from printing sensitive data from matching domains" | toggle |
| Restrict Content → Restrict Viewing Classified Content | "Block access to content based on your organization's data classification labels" | labels Public / Private / Confidential / Secret (custom allowed, max 10); must match the organisation's DLP labels |
| Restrict Screen Sharing (Enterprise Browser only) | "Prevents screen capturing or sharing apps to grab the screens of work apps" | toggle |
| Restrict Key Logging (Enterprise Browser only) | "Prevents key logging apps from logging keystrokes" | toggle |
| Show Gray Border | "Draws a gray border around protected web content" | toggle |
| Modify Headers | "Set, append or remove HTTP request and response headers for this domain" | rows of Request/Response, Set/Append/Remove, Header, Value; values may hold `%netzilo.*%` variables (§5b, §5c) |
| Allow Exceptions | "Define exceptions for restrictions for certain users" | **Allow temporary removal of restrictions** on/off; **Expires in** 1–180 **Hours** or **Minutes** (default 24 hours; stored in seconds as `allow_exception.expiration`); **Provide a link to the following support site:**; **Allow exceptions for the following groups:** |

The Enterprise Browser's domain settings are therefore Use Enterprise Workspace, Use
Disposable Browser, Restrict Downloads, Restrict Uploads, Block URLs, Restrict Content,
Restrict Screen Sharing, Restrict Key Logging, Show Gray Border, Modify Headers and Allow Exceptions; the
extension's are the same without Restrict Uploads, Restrict Screen Sharing and Restrict
Key Logging. Older dashboards also show **Prevent LLM Prompt Injections**, **Make
Session Cookies Temporary** and, for the Enterprise Browser, **Verify Workspace
Integrity**: nothing on the device acts on them. They also offer **Restrict Uploading
Source Code** and **Restrict Viewing Source Code** under Restrict Content
(`restrict_upload_source`, `restrict_view_source`); the dashboard no longer does, and
saving a domain's Restrict Content turns both off. Govern AI chats with guardrails
(`49-browser-extension-aidr.md`); the Enterprise Workspace keeps its own **Verify
Workspace Integrity** (§2).

Every restriction produces events: `browser.url.blocked`, `browser.download.file`,
`browser.upload.file`, `browser.download.content` (content regex hit),
`browser.data.redacted`, `browser.data.print.blocked`, `browser.data.clipboard.blocked`,
`browser.data.code.upload.blocked`, `browser.data.code.redacted`, `browser.data.classified`,
`browser.data.screenshot.blocked`,
`browser.isolation.bluezone.required` (workspace required), `browser.isolation.redzone.required`
(disposable browser required), `browser.posture.check`, `browser.exception.request`,
`browser.url.access`.

**Published applications are not domain settings.** A published application has its own
**Restrictions** tab (watermark, redaction, clipboard, printing, downloads, uploads, block
URLs, gray border) that the reverse proxy enforces in its pages for every browser, with or
without the extension (`44-published-applications.md` §4.2). The extension does not
receive those, and a profile domain setting for the application's address applies in
addition, in browsers that carry the extension. Set the application's rules on the
application.

---

## 5a. Proxy (clientless access)

The extension component's **Proxy** tab decides whether the profile's users reach
internal resources from the browser through a Netzilo gateway, without the client.
Field `components.extension_proxy`:
`{"mode": "disabled" | "auto" | "custom", "pac": "…", "upstream": {"type": "none" | "proxy" | "pac", "value": "…"}}`.

| UI | Field | Notes |
|---|---|---|
| **Browser routing**: Disabled (default) / Automatic / Custom PAC | `mode` | Automatic needs Settings → Permissions → Allow clientless access; Custom PAC is served regardless |
| **Corporate proxy**: None (direct) / Proxy host:port / PAC URL | `upstream` | Automatic only; for a proxy set in the operating system, which the extension cannot see |
| **PAC script** (Custom PAC) | `pac` | must define `FindProxyForURL`, at most 64 KiB; send gateway traffic with `HTTPS host:port` |
| **Generate** | `POST /api/profiles/pac` | fills the editor with what Automatic would serve for chosen groups and OS; a snapshot, regenerate after routing changes |

A browser follows the first enabled profile by name, for its OS, whose groups hold one of
the user's groups and that has a proxy setting. How the routing is computed, the gateway,
and every "unavailable" reason: `43-clientless-access-gateway.md` §3 and §11.2.

---

## 5b. Modify Headers (header rules)

A domain setting's **Modify Headers** card changes HTTP headers on every request the
browser makes to the domain and its subdomains (pages, frames, scripts, fetch/XHR,
images, fonts, media, WebSockets) and on their responses. The extension applies them in
Chrome, Edge, Firefox, Safari and the Enterprise Browser on desktop; the Enterprise
Browser takes the rules of the profile's **Enterprise Browser** section, a browser with
the extension those of its **Enterprise Browser Extension** section. Field `headers` on
each entry of `browser_extension[]` and `enterprise_browser.domain_settings[]`:

```json
"headers": [
  {"target": "request",  "operation": "set",    "name": "X-Forwarded-For", "value": "%netzilo.externalip%, %netzilo.localip%"},
  {"target": "request",  "operation": "remove", "name": "X-Client-Data"},
  {"target": "response", "operation": "set",    "name": "Cache-Control",   "value": "no-store"}
]
```

| Field | Values | Meaning |
|---|---|---|
| `target` | `request` / `response` | the request to the domain, or its response |
| `operation` | `set` | send the header with this value, replacing one the page or the server set |
| | `append` | add the value to the header (comma-joined after an existing value; the header alone when there is none). On **requests** browsers append only to `Accept`, `Accept-Encoding`, `Accept-Language`, `Access-Control-Request-Headers`, `Cache-Control`, `Connection`, `Content-Language`, `Cookie`, `Forwarded`, `If-Match`, `If-None-Match`, `Keep-Alive`, `Range`, `TE`, `Trailer`, `Transfer-Encoding`, `Upgrade`, `User-Agent`, `Via`, `Want-Digest`, `X-Forwarded-For`; on responses to any header. Chrome and Edge need version 128 or later to append to a request header |
| | `remove` | drop the header (no `value`) |
| `name` | an HTTP header name (letters, digits and ``!#$%&'*+.^_`|~-``, at most 256) | |
| `value` | one line, at most 1024 characters, for `set` and `append` | may hold any variable of §5c, filled in per user and device before delivery |

**Rules.**
- A rule whose value names a variable without a value in that mode (e.g. `%netzilo.localip%`
  for the extension without the client, §5c) is **left out**: the header is not sent, never
  sent half-filled. A rule whose filled-in value would contain a line break is left out too.
- A domain setting changes a header at most once per direction (two rows for
  `X-Forwarded-For` on requests are refused; one on requests and one on responses are two
  changes).
- A `*` domain setting covers every domain that no other domain setting of the user's
  profiles names (also one without header rules), never the Netzilo sites themselves
  (`netzilo.com`).
- Where two profiles change the same header of a domain, the earlier profile wins.
- **Allow Exceptions** does not lift header rules: a temporary exception removes
  restrictions, not the headers (tenant restrictions stay in force).
- The domain may be written as a host (`app.example.com`, `.example.com`, `*.example.com`
  — all cover the subdomains) or a URL; a scheme, path and port are ignored, and
  international names are converted. An entry that is no host name is ignored.
- Changes reach a device with a client at its next update from management (seconds), and
  the extension alone within half a minute. The extension from 5.6.640 on applies header
  rules (it no longer sends the former `X-Netzilo-Config` header to any site).

**Typical rules.**

| Goal | Rule |
|---|---|
| Microsoft tenant restrictions | on `login.microsoftonline.com`, `login.microsoft.com`, `login.windows.net`: set `Restrict-Access-To-Tenants: contoso.com,fabrikam.com` and `Restrict-Access-Context: <directory ID>` |
| Google Workspace allowed domains | on `.google.com`: set `X-GoogApps-Allowed-Domains: example.com` |
| Pass the device's addresses to an app or its WAF | set `X-Forwarded-For: %netzilo.externalip%, %netzilo.localip%`; or append `%netzilo.ip%` to the one the page sends |
| Tell an app who and what is calling | set `X-User: %netzilo.email%`, `X-Device: %netzilo.hostname% (%netzilo.os% %netzilo.osversion%)` |
| Strip a header | remove `X-Client-Data`, or remove `Server` on responses |
| Keep pages out of the disk cache | response: set `Cache-Control: no-store` |

The profiles API refuses (HTTP 422, the message names the domain setting and the
header) a header name that is not a token, a value with a line break or over 1024
characters, `remove` with a value, `set`/`append` without one, `append` to a request
header outside the list above, a variable that is not in §5c (spelling and case count:
`%netzilo.Email%` is refused) and a header changed twice in one direction. The
dashboard's dialog points the same out before saving.

---

## 5c. Variables (`%netzilo.<name>%`)

Management fills these in for each user and device before it delivers a profile: in
header values (§5b), domain-setting and workspace watermarks, the workspace's **Create
desktop shortcuts** folder, work app paths and the Disposable Browser folder. A published
application's watermark takes the subset in the last column (`44-published-applications.md`
§4.2). Text that only looks like a variable stays as written; a variable without a value
becomes empty text in a watermark or path and leaves its header rule out (§5b).

| Variable | With the client (Enterprise Browser, extension next to the desktop client, workspace) | Extension without the client | Published app watermark |
|---|---|---|---|
| `%netzilo.username%` | the user's name in the identity provider (service users: their name) | same; `Unknown` when there is none | same as without the client |
| `%netzilo.email%` | the user's email in the identity provider | same | — |
| `%netzilo.userid%` | the user's Netzilo ID | same | — |
| `%netzilo.groups%` | the names of the user's groups, `, `-separated | same | — |
| `%netzilo.tenant%` | the tenant's subdomain on Netzilo Cloud, else the account's domain | same | — |
| `%netzilo.ip%` | the device's Netzilo address | the public address (as `externalip`: without the client there is no Netzilo address) | the public address |
| `%netzilo.externalip%` | the address management sees the device connect from: the public address behind NAT, or the egress of a corporate proxy or another VPN on the way; refreshed at every update | the address the extension's own policy request comes from | the public address at sign-in |
| `%netzilo.country%` | country code of `externalip` by geolocation | same | same |
| `%netzilo.region%` | city of `externalip` by geolocation | same; `Unknown` when it cannot be located | same |
| `%netzilo.localip%` | the local address the device reaches management from (the interface it actually uses, not a VM or container bridge; clients before 5.6.640: the first address they report) | — (browsers do not expose local addresses) | — |
| `%netzilo.localips%` | all local addresses, that one first, `, `-separated (no loopback, link-local or Netzilo address) | — | — |
| `%netzilo.hostname%` | the device's name | — | — |
| `%netzilo.fqdn%` | the device's Netzilo DNS name | — | — |
| `%netzilo.deviceid%` | the device ID the client reports | the extension's device ID (from 5.6.640) | the extension's device ID when it asserts one |
| `%netzilo.os%`, `%netzilo.osversion%` | operating system and version the client reports | the browser's (the extension's report, else the browser's own headers) | same as without the client |
| `%netzilo.serial%` | the device's serial number | — | — |
| `%netzilo.clientversion%` | the Netzilo client's version | the extension's version (from 5.6.640) | same as without the client |
| `%netzilo.browser%`, `%netzilo.browserversion%` | — (a device has many browsers) | the browser's name and version | same |

"—" means no value: the header rule is left out, the text gets nothing. Choose
variables by where the rule runs: for the extension without the client use
`externalip`, `os`, `browser`, `deviceid` and the user's variables; device details
(`localip`, `hostname`, `serial`) need the client. Management takes the connecting
address from `X-Real-IP`, then the first `X-Forwarded-For` entry, then the connection
itself: the reverse proxy in front of management must overwrite or remove both headers on
what devices send.

---

## 6. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET/POST /api/profiles ; PUT/DELETE /api/profiles/{id}
GET /api/templates/{work_app|saas_domain|redact_regex|block_url}
```
Body: `{"name","description","enabled","os":["Windows"],"groups":["<gid>"],
"components":{"netzilo_workspace":{"work_apps":[{"path":"…","cmd":"","name":"","hashes":[],"signers":[]}],"restrictions":{…},"checks":["<pc-id>"],"any_check_must_pass":false,"use_fuse":false,"fuse_allowed_apps":[]},
"browser_extension":[{"name":".example.com","block_urls":[],"restrict_downloads":[],"redact":[{"regex":"…","mask_with":"***","show_last":4}],"headers":[{"target":"request","operation":"set","name":"X-Forwarded-For","value":"%netzilo.externalip%"}],"checks":[],"any_check_must_pass":false, …}],
"extension_bookmarks":[{"name":"HR","url":"https://hr.example.com"}],
"extension_proxy":{"mode":"auto","upstream":{"type":"none"}},
"disposable_browser":"Disposable Browsers",
"enterprise_browser":{"domain_settings":[…],"bookmarks":[…],"encryption_key":"","wipe_data_when_closed":false,"extension_control":{"action":"allow","extensions":["<id>"]}}}}`
Read an existing profile with `GET` to see the exact shape before writing.

---

## 7. Procedures

- **Protect a SaaS app in normal browsers**: profile → OS Windows+Darwin → Browser
  Extension → domain `.salesforce.com` → Restrict Downloads `all`, Redact Data (card
  numbers), Restrict Printing, Watermark → Posture Checks (disk encryption) → Enable.
  Users' Chrome/Edge get the extension force-installed by the client — but only once the
  profile contains at least one Browser Extension domain setting; a profile with no
  domain rows installs nothing. On Linux the same managed policy also blocks every
  other extension in that browser, so warn Linux users before enabling.
- **Force sensitive apps into the workspace**: Workspace with Work Apps (Excel, SAP
  GUI) + Enforce Isolation (encryption key, wipe on close) + clipboard/print
  restrictions; add domain settings with **Use Enterprise Workspace** for the web
  front-ends.
- **Kiosk/untrusted browsing**: Disposable Browser folder + domain settings with **Use
  Disposable Browser** for high-risk categories.
- **Record contractor sessions**: configure Integrations → Event Streaming (S3/Min.io)
  first; then Record Desktop Activity with a privacy policy link; recordings appear in
  Activity (play icon) and in User Activity reports.
- **Exceptions**: Allow Exceptions with a support link and an approver group; requests
  are logged as `browser.exception.request`.

---

## 8. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Save shows **Upgrade Plan** | not Enterprise | upgrade (cloud) |
| Profile saved but nothing happens on devices | device not in profile groups or OS; profile disabled; client not connected | check groups/OS/Active; `netzilo status`; wait ~30 s |
| Extension not installed in Chrome/Edge | device is the Enterprise Browser (extension bundled) or Linux desktop policy path unsupported by that browser | install manually from the store or via browser policy (`10` §6) |
| Domain rules not applying | domain written without leading dot (subdomains not covered); posture check failing (`browser.posture.check` events) | fix domain; check |
| Workspace won't launch, no shortcuts, no network in work apps, blurred windows | see the dedicated table | §9 |
| "Record Desktop Activity" greyed out | no S3/Min.io integration | Integrations → Event Streaming |
| Users lose enclave files | Wipe Data When Closed on, or encryption key changed | expected; document it |
| Component icon missing in table for Enterprise Browser | display only | ignore |
| Older dashboards: a delete tooltip about policies is always shown | display only | delete proceeds |
| A header rule has no effect | the rule names a variable without a value in that mode (§5c: e.g. `%netzilo.localip%` with the extension alone), so it is left out; the domain is named by another domain setting, so a `*` rule does not cover it; an earlier profile changes the same header; the extension is older than 5.6.640; in Chrome/Edge before 128 an `append` to a request header is refused | read the expanded rules with `GET /api/profiles?expand=true` as that user; use a variable the mode has; update the extension or browser. The extension logs a refused rule as `session rules 10000-20000: … refused` |
| Saving a profile fails with 422 and a header message | §5b validation | fix the named rule |
| `X-Forwarded-For` shows the address of a proxy, not the device | `externalip` is the address management sees: a corporate proxy or VPN in front of the device, or an ingress that does not set `X-Real-IP`/`X-Forwarded-For` | expected for a proxy; make the reverse proxy in front of management set or strip `X-Real-IP` and `X-Forwarded-For` (§5c) |
| `%netzilo.localip%` is a container or VM address | a client before 5.6.640 (reports its first address) | update the client; or use `%netzilo.localips%` |
| Exception ends after minutes although hours were entered | the domain setting was saved by an older dashboard, which stored an hours value as minutes (2 hours → 120 s); minutes were stored correctly | open the domain setting, re-enter **Expires in**, save |

Events: `profile.created/updated/removed`, plus the browser/workspace events in §5 and
`workspace.app.started`, `workspace.posture.check`, `workspace.print.blocked`,
`workspace.injection.detected`, `workspace.selfdefense.activated`, `session.recorded`.

---

## 9. Troubleshooting the Workspace

Use this when an end user or admin reports that the Enterprise Workspace or Disposable
Browser is missing, will not open, has no network, looks wrong, or closed by itself.
`39-end-user-self-service.md` sends regular users' complaints here.

**Ground rules before you touch anything.**

- **Platform first.** Windows x64 with the full (admin) install is the only place a
  workspace exists (§1). On ARM64, a non-admin install, macOS or Linux the answer is
  "this feature is not available on your device", not a repair.
- **Two peers, two sets of tools.** A workspace with a setup key is its own peer,
  `<host>-WORKSPACE`, enrolled by key and therefore **owned by no user**. A regular user's
  session cannot run device tools against it (`39` §2 rule: only their own devices);
  an admin can. The host peer is where `diag.*`, `mod.*` and `shell.run` land in a
  regular-user session, and the workspace's files are visible from there.
- **Never print a workspace's command line or configuration file.** Both carry the
  encryption and setup keys. Read exit codes, service states, file sizes and log lines
  instead. If you accidentally receive one in tool output, do not repeat it.
- **Native workspace logs are encrypted.** The engine's own logs under
  `%ProgramData%\Netzilo Client` cannot be read on the device; collect them for
  escalation. The readable evidence is `client.log`, `client.<workspace>.log` and the
  checks below.
- **Restart with care.** A failed workspace creation is **not** retried by `mod.refresh`
  while the profile is unchanged; a profile edit by the admin or a client service restart
  is what retries it. A service restart logs the device out
  (`06-client-cli-reference.md`, `36-device-tools.md`) — get the user's consent and
  choose a moment when nothing is in flight. **Reset** destroys the workspace's data;
  never do it without the user (and, for an encrypted workspace, the admin) agreeing.

### 9.1 Evidence to collect

| Question | How (host peer unless noted) |
|---|---|
| Does the device qualify? | `diag.status`/peer record for OS = Windows, architecture x64; the user or admin confirms which installer was used (full/admin vs non-admin) |
| Is the workspace peer alive? | `GET /api/peers`, filter names ending `-WORKSPACE`; check `connected`, `last_seen`, groups. Absent = never enrolled (key problem, §9.3 row 1) |
| Is the setup key usable? | `GET /api/setup-keys/{id}`: `valid`, `revoked`, `expires`, `usage_limit` vs `used_times`, `type` (a `one-off` key is spent after the first enrolment) |
| Did the workspace's own client log in? | `diag.grep {file: "client.<workspace>.log", pattern: "login\|setup key\|failed\|Connected", ignore_case: true}` |
| Did creation fail? | `diag.grep {file: "client.log", pattern: "Error running command", ignore_case: true}` → `exit status <N>`, table in §9.2 |
| Are the services present and running? | `shell.run` PowerShell `Get-Service NtzlSvc,NtzlSb,ntzldrv,imdisk` (`imdisk` is the virtual-disk driver an encrypted workspace needs) |
| Is the work app really there? | `shell.run` `Test-Path '<app path from the profile>'` — use the exact configured path |
| Were shortcuts created? | list `$env:USERPROFILE\Desktop\<folder>` and `$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Netzilo\<folder>` (as:"user"); if they sit in `C:\Users\Public\Desktop` or `%ProgramData%\Microsoft\Windows\Start Menu\Programs\Netzilo` instead, the service could not see a signed-in user when it created them |
| Does the encrypted disk exist and how big is it? | `(Get-Item C:\Netzilo\<name>.box).Length` — fixed at creation, see §1 |
| Did the per-session engine start? | `reg query HKCU\Software\Netzilo\EngineInstance` as:"user" — each value holds an engine start result; non-zero means that engine failed to start |
| Is the local posture service reachable? | `Test-NetConnection 127.0.0.1 -Port 41336` |
| What did the workspace record? | Activity: `workspace.app.started`, `workspace.posture.check`, `workspace.injection.detected`, `workspace.selfdefense.activated`, `session.recorded` for that peer |

### 9.2 Creation exit codes

`client.log` line `Error running command: exit status <N>`:

| N | Meaning for the user |
|---|---|
| 1, 6, 9, 14 | internal or engine failure — collect logs, retry after a profile change or service restart, escalate if it repeats |
| 2, 10 | the profile as delivered could not be applied on this device — review the work-app rows and Enforce Isolation settings, then save the profile again |
| 3 | the workspace name is not acceptable — rename the profile to plain characters |
| 4 | the work app could not be started — wrong path, blocked by security software, or the user declined the recording consent |
| 5 | a work-app command line is too long — shorten arguments |
| 7 | the workspace no longer exists on disk — a profile change or service restart recreates it |
| 8 | a workspace with that name already exists — a profile change retries; if it repeats, Reset (destructive) |
| 11 | encrypted workspace configured but no key reached the device — check the profile's Encryption Key |
| 12, 13 | the encrypted disk could not be created or mounted — `imdisk` driver missing/stopped, or not enough free space on the system drive |
| 15 | this workspace type needs the admin (full) install — the device has the non-admin client |
| 16 | reboot required (typically right after install or upgrade) |
| 17 | the workspace must be reset — the encryption key changed; the client resets and recreates it, wiping its data |
| 18 | a work app failed hash/signer validation — the binary changed (update) or the rule is wrong |
| 19 | the workspace is corrupted — Reset (destructive) |
| 21–23 | the Workspace Filesystem could not start or mount — usually security software; see the last row of §9.3 |

### 9.3 Symptom table (most likely first)

| Symptom | What is happening | Do |
|---|---|---|
| Work apps have no network; "Initializing Netzilo ..." splash never clears; browser inside says offline | Setup key for the workspace is one-off/expired/revoked/exhausted, so the `-WORKSPACE` peer never logged in — or it logged in but its groups have no policy to the destination | `GET /api/setup-keys/{id}`; `client.<workspace>.log` grep; `GET /api/peers` for the `-WORKSPACE` peer. Admin replaces the key with a reusable one (a profile change restarts the workspace) or fixes the peer's groups/policies (`20`) |
| Every ordinary host lost access right after a policy change | An **Enterprise Workspace** or **Enterprise Browser** posture check was put on a normal policy; those signals are true only on `-WORKSPACE`/`-BROWSER` peers (§1) | Move the check to a policy whose sources are the workspace/browser peers; `21-posture-checks.md` |
| No shortcuts on the Desktop / Start Menu | (a) **Create Desktop Shortcut** folder name is empty; (b) the app is not at its configured path (`Test-Path`); (c) the service started before the user signed in, so shortcuts went to `C:\Users\Public\Desktop`; (d) creation failed (§9.2) | (a) admin sets a folder name; (b) install the app or fix the path — profiles never install software; (c) they appear for the user after the next sign-in or service restart; (d) exit-code table |
| Workspace never created at all | ARM64 or non-admin install (exit 15); services stopped; `imdisk` missing for an encrypted workspace; profile does not reach the device (groups/OS/disabled) | platform answer; `Get-Service`; `GET /api/profiles` and `GET /api/peers/{id}` groups; §8 second row |
| "Browse in Netzilo Workspace" does nothing, or the page is just blocked | Not Windows x64 admin — blocked is the only outcome elsewhere; on Windows, the workspace was never created (§9.2) so there is nothing for the `nz://` link to open | platform answer; check the shortcuts exist; `Get-Service NtzlSvc`; creation exit codes |
| Work app opens then closes at once; or never opens with **Record Desktop Activity** on | The recorder could not run: the user declined the privacy consent, or the S3/Min.io event-streaming integration is missing/misconfigured; the workspace closes when its recorder cannot run | Ask whether a consent prompt appeared; admin checks Integrations → Event Streaming; a `session.recorded` event proves the pipeline works |
| "Your workspace will be restarted in N seconds." | An admin saved a change to the Workspace component (§2) | Expected. Users save and let it restart; nothing to fix unless it repeats without admin changes — then check who is editing the profile (`profile.updated` events) |
| "Disk full" inside the workspace, saves fail | The encrypted disk is sized once at creation (≤ 4 GB or half the free space at that time) and does not grow | Users move files out of the workspace first (Create Document Shortcuts helps); the only way to a bigger disk is **Reset** (destroys the data — consent first) and recreate while the system drive has more free space, or the admin switches the profile to Use Workspace Filesystem |
| Work-app windows are blurred | A workspace posture check is failing (re-checked about every 15 s); `workspace.posture.check` events say which | Fix the underlying check (disk encryption, screen lock, antivirus, …, `21`); the blur clears by itself when it passes |
| Files the user put in the shortcut folder vanished | Every profile sync deletes and recreates the shortcut folder on the Desktop | Recover from backup if any; admin renames the folder to one nobody would store files in; tell users it is not a documents folder |
| Work apps crash or the Workspace Filesystem will not mount (exit 21–23) | Endpoint security treating the workspace engine as suspicious | Add exclusions for `%ProgramData%\Netzilo Client` and `C:\Netzilo` in the security product; retry after a profile change or service restart |
| User cannot paste into / copy out of a work app | Restrict Clipboard Access **to** / **from** workspace (§2) | Expected; admin decides. Show the user which direction is blocked |
| Work app does not appear in screen shares or screenshots | Restrict Screen Sharing | Expected; the admin can turn it off (which also makes Record Desktop Activity selectable again) |

When a row ends in "admin", a regular-user session hands off with the peer name, the
`-WORKSPACE` peer's status, the exit code and the profile name — enough for the admin to
act in one step (`39` §4).
