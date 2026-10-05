---
id: '40'
title: Netzilo — Windows Hosts (install, services, drivers, DNS, filter, posture)
requires:
- device-tools
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 29725
sections:
- id: '1'
  title: What is on a Windows host
  chars: 4981
- id: '2'
  title: Install, upgrade, uninstall (what each keeps or wipes)
  chars: 4704
- id: '3'
  title: Deploying at scale (Intune/SCCM/GPO, device context, proxies, switches)
  chars: 2756
- id: '4'
  title: Service and driver failures
  chars: 3075
- id: '5'
  title: DNS on Windows
  chars: 2236
- id: '6'
  title: Routes and firewall
  chars: 1881
- id: '7'
  title: AI network filter and interception certificate
  chars: 2830
- id: '8'
  title: Posture signals on Windows
  chars: 3584
- id: '9'
  title: Multi-user and RDP hosts
  chars: 1133
- id: '10'
  title: Collecting evidence safely
  chars: 1339
---
# Netzilo — Windows Hosts (install, services, drivers, DNS, filter, posture)

Windows is the platform where the client is more than one process: a service, a tray
application, kernel drivers, a network filter, an optional workspace, and an installer
that behaves differently depending on who runs it and from where. Most Windows tickets
are one of those pieces in an unexpected state, and the fix is usually a registry key, a
service name or an event-log query rather than a client command. This file gives the
inventory, what each operation keeps or wipes, and the symptom tables for the failures
that actually occur. Tool contracts are in `references/37-device-tool-reference.md`; the
diagnosis loop is `references/38-device-diagnosis-method.md`; the general client
troubleshooting table is `references/07-client-troubleshooting.md`. Workspace and
Enterprise Browser problems belong to `references/26-profiles-secure-workplace.md`; this
file only says where the workspace touches the host.

On Windows, `shell.run` executes as `SYSTEM` with no user `PATH`: use absolute paths or
`powershell -NoProfile -NonInteractive -Command`. `shell.run` with `as: "user"` runs in
the first active user session (§9).

## 1. What is on a Windows host

