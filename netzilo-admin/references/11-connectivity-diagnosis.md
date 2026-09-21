---
id: '11'
title: Netzilo — End-to-End Connectivity Diagnosis ("Host X is unreachable")
requires:
- api
- client-device
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 19339
sections:
- id: '0'
  title: Classify the target (2 minutes)
  chars: 1091
- id: '1'
  title: Is the Netzilo layer up on both ends?
  chars: 1038
- id: '2'
  title: Can A and the remote peer see each other?
  chars: 1401
- id: '3'
  title: Does policy allow it? (resolve it, don't eyeball it)
  chars: 2879
- id: '4'
  title: Is the route correct and delivered? (routed hosts and exit nodes)
  chars: 1666
- id: '5'
  title: Verify the routing peer itself (run on R)
  chars: 3078
- id: '6'
  title: Name resolution
  chars: 1182
- id: '7'
  title: Server-side checks (self-hosted only)
  chars: 928
- id: '8'
  title: 'A probe peer from your own shell: `netzilo up -F -U` and its SOCKS5 proxy'
  chars: 3969
- id: '9'
  title: Report template
  chars: 684
---
# Netzilo — End-to-End Connectivity Diagnosis ("Host X is unreachable")

> **Running this from the agent.** The device-side steps of this procedure (§1, §2, §4, §6)
> can be executed on the affected peer through the device tools — `diag.route_match`
> answers "does traffic to X go through Netzilo on this device" in one call, `diag.dns`
> resolves X the way the tunnel would, `diag.status {full: true}` shows direct-or-relayed
> per peer, and `diag.probe` tests the port from the device. The routing-peer checks in §5
> can run the same way on R. Playbook with stop conditions and OS branches:
> `references/38-device-diagnosis-method.md` §4.2; each tool's arguments and output:
> `references/37-device-tool-reference.md`.

**Audience:** an AI operator who has been told "device A cannot reach host X over
Netzilo" and must find the reason with evidence, not guesses. This runbook is the
procedure; `07-client-troubleshooting.md` and `08-network-administration.md` hold the
per-component detail it points to. Work top to bottom; stop at the first failing check
and fix it before continuing.

You will need: shell access to device **A** (source), the admin API token established in `SKILL.md`
(`09-api-and-automation.md` §1), and — when X is behind a route — shell access to the
routing peer **R**. Ask for the exact target: IP or name, port/protocol, and what "fails"
means (timeout, refused, DNS error, TLS error).

---

## 0. Classify the target (2 minutes)

| X is… | Path | Decisive checks |
|---|---|---|
| another Netzilo peer (`100.64.0.0/10` address or `<name>.netzilo.network`) | A ⇄ X directly (WireGuard, P2P or relayed) | §1, §2, §3 |
| a host in a LAN/VPC published by a **route** (private IP or a domain route) | A → routing peer R → X | §1, §2 (A→R), §4, §5 |
| an Internet host through an **exit node** | A → exit node R → Internet | §1, §2, §4 (with `0.0.0.0/0`), §5 |
| a DNS name that does not resolve | any of the above | §6 first |

Get the facts from A:

```bash
netzilo status -d                      # management/signal/relays, peers, routes
netzilo routes list                    # routes A currently holds and which are selected
getent hosts X ; dig +short X          # what X resolves to on A
ip route get <X-ip>                    # Linux: which interface A would use (expect wt0)
```

If `ip route get` does not choose `wt0` (macOS: `route -n get <X-ip>` → `utun100`), the
problem is on A: no route (§4) or a conflicting local route (`ip route show table all | grep <prefix>`).

---

## 1. Is the Netzilo layer up on both ends?

**A is the customer's device.** Every command in this file runs on their device, their
routing peer or their server, through them or through access they granted. Your own
machine's client is not A unless the customer enrolled it as a test peer (`SKILL.md`).

On A (`netzilo status -d`):

- `Management: Connected` and `Signal: Connected` — otherwise `07` §4 first; nothing
  below will work.
- `Relays: n/m Available` with at least one available — otherwise only direct P2P can
  work; fix relay reachability (`07` §4, `03` §4 for self-hosted).
- `Daemon status: NeedsLogin` → session expired; `netzilo up` (`07` §2).

On the other end (X if it is a peer, R if it is a routing peer): same checks. If you
cannot log in there, the dashboard tells you: Peers → search the name → green dot =
online; "Login required" badge = expired session; "Approval required" = blocked until
approved. An **offline routing peer** is the single most common cause of "the whole
office network disappeared".

---

## 2. Can A and the remote peer see each other?

On A, find the remote peer (X, or R for routed traffic) in `netzilo status -d`:

| Observation | Meaning | Action |
|---|---|---|
| Peer **not listed** | no enabled policy connects A's groups with the peer's groups | §3 |
| `Status: Disconnected`, handshake `-` | listed (policy OK) but no tunnel established | both sides need a relay or UDP path; compare `Relays` on both; check `Last connection update`; run `netzilo debug for 3m -A` on A while retrying |
| `Status: Connected`, `Connection type: Relayed` | works but via TURN | acceptable; if throughput is the complaint, open outbound UDP on both networks or set `--external-ip-map` on servers behind 1:1 NAT |
| `Connected`, handshake recent, but `ping <peer-netzilo-ip>` fails | policy allows the connection but not ICMP, or the peer's OS firewall drops it | check the rule protocol (ALL or ICMP needed for ping); test the real port instead: `nc -vz -w3 <ip> <port>` |
| `Connected`, ping OK, port refused/timeouts | policy port list or target service | `nc -vz`; §3 ports; on X `ss -ltnp` to confirm the service listens on all interfaces, and X's own firewall |

A quick two-sided test: on X run `sudo tcpdump -ni wt0 host <A-netzilo-ip>` (macOS
`utun100`) while A connects. Packets arriving on X but no reply → X's service/OS
firewall. No packets arriving → tunnel or policy on A's side.

---

## 3. Does policy allow it? (resolve it, don't eyeball it)

Policies are allow-only, evaluated between **groups**; both A and the destination must
be in groups covered by an **enabled** policy/rule with a matching protocol and port,
and every posture check attached to that policy must pass for A.

Dashboard: Peers → A → **Assigned Groups**; same for the destination peer; Network →
Policies → filter Sources/Destinations by those groups. API (faster and exact):

```bash
export NZ_URL=https://<domain>/api NZ_TOKEN=nzl_...
nz() { curl -sS -H "Authorization: Token $NZ_TOKEN" -H 'Accept: application/json' "$NZ_URL$1" "${@:2}"; }
A=$(nz /peers | jq -r '.[] | select(.name=="<A-name>") | .id')
B=$(nz /peers | jq -r '.[] | select(.name=="<X-or-R-name>") | .id')
nz /groups > /tmp/g.json
GA=$(jq -r --arg p "$A" '[.[] | select(.peers[]?.id==$p) | .id] | @json' /tmp/g.json)
GB=$(jq -r --arg p "$B" '[.[] | select(.peers[]?.id==$p) | .id] | @json' /tmp/g.json)
echo "A groups: $(jq -r --arg p "$A" '[.[] | select(.peers[]?.id==$p) | .name] | join(",")' /tmp/g.json)"
echo "B groups: $(jq -r --arg p "$B" '[.[] | select(.peers[]?.id==$p) | .name] | join(",")' /tmp/g.json)"
nz /policies | jq --argjson ga "$GA" --argjson gb "$GB" '
  .[] | select(.enabled) | . as $p | .rules[] | select(.enabled)
  | select( (any(.sources[]; IN($ga[])) and any(.destinations[]; IN($gb[])))
         or (.bidirectional and any(.sources[]; IN($gb[])) and any(.destinations[]; IN($ga[]))) )
  | {policy:$p.name, rule:.name, protocol, bidirectional, ports, port_ranges, allowed_routes, posture:$p.source_posture_checks, any_check_must_pass:$p.any_check_must_pass}'
```

The query prints every enabled rule where at least one of A's groups is a source and at
least one of the destination peer's groups is a destination (or the reverse for
bidirectional rules). Interpretation:

