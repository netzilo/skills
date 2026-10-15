---
id: '29'
title: Admin Skill — Edge Filters (binding AI policy to devices and to gateway users)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 17236
sections:
- id: '1'
  title: Model
  chars: 3232
- id: '2'
  title: Field reference (Create New Filter / Edit Filter)
  chars: 4023
- id: '3'
  title: API
  chars: 2096
- id: '4'
  title: Design patterns
  chars: 1807
- id: '5'
  title: Diagnosis — "the filter is not applying"
  chars: 4569
---
# Admin Skill — Edge Filters (binding AI policy to devices and to gateway users)

**Dashboard:** Edge → **Filters** (`/ai-edge/filters`). **API:** `/api/edge/filters`,
`/api/edge/filters/effective`, `/api/edge/filters/{id}/expanded`. **Who:** admins; a
regular user may `GET /api/edge/filters?os=…`, which answers only the enabled endpoint
filters that apply to them (what the browser extension reads).

A filter is the object that makes AI governance happen. It has a **type**:

| Type | Targets | Carries | Enforced by |
|---|---|---|---|
| **Endpoint** | devices: groups × operating systems; with the OS **Browser**, the signed-in user's browser extension | Agents (process paths to intercept), Guardrails | the Netzilo client on each device (`10-ai-security-aidr.md`); the browser extension for OS Browser (`49-browser-extension-aidr.md`) |
| **Gateway** | users: groups | Models (grants), Limits, MCP servers and bundles (grants), Gateways (addresses users reach), Guardrails | the AI Gateway, per user (`27-ai-gateway.md`) |

Without a matching, enabled filter a device records and enforces nothing, and a gateway
user is refused every model. Endpoints never see gateway filters; gateways never load
endpoint filters. Dialog subtitle: "Use this filter to govern AI traffic with
guardrails".

Filters carry **no posture conditions and no tool list** any more: posture is judged by
policies, profiles and published applications (`21-posture-checks.md`); MCP access is a
gateway filter grant (`46`).

---

## 1. Model

**Matching.**
- Endpoint: a device gets a filter when it belongs to **any** of the filter's groups
  **and** its OS is in the filter's OS list (Windows, Darwin, Linux, Android, iOS;
  compared case-insensitively). Several filters may match; their guardrails are merged
  into one rule set.
- Endpoint with the OS **Browser** (`browser`): the **browser extension** of every user
  in the filter's groups gets it (`GET /api/edge/filters?os=browser` with the user's own
  credentials). The browser is not a peer: it matches by the user's groups, never by a
  device. A desktop OS value never reaches the extension, and a filter listing only
  Browser never reaches a desktop client; list both when both should apply
  (`49-browser-extension-aidr.md` §2).
- Gateway: a user gets a filter when any of the filter's groups is among the user's
  groups (the user's own group memberships; a caller identified by its peer on the
  gateway's tunnel door adds the peer's groups). Several filters may match; grants are
  the **union**, limits the **lowest** of each kind, guardrails merged.
- The group **All** matches every device and every user.

**Agents** (endpoint only): only processes whose executable path matches an entry are
transparently steered into the client's TLS-inspecting proxy (Windows, macOS). Hooks,
the SDK and the browser extension do not use Agents: the extension ignores the list
entirely and is selected by the OS **Browser** instead. Empty = no transparent
interception. Linux has no per-app steering. A browser executable in Agents makes the
desktop client claim that browser, and the extension in it stands down (`49` §3).

**Grants** (gateway only):
- **Models** (required, ≥1): `provider/model` or `provider/*` ids, where `provider` is
  the provider's **id**, the model one of its catalogue names (`45` §1). The dialog does
  not save a gateway filter without one ("At least one Model must be selected"), nor does
  the API (422 `models is required and must contain at least one model`). A user whose
  filters grant no usable model (none saved by an older server, or the provider or model
  since disabled) is refused at the gateway.
- **MCP**: servers with all tools (`*`) or typed tool names; bundles by id.
- **Gateways**: the addresses users reach gateways at (`{name, url}`, http(s), no path);
  shown on the Workplace and probed there. A filter with models but no address grants
  the models, but the Workplace shows no card and users have nothing to paste.
