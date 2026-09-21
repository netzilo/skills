---
id: '37'
title: Netzilo — Device Tool Reference (contracts, arguments, outputs, OS notes)
requires:
- api
- device-tools
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 18442
sections:
- id: '0'
  title: The contract every tool shares
  chars: 2384
- id: '1'
  title: '`diag.catalog` — the tool list'
  chars: 362
- id: '2'
  title: '`diag.status` — connection state'
  chars: 1375
- id: '3'
  title: '`diag.config` — effective configuration'
  chars: 943
- id: '4'
  title: '`diag.routes` and `diag.route_match` — what goes through Netzilo'
  chars: 1112
- id: '5'
  title: '`diag.dns` and `diag.probe` — resolution and reachability from the device'
  chars: 2113
- id: '6'
  title: '`diag.posture` — what the device reports about itself'
  chars: 2054
- id: '7'
  title: '`diag.system` — host facts'
  chars: 534
- id: '8'
  title: '`diag.loglevel` and `mod.loglevel`'
  chars: 338
- id: '9'
  title: '`diag.logs` and `diag.grep` — the client log, on the device'
  chars: 2255
- id: '10'
  title: '`diag.bundle` — debug bundle, written on the device'
  chars: 471
- id: '11'
  title: '`mod.refresh` — force a sync'
  chars: 288
- id: '12'
  title: '`mod.disconnect` — bring the client down'
  chars: 667
- id: '13'
  title: '`shell.run` — a program on the device'
  chars: 2755
---
# Netzilo — Device Tool Reference (contracts, arguments, outputs, OS notes)

This is the contract for every tool a Netzilo client offers through the device tools.
It is written the way a coding agent's tool documentation is written: one card per tool
with what it is for, when to use it and when not to, every argument with its type and
default, every output field with its meaning, how it behaves on each operating system,
and how it fails. Read the card before the first call to a tool in a conversation; do not
learn a tool by calling it.

The catalog a device returns (`device_tools`) is authoritative for *which* tools exist on
that device and for the argument schema. This file is authoritative for what the fields
*mean* and how they differ by platform, which the schema cannot say.

## 0. The contract every tool shares

**Call.** `device_run(peer_id, name, arguments, reason)`. `arguments` is a JSON object
matching the tool's `args_schema`; a tool with no arguments takes `{}`. Unknown argument
names are rejected as `invalid`, never ignored.

**Envelope.** Every result has the same shape:

| Field | Meaning |
|---|---|
| `id`, `name` | the command and the tool that answered |
| `status` | `ok`, `error`, `invalid`, `unknown`, `disabled`, `unsupported`, `timeout` |
| `output` | the tool's payload, present on `ok` and sometimes alongside `timeout` |
| `error` | why it did not run, already redacted on the device |
| `truncated` | the payload was clipped; text keeps its beginning and end with a marker |
| `duration_ms` | time on the device |

**Statuses.** `ok` means the tool ran; for `shell.run` a non-zero `output.exit_code` is
still `ok`. `error` is a failure inside the tool. `invalid` is your arguments. `unknown`
is a name the device has no handler for. `disabled` is account policy for that family on
that device. `unsupported` is the platform or the daemon's privilege, and `error` names
which. `timeout` means the deadline passed; a partial payload may still be attached.

**Limits.** Default deadline 30 s, ceiling 120 s (`timeout_ms` where a tool accepts it).
Payload cap 64 KiB; any single text field cap 32 KiB, clipped in the middle. Everything
that leaves the device passes a redactor for named secrets (`password`, `token`,
`*_key`, `authorization`, pre-shared and private keys) and bearer credentials.

**Concurrency.** Diagnostics may run in parallel on one device; the client runs each on
its own goroutine. Run changes one at a time and read back between them.

**Delivery.** At most once, never retried by the platform. A `timeout` on a change or a
command does not tell you whether it took effect.