**Folders.** Program files live in `%ProgramData%\Netzilo Client\`: `netzilo.exe` (CLI
and service), `netzilo-ui.exe` (tray), `installer.exe` (install, upgrade, uninstall),
`launcher.exe` (the `nz://` protocol handler), `nzcontainer.exe` (workspace),
`afhelper64.exe`, `nwfilter.exe` and `nwfilter.dll` (AI network filter user-mode part),
`nwfilter64.sys` and `ntzldrv.sys` (drivers), `wintun.dll`, and the `sandbox\`, `imdisk\`
and `nzfs\` subfolders. Configuration and logs live in `%ProgramData%\Netzilo\`. Nothing
is added to `PATH`; a shell needs the full path to `netzilo.exe`.

**Files in `%ProgramData%\Netzilo`** and how to treat them:

| File | What it is | Handling |
|---|---|---|
| `client.log` | the client log (`diag.logs`, `diag.grep` read it) | read freely |
| `service.log` | service start-up and crash output, written before the client log exists | read when the service will not start |
| `nwfilter.log`, `nwfilter.log.1` | AI network filter log, 3 MB rotation | read with `diag.grep {file: ...}` (§7) |
| `nwfilter_policy.json` | the last filter rules the service applied, reloaded at start | read to see what the filter enforces |
| `unclean_shutdown_dns.txt` | marker written while DNS is installed; repaired at next start | presence after a crash is normal |
| `container.json`, `<workspace>.json` | workspace state; `<workspace>.json` holds secrets | collect only; workspace matters: `references/26-profiles-secure-workplace.md` |
| `netzilo_online_install.log`, `netzilo_offline_nsis_install.log` | plain-text installer logs | read freely |
| `installer_internal.log`, `core.log`, `nzcontainer.log` | encrypted logs of the native components | **collect, do not read**: only Netzilo support can decrypt them |
| `config.json`, `usservice<N>.json` | client configuration incl. the WireGuard private key | **secret**: never request contents; `diag.config` gives the safe view |
| `mcp.db`, token and PAT files, `netzilo-ca-key.pem` | credentials and the interception CA private key | **secret**: never read or copy into a conversation |
| `usservice<N>.log` | log of a non-administrator (per-user) client, `<N>` = user id | read freely |

**Services and drivers.** Query any of them with `sc.exe query <name>`:

| Name | Display / role | Start | Notes |
|---|---|---|---|
| `Netzilo` | the client service, runs as `SYSTEM` | automatic | recovery action: restart. Stopping it logs the device out (`references/06-client-cli-reference.md`) |
| `ntzldrv` | file protection driver | | protects the install folder and workspace data |
| `nwfilter` | AI network filter driver (`nwfilter64.sys`) | | present only on x64 administrator installs |
| `NtzlSb` | workspace sandbox driver | demand | workspace only |
| `NtzlSvc` | "Netzilo Sandbox Service" | automatic | workspace only |
| `dokan2`, `imdisk`, `deviodrv` | virtual disk drivers for the encrypted workspace | | workspace only |

**Named pipes** between the service and the filter: `\\.\pipe\nz_nwfilter_pipe` and
`\\.\pipe\nz_nwfilter_proxy_pipe`. A security product that blocks named-pipe creation for
unknown binaries breaks the filter (§7).

**Windows Firewall rules.** Two rules exist: `Netzilo`, an inbound allow rule scoped to
the device's own Netzilo IP, recreated by the service whenever the interface comes up; and
`Netzilo Client`, a program rule for `netzilo.exe`. Inspect them with
`netsh advfirewall firewall show rule name=Netzilo` (and `name="Netzilo Client"`). Two
caveats: a rule left from an earlier enrolment keeps the *old* IP until the service
recreates it, and a domain policy with `AllowLocalFirewallRules` set to False makes
Windows ignore both rules; `Get-NetFirewallProfile -PolicyStore ActiveStore | select
Name,Enabled,AllowLocalFirewallRules` shows which case you are in (§6).

**Registry.**

| Key | Meaning |
|---|---|
| `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` value `Netzilo` | tray autostart for that user. Quitting the tray removes it; the next start of the tray recreates it. The tunnel is the service's and is unaffected |
| `HKLM\Software\Netzilo`, `HKCU\Software\Netzilo` | installer and workspace state; removed by uninstall |
| `HKLM\System\CurrentControlSet\Control\NetziloPendingReboot` | set when a running driver could not be replaced; cleared by a reboot (§2) |
| `HKLM\System\CurrentControlSet\Control\NetziloDebug` (REG_MULTI_SZ) | components whose native logs are turned on, `*` for all; the logs are the encrypted ones above |
| `HKLM\SYSTEM\CurrentControlSet\Services\Netzilo\Environment` (REG_MULTI_SZ) | environment variables for the service, one `NAME=value` per line (§4) |
| `HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\DnsPolicyConfig\Netzilo-Match` | the client's split-DNS rule (§5) |

**Protocol handler.** `nz://` links (from the dashboard and the enterprise browser) are
handled by `launcher.exe`; a missing handler after a partial uninstall shows as "Windows
cannot open this link".

## 2. Install, upgrade, uninstall (what each keeps or wipes)

**Three installer forms, one product.**

| Form | URL under `https://pkg.netzilo.com` | Silent / switches | Use when |
|---|---|---|---|
| Online installer | `/download/windows/netzilo_setup.exe` | none needed for interactive use | a person with internet access installs by hand. It downloads the actual package from `pkg.netzilo.com` at install time |
| Offline installer | `/download/windows/x64/nz_installer_64.exe` | `-s` silent, `-na` non-administrator mode | scripted pushes, machines without direct internet, device-context deployment |
| MSI | `/download/windows/x64/netzilo_x64.msi` | properties `NONADMIN=1`, `CONFIGFILE=<path>`; always add `REBOOT=ReallySuppress` | tools that require a package (Intune Win32/LOB, SCCM, GPO software installation) |

Installers named `netzilo_setup_<name>.exe` or `netzilo_x64_<name>.msi` carry a tenant
name and apply that tenant's pre-seeded configuration (management URL and settings) at
install time; the person only signs in.

**Elevation.** Every form starts unelevated and requests elevation itself through UAC.
"Run as administrator" is not needed; an installer that is *denied* elevation continues as
a non-administrator install (§3), which is the usual origin of "the workspace and the AI
features are missing on this laptop".