- **Limits**: by id; each applies per user (`45` §2).

**Guardrails are optional on both types.** A filter without guardrails still targets,
grants and limits, but governs nothing on the content side: no prompt, answer or tool
call is judged and no detection is recorded. Bind at least one rule in report mode as
the usual minimum. Dashboards and servers from before October 2026 refused a filter
without a guardrail ("At least one Guardrail must be added").

**Expansion.** What reaches a device or a gateway is the **expanded** filter: guardrails,
models, limits, servers and bundles inlined, with disabled or deleted ones left out. Each
expanded filter has a content version; a gateway fetches only versions it does not hold.

---

## 2. Field reference (Create New Filter / Edit Filter)

### 2.1 Endpoint filter — tabs Targets | Agents | Guardrails | Name

| Tab | Field | UI help | Rule |
|---|---|---|---|
| Targets | Filter Type | **Endpoint**: "Devices in the selected groups. Operating systems and agents apply." | |
| Targets | Groups * | "Add or select which network groups this filter applies to (required)" | ≥1; each must exist |
| Targets | Operating Systems * | "Select which OS platforms this filter applies to (required)" | ≥1 ("At least one Operating System must be selected"; API: `os is required and must contain at least one OS`). Values: Windows, Darwin, Linux, Android, iOS, **Browser** (`browser`). **Browser** targets the browser extension of the groups' users and nothing else; the desktop values never reach the extension and vice versa. Agents are irrelevant for the extension. Confirm the picker's label in the customer's dashboard before quoting it |
| Targets | Enable Filter | "Use this switch to enable or disable the filter." | default on |
| Agents | Agents | "Specific agents can be targeted by entering process paths when this filter is active. Wildcards (`*`, `**`) and environment variables (e.g. `%PROGRAMFILES%`, `$HOME`) are supported and expanded on the endpoint." | e.g. `%ProgramFiles%\Google\Chrome\Application\chrome.exe`, `/Applications/Cursor.app/**`, `~/.local/bin/claude`; optional |
| Guardrails | Guardrails | "Add or browse guardrails that will be applied through this filter (optional)" | **Browse Guardrails** / **New Guardrail**; optional, recommended (§1) |
| Name | Name of the Filter *, Description | "Set an easily identifiable name for your filter (required)", placeholder "e.g., Developers AI access" | |

### 2.2 Gateway filter — tabs Targets | Models | Limits | MCP | Gateways | Guardrails | Name

| Tab | Field | UI help | Rule |
|---|---|---|---|
| Targets | Filter Type | **Gateway**: "AI gateways, for users in the selected groups. Endpoints skip this filter." | OS does not apply (forced empty) |
| Targets | Groups *, Enable Filter | as above | |
| Models | Models | "Grant the models users of this filter may call. Pick single models or a whole provider." → **Browse Models** ("Grant Models — Pick models from your providers, or a whole provider at once"; **All models** = "Every model this provider has, now and later"; "Apply (n)") | ≥1: while empty the tab warns "No model is granted: users of this filter are refused at the gateway until one is.", **Continue** stays disabled and **Save** answers "At least one Model must be selected" |
| Limits | Limits | "Apply spend budgets and rate limits to each user of this filter (optional). The lowest value wins when several filters apply." → **Browse Limits** / **Add Limit** | optional |
| MCP | MCP Servers, MCP Bundles | "Grant the MCP servers and MCP bundles users of this filter may call. A server grants all of its tools or the names you type." → **Browse MCP Servers** (per server: **All Tools** or names), **Browse MCP Bundles** | optional |
| Gateways | Gateways | "Where users of this filter reach their gateways. Shown in the Workplace with the models and MCP endpoints granted." → **Add Gateway**; each row a URL (placeholder `https://llm.example.com`); ⋯ → **Gateway Settings** (Name + URL); rows can be reordered | http(s) URL, trailing `/` trimmed; name defaults to the URL (422 `gateway address "…" must be an http(s) URL`) |
| Guardrails | Guardrails | as above | optional |
| Name | Name of the Filter *, Description | as above | |

In create mode **Continue** walks Targets → Models → Limits → Guardrails → Name; the
**MCP** and **Gateways** tabs are not on that path and must be opened by clicking them —
a common reason a new gateway filter ends up with no Workplace card.