- **No rule printed** → this is the cause. Either add A/destination to the right groups
  or create a policy (`08` §4). Remember the `All` group covers everyone only while the
  `Default` policy is enabled.
- Rule printed but **protocol/ports** exclude the traffic (e.g. TCP 443 only, user tries
  SSH) → extend ports or add a rule. One-way TCP/UDP rules need explicit ports.
- Rule printed with **posture checks** → check A against each (`nz /posture-checks/<id>`)
  and look for `peer.access.blocked` events naming A:
  `nz "/events/paginated?limit=50&code=peer.access.blocked&q=<A-name>" | jq '.events[] | {timestamp,meta}'`
  — the event meta names the failing check and reason.
- Rule has **`allowed_routes`** → routed destinations must fall inside those CIDRs (§4).
- Policy just changed → peers pick up changes within ~30 s; `netzilo refresh` on A.

Direction reminder: the initiating side enforces the rule, so after a policy fix the
change must reach **A** (check `netzilo status` on A shows the peer listed).

---

## 4. Is the route correct and delivered? (routed hosts and exit nodes)

Dashboard: Network → Routes → the network containing X's prefix (or `0.0.0.0/0` for
exit nodes). API: `nz /routes | jq '.[] | {network_id,network,domains,peer,peer_groups,groups,access_control_groups,enabled,metric,masquerade}'`.