**What install does.** Copies the program files to `%ProgramData%\Netzilo Client\`,
installs and starts the drivers and the `Netzilo` service, registers the tray autostart,
writes the plain installer log to `%ProgramData%\Netzilo\`. On ARM64 it installs the
network client only: no drivers, no workspace, no AI network filter.

**Upgrade** is in place: run the new installer of any form. There is no "already
installed, remove it first" prompt. Services and drivers are stopped, the old files are
set aside and replaced, configuration and enrolment in `%ProgramData%\Netzilo` are kept,
and the peer keeps its identity. If a running driver cannot be replaced, the installer
sets `HKLM\System\CurrentControlSet\Control\NetziloPendingReboot`, and every further
install attempt says "Please reboot computer and try again." until the machine reboots.

**Uninstall** is `"%ProgramData%\Netzilo Client\installer.exe" -u` (silent: `-u -q`),
also reachable from Settings → Apps → Netzilo Client. It removes the program files,
services and drivers, **and deletes `%ProgramData%\Netzilo`** (configuration, the peer's
WireGuard identity, tokens, all logs), `C:\Netzilo`, workspace containers, and
`HKLM\Software\Netzilo` and `HKCU\Software\Netzilo`. Consequences to state before anyone
runs it: a reinstall enrols as a **new peer** (the old entry goes stale and should be
deleted in the account), SSO users sign in again, workspace data is gone, and logs you
wanted are gone with it, so collect §10 first. A failed install rolls back the same way.
Switching a non-administrator install to administrator mode is a full uninstall followed
by a fresh install, with the same consequences.

**Installer dialogs and what they mean:**

| Dialog | Cause | Fix |
|---|---|---|
| `failed to download installer.` | the online installer could not reach `pkg.netzilo.com`. Offline machine, a proxy the installing identity does not have (a `SYSTEM` deployment context has no user proxy), or TLS inspection of the download | use the offline installer or the MSI; or allow the download host for the machine identity |
| `Please reboot computer and try again.` | `NetziloPendingReboot` is set from an earlier upgrade | reboot, then run the installer again |
| `Please uninstall sandbox software and try again.` | another sandboxing product's driver is active | remove or stop that product for the install |
| `Admin mode is already installed, please uninstall Netzilo Client and try again.` | a non-administrator install was attempted over an administrator install | install elevated, or uninstall first |
| `Cannot install netzilo driver.` / `Cannot install sandbox driver.` / `Cannot install imdisk driver.` / `Cannot install diskio driver.` | a driver could not be installed or started: blocked by a driver-control or code-integrity policy, or by security software | §4; check `Microsoft-Windows-CodeIntegrity/Operational` and the security product's log; allowlist the drivers |
| `Cannot install netzilo service.` / `Cannot start netzilo service.` | the service registration or first start failed | `service.log` and the Service Control Manager event (§4) |

Every dialog is also written to `netzilo_online_install.log` or
`netzilo_offline_nsis_install.log`, so a silent deployment that "did nothing" is diagnosed
from those two files, not from the deployment tool's exit code alone.

## 3. Deploying at scale (Intune/SCCM/GPO, device context, proxies, switches)

| Decision | Recommendation | Why |
|---|---|---|
| Which form | MSI for Intune LOB/Win32, SCCM and GPO software installation; offline `.exe -s` for scripted pushes | the online installer needs internet from the deployment identity and fails silently with `failed to download installer.` when it does not have it |
| Context | **device (system) context**, never user context | the MSI is per-user scoped and self-elevates; in user context on a non-administrator account it produces a non-administrator install (per-user client, userspace networking, no drivers, no workspace, no AI network filter) |
| Reboot handling | `REBOOT=ReallySuppress`; schedule the reboot yourself when the exit code or `NetziloPendingReboot` says one is pending | the installer may request a reboot to replace a running driver |
| Proxies | give the machine identity a proxy (WinHTTP or a system proxy policy) if the network requires one; or use offline/MSI | a `SYSTEM` context has no user proxy settings |
| Pre-seeding | tenant-named installer, or `CONFIGFILE=<path>` on the MSI | the person only signs in; no `--management-url` on the device |
| Enrolment | user devices: sign-in in the tray after install. Servers and kiosks: `netzilo.exe up --setup-key <KEY>` from an elevated shell | `references/05-client-install-and-deploy.md` §1 |
| Detection rule | file `%ProgramData%\Netzilo Client\netzilo.exe` and service `Netzilo` | `HKLM\Software\Netzilo` `Version` also exists; `C:\Program Files\Netzilo` does **not** |
| Security software | allowlist `%ProgramData%\Netzilo Client\`, the drivers `nwfilter64.sys` and `ntzldrv.sys`, and the two named pipes | see §7 |

Commands:

```powershell
# offline installer, silent
& ".\nz_installer_64.exe" -s
# MSI, silent, device context
msiexec /i netzilo_x64.msi /qn REBOOT=ReallySuppress
msiexec /i netzilo_x64.msi /qn REBOOT=ReallySuppress CONFIGFILE="C:\deploy\config.json"
# non-administrator mode on purpose (userspace networking, no drivers/workspace/filter)
& ".\nz_installer_64.exe" -s -na
msiexec /i netzilo_x64.msi /qn REBOOT=ReallySuppress NONADMIN=1
# silent uninstall
& "$env:ProgramData\Netzilo Client\installer.exe" -u -q
# enrol a server
& "$env:ProgramData\Netzilo Client\netzilo.exe" up --management-url https://<domain> --setup-key <KEY>
```

Post-deployment check across a fleet: `sc.exe query Netzilo` is RUNNING, `sc.exe query
ntzldrv` and `sc.exe query nwfilter` are RUNNING on x64 administrator installs, and the
peer appears in the account with the expected groups. A device that shows up as a peer but
has no drivers is a non-administrator install; its client log is
`%ProgramData%\netzilo\usservice<N>.log`, not `client.log`.

## 4. Service and driver failures

| Symptom | Evidence | Cause | Fix |
|---|---|---|---|
| service `Netzilo` stops immediately / tray says the service is not running | `service.log` has `failed to start daemon:` | configuration file is unreadable or corrupt | move `config.json` aside and start the service; the device re-enrols as a new peer (§2 consequences apply), so try repairing the file's permissions first |
| same, log has `failed to listen daemon interface` | `netstat -ano \| findstr 40836` shows another process | the daemon port is taken | free the port or set `--daemon-addr` in the service arguments |
| service starts, restarts in a loop | Service Control Manager events: `Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Service Control Manager'} -MaxEvents 50 \| ? Message -match Netzilo` | crash on start; the recovery action restarts it | read `service.log` and the last `client.log` lines; a driver that fails to load usually precedes it |
| drivers not running | `sc.exe query ntzldrv`, `sc.exe query nwfilter`, `sc.exe query NtzlSb` show STOPPED | blocked by Memory Integrity (HVCI), a code-integrity policy or security software | `Get-WinEvent -LogName Microsoft-Windows-CodeIntegrity/Operational -MaxEvents 30`; allowlist the drivers; on ARM64 the drivers are simply not installed |
| `netzilo up -F` behaves like a non-administrator client | run from an elevated shell, not as `SYSTEM` | the components only the service identity may start (filter, session features) are skipped and the client falls back to userspace networking | do not use `-F` on Windows for anything but a quick test; use the service |
| device shows `os: Windows 10 …` although it runs Windows 11 | `diag.system` | the OS name is reported from the OS build family; both report the same product name | never use the name in a posture check; use the kernel build (Windows 11 is ≥ `10.0.22000`), `references/21-posture-checks.md` §1 |
| nothing in `client.log` about the failure | the service never got that far | | `service.log` first, then the SCM events above |

