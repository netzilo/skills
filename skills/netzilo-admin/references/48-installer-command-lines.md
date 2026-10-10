---
id: '48'
title: Installer command lines — Netzilo client and Enterprise Browser
requires:
- client-device
executable_on:
- netzilo-harness
- human-operator
chars: 39824
sections:
- id: '1'
  title: Which file to use
  chars: 2215
- id: '2'
  title: How the Windows client installers fit together
  chars: 2014
- id: '3'
  title: The client MSI — `netzilo_x64.msi`
  chars: 6248
- id: '4'
  title: Quick reference — Windows client command lines
  chars: 1066
- id: '5'
  title: The offline EXE — `nz_installer_64.exe`
  chars: 2215
- id: '6'
  title: The pack — `nz_installer_64.pack`
  chars: 1036
- id: '7'
  title: The online EXE — `netzilo_setup.exe`
  chars: 729
- id: '8'
  title: Tenant-named installers
  chars: 1319
- id: '9'
  title: Admin mode and non-admin (network-only) mode
  chars: 1289
- id: '10'
  title: Pre-enrolment with `CONFIGFILE` — the `deploy-user` file
  chars: 3302
- id: '11'
  title: What an install leaves on the machine
  chars: 1360
- id: '12'
  title: Upgrades — Windows client
  chars: 970
- id: '13'
  title: Enterprise Browser — the MSI `netzilo_enterprise_browser.msi`
  chars: 3392
- id: '14'
  title: Enterprise Browser — the EXE `netzilo_enterprise_browser.exe`
  chars: 2476
- id: '15'
  title: Uninstall — Windows client
  chars: 1383
- id: '16'
  title: macOS
  chars: 1668
- id: '17'
  title: Linux
  chars: 1117
- id: '18'
  title: Diagnosis
  chars: 3523
- id: '19'
  title: Known installer limitations — what to avoid
  chars: 1638
---
# Installer command lines — Netzilo client and Enterprise Browser

Every installer Netzilo publishes, every parameter it accepts, and the exact command line
for each deployment case: interactive, silent, non-admin, pre-enrolled, through Intune,
SCCM/ConfigMgr, Group Policy or Jamf, upgrade and uninstall. Windows MSI and EXE alike,
macOS packages, and Linux.

Related: `05-client-install-and-deploy.md` (enrolment, fleets, containers),
`40-windows-hosts.md` (what runs on a Windows host after install),
`26-profiles-secure-workplace.md` (Enterprise Browser profiles), `06-client-cli-reference.md`
(`netzilo up` and the other commands).

**Read §1 first.** The Windows client has four installer files that look alike but take
different switches. A switch that is right for one is silently ignored by another, and
the install then succeeds in the wrong mode.

---

## 1. Which file to use

All files are served from `https://pkg.netzilo.com`.

| Product | File | Download path | Takes parameters? | Use it for |
|---|---|---|---|---|
| Client, Windows x64 | **MSI** `netzilo_x64.msi` | `/download/windows/x64/netzilo_x64.msi` | `NONADMIN`, `CONFIGFILE` | **every managed deployment** (Intune, SCCM, GPO, scripts) |
| Client, Windows x64 | **Offline EXE** `nz_installer_64.exe` | `/download/windows/x64/nz_installer_64.exe` | `/S`, `NONADMIN=1`, `CONFIGFILE=` (fragile, §5) | a person installing by hand without internet at install time |
| Client, Windows x64 | **Pack** `nz_installer_64.pack` | `/download/windows/x64/nz_installer_64.pack` | `-q`, `-s`, `-na`, `--config-file=` | scripts that need non-admin mode **and** a config file together (§6) |
| Client, Windows | **Online EXE** `netzilo_setup.exe` | `/download/windows/netzilo_setup.exe` | `/S`, `NONADMIN=1`, `CONFIGFILE=` (fragile) | a person installing by hand; **never** for managed deployment (§7) |
| Enterprise Browser, Windows x64 | **MSI** `netzilo_enterprise_browser.msi` | `/download/windows/netzilo_enterprise_browser.msi` | `TENANT`, `SHORTCUTNAME` | every managed deployment of the browser (§12) |
| Enterprise Browser, Windows x64 | **EXE** `netzilo_enterprise_browser.exe` | `/download/windows/netzilo_enterprise_browser.exe` | `--system-level`, `--netzilo-tenant=`, `--netzilo-update=`, `--shortcut-name=` | scripted install when the update URL must be set (§13) |
| Enterprise Browser, Windows | **Online EXE** `browser_setup.exe` | `/download/windows/browser_setup.exe` | none | a person installing for themselves (§14) |
| Client, macOS | `nz_installer_arm64.pkg`, `nz_installer_amd64.pkg` | `/download/macos/arm64/…`, `/download/macos/amd64/…` | none | every macOS deployment (§16) |
| Enterprise Browser, macOS | `.pkg` / `.dmg` from the dashboard's download page | — | none | §16.2 |
| Client, Linux | `install_netzilo_linux.sh`, or the binary `netzilo` | `/download/linux/install_netzilo_linux.sh`, `/download/linux/netzilo` | none | §17 |

There is no x86 or ARM64 Windows MSI and no ARM64 Windows EXE. On Windows on ARM, the
x64 installers run in **network-only mode** automatically (§9).

---

## 2. How the Windows client installers fit together