Checklist:

1. **Route enabled** and its **network/domains** actually contain X's IP (a `/24` that
   does not cover X is a frequent miss).
2. **Distribution groups** include a group A belongs to → A must show the route in
   `netzilo routes list` (`Status: Selected`). If A does not see it: A not in the group,
   route disabled, or another route with the same prefix is selected — `netzilo routes select <id>`.
3. **Routing peer R** (or a peer in the routing group) is **Linux**, **online**, and
   **connected to A** (§2 with R as the remote peer). With HA, at least one routing peer
   must be connected; `netzilo status -d` on A shows `Routes:` per peer.
4. **Policy A → R** exists (§3 with B = R) for the protocol/ports of the traffic to X.
   Routed traffic is checked against the policy between A's group and R's group; if the
   rule carries `allowed_routes`, X must be inside one of them. If the route has
   **Policy Groups** (`access_control_groups`), the rule must reference that group.
5. **Masquerade**: on unless X's network has a return route to `100.64.0.0/10` via R.
   With masquerade **off** and no return route, packets reach X but replies never come
   back (tcpdump on R shows requests only).
6. **Metric / HA**: two networks with overlapping prefixes → the lower metric wins;
   `netzilo routes list` on A shows which is selected.

---

## 5. Verify the routing peer itself (run on R)

```bash
netzilo status -d | head -20                 # R connected; A listed as a connected peer
sysctl net.ipv4.ip_forward                   # must be 1 (the client sets it)
ip route get <X-ip>                          # must exit via R's LAN/VPC interface, not wt0
ping -c2 <X-ip>; nc -vz -w3 <X-ip> <port>    # R itself must reach X
ip rule show | grep -i netzilo               # fwmark rule (priority 110) → table 7120
ip route show table 7120                     # Netzilo routes on R
```

Firewall rules the client installs on R (inspect, do not edit by hand):

```bash
sudo nft list table inet netzilo              # nftables backend
#   chains: netzilo-acl-input-rules / -output-rules (policies for R itself),
#           netzilo-rt-fwd (allowed forwarded traffic), netzilo-rt-nat (masquerade)
sudo iptables -S | grep -i NETZILO            # iptables backend
#   chains: NETZILO-ACL-INPUT, NETZILO-ACL-OUTPUT, NETZILO-RT-FWD, NETZILO-RT-NAT
sudo iptables -t nat -S NETZILO-RT-NAT        # MASQUERADE for the routed network when masquerade is on
```

Absence of `netzilo-rt-fwd` / `NETZILO-RT-FWD` rules for X's prefix means R has not
received the route (or is not the selected router) — go back to §4. Presence of the
rules but no traffic → look at the packets:

```bash
sudo tcpdump -ni wt0 host <A-netzilo-ip> and host <X-ip>     # arriving from A?
sudo tcpdump -ni <lan-iface> host <X-ip>                    # forwarded to X? replies?
sudo conntrack -L 2>/dev/null | grep <X-ip>                 # NAT state (if conntrack installed)
```