**Service environment.** Persistent variables for the service (for example a debug log
level or a userspace-WireGuard test) go into
`HKLM\SYSTEM\CurrentControlSet\Services\Netzilo\Environment` as REG_MULTI_SZ lines
`NAME=value`, followed by a service restart. Remember that stopping or restarting the
service is a full client shutdown that logs the device out and resets its enrolment state
(`references/06-client-cli-reference.md`, `references/36-device-tools.md`); prefer
`mod.loglevel` for a temporary level.

```powershell
sc.exe query Netzilo; sc.exe query ntzldrv; sc.exe query nwfilter; sc.exe query NtzlSb
sc.exe qc Netzilo
Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Service Control Manager'} -MaxEvents 50 | ? Message -match Netzilo | fl TimeCreated,Message
Get-WinEvent -LogName Microsoft-Windows-CodeIntegrity/Operational -MaxEvents 30 | fl TimeCreated,Message
```

With device tools: `diag.grep {file: "C:\\ProgramData\\Netzilo\\service.log", pattern:
"failed to"}`.

## 5. DNS on Windows

The client installs two things: the **primary resolver** on the `wt0` adapter (interface
key `HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{GUID}`, values
`NameServer` and `SearchList`), and **match domains** as a Name Resolution Policy Table
rule `HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\DnsPolicyConfig\Netzilo-Match`.
Which of the two exists depends on the account's nameserver groups: an account with only
match-domain groups leaves `wt0` **without a DNS server**, and that is normal, not a
fault.