**Identity of the daemon.** Tools run as the client process: `root` on macOS and Linux
(launchd, systemd), `SYSTEM` on Windows (service). A client started by hand with
`netzilo up -F` runs as the person who started it, and `as: "root"` in `shell.run` then
means *that* person.

**Operating system, once.** The device line from `device_tools` says what it runs. On
macOS the client reports its kernel name, so **"Darwin" means macOS**. Decide the OS
branch from that line before choosing a tool or writing a command; do not test for it.

## 1. `diag.catalog` — the tool list

Purpose: return the tools this device offers, with summaries and argument schemas.
`device_tools` already gives you this; call it directly only when a result came back
`unknown` or `disabled` and you suspect the catalog changed. No arguments. Output: an
array of `{name, summary, mutating, args_schema}`. Same on every OS.

## 2. `diag.status` — connection state

**Use for:** is the client connected to management and signal; is a peer direct or
relayed; how stale is a handshake. **Not for:** whether a policy allows something (that is
the account, `references/20-policies-access-control.md`).

| Argument | Type | Default | Meaning |
|---|---|---|---|
| `full` | bool | false | include `fullStatus` with every peer, relay and nameserver group |

Output: `status` (`Connected`, `Connecting`, `Disconnected`, …), `daemonVersion`, and with
`full`: `fullStatus.managementState`, `signalState`, `localPeerState` (`IP`, `pubKey`,
`kernelInterface`, `fqdn`, `routes`), `peers[]` (`IP`, `fqdn`, `connStatus`, `relayed`,
`direct`, `lastWireguardHandshake`, `latency`, `bytesRx/Tx`, `routes`), `relays[]`,
`dns_servers[]` (`servers`, `domains`, `enabled`, `error`).

Reading it: `relayed: true` with high `latency` is the usual "slow". A peer whose
`lastWireguardHandshake` is minutes old with `connStatus` Connected is a stale tunnel.
An empty `peers` while management is Connected means the network map has nothing for
this device: policy, not connectivity. `kernelInterface: false` means the userspace
stack (`-U`), which is normal for a foreground client and unusual for a daemon.

OS: identical fields. Interface name is `utun100` on macOS and `wt0` on Linux and
Windows unless the admin changed it.

## 3. `diag.config` — effective configuration

**Use for:** which management server the device talks to, which interface and port, and
which feature flags are on. No arguments.

Output: `managementUrl`, `adminURL`, `configFile`, `logFile`, `interfaceName`,
`wireguardPort` (a string, because it is a 64-bit field on the wire), `preSharedKey`
(`**********` when set, absent when not), `disableAutoConnect`, `serverSSHAllowed`,
`rosenpassEnabled`, `rosenpassPermissive`.

Reading it: `logFile: "console"` means there is no log file, and `diag.logs`,
`diag.grep` and `diag.bundle` will all refuse; that is what a hand-started client looks
like. A `managementUrl` that is not the customer's server is the whole answer to "why
does this device not appear".

OS: `configFile` is `/etc/netzilo/config.json` on macOS and Linux and
`%PROGRAMDATA%\Netzilo\config.json` on Windows. Never ask for the file's contents; it
holds the WireGuard private key.

## 4. `diag.routes` and `diag.route_match` — what goes through Netzilo

`diag.routes` (no arguments) lists every route the client knows: `ID`, `network`,
`selected`, `domains`, `resolvedIPs` per domain. `selected: false` means the route
exists in the account but is switched off on this device.

`diag.route_match` answers the question directly:

| Argument | Type | Required | Meaning |
|---|---|---|---|
| `target` | string | yes | an IP address or a hostname |

Output: `kind` (`address` or `domain`), `matched`, `best` (the route that carries it, or
the most specific match when none is selected), `candidates[]` sorted most specific
first, each with `reason` and `specificity`, and a one-line `verdict`.

Reading it: quote the `verdict`. A selected route beats a more specific unselected one,
because an unselected route carries nothing. `matched: false` means traffic to the
target does not enter Netzilo on this device at all, which is not a fault.

