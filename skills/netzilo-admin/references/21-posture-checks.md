---
id: '21'
title: Admin Skill — Posture Checks
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 17979
sections:
- id: '1'
  title: Check types (cards in the Create/Update Posture Check modal)
  chars: 8028
- id: '2'
  title: Creating and attaching
  chars: 985
- id: '3'
  title: API
  chars: 1931
- id: '4'
  title: Design guidance
  chars: 1979
- id: '5'
  title: Diagnosis
  chars: 4346
---
# Admin Skill — Posture Checks

**Dashboard:** Endpoint → **Posture Checks** (`/posture-checks`). **API:** `/api/posture-checks`.
**Used by:** Policies (source peers), Profiles (workspace/browser domain settings), Edge
Filters (AI tool access). Free-plan tenants see **Upgrade Plan** instead of Save.

A posture check is a named bundle of conditions evaluated against a peer (device). It
does nothing on its own; it acts where it is attached, and it blocks the peer from the
rules of that policy/profile/filter when it fails. Failures are logged as
`peer.access.blocked` (policies), `workspace.posture.check` / `browser.posture.check`
(profiles) and `tool.blocked` with scanner type `posture` (AI Edge).

---

## 1. Check types (cards in the Create/Update Posture Check modal)

Each card has an On/Off pill; turning a configured card off asks "Disable this check? …
All settings of this check will be lost."

| Card | What it evaluates | Configuration | Platforms |
|---|---|---|---|
| **Netzilo Client Version** | client version ≥ minimum | "Minimum required version" e.g. `0.25.0` (semver) | all |
| **Country & Region** | public IP geolocation | Allow / Block; list of country (+ optional city) entries; **Allow** list blocks every other location, **Block** list allows every other | all; needs the server's GeoLite2 database |
| **Date & Time** | current time within rules | rules with Start/End time, timezone, recurrence Daily / Weekly (weekdays) / Monthly (months), optional start/end dates | all |
| **Peer Network Range** | the peer's local/public IP ranges | Allow / Block; CIDR list `172.16.0.0/16` | all |
| **Operating System** | OS and version | per tab Linux / Windows / macOS / iOS / Android: Allow / Block; "All versions" or "Equal or greater than" a named version (Windows 11, macOS Sonoma, iOS 17, Android 15 …) or custom number; Linux/Windows compare **kernel** version | all |
| **Peer Domain Membership** | AD/directory domain the device is joined to | Allow / Block; domain names | Windows |
| **Endpoint Security Settings** | device hygiene; **all enabled items must pass** | Antivirus (active — Windows reads Defender / Security Center state; Linux reads the ClamAV daemon; macOS: consult the peer detail indicator), Firewall (Windows, macOS), Disk Encryption (Windows, Linux, macOS), Screen Lock (password-protected lock — Windows, Linux, macOS), OS Updates (Linux, macOS; the Windows value does not reflect Windows Update state) | per item; see the signal caveats below |
| **Advanced Endpoint Settings** | presence/absence indicators; **all enabled items must pass** | Enterprise Workspace and Enterprise Browser (true only on the workspace's own peer / the browser's own peer, **never on the host peer**; on a normal policy they block every ordinary device), Netzilo Gateway (true only for a browser session of a Netzilo gateway, `43-clientless-access-gateway.md`; every device with the Netzilo client fails it, so it belongs on policies meant for browser users), Netzilo Extension (the Netzilo browser extension on the device: always true for a desktop client — Windows, macOS, Linux — and for the Enterprise Browser, always false on iOS and Android, true for a gateway browser session, false for a reverse-proxy session; nothing is inspected on the device), Virtual Device (must **not** be a VM — Windows, Linux, macOS), Device Integrity (not rooted/jailbroken/debugged — Windows, Linux, macOS, iOS, Android), Registry Key & Value (Windows; All/Any; hive HKLM/HKCU/HKCR/HKCC/HKU, key, value; glob wildcards on key path and value name; value data is not compared), File & Folder (All/Any; per OS path + optional content regex), Running Processes (All/Any; per OS path patterns) | per item |