| Symptom | Evidence | Cause | Fix |
|---|---|---|---|
| peer names or an internal zone do not resolve, `diag.dns` says the tunnel resolver answers | `Get-DnsClientNrptPolicy` shows no `Netzilo-Match` rule, or shows rules under the GPO path | a Group Policy NRPT (`HKLM\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient\DnsPolicyConfig`, typical for Always On VPN or DirectAccess) overrides local rules | add the zone to the GPO policy, or exempt these devices from it |
| client log `binding dns on … is not available` | `Get-NetUDPEndpoint -LocalPort 53` names another process | UDP 53 is taken (a local DNS server, another VPN's resolver) | stop or move that listener; there is no custom-port option on Windows |
| stale answers after a change | | Windows resolver cache | `Clear-DnsClientCache` |
| `wt0` shows no DNS server | `Get-DnsClientServerAddress -InterfaceAlias wt0` empty | match-only configuration | none needed |
| names resolve on the LAN resolver after an unclean stop | `unclean_shutdown_dns.txt` present | the previous run did not restore DNS | the next service start repairs it |
| after uninstall, internal names fail | `Netzilo-Match` still present | the rule survived a failed or interrupted uninstall | `reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\DnsPolicyConfig\Netzilo-Match" /f`, then `Clear-DnsClientCache` |

```powershell
Get-DnsClientNrptPolicy
Get-DnsClientServerAddress -InterfaceAlias wt0
Get-NetUDPEndpoint -LocalPort 53 | select OwningProcess
Clear-DnsClientCache
```

Account-side DNS design and the two-resolver model: `references/23-dns-management.md`,
`references/38-device-diagnosis-method.md` §4.3.

## 6. Routes and firewall

Routes are ordinary Windows routes on `wt0`; `Find-NetRoute -RemoteIPAddress <ip>` shows
which interface wins. An identical prefix already present locally is skipped (client log
`Skipping adding a new route for network … because it already exists`), and a more
specific local route wins by longest match; the typical case is a home LAN numbered like
an office route (`references/38-device-diagnosis-method.md` §4.2).

| Symptom | Evidence | Cause | Fix |
|---|---|---|---|
| other peers cannot reach this device, this device reaches them | `netsh advfirewall firewall show rule name=Netzilo` shows a `LocalIP` that is not the device's current Netzilo IP | the inbound rule is stale from an earlier enrolment | restart the connection (Disconnect/Connect); the service recreates the rule |
| same, rule is correct | `Get-NetFirewallProfile -PolicyStore ActiveStore \| select Name,Enabled,AllowLocalFirewallRules` shows `AllowLocalFirewallRules: False` | domain policy ignores local rules | add an inbound allow rule for `netzilo.exe` (or for the `100.64.0.0/10` range on the `wt0` adapter) to the GPO |
| a routed subnet is unreachable, `diag.route_match` matches and is selected | `Find-NetRoute` names the LAN adapter | local route conflict | renumber or publish a narrower range (`references/22-network-routes-and-exit-nodes.md`) |
| traffic to a routed subnet is blocked by a third-party firewall | that product's log | host firewall or EDR network control treats `wt0` as untrusted | mark the adapter or the `100.64.0.0/10` range as trusted in that product |

```powershell
Find-NetRoute -RemoteIPAddress <ip>
Get-NetRoute -InterfaceAlias wt0
netsh advfirewall firewall show rule name=Netzilo
netsh advfirewall firewall show rule name="Netzilo Client"
Get-NetFirewallProfile -PolicyStore ActiveStore | select Name,Enabled,AllowLocalFirewallRules
```

## 7. AI network filter and interception certificate

The AI network filter is the driver `nwfilter` plus the user-mode `nwfilter.exe`, started
and supervised by the service. A healthy start writes to `client.log`:
`NWFilter: started nwfilter.exe (PID=…)` and then `NWFilter: filter driver connected`. A
crash writes `NWFilter: nwfilter.exe (PID=…) exited unexpectedly — restarting in …`. The
filter's own log is `%ProgramData%\Netzilo\nwfilter.log`:

```
diag.grep {file: "C:\\ProgramData\\Netzilo\\nwfilter.log", pattern: "error|fail", ignore_case: true, max_matches: 30}
diag.grep {pattern: "NWFilter:", max_matches: 20}
```

| Symptom | Evidence | Cause | Fix |
|---|---|---|---|
| AI tools are not governed; no `filter driver connected` line | `sc.exe query nwfilter` STOPPED; CodeIntegrity events | driver blocked by Memory Integrity, a code-integrity policy or EDR | `Get-WinEvent -LogName Microsoft-Windows-CodeIntegrity/Operational -MaxEvents 30`; allowlist `nwfilter64.sys` and the install folder |
| `exited unexpectedly — restarting` repeats | `nwfilter.log` | another Windows Filtering Platform redirector on the host (Zscaler Client Connector, GlobalProtect, other filter-based network products), or security software killing the process | allowlist `nwfilter.exe` and the two pipes; with another redirector, decide which product owns redirection on that device |
| ordinary applications lose network at logon, before any AI tool runs | `nwfilter_policy.json` lists `restricted_adapters` | the profile's "restricted adapters" are enforced from service start, before sign-in, and apply to every process on those adapters | remove the adapter from the profile (`references/29-edge-filters.md`, `references/26-profiles-secure-workplace.md`) |
| a per-user agent path is not matched after a reboot | the rule uses `%LOCALAPPDATA%` or `%USERPROFILE%` | those variables are expanded for the active user when filters change; after a reboot with nobody signed in they expand to the system profile | have the person sign in, then Disconnect/Connect (`mod.refresh` does not re-expand paths) |
| Node-based tools fail TLS to intercepted hosts | `client.log` `MITM: certutil -addstore failed` | the interception CA did not reach the Local Machine Root store (security software blocked `certutil`) | from an elevated or `SYSTEM` shell: `certutil -addstore -f Root "%ProgramData%\Netzilo\netzilo-ca.pem"` |
| the same, but only in a terminal opened before install | `NODE_EXTRA_CA_CERTS` missing in that process | the variable is set machine-wide at install and read at process start | sign out and in, or open a new terminal |

Never copy `netzilo-ca-key.pem` anywhere; the public `netzilo-ca.pem` is the only file
these fixes need. Filter design and rules: `references/29-edge-filters.md`,
`references/10-ai-security-aidr.md`.

## 8. Posture signals on Windows

Each Windows posture signal reads a specific source, and the source is narrower than the
signal's name. Read `diag.posture` for the raw value and check the source below before
telling anyone the device "is not encrypted" or "has no antivirus".

| Signal | What is read | Operational caveat | Check on the device |
|---|---|---|---|
| Antivirus | Microsoft Defender registry state (`PassiveMode`, `DisableRealtimeMonitoring`), with Windows Security Center as the fallback | "up to date" is not measured separately; a third-party product registered in Security Center counts as enabled | `Get-MpComputerStatus \| select AMRunningMode,RealTimeProtectionEnabled` |
| OS updates | a Windows-side indicator that does not reflect Windows Update state | **never cite this signal as evidence of patching**; use the build number from `diag.system` and the customer's patch tooling | `Get-HotFix \| sort InstalledOn -Descending \| select -First 5` |
| Disk encryption | BitLocker on drive `C:` with protection **On** only; re-read about every 5 minutes | suspended protection, a system drive with another letter, and third-party full-disk encryption all read as *not encrypted* | `manage-bde -status C:` |
| Firewall | the local profile setting | a firewall state enforced by Group Policy may not be reflected; confirm with the active store | `Get-NetFirewallProfile -PolicyStore ActiveStore \| select Name,Enabled` |
| Domain membership | the NetBIOS domain name (`CORP`), not the DNS name (`corp.example.com`) | enter the short name in the check; an Entra-only joined device reports no domain | `(Get-CimInstance Win32_ComputerSystem).Domain`, `dsregcmd /status` |
| Registry Key & Value | existence of the key and the value; glob wildcards in the key path and value name | the value's *data* is not compared; use a File & Folder content check or a Running Processes check when data matters. `HKCU` is the service account's hive, not the person's | `reg query "<hive>\<key>" /v <value>` |
| File & Folder | path existence, optional content match | paths expand with the system account's environment (`%USERPROFILE%` is the service's profile) | `Test-Path` from `shell.run` (runs as `SYSTEM`, same view) |
| Virtual Device | signs of a hypervisor or a remote session | fires on physical PCs with Virtualization-based Security / Memory Integrity, Hyper-V or WSL2, the Hyper-V registry key, or any RDP session; cached until the service restarts | `diag.grep {pattern: "Running in VM\|Running in RDP"}`; `(Get-CimInstance Win32_ComputerSystem).HypervisorPresent` |
| Screen lock | the person's `Control Panel\Desktop` screensaver values (`ScreenSaveActive`, `ScreenSaverIsSecure`) in the first active session | a lock enforced by GPO or Intune, or sign-in-on-wake without a screensaver, reads *false* | `reg query "HKCU\Control Panel\Desktop" /v ScreenSaverIsSecure` via `shell.run as: "user"` |
| Device Integrity | debugger / tamper indicators | may flap briefly while security software injects into workspace applications | repeat `diag.posture` after a minute |
| Enterprise Workspace / Enterprise Browser | whether *this peer* is the workspace's or the browser's own peer | always false on the ordinary host peer; a policy with either enabled blocks every normal Windows host | `references/21-posture-checks.md` §1, `references/26-profiles-secure-workplace.md` |

