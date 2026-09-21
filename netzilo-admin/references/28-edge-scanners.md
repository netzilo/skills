---
id: '28'
title: Admin Skill — Edge Scanners (detection rules)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 10620
sections:
- id: '1'
  title: Model
  chars: 1169
- id: '2'
  title: Field reference (Add / Edit Scanner)
  chars: 1801
- id: '3'
  title: Minimal rule template
  chars: 1328
- id: '4'
  title: Testing with Replay
  chars: 1110
- id: '5'
  title: API
  chars: 664
- id: '6'
  title: Lifecycle procedure
  chars: 576
- id: '7'
  title: Diagnosis
  chars: 1359
- id: '8'
  title: Limits to state before a customer discovers them
  chars: 1497
---
# Admin Skill — Edge Scanners (detection rules)

**Dashboard:** Edge → **Scanners** (`/ai-edge/scanners`). **API:** `/api/edge/scanners`,
`/api/edge/scanners/catalog`, `/api/edge/scanners/generate`,
`/api/peers/{id}/aidr-snapshot/replay`. **Licence:** Enterprise (premium scanners show
`Enterprise subscription required` otherwise).

A scanner is a YAML rule evaluated by the client on AI traffic (LLM prompts/responses,
MCP tool calls, HTTP, semantic events, process/file activity). Scanners do nothing until
bound to devices through a **Filter** (`29-edge-filters.md`). For deep rule authoring
load `32-detection-rule-authoring.md`; this skill is the administrator's view: catalog, lifecycle,
testing, and diagnosis.

**Public rule library:** Netzilo maintains an open Sigma+AIDR corpus at
`https://github.com/netzilo/aidr-sigma` — over a thousand ready-to-use rules under
`ai_agent/`, the authoritative format specification (`Agent.md`), and a linter
(`tools/rulelint.py`). Start there before writing a rule from scratch: find a close
match, paste its YAML into **Add Scanner**, adjust, and Replay it (§4).

---

## 1. Model

- **Premium (global) scanners** — provided by Netzilo, badge **Premium**, read-only,
  cannot be disabled or deleted; locked on non-Enterprise plans (badge **Locked**).
  Current set: Path Traversal Detection (block), PII Detection in Tool Output (redact),
  Prompt Injection Detection (scan), API Key and Secret Redaction (redact), SSH Key
  Exfiltration in Tool Input (block), System Enumeration & CLI Tool Exfiltration (block).
- **Account scanners** — your rules; editable; **Used by** shows which filters bind them.
- Rule fields shown in the table are derived from the YAML: **Level** (`level` or
  `severity`: critical/high/medium/low), **Category** (from `tags`, e.g.
  `attack.initial-access` → "Initial Access"), routing contexts (`logsource.category`).
- Evaluation order: rules in a filter are evaluated per event; the first rule that fires
  with a terminal action (block/allow/redact/report) decides; explicit `allow` rules
  should come first.
- Verdict logging: `tool.blocked` (with `rule_name`, `filter_name`, scanned text),
  `tool.detected` (report-only match), `tool.allowed`, `semantic.event`, `aidr.graph`
  (session snapshot).

---

## 2. Field reference (Add / Edit Scanner)

Tabs **Scanner** and **Name & Description**.

| Element | UI text | Notes |
|---|---|---|
| YAML Rule Definition | "Define the scanner rule in YAML format. Name and description sync automatically." | CodeMirror editor; `title:` ↔ Scanner Name, `description:` ↔ Description; parse problems shown as "YAML Parse Warning: …" |
| Enable Scanner | "Use this switch to enable or disable the scanner." (Premium: "Premium scanners cannot be disabled.") | |
| Replay (▶) | "Replay this rule against a peer snapshot" (disabled: "Write a rule before replaying" / "Fix YAML errors before replaying") | opens **Replay Scanner** (§4) |
| AI (✦) | "Generate with AI" | only when an OpenAI/Anthropic integration exists; describe the detection in prose, the YAML streams into the editor; error "No AI integration configured. Please add an OpenAI or Anthropic integration in Settings → Integrations." |
| Scanner Name / Description | "Set an easily identifiable name for your scanner. This will automatically sync with the YAML rule." | both required |

Validation on save (in order): "Scanner name is required", "Description is required",
"YAML rule is required", "YAML syntax error: …", "YAML rule must contain at least one
document". Saved fields: `context` (from `context:` or `logsource.category`, default
`all`), `severity` (from `level`/`severity`, default `high`), `categories` (from tags).