Version semantics for **Operating System**: Block = the OS is excluded entirely; Allow
"All versions" = any version; Allow "Equal or greater than" = minimum. Only the operating
systems the check lists pass: any other, including one the peer reports that the check
cannot recognise (an API client that names no operating system, say), is blocked. A
check that lists no operating system is skipped, which is how the dashboard saves a
check with every tab on Block. A reverse-proxy peer reports the operating system of the
browser it was signed in from (`44-published-applications.md` §10.3). Windows values
are kernel builds (Windows 10 22H2 `10.0.19045`, Windows 11 23H2 `10.0.22631`, Server
2022 `10.0.20348`); Linux is the kernel (e.g. `6.1`).

Peer detail page shows the live posture indicators the checks read: firewall, antivirus,
disk encryption, OS updates, virtual device, screen lock, device integrity, Enterprise
Workspace, Enterprise Browser — use it to predict a check's result before attaching it.

**Signal caveats (what each indicator actually reads).** State these when a compliant
device fails, instead of telling the customer the device is misconfigured:

- *Antivirus*: Windows reads Microsoft Defender's registry state (passive mode, real-time
  monitoring) with Windows Security Center as fallback; "up to date" is not measured
  separately. Linux reports active only while the ClamAV daemon runs. macOS: check the
  peer detail indicator on a known-good Mac before gating on it.
- *OS updates*: on Windows the value does not reflect Windows Update state — never cite
  it as evidence that a device is or is not patched; use the kernel build instead.
- *Disk encryption*: Windows reads BitLocker on `C:` with protection **On** only
  (suspended, another system drive letter, third-party encryption read as not
  encrypted; refreshed about every 5 minutes).
- *Firewall*: Windows reads the local profile setting; a state enforced by Group Policy
  may not be reflected.
- *Peer Domain Membership*: the NetBIOS name (`CORP`), not the FQDN; Entra-only joined
  devices report no domain.
- *Registry Key & Value*: existence only; `HKCU` is the service account's hive, not the
  signed-in user's. *File & Folder* paths expand with the system account's environment.
- *Virtual Device*: on Windows also fires on physical PCs with Virtualization-based
  Security / Memory Integrity, Hyper-V or WSL2, or any RDP session; cached until the
  service restarts.
- *Screen Lock*: Windows reads the user's screensaver settings only; a lock enforced by
  GPO/Intune or sign-in-on-wake reads false. Linux: GNOME/KDE only.
- *Device Integrity*: may flap briefly while security software injects into workspace
  applications.
- *Enterprise Workspace / Enterprise Browser*: true only for the workspace's or browser's
  own peer; the macOS workspace signal means "MDM-enrolled Mac"; Linux never reports it.
  At a **published application's door** (`44-published-applications.md` §4.1) the
  Workspace item reads the posture of the Netzilo client inside the Workspace (so an old
  or stopped client fails it), and the Enterprise Browser item reads the browser's own
  User-Agent.
- *Netzilo Extension*: the Netzilo browser extension on the device. Not probed: a desktop
  client (Windows, macOS, Linux) and the Enterprise Browser always report it, iOS and
  Android never do; a gateway browser session reports it (the extension is what it
  serves), a reverse-proxy session does not. Clients older than the item report nothing,
  which reads as false. API field `netzilo_extension_check`; peer signal
  `meta.netzilo_meta.is_netzilo_extension`, shown on the peer page beside the Gateway one.
- *Netzilo Gateway*: true only for a gateway's browser session (a `vp-<n>-PROXY` peer); it
  is not probed on any device, so an endpoint can never satisfy it. It is also the one
  Advanced item a browser session can pass: the others fail for browser sessions
  (`43-clientless-access-gateway.md` §3.4). The peer page shows the signal beside the
  Workspace and Browser ones. API field `netzilo_gateway_check`; peer signal
  `meta.netzilo_meta.is_netzilo_gateway`. Put it alone in its check and attach that check to
  network policies only: on a profile's domain settings, a workspace or an MCP filter the
  device's client evaluates it and, never being a gateway session, blocks itself.
- *Operating System* for a browser session: the version comes from the User-Agent (macOS
  frozen at `10.15.7`, Windows 11 reported as `10.0`), so minimum-version rules misjudge
  browser sessions (`43-clientless-access-gateway.md` §3.4).
- A reverse-proxy peer (`vp-<n>-RPROXY`, published applications) carries the Netzilo
  Gateway item and no endpoint signals; *Country & Region* and *Peer Network Range* judge
  the user's public address, *Operating System* the system the browser reported at
  sign-in (`44-published-applications.md` §10.3).