OS: identical. Route programming differs underneath (`route` on macOS and Windows,
netlink with policy rules on Linux) but the client's view is the same.

## 5. `diag.dns` and `diag.probe` — resolution and reachability from the device

`diag.dns` resolves a name the way the tunnel would and compares with the host.

| Argument | Type | Default | Meaning |
|---|---|---|---|
| `name` | string | required | the hostname |
| `server` | string | the group that owns the name | override nameserver, `host` or `host:port` |
| `timeout_ms` | int | 5000 | 100–30000 |

Output: `group` (the nameserver group chosen by longest matching domain, `catch_all` when
it has none), `via_netzilo` (`server`, `addresses`, `error`, `duration_ms`),
`via_system` (the host resolver), `agree`, `verdict`.

Reading it: the four verdicts are the four diagnoses. Neither resolves: the name is
wrong or the zone is down. Host yes, tunnel no: the nameserver group is the problem.
Tunnel yes, host no: **the client's DNS is not installed on this device**, so apps never
reach it. Both, different addresses: split-horizon or a stale cache.

OS, and this matters here: the *host* resolver `via_system` uses is configured
differently on each platform, so "the client's DNS is not in use" has a different next
step. macOS: the client sets resolvers through the system configuration
(`scutil --dns` shows them). Linux: the client picks a manager at start — NetworkManager
over D-Bus if it runs, else systemd-resolved (host resolver is the `127.0.0.53` stub),
else `resolvconf`, else it writes `/etc/resolv.conf` directly; `references/07-client-troubleshooting.md` §6
has the per-manager checks. Windows: per-adapter DNS on the `wt0` adapter.

`diag.probe` tests reachability from the device:

| Argument | Type | Default | Meaning |
|---|---|---|---|
| `mode` | `dns` / `tcp` / `http` | `dns` | what to test |
| `target` | string | required | hostname for dns, `host:port` for tcp, URL for http |
| `timeout_ms` | int | 5000 | 100–30000 |

Output: `ok`, `duration_ms`, and per mode `addresses`, `remote_addr`, `status_code`,
`error`. A failed probe is a successful diagnosis: `ok: false` with `error` is data, not a
tool error. Its `dns` mode uses the host resolver; use `diag.dns` for the tunnel's.

## 6. `diag.posture` — what the device reports about itself

No arguments. Output: `device_id`, `domain_name`, `disk_encryption_enabled`,
`firewall_enabled`, `firewall_names`, `antivirus_enabled`, `antivirus_updated`,
`antivirus_names`, `screen_lock_enabled`, `os_updated`, `being_debugged`,
`virtual_device`, `netzilo_container`, `netzilo_browser`, `integrity_level`, `checks[]`
(`id`, `result`) and `failing[]`, a shortlist of signals that are off.

Reading it: `failing` is a list of candidates, not a verdict. The device does not know
which checks its account enforces; `references/21-posture-checks.md` does. Match
`failing` against the account's posture checks before telling anyone why they were
denied.

**Each signal is probed differently per OS, and some are only heuristics.** Know these
before you trust a field:

| Signal | macOS | Linux | Windows |
|---|---|---|---|
| disk encryption | FileVault (`fdesetup status`) | any `crypt` device in `lsblk` | BitLocker via WMI, registry fallback |
| firewall | Application Firewall global state | `ufw status` active, else `iptables -L` succeeds | Windows Firewall via WMI |
| antivirus | known AV processes / launch agents | **only** `clamav-daemon` active | Security Center via WMI |
| OS updated | `softwareupdate --list` empty | `unattended-upgrade` / `apt-get -s upgrade`; **Debian and Ubuntu only** | Windows Update state |
| screen lock | `askForPassword` and delay in `com.apple.screensaver` | GNOME `gsettings` or KDE `qdbus` **only** | registry, per signed-in user |
| debugger | ptrace | `TracerPid` in `/proc` | `IsDebuggerPresent` |
| domain | `dsconfigad` | `domainname` | joined domain |