Table: Name, Active, **Type** (Endpoint/Gateway), Groups, **Models** ("n Model(s)" or a
red **Grant Models** badge; "—" for endpoint filters), **MCP** ("n MCP(s)" / **Grant
MCP**), **Guardrails**; search "filters, groups, guardrails".

---

## 3. API

Prefer the API when you hold an admin token: read the current object, change one
field, write it back, read it again. Every `PUT` replaces the whole object.

```
GET/POST /api/edge/filters ; GET/PUT/DELETE /api/edge/filters/{id}
GET /api/edge/filters/effective?type=gateway|endpoint&user=<id>&peer=<id>   → [{id,name,type,version}]   (admin; ETag)
GET /api/edge/filters/{id}/expanded                                         → the expanded filter (admin; ETag)
```

Endpoint filter:
```json
{"name":"Developers AI policy","description":"","enabled":true,"type":"endpoint",
 "os":["Windows","Darwin"],"groups":["<group-id>"],
 "agents":["%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe","/Applications/Cursor.app/**","~/.local/bin/claude"],
 "guardrails":["<guardrail-id>"]}
```

Gateway filter:
```json
{"name":"Developers gateway","enabled":true,"type":"gateway","groups":["<group-id>"],
 "models":["<provider-id>/claude-sonnet-4-6","<provider-id2>/*"],
 "limits":["<limit-id>"],
 "mcp":[{"server_id":"<server-id>","tools":["*"]},{"server_id":"<server-id2>","tools":["search_docs"]}],
 "virtual_mcps":["<bundle-id>"],
 "gateways":[{"name":"Acme AI Gateway","url":"https://aigw.apps.example.com"}],
 "guardrails":["<guardrail-id>"]}
```

Rules: `type` empty means endpoint; on an endpoint filter the gateway-only fields are
reset to empty; `scanners` is accepted as an alias of `guardrails` and echoed back;
refusals name the cause (`model id "…" must be provider/model`, `provider of model …
does not exist`, `model … does not exist`, `MCP server … does not exist`, `MCP bundle …
does not exist`, `limit … does not exist`, `group … does not exist`, `guardrail … does
not exist`). Deleting a filter checks nothing. Events: **Filter created / updated /
deleted** (`filter.*`; meta includes `type` and the counts of guardrails, agents, models,
limits, mcp, gateways).

`/effective` is what the gateway asks per user; use it with an admin token to see which
gateway filters (or, with `type=endpoint&peer=`, which endpoint filters) apply to someone,
before touching anything.

---

## 4. Design patterns

| Goal | Filter |
|---|---|
| Visibility first (devices) | endpoint; groups `All`, all OSs; Agents = the AI apps in use; guardrails in report mode |
| Developers with IDE agents | endpoint; group `developers`; Agents: Cursor, VS Code, Claude Desktop, the terminal shells if CLI agents are steered; guardrails for secrets and PII in block |
| Finance browser AI use | endpoint; group `finance`; OS **Browser** (the extension, signed in by each user; add the desktop OSs with the browser executables in Agents only where the desktop client should inspect the browser instead — then the extension stands down); PII redaction + prompt-injection block |
| Servers/agents enrolled with setup keys | endpoint; group from the setup key's auto-groups; OS Linux (hooks/SDK path) |
| Everyone may use approved models through the gateway | gateway; group `All`; Models = the approved provider's models; Gateways = the published address; a monthly spend Limit; the baseline guardrails |
| A team with more | a second gateway filter for its group with the extra models and MCP servers; grants add up, the **lowest** limit still wins, so keep the baseline's limit generous or leave it off the baseline |
| MCP-focused team | gateway; MCP grants and a gateway address, plus the one model the team is meant to use (a gateway filter must grant at least one model); guardrails on tool calls and results |

Precedence when several filters match: endpoint guardrails are merged and evaluated
together, most severe rule first; a block from any wins; an `allow` rule in one filter
never exempts another filter's rule. Gateway grants are the union; limits the lowest.
Keep one baseline filter for `All` and group-specific filters on top, remembering that a
rule bound in the baseline reaches everyone.

---

## 5. Diagnosis — "the filter is not applying"