| tcpdump result | Cause | Fix |
|---|---|---|
| nothing on `wt0` | A is not sending via R (route not selected on A, or policy A→R blocks) | §4.2, §3 |
| on `wt0` but nothing on LAN interface | forwarding blocked: `ip_forward=0`, another host firewall (ufw/firewalld default `FORWARD DROP`), or `netzilo-rt-fwd` lacks the prefix | `sysctl -w net.ipv4.ip_forward=1`; allow forwarding in the host firewall (`ufw route allow in on wt0 out on <lan>`; firewalld `--add-masquerade`/zone forward); check §4 |
| out to LAN, no reply | X's own firewall, X's security group/NSG does not allow R's IP, or masquerade off without return route | fix X's firewall/SG (source = R's LAN IP, or `100.64.0.0/10` if masquerade off); enable masquerade |
| reply reaches R but not A | asymmetric routing on R (multiple interfaces), `rp_filter` | `NB_USE_LEGACY_ROUTING=true` in the service environment, or `sysctl net.ipv4.conf.all.rp_filter=2` |
| ICMP works, TCP does not | MTU/fragmentation on the LAN path or a middlebox | try `ping -M do -s 1200 <X-ip>` from R; lower MTU on the LAN hop; Netzilo tunnel MTU is fixed at 1280 |

Cloud specifics for R: the instance's **security group / NSG must allow egress to X**
and X's group must allow ingress from R's private IP (or the whole subnet). For traffic
to other VPCs/subnets the VPC route tables must route R's subnet ↔ X's subnet. For
exit nodes R needs a public egress path (NAT gateway or public IP) and the SG must allow
outbound Internet.

---

## 6. Name resolution

```bash
# on A
netzilo status | grep Nameservers          # n/m Available
getent hosts <peer>.netzilo.network        # peer names must resolve to 100.64.x.y
getent hosts <internal-name>               # names behind a private DNS server
```

| Symptom | Cause | Fix |
|---|---|---|
| peer names do not resolve | Netzilo resolver not installed on A (backend problem) | `07` §6 |
| private names do not resolve | no nameserver group distributed to A's groups, or the DNS server is itself behind a route (needs route + policy allowing UDP/TCP 53 A → R) | Network → DNS Servers: distribution groups; add route/policy for the resolver |
| match-domain resolver ignored | A's OS does not support match domains (Linux without systemd-resolved, older Windows) | add a primary (no match domains) nameserver group for `All` |
| name resolves to a public IP while a private one is expected | split-horizon: match domain missing or wrong | add the domain to the nameserver group's Match Domains |
| domain route not applied | domain routes are resolved on A every minute; the resolved IPs must be routable through R | wait / `netzilo refresh`; check "Keep Routes" |

---

## 7. Server-side checks (self-hosted only)

If many peers are affected at once, or §1 fails for everyone. For signal and STUN/TURN
specifically — the components that decide whether two peers can find each other and
whether a relayed path exists — use `03-server-troubleshooting.md` §4a, which tests each
in isolation. Quick first pass:

```bash
# on the server
C=$( [ -f /opt/netzilo/run/docker-compose.yml ] && echo /opt/netzilo/run || echo /opt/netzilo ); cd "$C"
sudo docker compose ps                                   # management, signal, coturn up?
sudo docker compose logs --tail=100 management | grep -iE "error|warn" | tail -20
sudo ss -lunp | grep -E ':3478|:5349'                    # relay listening
```

Then `03-server-troubleshooting.md` §4. Relay outages turn every non-P2P connection
into `Disconnected`; management outages stop policy/route updates but existing tunnels
keep working until keys rotate.

---

## 8. A probe peer from your own shell: `netzilo up -F -U` and its SOCKS5 proxy

When you have a shell with the `netzilo` binary but no running client you may use — or you
want a test that touches nothing on the host — start a throwaway peer in the foreground in
userspace mode. It answers "can a Netzilo peer in these groups reach X on this port" in
under a minute, without a TUN device, routes, or changes to the host's DNS.

`-F` (`--foreground-mode`) runs the engine in this process instead of a daemon; Ctrl-C stops
it. `-U` (`--userspace-mode`) uses the userspace TCP/IP stack: the peer's only way in is a
**local SOCKS5 proxy on `127.0.0.1`**. Run as a normal user, the client uses userspace mode
even without `-U`. Always choose the port yourself with `--socks5-port`: `netzilo status`
does not show it, and a run that is not root otherwise listens on a per-user port derived
from the home directory, not on `41339`. `NB_SOCKS5_LISTENER_PORT` overrides the flag.

```sh
D=$(mktemp -d)   # its own config, log and socket path, so a running client on this host is untouched
netzilo up -F -U -l debug --socks5-port 1080 \
  --management-url https://srv.netzilo.com:443 --pat "$NETZILOPAT" \
  --config "$D/config.json" --log-file "$D/client.log" --daemon-addr "unix://$D/daemon.sock" &
tail -f "$D/client.log"   # keep this open for the whole test, in a second shell if you have one
# A second probe on the same host also needs --wireguard-port 51821 (any free port).
```

**The log is the only view into a foreground client.** It has no daemon, so `netzilo status`
cannot see it, and nothing else reports what it is doing. Always run it with `-l debug`
(`--log-level debug`) and keep reading the log while you test: enrolment, the connection
to management and each peer connection are recorded there and nowhere else. At debug level
each connection through the proxy logs its path — `Dial Netzilo Route <addr>` went into
the tunnel, `Dial System Route <addr>` left through the host's own network (the
destination is not a Netzilo address or route), and `failed to dial via Netzilo route`
names the error. It is up when the log shows `Netzilo engine started, FQDN: … the
IP is: …` (`grep -m1 'engine started' "$D/client.log"`). When a request through the proxy
fails, read the lines it produced before drawing a conclusion. Then send traffic through
the proxy. Use the **`socks5h`** form so
the proxy resolves names through Netzilo DNS; plain `socks5` resolves on the host, whose
resolver knows no Netzilo names.

