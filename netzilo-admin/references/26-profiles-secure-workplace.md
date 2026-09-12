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
| **Enterprise Workspace** | native Windows applications ("work apps") run inside an isolated, encrypted enclave with restrictions (clipboard, printing, screen sharing, keylogging, watermark, recording, integrity) and optional posture checks | Windows |
| **Enterprise Browser** | Netzilo's own Chromium-based browser: bookmarks, per-domain restrictions, extension allow/block list, encrypted profile, wipe on close | Windows, macOS (mobile apps exist) |
| **Disposable Browser** | isolated throw-away browser sessions; everything is destroyed on close | Windows |
| **Enterprise Browser Extension** | per-domain DLP inside the user's normal browser (Chrome/Edge/Firefox/Safari): downloads, URL blocking, redaction, watermark, clipboard, printing, source-code controls, classified content, prompt-injection prevention, temporary cookies; the client force-installs the extension in Chrome/Edge when such a profile applies | any OS with a supported browser |

Profile fields: **Groups** (required), **OS** (Windows, Darwin, Linux, Android, iOS;
default Windows), components, **Enable Profile**, Name, Description. A device gets a
profile when it is in one of the groups and runs one of the OSs. Posture checks can gate
the workspace and each domain setting (All/Any evaluation).

Table: Name (enabled dot), Active toggle, OS icons, Groups, Components icons, Delete.

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
| Add Watermark | "Adds a watermark to graphical user interface of work apps" | text (e.g. `[USERNAME] - [DATE] - CONFIDENTIAL`), Dense / Sparse |
| Restrict Clipboard Access | "Restrict copying and pasting data from work apps to non-work apps" | Block copy/paste **from** workspace / **to** workspace / **to and from** |
| Restrict Printing | "Prevents work apps from printing sensitive data" | toggle |
| Restrict Screen Sharing | "Prevents screen capturing or sharing apps to grab the screens of work apps" | toggle; mutually exclusive with Record Desktop Activity |
| Record Desktop Activity | "Video records the desktop of users while they use workspace apps" | requires an **Amazon S3 or Min.io** event-streaming integration; requires a **privacy policy link** (users must accept before recording); recording is continuous and the workspace closes if recording stops; recordings appear in Activity as `session.recorded` |
| Restrict Key-logging | "Prevents key-logging applications to record key strokes of work apps" | toggle |
| Verify Workspace Integrity | "Hardens work apps against advanced attacks such as device rooting, debugging or memory injection attacks" | toggle; violations end the session (`workspace.injection.detected`, `workspace.selfdefense.activated`) |
| Create Desktop Shortcut for Work Apps | "Choose a folder name where users can find shortcuts for workapps" | folder name |
| Show Border | "Draws a border around work apps to identify them visually" | colour or None |

**Enforce Isolation → Settings**:

| Setting | Help text | Notes |
|---|---|---|
| Encryption Key | "Optional. Encryption key used for encrypting the virtual disk created for secure enclave." | generate/copy; changing an existing key **wipes the enclave data** (confirm dialog) |
| Use Workspace Filesystem | "Optional. Use encrypted container file system for better compatibility and performance." | toggle + **Allowed Apps** paths that may access it |
| Setup Key for Netzilo Network | "Optional. A setup key that is used to authenticate work apps to a Netzilo Network." | lets the enclave have its own peer identity |
| Use Workspace VPN | "Define VPN adapters exclusively for workspace." | adapters + allowed apps |
| Create Document Shortcuts | "Creates outside shortcuts for documents(e.g. .pdf, .ppt) downloaded inside isolated enclave for easy access" | toggle |
| Wipe Data When Closed | "Disposes all data e.g. files downloaded created inside enclave when all work apps are closed" | toggle |
| Trusted Certificates | "Define X.509 certificates to be trusted by applications running in workspace" | name + certificate (+ key) uploads |

**Posture Checks** tab: browse/new; **All** / **Any** evaluation; failing devices get
`workspace.posture.check` events and cannot open the workspace.

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

The Enterprise Browser is installed separately (`10-ai-security-aidr.md` §6); the
profile only configures it.

---

## 4. Disposable Browser — reference

Card text: "Creates a secure and isolated browsing environment on endpoints to protect
them against infections and web borne threats". Single setting: **Desktop Folder Name**
where users find the disposable browser shortcuts. Turn off by clearing the name. All
session data (history, cookies, cache, passwords, storage) is destroyed on close; tell
users to save work externally.

---

## 5. Domain Settings (Browser Extension and Enterprise Browser)

Header: "Configure protection settings for the web domain". Domain field: e.g.
`.netzilo.com` (leading dot = domain and subdomains). Tabs **Restrictions** / **Posture Checks**.