The account-side reason strings (`peer.access.blocked` meta `reason`) and the device log
line `Posture check '<name>' FAILED at <CheckType>` are listed in
`references/21-posture-checks.md` §5.

## 9. Multi-user and RDP hosts

One peer per machine: the service enrols the device once, and every signed-in user shares
the tunnel, the routes and the DNS. What differs per user is small and matters on session
hosts:

- `shell.run` with `as: "user"` runs in the **first active session**, which on a session
  host is not necessarily the person you are helping. Read the user the result reports
  (`whoami` first) before drawing conclusions.
- The screen-lock posture signal and `%LOCALAPPDATA%` / `%USERPROFILE%` path expansion
  (§7, §8) also act on the first active session. On a shared host the signal describes
  one user, and per-user agent paths match one profile.
- Any RDP session on the host makes the Virtual Device signal fire (§8). Do not attach a
  Virtual Device check to a policy whose source group contains session hosts or machines
  that people reach over RDP.
- The tray runs per session; one user quitting it removes only their own autostart (§1).
- A non-administrator install is per user: each user has their own client, port, and
  `usservice<N>.json` / `.log`. Two such users on one machine are two peers.

## 10. Collecting evidence safely

Collect in this order and stop when the cause is established
(`references/38-device-diagnosis-method.md` §2):