Table: Name (dot + description), Active toggle (Premium disabled), Level pill, Category,
**Used by** (No Filters / n Filters; click → Filters), Edit (Premium: "Premium scanners
cannot be edited"), Delete (disabled when used or Premium). Filter by severity.

**Browse Scanners** (from a filter): catalog with checkboxes; Locked rows cannot be
added; "Add Scanners (n)".

---

## 3. Minimal rule template

```yaml
title: Block obvious prompt-injection phrases
id: 7d3a2f1e-6b2c-4c1b-9d5e-0a1b2c3d4e5f
status: experimental
level: high
description: Blocks tool inputs containing instruction-override phrases.
logsource: {product: ai_agent, category: tool_input}
detection:
  sel:
    content|contains:
      - "ignore all previous instructions"
      - "you are now DAN"
  condition: sel
action: block
tags: [attack.initial-access]
```

`logsource.category` values: `tool_request`, `tool_response`, `tool_input`, `tool_output`,
`llm_request`, `llm_response`, `http_request`; semantic `skill_acquired`, `llm_reasoning`,
`external_message`, `file_upload`, `file_download`, `do_automation`, `llm_tool_call`,
`llm_tool_result`; syscall `execute_process`, `connects`, `file_read`, `file_write`,
`file_create`, `file_delete`, `file_rename`, `file_op`; `agent_events` / `all`; `periodic`.
Actions: `block`, `allow`, `report`, `redact` (`replace`, `keep_first`, `keep_last`),
`scan` (ML/AI classifier; `prompt:`, `on_timeout`, `on_error`), `blockmodel`,
`allowmodel`, `replacemodel`, `redirect`, `inject`, `replace`, `execute` (Starlark).
Default action when omitted: high/critical → block, else report. Field modifiers:
`|contains`, `|startswith`, `|endswith`, `|re`, `|all`, `|base64`, `|cidr`, `|windash`.

---

## 4. Testing with Replay

Replay evaluates a rule against a **recorded session snapshot** of a real device, so you
see what it would have done without deploying it.

1. Open the scanner → ▶ **Replay** (or on a peer page → Available Snapshots → View
   session snapshot → **Run Scanners**).
2. Choose **Peer** (only peers with AI data are listed; "No peers with AIDR data" means
   nothing was recorded yet) and **Snapshot** (latest first).
3. Optionally search events ("Search events…") and click graph nodes/edges to inspect
   payloads (Details → Copy JSON).
4. **Play**. Results: chips `blocked`, `redacted`, `detected`, `unchanged`; per event the
   diff `new_block`, `new_redact`, `new_detection`, `new_allow`, `new_report`,
   `unchanged`; "No detections — all events passed unchanged" means the rule never
   matched that snapshot.
5. Iterate on the YAML until the intended events (and only those) fire.

API: `POST /api/peers/{peerId}/aidr-snapshot/replay {"run_id":"…","rules_yaml":"…"}`;
snapshots `GET /api/peers/{peerId}/aidr-snapshot`; peers with data `GET /api/peers?has_aidr_graph=true`.

---

## 5. API

Prefer this over dashboard clicking when you hold an API token: read the current
object, change one field, write it back, then re-read to verify. Ask the customer for a
token as described in `00-operator-playbook.md` §4.1. Remember every `PUT` replaces the
whole object — always `GET` first.

```
GET/POST /api/edge/scanners ; GET /api/edge/scanners/catalog ; GET/PUT/DELETE /api/edge/scanners/{id}
GET /api/edge/scanners/generate  → {"enabled":bool}
POST /api/edge/scanners/generate {"prompt":"…","current_yaml":"…"} (streamed)
```
Body: `{"name":"…","description":"…","severity":"high","context":["tool_input"],"rule_yaml":"…","enabled":true}`.

---

## 6. Lifecycle procedure

1. **Draft** in report mode (`action: report`) — or generate with AI and review.
2. **Replay** against several snapshots (different agents/users).
3. **Deploy** by adding the scanner to a filter for a pilot group; run 1–2 weeks; review
   `tool.detected` events (Activity, category AI Edge) and the AI Activity report.
4. **Tighten** (exclusions, anchors) and switch to `block`/`redact`.
5. **Widen** the filter groups. Keep premium scanners enabled in every filter.
6. **Review** monthly: `tool.blocked` volumes per rule; retire noisy rules.

---

## 7. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Rule saved, never fires | not in any filter (Used by = No Filters); filter does not match the device; wrong `logsource.category` for where the content is; an earlier `allow` in the same filter | bind it; check filter targets; Replay to see the real context/payload |
| Fires far too often | broad `contains`; no exclusions | tighten; add `excl` selection and `condition: sel and not excl`; report mode |
| Redaction not visible | redaction applies to matched content only; streaming responses from some SDK wrappers are not redacted | Replay shows `new_redact`; check the event's scanned text |
| AI button missing | no AI integration | Integrations → Artificial Intelligence |
| Replay: "No peers with AIDR data" | no device has produced a session snapshot yet | generate traffic on a filtered device; wait for `aidr.graph` events |
| Cannot delete | Premium, or used by filters | remove from filters |
| Locked in catalog | plan | Enterprise |
| Blocked call but wrong rule named in the event | first firing rule wins across all scanners in the filter | reorder/allow explicitly |
| `scan` rules slow down the agent | AI classifier latency | narrow the `detection` upstream; use `on_timeout: report` |

Events: `scanner.created/updated/deleted`, `tool.blocked`, `tool.detected`, `semantic.event`.

## 8. Limits to state before a customer discovers them

**There is no version history and no rollback.** Editing a rule replaces it. The previous
content is not retained anywhere, and the activity record notes that a change happened
without storing what it was. The version field on a scanner is free text that you
maintain yourself; nothing sits behind it.

The consequence is a working practice, not a setting: **fetch and save a rule before
every edit.** Keep the saved copies in the customer's own version control. That file is
the only way back to a working rule.

**Premium rule sensitivity cannot be tuned.** Catalogue rules that use model-based
detection run at a fixed confidence threshold built into the client. It is not exposed in
the rule, the dashboard or the API. If such a rule produces false positives, the levers
are to unbind it from the filter covering the affected group, or to write a custom rule
with narrower matching. Editing the premium rule is refused. Do not promise a sensitivity
setting.

**Per-group exemption is done with filters, not with rules.** A rule has no group field.
To exempt a population, give them a filter that does not bind that rule.

**Performance is not instrumented for customers.** There is no published overhead figure
and no per-rule timing exposed in the product. When users report that AI tools feel slow,
narrow the rules and move expensive ones to report mode, and say plainly that no
measurement is available rather than quoting a number.