Consequences: on a Linux desktop that is not GNOME or KDE, `screen_lock_enabled` is
`false` regardless of reality; on Fedora, Arch or SUSE, `os_updated` is `false` because
the probe is apt-based; on Linux with any AV other than ClamAV, `antivirus_enabled` is
`false`. Say "the client cannot see this on that platform" rather than "the check
fails". iOS and Android report a fixed neutral set.

## 7. `diag.system` — host facts

No arguments. Output: `os`, `os_version`, `platform`, `kernel`, `kernel_version`, `goos`,
`arch`, `hostname`, `cpus`, `client_version`, `ui_version`, `product_name`,
`manufacturer`, `now`.

Reading it: switch on `goos` (`darwin`, `linux`, `windows`), not on `os`. On macOS `os`
is `Darwin` and `os_version` is the macOS version; on Linux `os` is the distribution and
`platform` the architecture string; on Windows `os` is the edition. `client_version` is
what management sees as the peer's version.

## 8. `diag.loglevel` and `mod.loglevel`

`diag.loglevel` (no arguments) returns `level` as the enum name (`INFO`, `DEBUG`, …).
`mod.loglevel` takes `level` as a lower-case name: `panic`, `fatal`, `error`, `warn`,
`info`, `debug`, `trace`. Same on every OS. Raising it is only useful if you then
reproduce and read; lower it afterwards.

## 9. `diag.logs` and `diag.grep` — the client log, on the device

The client log is one file, `client.log`, beside which rotations may sit.

| | macOS / Linux | Windows |
|---|---|---|
| log file | `/var/log/netzilo/client.log` | `%PROGRAMDATA%\Netzilo\client.log` |
| same directory also holds | nothing sensitive | `config.json`, `token.dat` |

Line format: `2026-09-22T20:31:50+03:00 DEBG client/internal/engine.go:856: message`.
Levels appear as `DEBG`, `INFO`, `WARN`, `ERRO`. Search with `ignore_case` and the
four-letter forms, for example `"warn|erro"`.

`diag.logs` tails:

| Argument | Type | Default | Meaning |
|---|---|---|---|
| `lines` | int | 200 | 1–2000 trailing lines |
| `contains` | string | — | keep only lines containing this, case-insensitively |

Output: `path`, `lines`, `text`, `truncated`, `size_bytes`.

`diag.grep` searches on the device and returns only matches:

| Argument | Type | Default | Meaning |
|---|---|---|---|
| `pattern` | RE2 regex | required | Go/ripgrep syntax; no backreferences |
| `file` | string | the client log | another file **inside the log directory only** |
| `all_files` | bool | false | every file beside the log, newest first, `.gz` included |
| `ignore_case` | bool | false | |
| `context` | int | 0 | 0–10 lines before and after each match |
| `max_matches` | int | 100 | 1–1000 |
| `from_start` | bool | false | first matches instead of the most recent |

Output: `pattern`, `files[]`, `total` (exact, even when few are returned), `matches[]`
(`file`, `line`, `text`, `before[]`, `after[]`), `truncated` (more matches than
returned), `incomplete` (the scan hit its byte ceiling or deadline, so `total` is a
floor), `skipped[]` (binary files), `scanned_bytes`, `verdict`.

Reading it: "3 returned of 50,195 total" and "3 returned of 3 total" are different
diagnoses; always report `total`. `incomplete: true` means "no matches" is not a safe
conclusion. `all_files` means the client log and its rotations (`client.log.1`,
`client.log.2.gz`, dated variants) and nothing else, so on Windows the `config.json` and
`token.dat` that share the directory are never candidates.

Both refuse when `logFile` is `console`, and `file` outside the log directory is
refused with a pointer to `shell.run`.

## 10. `diag.bundle` — debug bundle, written on the device

| Argument | Type | Default | Meaning |
|---|---|---|---|
| `anonymize` | bool | false | replace addresses and domains, matching the CLI flag |

