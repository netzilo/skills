---
id: '28'
title: Admin Skill — Edge Guardrails (detection rules)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 16220
sections:
- id: '1'
  title: Model
  chars: 2001
- id: '2'
  title: Field reference (Add / Edit Guardrail)
  chars: 1418
- id: '3'
  title: Minimal rule template
  chars: 3580
- id: '4'
  title: Testing with Replay
  chars: 1072
- id: '5'
  title: API
  chars: 858
- id: '6'
  title: Lifecycle procedure
  chars: 803
- id: '7'
  title: Diagnosis
  chars: 2734
- id: '8'
  title: Limits to state before a customer discovers them
  chars: 1881
---
# Admin Skill — Edge Guardrails (detection rules)

**Dashboard:** Edge → **Guardrails** (`/ai-edge/guardrails`). **API:**
`/api/edge/guardrails`, `/api/edge/guardrails/generate`, `/api/aidr/replay`. The older
name **scanners** is kept as an alias: `/api/edge/scanners…` answers the same handlers,
and a filter body accepts `scanners` as an alias of `guardrails`; the activity codes for
the object are `guardrail.created|updated|deleted`.

A guardrail is a YAML rule (Sigma with Netzilo extensions) evaluated on AI traffic. It
does nothing until a **Filter** binds it (`29-edge-filters.md`); the same guardrail runs
in two places depending on the filter's type:

| Bound in | Runs on | Sees |
|---|---|---|
| an **endpoint** filter | the Netzilo client of each device in the filter's groups and OS | LLM prompts and responses of intercepted apps, hooks and the extension; MCP over HTTP from intercepted apps; HTTP requests; semantic events; process and file activity (where the client has those probes) |
| a **gateway** filter | the AI Gateway, per user of the filter's groups | prompts and answers (streamed or not) on the OpenAI chat, Responses and Anthropic Messages surfaces, tool calls a model asks for, every MCP tool call and result through `/mcp/<slug>`; not embeddings or text completions. No process, file or connect contexts: rules needing them are not loaded there |

For deep authoring (Starlark scripts over the behaviour graph, the full field, modifier,
action and builtin reference), load `32-detection-rule-authoring.md`. This file is the
administrator's view: lifecycle, the dialog, testing, diagnosis.

**Public rule library:** `https://github.com/netzilo/aidr-sigma` — rules under
`ai_agent/`, the format specification (`Agent.md`), a linter (`tools/rulelint.py`).
Start there: find a close match, paste it into **Add Guardrail**, adjust, Replay.

---

## 1. Model

- Every guardrail belongs to the account. **There is no catalogue of premium or global
  rules any more**, no Locked badge and no plan gate on guardrails; a server upgraded
  from the earlier release deleted its global rules and dropped their references from
  filters at start (`deleted N global guardrail row(s)`, `filter …: dropped N guardrail
  reference(s) that no longer exist` in the management log). Rules formerly provided
  that way (prompt-injection, secret redaction, PII, path traversal, SSH-key
  exfiltration, system enumeration) are in the public library.
