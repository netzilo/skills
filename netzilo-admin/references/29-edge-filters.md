---
id: '29'
title: Admin Skill — Edge Filters (binding AI policy to devices)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 9519
sections:
- id: '1'
  title: Model
  chars: 927
- id: '2'
  title: Field reference (Create New Filter / Edit Filter)
  chars: 2055
- id: '3'
  title: API
  chars: 802
- id: '4'
  title: Design patterns
  chars: 1565
- id: '5'
  title: Diagnosis — "the filter is not applying"
  chars: 3486
---
# Admin Skill — Edge Filters (binding AI policy to devices)

**Dashboard:** Edge → **Filters** (`/ai-edge/filters`). **API:** `/api/edge/filters`.
**Licence:** any plan can create and use Filters. Only **premium (global catalogue)
scanner rules bound inside a filter** require Enterprise; the server rejects those with
`Enterprise subscription required to use premium scanner rule <id>`. Custom scanners you
author yourself carry no plan restriction.

A filter is the object that makes AI governance happen on a device. Without a matching,
enabled filter a device records nothing and enforces nothing. Header text: "Use this
filter to restrict access to MCP servers and tools".

---

## 1. Model

A filter = **Targets** (groups × operating systems) + **Agents** (process paths to
intercept) + **Tools** (approved MCP tools, or the Unsanctioned wildcard) + **Scanners**
(rules) + **Posture Checks** (device conditions) + enable + name.

Matching: a device gets a filter when it belongs to **any** of the filter's groups **and**
its OS is in the filter's OS list. Several filters can match the same device; their
tools and scanners are combined; posture checks of a filter gate that filter's tools.
The group `All` matches every device.

Agents: only processes whose executable path matches an Agents entry are transparently
steered into the client's TLS-inspecting proxy (Windows, macOS). Coding-agent hooks, the
SDK and the browser extension do not need Agents entries; the browser extension matches
filters whose Agents contain the browser name. An empty Agents list means "no
transparent interception".

---

## 2. Field reference (Create New Filter / Edit Filter)

Tabs in order: **Targets**, **Agents**, **Tools**, **Scanners**, **Posture Checks**,
**Name & Description**.

| Tab | Field | UI help | Rule |
|---|---|---|---|
| Targets | Groups * | "Add or select which network groups this filter applies to (required)" | ≥1; new names are created |
| Targets | Operating Systems * | "Select which OS platforms this filter applies to (required)" | Windows, Darwin, Linux, Android, iOS |
| Targets | Enable Filter | "Use this switch to enable or disable the filter." | default on |
| Agents | Agents | "Specific agents can be targeted by entering process paths when this filter is active. Wildcards (`*`, `**`) and environment variables (e.g. `%PROGRAMFILES%`, `$HOME`) are supported and expanded on the endpoint." | e.g. `%ProgramFiles%\Google\Chrome\Application\chrome.exe`, `/Applications/Cursor.app/**`, `~/.local/bin/claude`; optional |
| Tools | Tools * | "Add or browse MCP tools that will be available through this filter (required)" | **Browse Tools** (catalog + **Unsanctioned Tools** wildcard) or **New Tool** |
| Scanners | Scanners * | "Add or browse security scanners that will be applied through this filter (required)" | **Browse Scanners** / **New Scanner**; premium scanners cannot be edited here |
| Posture Checks | — | "Choose whether all posture checks must pass or if any one set can pass" → All / Any | optional |
| Name & Description | Name of the Filter * | "Set an easily identifiable name for your filter (required)" | |

Validation order on save: "Filter name is required", "At least one Operating System
must be selected", "At least one Group must be selected", "At least one Tool must be
added", "At least one Scanner must be added".

Table: Name (dot, description), Active toggle, OS icons, Groups, Tools (n Tool(s) or
**Add Tool**), Scanners (n Scanner(s) or **Add Scanner**), Posture Checks (n or **Add
Posture Check**), Edit / Delete. Filters All/Active/Inactive; group selector; search
"filters, groups, tools, scanners".

---

## 3. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET/POST /api/edge/filters ; GET/PUT/DELETE /api/edge/filters/{id}
```
```json
{"name":"Developers AI policy","description":"","enabled":true,
 "os":["Windows","Darwin"],"groups":["<group-id>"],
 "agents":["%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe","/Applications/Cursor.app/**","~/.local/bin/claude"],
 "tools":["<tool-id>","*"],"scanners":["<scanner-id>"],
 "posture_checks":["<check-id>"],"any_check_must_pass":false}
