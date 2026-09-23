---
id: '21'
title: Admin Skill — Posture Checks
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 13662
sections:
- id: '1'
  title: Check types (cards in the Create/Update Posture Check modal)
  chars: 5077
- id: '2'
  title: Creating and attaching
  chars: 985
- id: '3'
  title: API
  chars: 1901
- id: '4'
  title: Design guidance
  chars: 1433
- id: '5'
  title: Diagnosis
  chars: 3556
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
| **Advanced Endpoint Settings** | presence/absence indicators; **all enabled items must pass** | Enterprise Workspace and Enterprise Browser (true only on the workspace's own peer / the browser's own peer, **never on the host peer**; on a normal policy they block every ordinary device), Virtual Device (must **not** be a VM — Windows, Linux, macOS), Device Integrity (not rooted/jailbroken/debugged — Windows, Linux, macOS, iOS, Android), Registry Key & Value (Windows; All/Any; hive HKLM/HKCU/HKCR/HKCC/HKU, key, value; glob wildcards on key path and value name; value data is not compared), File & Folder (All/Any; per OS path + optional content regex), Running Processes (All/Any; per OS path patterns) | per item |

Version semantics for **Operating System**: Block = the OS is excluded entirely; Allow
"All versions" = any version; Allow "Equal or greater than" = minimum. Windows values
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
    "advanced_settings_check":{"virtual_device_check":true,"device_integrity_check":true,
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
`workspace.posture.check`, `browser.posture.check`, `tool.blocked`.

**Failure reasons.** The `reason` in `peer.access.blocked` meta names the failing item
with one of these strings:

| Reason | Item |
|---|---|
| `An antivirus is not active and running` | Antivirus |
| `A firewall is not active and running` | Firewall |
| `Disk encryption is not enabled` | Disk Encryption |
| `A screenlock with a password is not enabled` | Screen Lock |
| `Peer operating system is not updated` | OS Updates |
| `Peer is not using a Netzilo container` | Enterprise Workspace |
| `Peer is not using a Netzilo browser` | Enterprise Browser |
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