| Setting | Help text | Notes |
|---|---|---|
| Use Enterprise Workspace | "Enforces use of Enterprise Workspace while visiting matching web domains" | only when the profile has a Workspace; exclusive with Disposable Browser |
| Use Disposable Browser | "Enforces use of disposable browser while visiting matching web domains" | only when Disposable Browser is configured |
| Restrict Downloads | "Restrict files that could be downloaded from matching web domains" | `all`, or regex matching file content; templates offered |
| Restrict Uploads (Enterprise Browser only) | "Restrict files that could be uploaded to matching web domains" | same |
| Block URLs | "Define URL patterns that should be blocked from being accessed" | patterns/regex |
| Restrict Content → Redact Data | "Define sensitive data patterns and mask them before displaying" | rows: Pattern (regex; templates for cards, SSNs…), Mask with, Last N visible |
| Restrict Content → Add Watermark | "Adds a watermark to web site while visiting" | text, Dense/Sparse |
| Restrict Content → Restrict Clipboard | "Restrict copying and pasting data from matching web domains" | toggle; Enterprise Browser variant adds allowed paste domains |
| Restrict Content → Restrict Printing | "Prevents browser from printing sensitive data from matching domains" | toggle |
| Restrict Content → Restrict Uploading Source Code | "Detect and block source code uploads heuristically" | toggle |
| Restrict Content → Restrict Viewing Source Code | "Detect and redact source code snippets in pages" | toggle |
| Restrict Content → Restrict Viewing Classified Content | "Block access to content based on your organization's data classification labels" | labels Public / Private / Confidential / Secret (custom allowed, max 10); must match the organisation's DLP labels |
| Restrict Screen Sharing / Restrict Key Logging / Verify Workspace Integrity (Enterprise Browser only) | | toggles |
| Prevent LLM Prompt Injections | "Intercept and secure AI conversations against injection attacks" | toggle (ChatGPT, Claude, Gemini, Copilot pages) |
| Make Session Cookies Temporary | "Marks session cookies for deletion when the browser is closed" | toggle |
| Show Gray Border | "Draws a gray border around protected web content" | toggle |
| Allow Exceptions | "Define exceptions for restrictions for certain users" | temporary removal on/off, **Expires in** (Hours/Minutes; currently stored as minutes), support link, groups allowed to request |

Every restriction produces events: `browser.url.blocked`, `browser.download.file`,
`browser.upload.file`, `browser.download.content` (content regex hit),
`browser.data.redacted`, `browser.data.print.blocked`, `browser.data.clipboard.blocked`,
`browser.data.code.upload.blocked`, `browser.data.code.redacted`, `browser.data.classified`,
`browser.data.screenshot.blocked`, `browser.data.prompt.injection.blocked`,
`browser.isolation.bluezone.required` (workspace required), `browser.isolation.redzone.required`
(disposable browser required), `browser.posture.check`, `browser.exception.request`,
`browser.url.access`.

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
"browser_extension":[{"name":".example.com","block_urls":[],"restrict_downloads":[],"redact":[{"regex":"…","mask_with":"***","show_last":4}],"checks":[],"any_check_must_pass":false, …}],
"extension_bookmarks":[{"name":"HR","url":"https://hr.example.com"}],
"disposable_browser":"Disposable Browsers",
"enterprise_browser":{"domain_settings":[…],"bookmarks":[…],"encryption_key":"","wipe_data_when_closed":false,"extension_control":{"action":"allow","extensions":["<id>"]}}}}`
Read an existing profile with `GET` to see the exact shape before writing.

---

## 7. Procedures

- **Protect a SaaS app in normal browsers**: profile → OS Windows+Darwin → Browser
  Extension → domain `.salesforce.com` → Restrict Downloads `all`, Redact Data (card
  numbers), Restrict Printing, Watermark → Posture Checks (disk encryption) → Enable.
  Users' Chrome/Edge get the extension force-installed by the client.
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
| Workspace won't launch | app path wrong, app not installed, posture failing, recording enabled without storage integration | fix path; check events; configure S3/Min.io |
| "Record Desktop Activity" greyed out | no S3/Min.io integration | Integrations → Event Streaming |
| Users lose enclave files | Wipe Data When Closed on, or encryption key changed | expected; document it |
| Component icon missing in table for Enterprise Browser | display only | ignore |
| Delete tooltip about policies always shown | display only | delete proceeds |
| Exception expiry shorter than expected | stored as minutes even when Hours selected | enter the value in minutes |

Events: `profile.created/updated/removed`, plus the browser/workspace events in §5 and
`workspace.app.started`, `workspace.posture.check`, `workspace.print.blocked`,
`workspace.injection.detected`, `workspace.selfdefense.activated`, `session.recorded`.