Output: `path` of the archive, written beside the log file. **Nothing uploads it.** The
person still sends it (`references/12-escalation-package.md` §11). Refuses when logging
to console. Use `diag.grep` and `diag.logs` for diagnosis; the bundle is for escalation.

## 11. `mod.refresh` — force a sync

No arguments. Triggers an immediate sync with management. Output `{action, applied,
detail}`. First thing to try after an account change the device has not picked up; then
read `diag.routes` or `diag.status` back. Same on every OS. Not user-visible.

## 12. `mod.disconnect` — bring the client down

No arguments. **Signs the person out**: the stored session is cleared and they must sign
in again. The result is returned first, marked `applied: false` with a `detail` saying it
is scheduled, and the disconnect happens the moment the result has left the device,
because it tears down the connection the result travels on. The device answers nothing
further until someone signs it in again. There is no reconnect tool and no separate
logout, deliberately: neither could work over a connection the command itself ends.

OS: identical for a daemon. For a client started by hand with `netzilo up -F`, the
process exits.

## 13. `shell.run` — a program on the device

| Argument | Type | Default | Meaning |
|---|---|---|---|
| `cmd` | string | required | program; resolved on `PATH` if not absolute |
| `args` | string[] | `[]` | passed **verbatim**; no shell expansion |
| `as` | `root` / `user` | `root` | daemon's own identity, or the signed-in desktop user |
| `cwd` | string | daemon's | working directory |
| `env` | object | — | environment overrides on top of the daemon's |
| `stdin` | string | — | written to the program's input |
| `timeout_ms` | int | 30000 | up to 120000; the whole process tree is killed on expiry |

Output: `cmd`, `args`, `as`, `user` (the account it actually ran as), `cwd`, `pid`,
`exit_code`, `stdout`, `stderr`, `truncated`, `timed_out`, `duration_ms`.

Reading it: `exit_code` is the finding. `timed_out: true` means the device killed it and
returned what it had captured. `user` differs from what you asked when the daemon is not
privileged: a foreground client runs everything as its own user.

Pipelines and redirects need the shell as the program:

```
{"cmd": "sh", "args": ["-c", "ls -la /var/log/netzilo | tail -20"]}
{"cmd": "powershell", "args": ["-NoProfile", "-NonInteractive", "-Command", "Get-Service Netzilo | Format-List"]}
```

**OS.** `as: "user"` drops from root to the console user on macOS and Linux and is
`unsupported` with a privilege message when the daemon is not root; on Windows it
duplicates the signed-in session's token, needs the SYSTEM service, and gives the child
that user's environment. Process cleanup is a process-group kill on macOS and Linux and
`taskkill /T /F` on Windows. A Windows service has `System32` on its `PATH` but not the
user's tools; use absolute paths or `powershell`. The service has no console, so
anything interactive hangs until the timeout.

| Need | macOS | Linux | Windows (PowerShell) |
|---|---|---|---|
| service state | `launchctl print system/Netzilo` | `systemctl status netzilo` | `Get-Service Netzilo` |
| interface | `ifconfig utun100` | `ip addr show wt0` | `Get-NetAdapter wt0` |
| routes | `netstat -rn` | `ip route`; `ip rule` | `Get-NetRoute` |
| host DNS | `scutil --dns` | `resolvectl status` or `cat /etc/resolv.conf` | `Get-DnsClientServerAddress` |
| listening UDP | `lsof -nP -iUDP` | `ss -lunp` | `Get-NetUDPEndpoint` |
| signed-in user | `stat -f %Su /dev/console` | `loginctl list-sessions` | `query user` |

**Never** with `shell.run`: anything destructive; reading credential files (`config.json`,
`token.dat`, `*.pem`, `*.key`, browser stores); installing software or changing network
settings; `netzilo up`/`down` (use `mod.*`); working around a `disabled` or `403`
answer; piping a whole log into the result (search on the device with `diag.grep`).