```
`"*"` in `tools` = Unsanctioned Tools wildcard.

---

## 4. Design patterns

| Goal | Filter |
|---|---|
| Visibility first | groups `All`, all OSs, Agents = the AI apps in use, Tools = Unsanctioned wildcard + approved list, Scanners = premium set + custom rules in report mode |
| Developers with IDE agents | group `developers`; Agents: Cursor, VS Code, Claude Desktop, terminal shells if CLI agents are steered; Tools = approved dev MCP servers + wildcard; Scanners = premium + secrets/PII rules in block |
| Finance browser AI use | group `finance`; Agents: browser executables (or rely on the extension); Tools = wildcard only; Scanners = PII redaction + prompt injection block |
| Servers/agents enrolled with setup keys | group from the setup key's auto-groups; OS Linux; Tools/Scanners as needed (hooks/SDK path) |
| High-assurance | posture checks (disk encryption, OS updates) with **All** |

Precedence when several filters match: tools and scanners accumulate; posture checks are
per filter. The scanners of all matching filters are merged into one list and evaluated
together, most severe rule first; a block from any of them wins, and an `allow` rule in
one filter never exempts traffic from another filter's rule. The full evaluation model is
in `32-detection-rule-authoring.md`, section "Evaluation Order and Verdicts". Keep one
baseline filter for `All` and add group-specific filters on top, but remember that a rule
bound in the baseline filter reaches every device: to exempt a group from a rule, keep
that rule out of the baseline and bind it only in the filters for the groups that need
it.

---

## 5. Diagnosis — "the filter is not applying"

Check in this order on the device:

1. **Device in a filter group and OS?** Peers → device → Assigned Groups; filter →
   Targets. Group `All` is the only implicit membership.
2. **Filter enabled**, has ≥1 tool and ≥1 scanner (a filter cannot be saved otherwise,
   but check disabled toggles).
3. **Client connected and synced**: `netzilo status` shows Management Connected; after
   each change the client log contains `Successfully updated MCP Gateway filters: N
   filters applied` and `Gateway IPC: updating static rules (version: …, N rules, M
   filter profiles)` (the per-load count `Gateway static rules updated: N loaded, F
   failed` appears at debug log level). `Failed rules: [<rule-id>, …]` names rules that
   did not load (a line `[partition] rule <rule-id>: parse error: <detail>` usually
   precedes it): open each named scanner, fix its YAML and save; the rest of the rules
   keep working. `Gateway static rules update failed: <reason>` means the device did not
   accept the rule update at all: restart the client service, run `netzilo refresh`, and
   re-check the log. `netzilo refresh` forces a sync.
4. **Traffic actually reaches the engine**:
   - Desktop app: its executable path must match an **Agents** entry (Windows/macOS);
     Linux has no transparent per-app steering — use hooks/SDK or point the app at the
     proxy (`10-ai-security-aidr.md` §3).
   - Coding-agent CLI: `netzilo hook verify --framework=<x>` → `Status: ready ✓`.
   - Browser: extension installed (force-installed only with a Browser Extension
     profile); or the browser executable in Agents.
   - SDK agent: enrolled with a setup key whose group is in the filter.
5. **Posture checks** of the filter pass for the device. A failing check produces a
   `tool.blocked` event with the posture reason and the client log line
   `Posture check BLOCKED for domain <domain>: <reason>`. If the posture evaluation itself
   cannot complete (for example it times out), the log shows
   `Posture check failed for domain <domain>: …` and the request is denied: the posture
   gate fails closed, and there is no filter setting to change that. Posture results are
   cached for up to 5 minutes, so a device that has just been fixed may stay blocked for
   that long; saving the filter clears the cache on the device's next sync.
6. **Evidence**: Activity → Events, category AI Edge, filter by the user/peer:
   `tool.detected`/`tool.blocked` events name the **filter** and **rule**; `aidr.graph`
   snapshots on the peer page prove the engine sees traffic.

| Symptom | Cause | Fix |
|---|---|---|
| No events at all from a device | steps 1–4 | as above |
| Events but nothing blocked | scanners in report mode; tool approved | change actions; remove tool or use wildcard |
| Everything blocked | wildcard without approved tools; posture check failing | approve tools; check posture |
| Chrome not intercepted although in Agents | path mismatch (env var casing, wrong install dir); user runs a different browser | use `%ProgramFiles%\Google\Chrome\Application\chrome.exe` and `%LocalAppData%\…` variants |
| Works on Windows, not on Linux | Linux lacks per-app steering | hooks/SDK/proxy env |
| Filter save fails | validation list above | complete required tabs |
| Group cannot be deleted | referenced by a filter | edit filter first |

Events: `filter.created/updated/deleted`, `tool.allowed/blocked/detected`,
`semantic.event`, `aidr.graph`.