Windows detail and the device-side checks for each signal: `40-windows-hosts.md` §8.

---

## 2. Creating and attaching

1. Endpoint → Posture Checks → **Add Posture Check** → turn on one or more cards →
   configure → **Continue** → name (e.g. "Managed Windows laptops") and description →
   **Create Posture Check**.
2. Attach:
   - Policy: Network → Policies → policy → **Posture Checks** tab → Browse Checks →
     select → choose **All** / **Any** evaluation → Save Changes.
   - Profile: Endpoint → Profiles → profile → Enterprise Workspace card or a domain
     setting → **Posture Checks** tab.
   - Edge Filter: Edge → Filters → filter → **Posture Checks** tab.
3. Verify: pick a device that should fail, try the access, confirm the
   `peer.access.blocked` (or workspace/browser/tool) event names your check.

Table columns: Name, Checks (icon stack with tooltips), Used by (Policies / Profiles /
Filters badges with "Go to …" buttons), Delete (disabled while used: "This posture check
is assigned to a policy, a profile, or a filter and cannot be deleted…").

---

## 3. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET/POST /api/posture-checks
GET/PUT/DELETE /api/posture-checks/{id}
GET /api/locations/countries ; GET /api/locations/countries/{cc}/cities
```
Body skeleton (include only the checks you configure):
```json
{"name":"Managed Windows laptops","description":"",
 "checks":{
  "nb_version_check":{"min_version":"4.4.0"},
  "os_version_check":{"windows":{"min_kernel_version":"10.0.19045"},"darwin":{"min_version":"13"}},
  "geo_location_check":{"action":"allow","locations":[{"country_code":"DE"},{"country_code":"US","city_name":"Austin"}]},
  "peer_network_range_check":{"action":"deny","ranges":["10.99.0.0/16"]},
  "date_time_checks":{"rules":[{"startTime":"08:00","endTime":"18:00","timeZone":"+01:00","recurrence":{"type":"weekly","values":["Mon","Tue","Wed","Thu","Fri"]}}]},
  "netzilo_check":{
    "peer_domain_check":{"action":"allow","domains":["corp.example.com"]},
    "security_settings_check":{"disk_encryption_check":true,"screen_lock_check":true,"firewall_check":true},
    "advanced_settings_check":{"virtual_device_check":true,"device_integrity_check":true,"netzilo_gateway_check":false,
      "registry_check":{"action":"all","registry":[{"dir":"HKLM","key":"SOFTWARE\\Corp\\Agent","value":"Installed"}]},
      "file_folder_check":{"action":"any","check":{"windows":[{"path":"C:\\Program Files\\EDR\\*","content":""}]}},
      "processes_check":{"action":"all","check":{"windows":["C:\\Program Files\\EDR\\edr.exe"],"darwin":["/Applications/EDR.app/Contents/MacOS/edr"]}}}}}}
```
Omitted OS keys in `os_version_check` mean that OS is blocked; use `"min_version":"0"`
to allow all versions of an OS.

---

## 4. Design guidance

- Prefer **Any** evaluation with several checks when platforms differ (e.g. one check
  for Windows, one for macOS) and **All** when layering (version + encryption).
- Geolocation: the client's *public* IP is looked up; VPN-behind-VPN and mobile carriers
  produce surprises. Start with **report-style** observation (attach to a low-impact
  policy) before gating production access.
- Security Settings items read different sources per OS (§1 caveats): Antivirus on
  Linux means the ClamAV daemon, OS Updates on Windows is not Windows Update state. Put
  per-OS checks in separate posture checks combined with **Any**, and confirm each on a
  known-good device of that OS before gating production access.
- Virtual Device: blocks VMs, including servers, and on Windows also physical PCs with
  Memory Integrity / Hyper-V / WSL2 and any host reached over RDP. Never attach it to a
  policy whose source group contains servers, routing peers or session hosts.
- Enterprise Workspace and Enterprise Browser items belong only on policies (or profile
  settings) whose sources are the workspace's or browser's own peers; on a policy for
  ordinary devices they block every host.
- Device Integrity requires the mobile apps / desktop client to report it; older clients
  fail the check.
- Client Version checks are the safest lever to force upgrades: pair with the
  dashboard's "Update available" indicator.
- **Browser sessions (clientless access)** are evaluated against the browser, not a
  managed device: OS version from what the browser reports, Client Version from the
  extension's version, Geolocation and Peer Network Range from the browser's public IP.
  Process checks and every Netzilo endpoint check (firewall, antivirus, disk encryption,
  screen lock, …) always fail for them when enforced, by design. A policy that should
  admit browser users needs no such checks; give them their own policy
  (`43-clientless-access-gateway.md` §3.4).

---

## 5. Diagnosis

| Symptom | Check | Fix |
|---|---|---|
| Users blocked unexpectedly | Activity → Events → `peer.access.blocked`: meta shows `posture_check`, `policy`, `reason` | adjust the check or move the user's device out of the policy's source group |
| Check has no effect | it is not attached (Used by = "No Policies") or Default policy still permits everything | attach; disable Default |
| Geolocation check blocks everyone (self-hosted) | server has no GeoLite2 database (management log "could not initialize geo location service") | provide the database or remove the check |
| OS check blocks all Windows | value entered as marketing version (11) instead of kernel build | use `10.0.22000`+ or pick the named version |
| Security Settings check fails on a compliant device | which indicator is red on the peer detail page, and what does that indicator read (§1 caveats; Windows: `40-windows-hosts.md` §8)? | fix the device setting the indicator reads, or remove the item |
| Enterprise Workspace / Browser check blocks every device | the policy's source group contains ordinary host peers | move the item to a check attached to the workspace/browser peers only |
| Cannot delete a check | still referenced | table "Used by" tells where; remove there first |
| Save shows "Upgrade Plan" | Free plan | upgrade (cloud) |
| Date & Time check off by hours | timezone in the rule vs device | rules evaluate against the rule's timezone; set it explicitly |
| Check passes on the dashboard but access still blocked | another policy/check, or the filter's own posture check (AI Edge) | resolve rules (`20-policies-access-control.md` §6) |

Events to search: `posture.check.created/updated/deleted`, `peer.access.blocked`,
`workspace.posture.check`, `browser.posture.check`, `tool.blocked`, and for a published
application's door `published_app.access_denied` (`44-published-applications.md` §4.1).

**Failure reasons.** The `reason` in `peer.access.blocked` meta, and in
`published_app.access_denied` meta (also shown to the user in the sign-in dialog), names
the failing item with one of these strings:

| Reason | Item |
|---|---|
| `An antivirus is not active and running` | Antivirus |
| `A firewall is not active and running` | Firewall |
| `Disk encryption is not enabled` | Disk Encryption |
| `A screenlock with a password is not enabled` | Screen Lock |
| `Peer operating system is not updated` | OS Updates |
| `Peer is not using Netzilo Enterprise Workspace` | Enterprise Workspace (servers before this wording said `a Netzilo container`) |
| `Peer is not using Netzilo Enterprise Browser` | Enterprise Browser (before: `a Netzilo browser`) |
| `Peer is not a Netzilo gateway session` | Netzilo Gateway |
| `Peer is not using the Netzilo extension` | Netzilo Extension: an iOS or Android device, a reverse-proxy session, or a client older than the item |
| `Endpoint checks cannot be satisfied by a browser session` | any endpoint item (Security Settings, Workspace, Browser, Virtual Device, Device Integrity, Registry, File & Folder, Processes, Domain) on a browser session; by design (`43-clientless-access-gateway.md` §3.4) |
| `Peer is using a virtual device` | Virtual Device |
| `Peer's device integrity is breached` | Device Integrity |
| `A required registry key is not found` / `Required registry check result not reported` | Registry Key & Value (the second: the client did not report the item, typically an old client or a non-Windows device) |
| `A required file or folder is not found` / `Required file/folder check result not reported` | File & Folder |
| `A required process is not running` / `Required process check result not reported` | Running Processes |
| `Access not allowed during this time period` | Date & Time |

The event is written only while a destination peer is connected, so its absence proves
nothing (`38-device-diagnosis-method.md` §1). The device's own log is the primary record:
`Posture check '<name>' (ID=<id>) FAILED` followed by `Posture check '<name>' FAILED at
<NBVersionCheck | OSVersionCheck | GeoLocationCheck | NetworkRangeCheck | NetziloChecks |
DateTimeCheck>`; search it with `diag.grep {pattern: "Posture check .* FAILED"}`
(`36-device-tools.md`). `NetziloChecks` covers every Endpoint Security, Advanced Endpoint
and Domain item; `diag.posture` then shows which signal is false.