### 5.1 Endpoint filter, on the device

1. **Device in a filter group and OS?** Peers → device → Assigned Groups; filter → Targets.
   `All` is the only implicit membership.
2. **Filter enabled, type Endpoint, with guardrails bound** (without any, nothing is
   judged and no verdict event appears).
3. **Client connected and synced:** `netzilo status` shows Management Connected; after each
   change the client log shows `Filters applied: N` (and at debug level `Rules updated: N
   loaded, F failed, version=mgmt-sync-…`). `Failed rules: [<id>, …]` names guardrails
   that did not parse: fix each one's YAML. `Failed to load rules into the intake host:
   …` / `Failed to apply filters, will retry on next sync` means the device did not accept
   the update: `netzilo refresh`, then the log again; a restart only after consent
   (`SKILL.md` rule 3).
4. **Traffic reaches the engine:** desktop app path in **Agents** (Windows/macOS; Linux
   needs hooks, the SDK or the proxy env, `10` §3); CLI agent `netzilo hook verify
   --framework=<x>` → ready; browser: the extension, or the browser executable in Agents;
   SDK agent: enrolled with a setup key whose group is in the filter.
5. **Browser filter not applying** (the extension, not the client): the user is in one
   of the filter's groups; the filter's OS list contains **Browser**; the user is signed
   in to the extension (popup: **Protection: Active**, filters count ≥ 1); the extension
   has not stood down for the desktop client (popup status "the desktop client governs
   this browser" — then the client's Agents and inspection decide, `49` §3). Press the
   popup's Refresh after a change; `49` §10 has the full table.
6. **Evidence:** Activity → Events, category AI Edge, filtered by the user or peer: `ai.*`
   events name the filter and rule (source `mitm` from the client, `extension` from the
   browser); the peer's or the browser's behaviour graph (`/api/aidr/…`) proves the
   engine sees traffic. Clean traffic from a current client shows as a session in
   Activity → AI Sessions (point `endpoint`), not as events.

### 5.2 Gateway filter, for a user

1. `GET /api/edge/filters/effective?type=gateway&user=<id>` (admin token) lists what
   applies. Empty → the user's groups match no enabled gateway filter.
2. The filter grants **Models**? The gateway refuses with `no model is granted to this
   user` / `model X is not granted to this user` otherwise.
3. The filter lists a **Gateway** address? Without it the Workplace shows no card.
4. The gateway loaded it: `gateway ai: filters for user <id> …: [<ids>]` in
   `journalctl -u netzilo-aigw`; a policy change reaches the gateway with its next sync
   (seconds), a user is re-checked within `--ai-policy-refresh` (60 s).
5. **Evidence:** `ai.*` events with source `gateway`; the session in Activity → AI
   Sessions; usage in the AI Usage report.

| Symptom | Cause | Fix |
|---|---|---|
| No events at all from a device | §5.1 steps 1–4; or a current client with no rule matching, which reports verdicts only (expected) | as above; check Activity → AI Sessions |
| Events but nothing blocked | guardrails in report mode | change actions |
| Chrome not intercepted although in Agents | path mismatch (env var casing, install dir); another browser | use `%ProgramFiles%\…` and `%LocalAppData%\…` variants |
| Works on Windows, not on Linux | Linux lacks per-app steering | hooks/SDK/proxy env; for the browser, the extension (OS **Browser**) |
| Browser filter ignored | OS list has only desktop values; user not in the groups; not signed in to the extension; stood down for the client | §5.1 step 5 |
| Filter save fails | validation above; a deleted guardrail still referenced | complete the tabs; remove the id |
| Gateway users refused after the filter was saved | the granted provider or model was disabled since, or the filter was saved with no models by an older server | grant an enabled model |
| Workplace shows no card though models work | Gateways tab empty | add the address |
| A user gets more than intended | another filter (the `All` baseline) grants it too; grants are a union | narrow the baseline |
| A user gets less than intended | another filter carries a lower limit | find it with `/effective` and the filters' `limits` |
| Group cannot be deleted | referenced by a filter | edit the filter first |

Events: `filter.created/updated/deleted`; verdicts `ai.allowed/blocked/redacted/redirected/detected` (`ai.allowed` only from hosts that do not record AI sessions).