1. Account: peer `connected`, `last_seen`, `login_expired`, groups, `os` and
   `kernel_version`.
2. Device tools: `diag.status`, `diag.system`, `diag.posture`, then `diag.grep` on
   `client.log`; `diag.grep {file: ...}` for `service.log` and `nwfilter.log`.
3. Shell (read-only): the `sc.exe query`, `Get-WinEvent`, `Get-DnsClientNrptPolicy`,
   `netsh advfirewall … show rule` and `Find-NetRoute` commands above.
4. Files to **collect**, never read: `installer_internal.log`, `core.log`,
   `nzcontainer.log` (encrypted; Netzilo support decrypts them).
5. Files never to collect or quote: `config.json`, `usservice*.json`, `mcp.db`, token and
   PAT files, `netzilo-ca-key.pem`, `<workspace>.json`.

Native component logging: set `HKLM\System\CurrentControlSet\Control\NetziloDebug`
(REG_MULTI_SZ) to `*`, reproduce, collect the encrypted logs, then delete the value; it
is for support escalation (`references/12-escalation-package.md`), not for reading on the
device. `diag.bundle` writes the client's own debug bundle on the device; it does not
include the encrypted native logs. Before any uninstall or reinstall, remember §2: the
uninstall deletes every log in `%ProgramData%\Netzilo`.