- Table columns are derived from the YAML: **Level** (`level`/`severity`: Critical,
  High, Medium, Low), **Category** (from `tags`: `attack.initial-access` → "Initial
  Access"; technique ids are dropped), **Used by** (the filters that bind it).
- Evaluation: all rules bound to the device (every matching endpoint filter) or to the
  user (every matching gateway filter) are evaluated per event, most severe `level`
  first, then by rule `id`; the most severe matching rule decides and is the one named
  in the event; after a block only `redact` and `execute` rules still run; an `allow`
  rule never overrides a block; position in a list has no effect
  (`32-detection-rule-authoring.md`, "Evaluation Order and Verdicts").
- Verdict events (category AI Edge): **AI allowed** (`ai.allowed`), **AI blocked**
  (`ai.blocked`), **AI redacted** (`ai.redacted`), **AI redirected** (`ai.redirected`),
  **AI detected** (`ai.detected`, a report-only match). Every one carries the rule
  (`rule_name`, `rule_id`), the filter (`filter_name`), the surface (`llm_request`,
  `llm_response`, `tool_call`, `tool_result`, `http_request`, …), the agent, model or
  tool, the source (`mitm`, `hook`, `extension`, `gateway`) and, when a rule matched
  content, the matched excerpt and the content as the chain left it (after redaction,
  at most 8 KB). `34-event-catalogue.md`, `30-activity-reports-and-integrations.md` §1.

---

## 2. Field reference (Add / Edit Guardrail)

Tabs **Guardrail** and **Name & Description**; header icons **Replay** (▶), **Generate
with AI** (✦, shown when a model is approved for Threat Analysis), maximise, close.

| Element | UI text | Notes |
|---|---|---|
| YAML Rule Definition | "Define the guardrail rule in YAML format. Name and description sync automatically." | editor; `title:` ↔ Guardrail Name, `description:` ↔ Description; parse problems shown as "YAML Parse Warning: …" |
| Enable Guardrail | "Use this switch to enable or disable the guardrail." | a disabled guardrail is dropped from every filter's expanded rules on the next sync |
| Guardrail Name / Description | "…This will automatically sync with the YAML rule." | both required; name uniqueness is **not** enforced |
| Generate with AI | "Describe what to detect… (Enter to send)" | streams YAML into the editor; without an approved model: "No AI model is approved for Threat Analysis. Add a provider under Integrations → Artificial Intelligence and approve a model for Threat Analysis." |

Saved fields: `severity` (from `level`/`severity`, default high), `context_type` (from
`context`/`logsource.category`, default `all`), `rule_yaml`, `name`, `description`,
`enabled`. The YAML is not validated by the server; a rule that does not parse fails on
the device (`Failed rules: [<id>]`) or at the gateway (`N failed` in its policy line).

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

`logsource.category` (routing context): `tool_request` (= tool_input + prompt and
sampling requests), `tool_response`, `tool_input`, `tool_output`, `llm_request`,
`llm_response`, `http_request`; semantic `skill_acquired`, `llm_reasoning`,
`external_message`, `file_upload`, `file_download`, `do_automation`, `llm_tool_call`,
`llm_tool_result`; syscall `execute_process`, `connects`, `file_read`, `file_write`,
`file_create`, `file_delete`, `file_rename`, `file_op` (all five); `agent_events` / `all`;
`periodic` (30 s background scripts, must be `execute`).
Actions: `block`, `allow`, `report`, `redact` (`replace` default `[REDACTED]`,
`keep_first`, `keep_last`), `scan` (the built-in prompt classifier when `prompt:` is
empty; an AI judge with the given instruction otherwise; `on_timeout`, `on_error`),
`blockmodel`, `allowmodel`, `replacemodel`, `redirect`, `inject`, `replace`, `execute`
(Starlark; `script`, `on_timeout`, `on_error` — an `execute` rule can also judge with
an LLM or System One, `llm_call()` / `system_one()`, `32`). Default action when omitted: high or
critical → block, else report. `on_error`/`on_timeout` take `block|allow|report` and
**default to allow (fail-open)**; `on_error: block` makes a scan or script rule
fail-closed. Field modifiers: `|contains`, `|startswith`, `|endswith`, `|re`, `|all`,
`|base64`, `|cidr`, `|windash`.

`scan` with an instruction and the built-in classifier both run through management
(`POST /api/ai/scanprompt`; the built-in classifier needs prompt scanning enabled on the
server, the AI judge needs a model approved for **Threat Analysis** under Integrations →
Artificial Intelligence). A scan that cannot run (management unreachable, no approved
model, timeout) is an **error for the rule's `on_error`**, not an allow by default.

Two tested PII templates, prompt direction. The response rule is the same with
`event_type: llm_response` and its own `id`; the API body carries
`"context":["agent_events"]`. Both redact in the prompt as sent and in the answer, on
devices, in the browser extension and at the gateway.

```yaml
title: Redact US social security numbers in prompts
id: 1c2d3e4f-5a6b-4c7d-8e9f-0a1b2c3d4e5f
level: high
logsource: {product: ai_agent, category: agent_events}
detection:
  sel:
    event_type: llm_request
    content|re: '\b\d{3}[-\x{2010}-\x{2015} ]\d{2}[-\x{2010}-\x{2015} ]\d{4}\b'
  condition: sel
action: redact
replace: "[SSN-REDACTED]"
```

```yaml
title: Redact payment card numbers in prompts
id: 2d3e4f5a-6b7c-4d8e-9f0a-1b2c3d4e5f6a
level: high
logsource: {product: ai_agent, category: agent_events}
detection:
  sel:
    event_type: llm_request
    content|re: '\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6(?:011|5\d{2}))(?:[ \x{2010}-\x{2015}-]?\d{4}){3}\b'
  condition: sel
action: redact
replace: "[CARD-REDACTED]"
```

**Patterns that silently fail.** `|re` is RE2: a lookaround, a backreference or a `\u`
escape does not compile, and the rule never fires. The list is in
`32-detection-rule-authoring.md`, "`|re` is RE2 — four things that silently kill a
rule". Read the host's rule load after every save (§7, first row).

---

## 4. Testing with Replay

Replay evaluates a rule against a device's **recorded behaviour graph** without deploying
it.

1. Open the guardrail → ▶ **Replay** ("Test rule "{name}" against a peer's behavior
   graph").
2. **Select a peer…** (only peers with AI data; "No peers with AIDR data" means nothing
   was recorded yet), optionally **Search observations…**, then **Play**.
3. Tabs **Search Results | Replay Results | Output**; the summary counts blocked,
   detected, allowed, errors and observations. Iterate on the YAML until the intended
   observations (and only those) fire.

API: `POST /api/aidr/replay {"scope":"source:<peerId>","since":…,"until":…,"rules_yaml":"…","limit":…}`
(admin or service user; 1 MB of YAML; 90 s). Observations and sessions:
`GET /api/aidr/sessions|graph|observations|detections|search?q=&scope=…`.

Replay runs the rule over recorded observations with the endpoint's contexts; it does
not exercise the gateway. Test a gateway-bound rule with a real request through the
gateway and read the **AI blocked / AI detected** event.

---

## 5. API

```
GET/POST /api/edge/guardrails ; GET/PUT/DELETE /api/edge/guardrails/{id}
GET /api/edge/guardrails/generate  → {"enabled":bool,"providers":[…]}  (428 when no model is approved for Threat Analysis)
POST /api/edge/guardrails/generate {"prompt":"…","current_yaml":"…"}  (event stream; 428 no provider, 422 provider not approved)
```
Body: `{"name":"…","description":"…","severity":"high","context":["tool_input"],"rule_yaml":"…","enabled":true}`
— `severity` one of `low|medium|high|critical` (case-insensitive), `context` a list of
which only the first value is stored. Every `PUT` replaces the whole object: `GET` first.

Deleting a guardrail does **not** check filters: the filters that bound it drop it
silently at expansion, and the next save of such a filter fails with
`guardrail <id> does not exist` until the id is removed from it.

---

## 6. Lifecycle procedure

1. **Draft** in report mode (`action: report`), or generate with AI and review.
2. **Replay** against several peers' observations (different agents, users).
3. **Deploy** by binding the guardrail in a filter for a pilot group — an endpoint
   filter for devices, a gateway filter for gateway users — run 1–2 weeks; review **AI
   detected** events (Activity, category AI Edge) and the **AI Agent Activity** report.
4. **Tighten** (exclusions, anchors) and switch to `block`/`redact`.
5. **Widen** the filter's groups.
6. **Review** monthly: **AI blocked** volumes per rule (Dashboard → Agentic Activity →
   Top Guardrails; Activity filtered by `ai.blocked`); retire noisy rules.
7. **Keep a copy** of every rule in the customer's version control before each edit (§8).

---

## 7. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Rule saved, never fires | not bound (Used by = No Filters); the filter does not match the device or user; wrong `logsource.category` for where the content is; bound in a gateway filter but needs an endpoint-only context (process, file, connect); a more severe rule already blocks the same events, so a lower-severity `report` rule is skipped | bind it; check filter targets and type; Replay to see the real context and payload |
| Fires far too often | broad `contains`; no exclusions | tighten; `excl` selection + `condition: sel and not excl`; report mode |
| Redaction not visible | redaction applies to matched content only; a match longer than about 1 KB in a streamed answer has its start released before the rule sees all of it; a Cursor streamed request is blocked instead of redacted | Replay shows the redaction; check the event's content |
| ✦ button missing / generate returns 428 | no model approved for Threat Analysis | Integrations → Artificial Intelligence → approve one |
| Replay: "No peers with AIDR data" | no device has produced observations yet | generate traffic on a filtered device |
| Blocked call but another rule named in the event | the named rule is the most severe match across all filters (equal severity: lowest rule `id`) | correct the `level` values or narrow the other rule; reordering has no effect |
| `scan` rules slow down the agent | classifier or AI-judge latency (15 s timeout on devices and gateways) | narrow the `detection` first; `on_timeout: report` |
| Device log `Failed rules: [<id>, …]` / gateway log `… N rule(s) loaded, N failed` | those rules do not parse | open each, fix the YAML, save |
| Rule saved but the host reports it failed: client log `Rules updated: n loaded, k failed`, the extension's status (failed rules by name), gateway log `… N failed` | the `\|re` pattern does not compile as RE2: lookaround, a backreference, `\u` | rewrite the pattern (`32-detection-rule-authoring.md`, the RE2 section), save, read the next rule load |
| SSN rule never matches the test data | the pattern excludes the 9xx and 000 ranges test data is made of, or the hyphens in the text are not ASCII (U+2010–U+2015) | use the §3 pattern: open ranges and the separator class `[-\x{2010}-\x{2015} ]` |
| Redaction in the event but not in the page or the answer | an old extension or client renders the original; the event shows what the engine produced | check the host's version (the extension's in its popup, the client's in Peers) and upgrade |
| Filter save fails `guardrail <id> does not exist` | a bound guardrail was deleted | remove it from the filter |

Events: `guardrail.created/updated/deleted`; verdicts `ai.*`.

---

## 8. Limits to state before a customer discovers them

**There is no version history and no rollback.** Editing a rule replaces it; the previous
content is kept nowhere, and the activity record notes only that a change happened. The
working practice: **fetch and save a rule before every edit**, in the customer's own
version control.

**Per-group exemption is done with filters, not with rules.** A rule has no group field,
and an `allow` rule exempts nobody. To exempt a population, give them a filter that does
not bind the rule, and make sure no other filter matching them (a baseline `All` filter,
for example) binds it. To exempt specific traffic for everyone, narrow the rule's own
conditions. Prove every exception with Replay and a live pilot.

**The gateway does not inspect every surface** (`27-ai-gateway.md` §1): prompt, answer
and tool-call rules reach the OpenAI chat, Responses and Anthropic Messages surfaces,
streamed or not (a streamed answer is held about 1 KB behind the model so it can be
redacted); embeddings and text completions are counted, not scanned.

**A script is not checked when the guardrail is saved.** The editor validates the YAML,
not the Starlark in `script:`; a script that fails to parse loads and takes its
`on_error` verdict at run time (`32`, Starlark is not Python). Replay the rule after every
script edit.

**Judge rules cost a model call per match.** Each `llm_call()` and `system_one()` is a
paid round trip through management, run synchronously on the matched call: scope the
detection tightly (an agent, a tool, a context) and let a cheap check or System One
decide before an `llm_call()`.

**Performance is not instrumented for customers.** No overhead figure and no per-rule
timing are exposed. When AI tools feel slow, narrow the rules and move expensive ones to
report mode, and say plainly that no measurement is available.