All four Windows client files end up running the same install engine, `installer.exe`,
which copies itself to `%ProgramData%\Netzilo Client\`:

```
netzilo_x64.msi ──────────► runs the pack as:  -q [-na] "--config-file=<CONFIGFILE>"
nz_installer_64.exe (NSIS) ► runs the engine:  -i -s [-na] "--config-file=<CONFIGFILE>"
nz_installer_64.pack ─────► runs the engine:  -i  + the switches you pass
netzilo_setup.exe (online) ► downloads the pack (or the MSI) and runs it
                                   │
                                   ▼
installer.exe -i   (runs as the calling user)
   ├─ with a config file: netzilo.exe deploy-user --config-file <file>   (§10)
   └─ elevates itself (UAC "runas") for the machine-wide part,
      unless non-admin mode (§9)
```

Consequences that hold for every Windows client file:

- **The engine elevates itself.** The MSI is a per-user package and the EXEs request no
  elevation of their own. The machine-wide part (drivers, services) is started with a UAC
  elevation request.
  - Run as **SYSTEM** (Intune or ConfigMgr device context) or as an elevated
    administrator, there is no prompt.
  - Run as a **standard user**, Windows shows a UAC credential prompt, even under `/qn`.
  - **If the prompt is cancelled or refused, the install fails with exit code 1.** It
    does not fall back to a non-admin install. Non-admin mode only comes from `-na` /
    `NONADMIN=1`, a tenant config that asks for it (§8), or an ARM64 machine.
- **The install folder is fixed:** `%ProgramData%\Netzilo Client`. No property or switch
  changes it (`INSTALLDIR`, `/D=` and `TARGETDIR` have no effect).
- **An install refuses to start while a reboot is pending** from a previous Netzilo
  install or uninstall: "Please reboot computer and try again." (exit 1). Reboot first.
- **An install refuses to start while the Sandboxie service (`sbiesvc`) is running:**
  "Please uninstall sandbox software and try again." (exit 1).

---

## 3. The client MSI — `netzilo_x64.msi`

**Use the MSI for every managed deployment.** It is the only Windows client file whose
properties are parsed reliably and which suppresses every dialog.

| Fact | Value |
|---|---|
| Product name | Netzilo Client (publisher Netzilo) |
| Scope | **per-user** package (`InstallScope=perUser`), x64 |
| UpgradeCode | `{70905420-FC56-4EAC-8A4E-EE444EB1D298}` |
| ProductCode | **different for every build** — never hard-code it; detect by file or registry (§3.4) |
| Install folder | fixed, `%ProgramData%\Netzilo Client` |
| Add/Remove Programs | one entry, "Netzilo Client", owned by the MSI (Repair and Modify hidden) |
| Licence dialog | shown only in a full UI install; skipped by `/qn`, `/qb` and `/passive` |

### 3.1 Properties

| Property | Values | Default | What it does |
|---|---|---|---|
| `NONADMIN` | `1` | `0` | `1` installs in **non-admin (network-only) mode** (§9). Any other value is admin mode |
| `CONFIGFILE` | path to a `deploy-user` JSON file (§10) | empty | Pre-enrols the device: the engine runs `netzilo deploy-user` with this file. **A relative path is resolved against the folder the .msi is in.** An absolute path (`C:\…`, any drive letter) or a UNC path (`\\server\share\…`) is used as is. Use backslashes: a path written with forward slashes (`C:/…`) is treated as relative |

Both properties are secure (they pass to the install engine under a managed install).
Neither is remembered: the installed mode is remembered by the client itself (§11), and
`CONFIGFILE` must **not** be passed again on upgrades if it contains `apiurl` (§10.3).

Properties that exist in the package but **do nothing** if set: `INSTALLDIR`,
`TARGET_INSTALLDIR`, `FULL_CONFIGPATH`, `SHOWTRAY`, `SHOWLOGO`, `BOOTMODE`, `SYSTEMTYPE`,
`DRIVEMASK`, `FORCE_UPDATE`. Do not tell an admin any of them works.

### 3.2 Command lines

Run from an elevated prompt or as SYSTEM.

```bat
:: Silent install, admin mode (the normal case)
msiexec /i netzilo_x64.msi /qn /norestart /l*v "%TEMP%\netzilo_msi.log"

:: Silent install, admin mode, pre-enrolled with a deploy-user file
msiexec /i netzilo_x64.msi /qn /norestart CONFIGFILE="C:\Deploy\netzilo-deploy.json" /l*v "%TEMP%\netzilo_msi.log"

:: Config file next to the .msi (relative path)
msiexec /i "\\fs01\pkg\netzilo\netzilo_x64.msi" /qn /norestart CONFIGFILE=netzilo-deploy.json

:: Silent install, non-admin (network-only) mode
msiexec /i netzilo_x64.msi /qn /norestart NONADMIN=1