```sh
curl -sv --socks5-hostname 127.0.0.1:1080 http://db-proxy.netzilo.network:8080/  # HTTP(S)
curl -sv -x socks5h://127.0.0.1:1080 https://10.20.5.7/                            # same, proxy URL form
nc -vz -X 5 -x 127.0.0.1:1080 10.20.5.7 5432                                      # any TCP port (OpenBSD nc)
ssh -o ProxyCommand='nc -X 5 -x 127.0.0.1:1080 %h %p' admin@10.20.5.7              # SSH through it
ALL_PROXY=socks5h://127.0.0.1:1080 some-cli ...                                    # tools that honour ALL_PROXY
```

Read the result the way §3 and §4 read policy and routes:

- **The probe is its own peer.** It registers in the account with the groups its PAT's user
  or its setup key gives it, and policy applies to it, not to the affected device. A
  success proves the path works *for a peer in those groups*; compare its groups with
  device A's before you call A's problem solved. A failure where A's groups would pass is
  a policy finding about the probe, not about A.
- **It tests the Netzilo path only.** Routed destinations (§4) and exit nodes apply to it
  like any peer. Destinations outside Netzilo leave through the host's own network.
- **TCP through SOCKS5 only.** `ping` does not go through a SOCKS5 proxy; test a port.
- **Clean up.** Stop it with Ctrl-C (`kill %1`) and delete `$D`. If the peer stays listed
  in the dashboard, remove it (`DELETE /api/peers/{id}`) so it does not linger in the
  account's groups.

## 9. Report template

State the classification (§0), then the first failing check and its evidence, e.g.:

> A (`laptop-jane`, groups `developers`) → X `10.20.5.7:5432` via route `dc-1`
> (`10.20.0.0/16`, routing peer `dc-router-1`, masquerade on). A and `dc-router-1` are
> connected P2P. Policy `dev-to-dc` allows TCP 5432 `developers → dc-routers`. On
> `dc-router-1`, tcpdump shows SYNs leaving `ens5` to 10.20.5.7 with no reply; the
> database host's security group only permits `10.20.1.0/24`. Fix: allow `10.20.9.15/32`
> (router's private IP) on port 5432 in that security group.

Always include the commands you ran and their output, what you changed, and how to
revert it.