:: Progress bar only, no questions
msiexec /i netzilo_x64.msi /passive /norestart
```

`/norestart` (or `REBOOT=ReallySuppress`) matters: when a Netzilo driver update needs a
reboot, the package schedules one, and without suppression a silent install can restart
the machine. With suppression the install returns `3010` and the reboot is up to you.

From PowerShell, keep the whole property in one argument:

```powershell
Start-Process msiexec.exe -Wait -ArgumentList '/i','netzilo_x64.msi','/qn','/norestart','CONFIGFILE="C:\Deploy\netzilo-deploy.json"','/l*v','C:\Windows\Temp\netzilo_msi.log'
```

Transforms (`TRANSFORMS=your.mst`) work as for any MSI. A transform can set only
`NONADMIN` and `CONFIGFILE`, so it adds nothing beyond the command line.

### 3.3 What the MSI does on top of the engine

1. **Tenant config download.** The MSI reads its own file name. If the name contains `_`,
   the text after the **last** `_` (without `.msi`) is a tenant name, and the MSI
   downloads `https://pkg.netzilo.com/download/configs/<tenant>.config` and writes it over
   `%ProgramData%\Netzilo\config.json`. Keep the published name `netzilo_x64.msi`
   unless Netzilo gave you a tenant-named file (§8). The URL it tried is written to the
   MSI log (`DownloadJson url:`).
2. Runs the engine silently (`-q`), so no engine dialog can appear.
3. After the install, checks whether a reboot is pending and schedules one (admin mode
   only); see `/norestart` above.

### 3.4 Intune, ConfigMgr (SCCM), Group Policy

- **Run in device/system context.** Intune: package the MSI as a **Windows app (Win32)**
  (`.intunewin`) with install behaviour **System**. Do not use an Intune line-of-business
  MSI app: Intune installs a per-user MSI in the user's context, where a standard user gets
  a UAC prompt they cannot complete (§2). ConfigMgr: "Install for system". Group Policy:
  computer configuration software installation.
- **Install command** (Intune Win32 / ConfigMgr):
  `msiexec /i netzilo_x64.msi /qn /norestart` (add `CONFIGFILE="…"` if you pre-enrol).
  **Uninstall command**: see §15.
- **Detection rule — do not use the MSI ProductCode.** It changes with every build, so a
  ProductCode rule reports "not installed" after the next release. Detect instead:
  - file `%ProgramData%\Netzilo Client\netzilo.exe` exists, or
  - registry `HKLM\SOFTWARE\Netzilo`, value `Version` exists (admin mode; the value is the
    build number). Non-admin installs write it under `HKCU` instead.
- **Return codes:** `0` success, `3010` success with reboot required (with `/norestart`),
  `1603` the install engine failed (§18 for causes), `1618` another install is running,
  `1638`/`1639` standard msiexec errors.
- **Add/Remove Programs:** the per-user MSI registers in the context that ran it. Installed
  as SYSTEM, the "Netzilo Client" entry belongs to SYSTEM and is not shown to signed-in
  users; uninstall it from the same context (Intune/ConfigMgr uninstall, §15).
- **Do not force the client MSI per-machine** (`ALLUSERS=1`): see §19, item 4.

### 3.5 Version and upgrade behaviour of the MSI

- The MSI performs a **major upgrade** of any installed Netzilo Client MSI, including the
  same version ("A newer version of Netzilo Client is already installed." blocks only a
  real downgrade).
- Builds from one release line differ only in the fourth version field, which Windows
  Installer ignores. **Any build of the line can therefore replace any other, including an
  older one.** Do not rely on the MSI to refuse an old build; deploy the version you mean.
- The old product's uninstall step is skipped during the upgrade, so the device keeps its
  configuration and identity — unless the new MSI is tenant-named (§8) or you pass a
  `CONFIGFILE` with `apiurl` (§10.3).

---

## 4. Quick reference — Windows client command lines

| Goal | Command |
|---|---|
| Silent admin install (managed) | `msiexec /i netzilo_x64.msi /qn /norestart` |
| Silent admin install + pre-enrol | `msiexec /i netzilo_x64.msi /qn /norestart CONFIGFILE="C:\Deploy\netzilo-deploy.json"` |
| Silent non-admin install | `msiexec /i netzilo_x64.msi /qn /norestart NONADMIN=1` |
| Silent non-admin install + pre-enrol | `msiexec /i netzilo_x64.msi /qn /norestart NONADMIN=1 CONFIGFILE="C:\Deploy\netzilo-deploy.json"` |
| Verbose MSI log | add `/l*v "C:\Windows\Temp\netzilo_msi.log"` |
| Offline EXE, silent | `nz_installer_64.exe /S` |
| Offline EXE, silent non-admin | `nz_installer_64.exe /S NONADMIN=1` (NONADMIN must be the **last** argument) |
| Pack, silent, non-admin + config | `nz_installer_64.exe -q -na "--config-file=C:\Deploy\netzilo-deploy.json"` (the `.pack` file renamed to `.exe`) |
| Uninstall (MSI install) | `msiexec /x {ProductCode} /qn /norestart` (§15) |
| Uninstall (EXE install) | `"%ProgramData%\Netzilo Client\installer.exe" -u -q` |

---

## 5. The offline EXE — `nz_installer_64.exe`

An NSIS installer that carries the whole client. It needs no internet **unless** its file
name is tenant-named (§8).

| Switch | Meaning |
|---|---|
| `/S` | Silent: no installer pages. **Uppercase S, with a slash.** `-s` is not a switch of this file and is ignored — the installer then shows its pages |
| `NONADMIN=1` | Non-admin (network-only) mode |
| `CONFIGFILE=<path>` | `deploy-user` file (§10). A relative path is resolved against the EXE's folder |

**How this file parses `NONADMIN=` and `CONFIGFILE=` — read before using them.** The value
of each option runs to the **next letter N (for `NONADMIN=`) or C (for `CONFIGFILE=`)**,
upper or lower case, that is not inside quotes. Therefore:

| You write | What the installer gets |
|---|---|
| `nz_installer_64.exe /S NONADMIN=1` | non-admin ✔ (`NONADMIN=1` is last) |
| `nz_installer_64.exe NONADMIN=1 /S` | **admin** — the value is read as `1 /S`, which is not `1` |
| `nz_installer_64.exe /S CONFIGFILE=C:\Deploy\cfg.json` | **no config file** — the value stops at the `C` of `C:` |
| `nz_installer_64.exe /S CONFIGFILE="C:\Deploy\cfg.json"` | config file ✔ (quoted, and last) |
| `nz_installer_64.exe /S CONFIGFILE="…" NONADMIN=1` | **install fails** ("Cannot access config file.", exit 1) — `NONADMIN=1` becomes part of the path |
| `nz_installer_64.exe /S NONADMIN=1 CONFIGFILE="…"` | **admin** — `NONADMIN` reads `1 ` plus the start of the next option |

Rules: quote the `CONFIGFILE` path, put the option **last**, and **never pass both options
to this file.** From PowerShell the quotes are stripped unless you pass the argument
through `cmd /c` or `Start-Process -ArgumentList` with the quotes inside the string; use
the MSI or the pack instead.

Further behaviour:

- Under `/S` the installer runs the engine with `-s`, not `-q`: **error and reboot
  message boxes can still appear.** Only the MSI suppresses them.
- **Do not rely on the exit code.** Check the result instead: the service and
  `%ProgramData%\Netzilo Client\netzilo.exe` (§3.4 detection).
- Log: `%ProgramData%\Netzilo\netzilo_offline_nsis_install.log` (download and launch
  steps only; see §18 for where errors are logged).

---

## 6. The pack — `nz_installer_64.pack`

The same client payload as a self-extracting archive that runs the engine directly.
**Rename it to `.exe` before running it.** It is the only file to which non-admin mode
and a config file can both be passed reliably from a script.

| Switch | Meaning |
|---|---|
| `-q` | Quiet: no progress window **and no message boxes**. Also writes no Add/Remove Programs entry — use `-s` instead when you want the entry |
| `-s` | Silent: no progress window; message boxes can still appear; writes the Add/Remove Programs entry |
| `-na` | Non-admin (network-only) mode |
| `--config-file=<absolute path>` | `deploy-user` file (§10). Use an absolute path; quotes around the path are accepted |

Switches are case-insensitive and must be separate tokens.

```bat
copy nz_installer_64.pack nz_installer_64.exe
nz_installer_64.exe -s
nz_installer_64.exe -s -na "--config-file=C:\Deploy\netzilo-deploy.json"
```

An install with `-q` has no Add/Remove Programs entry; uninstall it with the engine (§15).

---

## 7. The online EXE — `netzilo_setup.exe`

A small downloader. At run time it downloads the real installer from `pkg.netzilo.com`
(the pack, or the MSI when a tenant config asks for it) and runs it.

- Same options as the offline EXE (`/S`, `NONADMIN=1`, `CONFIGFILE=`) with the **same
  parsing rules (§5)**.
- **It reports success (exit 0) even when the download or the install failed.** Only the
  last page's text changes. A deployment tool cannot tell a failed install from a good one.
  **Use it only for a person installing interactively**; use the MSI for anything managed.
- Without internet at install time it fails with "failed to download installer."
- Log: `%ProgramData%\Netzilo\netzilo_online_install.log`.

---

## 8. Tenant-named installers

A Netzilo-provided installer whose file name ends in `_<tenant>`
(`netzilo_x64_<tenant>.msi`, `nz_installer_64_<tenant>.exe`, `netzilo_setup_<tenant>.exe`)
downloads `https://pkg.netzilo.com/download/configs/<tenant>.config` when it runs and
**writes it over** `%ProgramData%\Netzilo\config.json`.

- `<tenant>` is the text after the **last** underscore, cut at the first space. A browser
  duplicate such as `netzilo_setup_acme (1).exe` still means `acme`; a tenant name cannot
  contain `_`. Renaming the published file to `…_<anything>` makes the installer fetch that
  name.
- The config is **re-applied on every run, upgrades included**. A tenant-named file used
  for an upgrade replaces the device's existing `config.json` — and with it the device's
  identity — by the published one. **Upgrade with the plain-named file** (`netzilo_x64.msi`)
  to keep a device's identity.
- The online EXE additionally reads `"msi": true` (install through the MSI) and
  `"nonadmin": true` (non-admin mode) from a tenant config. `NONADMIN=1` on the command line
  can turn non-admin on, never off.
- Tenant-named installers are prepared by Netzilo for a tenant; customers do not publish
  configs. Prefer `CONFIGFILE` (§10) or a setup key after install (`05`) for your own
  pre-enrolment.

---

## 9. Admin mode and non-admin (network-only) mode

| | Admin mode (default) | Non-admin mode (`NONADMIN=1`, `-na`, ARM64) |
|---|---|---|
| Elevation | UAC elevation for the machine-wide part | none |
| Components | client service, drivers (sandbox, network filter for AI governance, virtual disk), sandbox service, Workspace | **network only**: the client and its tray app; no drivers, no sandbox, no Workspace, no network filter |
| Registry root | `HKLM\SOFTWARE\Netzilo` | `HKCU\Software\Netzilo` |
| `PATH` | `%ProgramData%\Netzilo Client` appended to the **machine** `Path` | appended to the **user** `Path` |
| Shortcuts | Start menu and common desktop `Netzilo` | Start menu and the user's desktop, started with `--nonadmin=true` |
| Remembered as | — | `HKCU\Software\Netzilo\NonAdmin = 1` (DWORD) for the installing account |

- The mode is chosen at the first install and **remembered**: later upgrades and
  uninstalls read it back; you do not pass `NONADMIN` again.
- A **non-admin install over an existing admin install is refused** ("Admin mode is already
  installed, …", exit 1). An **admin install over a non-admin install** removes the
  non-admin install first, then installs admin mode.
- On **Windows on ARM** every install is network-only, whatever you pass.

---

## 10. Pre-enrolment with `CONFIGFILE` — the `deploy-user` file

`CONFIGFILE` / `--config-file` is **not** a settings file. It is the input of
`netzilo deploy-user`: with a service user's token it creates (or updates) a Netzilo
**user** and a personal access token for that user, and the device signs in with that
token. No SSO sign-in is involved.

### 10.1 File format (JSON)

| Key | Type | Required | Meaning |
|---|---|---|---|
| `servicetoken` | string | yes, unless `usertoken` | access token of an **admin or service user**, used to create the user and token |
| `apiurl` | string | no | management URL (`https://srv.netzilo.com` for Cloud, your server's address for self-hosted). **See §10.3 before using it** |
| `email` | string | yes, unless `use_current_user` | the user to create or update |
| `fullname` | string | no | display name |
| `use_current_user` | bool | no | take the e-mail and name from the signed-in Windows user |
| `groups` | string[] | no | groups to put the user in; missing groups are created |
| `password` | string | no | user password |
| `tokenname` | string | no | name of the personal access token created for the user |
| `tokenexp` | int | no | token lifetime in days, 1–365 (default 365) |
| `accountid` | string | no | account id |
| `usertoken` | string | no | an **existing** personal access token of the user: skips user and token creation; requires `apiurl` |
| `debug` | bool | no | verbose output |

String values may use `${VARIABLE}` environment expansion.

```json
{
  "servicetoken": "nzl_…",
  "use_current_user": true,
  "groups": ["Laptops", "Sales"],
  "tokenname": "device-enrolment",
  "tokenexp": 365
}
```

### 10.2 What happens

1. The install engine copies the file to `%LOCALAPPDATA%\Temp\Netzilo\config.json` of the
   **account that runs the installer** (SYSTEM: `C:\Windows\Temp\…` equivalent of its
   profile) and runs `netzilo deploy-user` with it.
2. The user is created with the role **user**; a personal access token is created and
   stored encrypted in `%ProgramData%\Netzilo\pat.dat`.
3. The client then signs in with that token whenever no setup key is given.

The result of `deploy-user` does not fail the install: a wrong token or an unreachable
server gives a **successful install of a device that is not enrolled**. Check the device
in the dashboard after the rollout.

### 10.3 Cautions

- **The copied file is not deleted after the install.** It holds the service token in
  plain text in the installing account's temp folder. Use a service user created for
  enrolment, give it only what enrolment needs, rotate its token after the rollout, and
  delete `%LOCALAPPDATA%\Temp\Netzilo\config.json` of the installing account.
- **With `apiurl`, the device's client configuration is rewritten:** a new WireGuard key
  (a new peer identity), the management URL from `apiurl`, and the admin (dashboard) URL
  set to `https://go.netzilo.com` — also on self-hosted servers. On a self-hosted server,
  set the dashboard address afterwards (`netzilo up --admin-url https://<your domain>`)
  or leave `apiurl` out and set the management URL with `netzilo up --management-url`.
- **Never pass a `CONFIGFILE` containing `apiurl` on an upgrade.** It re-runs
  `deploy-user`: another token, and a new identity for the device.

---

## 11. What an install leaves on the machine

| Item | Admin mode | Non-admin mode |
|---|---|---|
| Program files | `%ProgramData%\Netzilo Client\` (incl. `installer.exe`, `netzilo.exe`, `netzilo-ui.exe`) | same folder |
| Client configuration, identity, token | `%ProgramData%\Netzilo\config.json`, `pat.dat` | same |
| Client service | installed and started (`netzilo service install` / `start`) | — |
| Drivers and sandbox | sandbox filter driver, `NtzlSvc` "Netzilo Sandbox Service", virtual disk drivers, network filter; `C:\Netzilo`; `C:\Windows\Netzilo.ini` | — |
| URL handler | `nz://` (machine) | `nz://` (user) |
| `PATH` | machine `Path` += `c:\programdata\netzilo client` | user `Path` += same |
| Version | `HKLM\SOFTWARE\Netzilo\Version` | `HKCU\Software\Netzilo\Version` |
| Add/Remove Programs | the MSI's entry (MSI); otherwise "Netzilo Client" with `UninstallString "%ProgramData%\Netzilo Client\installer.exe" -u` (not with `-q`) | same, under HKCU |
| Shortcuts | Start menu `Netzilo`; desktop `Netzilo` | user desktop |
| After a successful install | the tray app starts for the signed-in user | same |

A failed install **rolls back completely**, and the rollback deletes `%ProgramData%\Netzilo`
— including the installer logs, any downloaded tenant config and `pat.dat`. Capture the MSI
log (`/l*v`) so something survives (§18).

---

## 12. Upgrades — Windows client

| Path | Behaviour |
|---|---|
| Any client file over an installed client | the engine detects the install and upgrades in place: stops the Netzilo services and drivers, replaces the files, re-runs `deploy-user` only if a config file was passed, restarts the services. Configuration and identity are kept |
| MSI over MSI | major upgrade (§3.5); same in-place engine upgrade |
| Tenant-named file | **identity replaced** by the published config (§8) |
| Driver changed while loaded | the upgrade completes and **requests a reboot** (MSI `3010` with `/norestart`). Installs are refused until the reboot (§2) |
| Services do not come back within ~10 s | the upgrade fails (MSI `1603`; EXE exit 1) |

- The EXE forms do **not** compare versions: they install whatever version they carry,
  older or newer.
- You do not re-pass `NONADMIN`; the mode is remembered (§9).
- In-app update from the tray is a separate mechanism (`05` §7).

---

## 13. Enterprise Browser — the MSI `netzilo_enterprise_browser.msi`

| Fact | Value |
|---|---|
| Product name | Netzilo Enterprise Browser (publisher Netzilo) |
| Scope | **per-machine** (`InstallScope=perMachine`), x64; installs to `%ProgramFiles%\Netzilo\NetziloEnterpriseBrowser\Application\` |
| UpgradeCode | `{70905420-FC56-4EAC-8A4E-EE444EB1D298}` — **the same as the client MSI** (§19, item 4) |
| How it installs | runs the browser installer as LocalSystem with `--netzilo-tenant=[TENANT] --shortcut-name="[SHORTCUTNAME]" --msi --system-level` |

### 13.1 Properties

| Property | Value | What it does |
|---|---|---|
| `TENANT` | your **Workplace / dashboard address**: `https://go.netzilo.com` on Netzilo Cloud, `https://<your domain>` self-hosted | written to `netzilo.json` in the browser's install folder; the built-in Netzilo extension uses it as its portal. **Also used as the browser's update host** — see §13.3 |
| `SHORTCUTNAME` | text, e.g. `Acme Browser` | name of the desktop and Start-menu shortcuts. Empty = the default name |

**Neither property is remembered.** Pass both on **every** install and upgrade: an MSI
upgrade without `TENANT` rewrites `netzilo.json` with an empty tenant, and without
`SHORTCUTNAME` the custom shortcut name is removed.

There is no MSI property for the update URL.

### 13.2 Command lines

```bat
:: Silent per-machine install (Intune, ConfigMgr, GPO: system context)
msiexec /i netzilo_enterprise_browser.msi /qn /norestart TENANT=https://go.netzilo.com SHORTCUTNAME="Acme Browser" /l*v "%TEMP%\netzilo_browser_msi.log"

:: Self-hosted server
msiexec /i netzilo_enterprise_browser.msi /qn /norestart TENANT=https://netzilo.example.com SHORTCUTNAME="Acme Browser"
```

`TENANT` is passed to the browser installer without quotes: the value must not contain
spaces or double quotes.

- **Detection rule:** file `%ProgramFiles%\Netzilo\NetziloEnterpriseBrowser\Application\netzilobrowser.exe`
  exists. The MSI ProductCode changes with every build.
- **Return codes:** standard msiexec (`0`, `3010`, `1603`, `1618`).

### 13.3 The tenant is also the update host

The browser checks for updates (Settings → About, `chrome://settings/help`) at
`<TENANT>/download/windows/browser_updates.json`, unless an explicit update URL was set
at install time. With `TENANT=https://go.netzilo.com` that address does not exist, so the
**update check fails**; a self-hosted dashboard does not serve it either. The default
update source, used when no tenant is set, is
`https://pkg.netzilo.com/download/windows/browser_updates.json`.

- To keep in-browser update checks working, install with the **EXE** and set the update
  URL explicitly (§14).
- With the MSI, update the browser by deploying the new MSI (with `TENANT` and
  `SHORTCUTNAME` again).

### 13.4 Upgrade and uninstall

- **Upgrade:** deploy the new MSI with the same properties. The old MSI's uninstall step is
  skipped during the upgrade.
- **Uninstall:** `msiexec /x {ProductCode} /qn /norestart`. The uninstall runs the browser's
  own uninstaller for **the Chromium version that MSI shipped**. If the browser was updated
  since (by the EXE or in-browser), that uninstaller path no longer exists and the
  uninstall fails with `1603`. Then uninstall with the browser's current uninstaller
  (§14.3) and remove the MSI registration with `msiexec /x {ProductCode} /qn` afterwards.

---

## 14. Enterprise Browser — the EXE `netzilo_enterprise_browser.exe`

The browser's own (Chromium) installer with Netzilo switches.

| Switch | What it does |
|---|---|
| `--system-level` | per-machine install to `%ProgramFiles%` (requires elevation; run as SYSTEM or elevated admin). Without it the browser is installed for the current user only |
| `--netzilo-tenant=<URL>` | writes `netzilo.json` with the tenant (your Workplace/dashboard address, §13.1). Present with an empty value, it writes an empty tenant |
| `--netzilo-update=<URL>` | the **full URL of the update JSON**; only used together with `--netzilo-tenant`. Use `https://pkg.netzilo.com/download/windows/browser_updates.json` |
| `--shortcut-name=<name>` | shortcut name; **per-machine installs only**. Absent or empty removes a custom name |
| `--msi` | used by the MSI only: suppresses the browser's own Add/Remove Programs entry. Do not pass it yourself |

### 14.1 Command lines

```bat
:: Per-machine, tenant set, update checks kept working
netzilo_enterprise_browser.exe --system-level --netzilo-tenant=https://go.netzilo.com --netzilo-update=https://pkg.netzilo.com/download/windows/browser_updates.json --shortcut-name="Acme Browser"

:: Per-user (a person installing for themselves)
netzilo_enterprise_browser.exe --netzilo-tenant=https://go.netzilo.com --netzilo-update=https://pkg.netzilo.com/download/windows/browser_updates.json
```

Values must not contain double quotes or backslashes (they are written into a JSON file
without escaping).

### 14.2 Behaviour

- Re-running the EXE updates in place. **Downgrades are allowed.**
- The installer always registers the `netzilo-ssh` and `netzilo-rdp` link handlers used by
  the Workplace.
- The browser carries its own copy of the Netzilo client and starts it per user session in
  userspace mode. It does **not** use an installed Netzilo Client service or its
  configuration; each browser session becomes its own peer (`26`).

### 14.3 Uninstall (EXE installs)

Through Add/Remove Programs ("Netzilo Enterprise Browser"), or the browser's uninstaller:

```bat
"%ProgramFiles%\Netzilo\NetziloEnterpriseBrowser\Application\<version>\Installer\setup.exe" --uninstall --system-level --force-uninstall
```

`<version>` is the folder name of the installed version under `Application\`. For a
per-user install, use the same command from
`%LOCALAPPDATA%\Netzilo\NetziloEnterpriseBrowser\Application\<version>\Installer\` without
`--system-level`.

---

## 15. Uninstall — Windows client

| Installed with | Silent uninstall |
|---|---|
| MSI | `msiexec /x {ProductCode} /qn /norestart` — find the ProductCode of the installed build under `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\` (or `HKCU`/SYSTEM's hive for the per-user MSI) by DisplayName "Netzilo Client", or with `Get-Package "Netzilo Client"` in the same context that installed it |
| EXE or pack | `"%ProgramData%\Netzilo Client\installer.exe" -u -q` |

- `-u` alone shows dialogs; `-u -s` hides only the progress window.
- The engine's uninstall **always returns 0**; verify that `%ProgramData%\Netzilo Client`
  is gone.
- Uninstalling an MSI install with `installer.exe -u` removes the client but leaves the MSI
  entry behind; use `msiexec /x` for MSI installs.
- Admin mode may ask for a reboot to finish removing drivers ("Please reboot computer to
  complete uninstallation!", suppressed with `-q` / `/qn`).

**What uninstall removes — there is no "keep configuration" option:**
the services and drivers, `%ProgramData%\Netzilo Client`, **`%ProgramData%\Netzilo`
(configuration, the device's identity, `pat.dat`, logs)**, `C:\Netzilo`, the Netzilo
registry keys under HKLM and HKCU, the `Netzilo` autostart value, the `nz://` handler, the
shortcuts and the `PATH` entry. A reinstall is a **new peer**; remove the old one from the
dashboard (`24`).

---

## 16. macOS

### 16.1 Client `.pkg`

```bash
sudo installer -pkg nz_installer_arm64.pkg -target /     # Apple silicon
sudo installer -pkg nz_installer_amd64.pkg -target /     # Intel
```

- **No parameters.** The package has no choices and reads no configuration file or
  environment variable at install time. It installs `/Applications/Netzilo.app`, then
  (re)installs and starts the client service and starts the tray app.
- It appends `/Applications/Netzilo.app/Contents/MacOS` to the `PATH` in the `~/.zshrc` (or
  `~/.bashrc`) of the account running the installer — **root's** under `sudo installer`,
  Jamf or another MDM, so signed-in users do not get the `netzilo` command on their `PATH`.
  Call `/Applications/Netzilo.app/Contents/MacOS/netzilo` by full path in scripts.
- Re-installing the package upgrades in place.
- **Enrol after install:** `sudo /Applications/Netzilo.app/Contents/MacOS/netzilo up --setup-key <key>`
  (plus `--management-url https://<your server>` when self-hosted), or `deploy-user`
  (§10), or let the user sign in from the tray (`05`).
- **Jamf / MDM:** deploy the package as is, then run the `netzilo up --setup-key …` line as
  a policy script. Pre-approve the system extensions `com.netzilo.NetziloFilter` and
  `com.netzilo.NetziloSecurity` with a SystemExtensions payload so users are not prompted
  (`05` §3).

### 16.2 Enterprise Browser `.pkg` / `.dmg`

- Installs `/Applications/Netzilo Enterprise Browser.app`. **No parameters and no tenant
  setting**: macOS has no install-time way to set the tenant; the browser uses its defaults.
- `sudo installer -pkg <file>.pkg -target /`, or drag the app from the `.dmg`.

---

## 17. Linux

### 17.1 Client

```bash
curl -fsSL https://pkg.netzilo.com/download/linux/install_netzilo_linux.sh | sh
```

- **No arguments and no environment variables.** The script stops and removes an existing
  client, downloads `https://pkg.netzilo.com/download/linux/netzilo` to `/usr/bin/netzilo`
  (via `/opt/netzilo`), installs the systemd service `Netzilo`, starts and enables it. It
  needs `sudo`, `wget` and systemd.
- It installs the command-line client only; the tray app (`/download/linux/netzilo-ui`) is
  a separate download.
- **Enrol after install:** `sudo netzilo up --setup-key <key>` (add
  `--management-url https://<your server>` for self-hosted).
- Without the script (images, containers, other init systems): download the binary, then
  `netzilo service install` and `netzilo service start` (`05`).
- There is no `.deb` or `.rpm` package of the client.

### 17.2 Enterprise Browser

A `.deb` package `netzilo-enterprise-browser`, installed to `/opt/netzilo/enterprisebrowser`
(`sudo apt install ./netzilo-enterprise-browser_*.deb`). No install-time parameters and no
tenant setting.

---

## 18. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| `nz_installer_64.exe -s` shows the installer pages | `-s` is not a switch of the offline EXE | `nz_installer_64.exe /S`, or use the MSI |
| `NONADMIN=1` on an EXE gave an admin install | the option was not the last argument (§5) | put it last, or use `msiexec … NONADMIN=1` |
| EXE with `CONFIGFILE=` installed but the device is not enrolled | the unquoted path started with or contained a `C` (§5), or `deploy-user` failed (wrong token, server unreachable) | use the MSI's `CONFIGFILE`; check the token; enrol with `netzilo up --setup-key` |
| "Cannot access config file." | the config-file path does not exist **for the account running the installer** (SYSTEM cannot read a user's mapped drive), or `NONADMIN=1` was appended to the path (§5) | absolute local or UNC path readable by that account |
| "Please reboot computer and try again." | a Netzilo driver change is waiting for a reboot | reboot, run again |
| "Please uninstall sandbox software and try again." | Sandboxie is running | remove it |
| "Admin mode is already installed, …" | non-admin install over an admin install | uninstall first, or install admin mode |
| Install fails right after a UAC prompt was cancelled | no fallback to non-admin | deploy as SYSTEM, run elevated, or pass `NONADMIN=1` |
| MSI returns `1603` | the install engine failed; its reason is in the MSI log only as "returned actual error code 1" | run the pack with `-s` interactively on that machine to see the engine's message; check the causes above |
| MSI returns `3010` | a driver update needs a reboot | reboot |
| Silent install rebooted the machine | `/norestart` / `REBOOT=ReallySuppress` missing | add it |
| Online EXE "succeeded" but nothing is installed | it always exits 0 (§7) | use the MSI |
| Intune reports the app as not installed after a new release | ProductCode detection rule | file or registry detection (§3.4) |
| Device lost its identity after an upgrade | tenant-named installer (§8) or `CONFIGFILE` with `apiurl` (§10.3) | upgrade with the plain-named MSI and no `CONFIGFILE`; remove the old peer |
| A user cannot find "Netzilo Client" in Add/Remove Programs | per-user MSI installed as SYSTEM, or a pack install with `-q` | uninstall from the deployment tool / with the engine (§15) |
| Installer logs are gone after a failed install | the rollback deletes `%ProgramData%\Netzilo` | always deploy with `/l*v` to a path outside it |
| Browser shortcut lost its custom name after an MSI upgrade / extension shows no portal | `SHORTCUTNAME` / `TENANT` not passed again (§13.1) | redeploy with both properties |
| Browser "About" update check fails | `TENANT` is used as the update host (§13.3) | reinstall with the EXE and `--netzilo-update=…` |
| Browser MSI uninstall fails with `1603` | browser updated since that MSI (§13.4) | browser's own uninstaller, then `msiexec /x` |

Where the logs are:

| Log | Written by |
|---|---|
| your `/l*v` file | the MSI (custom actions, tenant-config URL, engine exit code) |
| `%ProgramData%\Netzilo\netzilo_offline_nsis_install.log` | the offline EXE (download and launch steps) |
| `%ProgramData%\Netzilo\netzilo_online_install.log` | the online EXE |
| `%ProgramData%\Netzilo\installer_internal.log` | the install engine; **encrypted**, readable by Netzilo support only — attach it to an escalation (`12`) |

The engine's dialogs ("Please reboot…", "Cannot access config file.") are logged only in
the encrypted engine log, not in the NSIS logs.

---

## 19. Known installer limitations — what to avoid

These are product behaviours, not configuration mistakes. Plan around them and do not
promise otherwise.

1. **Offline/online EXE option parsing (§5).** `NONADMIN=` and `CONFIGFILE=` are cut at the
   next N/C. Use the MSI or the pack when either option matters.
2. **The online EXE always exits 0 (§7).** Never use it for managed deployment.
3. **Silent EXEs can still show message boxes (§5).** Only the MSI and the pack with `-q`
   are dialog-free.
4. **The client MSI and the browser MSI share one UpgradeCode.** They stay separate only
   because the client MSI is per-user and the browser MSI per-machine. **Do not install the
   client MSI with `ALLUSERS=1`**: the two products would then treat each other as versions
   of the same product, and installing one removes or blocks the other.
5. **The client MSI version field.** Any build of a release line can replace any other,
   including an older one (§3.5).
6. **Tenant-named installers overwrite the device's configuration on every run (§8).**
7. **`CONFIGFILE` leaves the service token in the installing account's temp folder, and
   with `apiurl` rewrites the device's identity and sets the dashboard address to
   `go.netzilo.com` (§10.3).**
8. **Uninstall removes everything** under `%ProgramData%\Netzilo`, with no keep option
   (§15).
9. **Browser MSI properties are not remembered; the browser's update host is the tenant;
   the browser MSI's uninstall depends on the shipped Chromium version (§13).**
10. **macOS and Linux installers take no parameters**; enrolment is always a step after
    install (§16, §17).
