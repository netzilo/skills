---
id: '28'
title: Admin Skill — Edge Guardrails (detection rules)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 26512
sections:
- id: '1'
  title: Model
  chars: 2165
- id: '2'
  title: Field reference (Add / Edit Guardrail)
  chars: 5270
- id: '3'
  title: Minimal rule template
  chars: 3580
- id: '4'
  title: Testing a rule
  chars: 4494
- id: '5'
  title: API
  chars: 2443
- id: '6'
  title: Lifecycle procedure
  chars: 885
- id: '7'
  title: Diagnosis
  chars: 3685
- id: '8'
  title: Limits to state before a customer discovers them
  chars: 1968
---
# Admin Skill — Edge Guardrails (detection rules)

**Dashboard:** Edge → **Guardrails** (`/ai-edge/guardrails`). **API:**
`/api/edge/guardrails`; the dialog's AI panel is the AI Assistant
(`/api/support/sessions?kind=guardrail_authoring`, `/api/support/sessions/{id}/messages`,
§2.1). The older
name **scanners** is kept as an alias: `/api/edge/scanners…` answers the same handlers,
and a filter body accepts `scanners` as an alias of `guardrails`; the activity codes for
the object are `guardrail.created|updated|deleted`.

A guardrail is a YAML rule (Sigma with Netzilo extensions) evaluated on AI traffic. It
does nothing until a **Filter** binds it (`29-edge-filters.md`); the same guardrail runs
in two places depending on the filter's type:

| Bound in | Runs on | Sees |
|---|---|---|
| an **endpoint** filter | the Netzilo client of each device in the filter's groups and OS | LLM prompts and responses of intercepted apps, hooks and the extension; MCP over HTTP from intercepted apps (a result judged text by text, `10-ai-security-aidr.md` §7); HTTP requests; semantic events; process and file activity (where the client has those probes) |
| a **gateway** filter | the AI Gateway, per user of the filter's groups | prompts and answers (streamed or not) on the OpenAI chat, Responses and Anthropic Messages surfaces, tool calls a model asks for, every MCP tool call and result through `/mcp/<slug>`; not embeddings or text completions. No process, file or connect contexts: rules needing them are not loaded there |

For deep authoring (Starlark scripts over the behaviour graph, the full field, modifier,
action and builtin reference), load `32-detection-rule-authoring.md`. This file is the
administrator's view: lifecycle, the dialog, testing, diagnosis.

**Public rule library:** `https://github.com/netzilo/aidr-sigma` — rules under
`ai_agent/`, the format specification (`Agent.md`), a linter (`tools/rulelint.py`).
Start there: find a close match, paste it into **Add Guardrail**, adjust, test (§4).

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
  High, Medium, Low), **Category** (the ATT&CK tactic tags only: `attack.initial-access` →
  "Initial Access"; technique, ATLAS and OWASP ids are not categories; two are
  shown, the rest as "+N" with the list on hover — tag every rule as `32`
  "Tagging" says), **Used by** (the filters that bind it).
- Evaluation: all rules bound to the device (every matching endpoint filter) or to the
  user (every matching gateway filter) are evaluated per event, most severe `level`
  first, then by rule `id`; the most severe matching rule decides and is the one named
  in the event; after a block only `redact` and `execute` rules still run; an `allow`
  rule never overrides a block; position in a list has no effect
  (`32-detection-rule-authoring.md`, "Evaluation Order and Verdicts").
- Verdict events (category AI Edge): **AI blocked** (`ai.blocked`), **AI redacted**
  (`ai.redacted`), **AI redirected** (`ai.redirected`), **AI detected** (`ai.detected`, a
  report-only match). Allowed calls are not events; they are in AI sessions. Every one carries the rule
  (`rule_name`, `rule_id`), the filter (`filter_name`), the surface (`llm_request`,
  `llm_response`, `tool_call`, `tool_result`, `http_request`, …), the agent, model or
  tool, the source (`mitm`, `hook`, `extension`, `gateway`) and, when a rule matched
  content, the matched excerpt and the content as the chain left it (after redaction,
  at most 8 KB). `34-event-catalogue.md`, `30-activity-reports-and-integrations.md` §1.

---

## 2. Field reference (Add / Edit Guardrail)

The dialog is a window: drag it by its title bar, resize it from any edge or corner,
maximise it, or double-click the title bar for the default size; it reopens where it was
left. Tabs **Guardrail** and **Name & Description**; title bar icons: the
**AI panel** toggle (✦, tooltip "Write with the AI Assistant" / "Hide AI panel"; shown to
admins when a model is approved for **Assistant**), maximise, close.

| Element | UI text | Notes |
|---|---|---|
| YAML Rule Definition | "Define the guardrail rule in YAML format. Name and description sync automatically." | editor; `title:` ↔ Guardrail Name, `description:` ↔ Description; parse problems shown as "YAML Parse Warning: …" |
| Enable Guardrail | "Use this switch to enable or disable the guardrail." | a disabled guardrail is dropped from every filter's expanded rules on the next sync |
| Guardrail Name / Description | "…This will automatically sync with the YAML rule." | both required; name uniqueness is **not** enforced |
| AI panel (right of the editor, open by default) | "Describe what you want to detect and the assistant writes the rule into the editor"; suggestions "Detect prompt injection attempts", "Redact social security numbers and credit card numbers" | the AI Assistant chat, writing into the editor (§2.1); absent when no model is approved for Assistant or the user is not an admin |
| Undo (above the editor) | "Undo" | after the assistant wrote the rule: puts back what the editor held before that write; disappears when you edit by hand |

Saved fields: `severity` (from `level`/`severity`, default high), `context_type` (from
`context`/`logsource.category`, default `all`), `rule_yaml`, `name`, `description`,
`enabled`. The YAML is not validated by the server; a rule that does not parse fails on
the device (`Failed rules: [<id>]`) or at the gateway (`N failed` in its policy line).

### 2.1 Writing a rule with the AI Assistant

The dialog's AI panel is the **AI Assistant** (`42-ai-assistant-self-hosted.md`), not a
separate generator.

- **Who and which model.** Shown to owners and admins when a model is approved for
  **Assistant** under Integrations → Artificial Intelligence — the same condition as
  the header's AI Assistant button (`GET /api/ai/capabilities` →
  `capabilities.assistant`). It answers with the Assistant model picked in the
  composer's model picker. **Threat Analysis** plays no part here: it is the AI judge of
  rules at run time (`scan` with a `prompt`, `llm_call()`, `30` §4a).
- **Threads.** The panel opens on a clean thread. **+** starts another; the history
  button lists the admin's earlier guardrail threads to continue or delete. A thread is a
  support session of kind `guardrail_authoring` (`POST /api/support/sessions
  {"kind":"guardrail_authoring"}`, admins only; created when its first message is sent),
  titled by its first message. One thread can cover several guardrails, so "do the same
  for responses" works across rules; a long thread is compacted like any assistant
  conversation, keeping one record per guardrail. **Load earlier messages** pages back
  through it. The threads also appear in the header AI Assistant's history, tagged
  **Guardrail Authoring**; the header assistant does not resume them on its own.
- **It works on what the editor holds now.** Every message from the dialog carries the
  editor's current content (`editor: {guardrail_id, name, yaml}` on
  `POST /api/support/sessions/{id}/messages`; accepted only on a guardrail authoring
  thread — otherwise `422` "editor context belongs to a guardrail authoring session" —
  and only from an owner or admin — otherwise `403` "only admins can author
  guardrails"; over 256 KiB, `422` "the rule in the editor is too large"). It
  goes with that turn only and is never stored in the conversation, so hand edits between
  messages are what the assistant sees next.
- **It writes, the admin saves.** The assistant writes the **complete** rule with its
  `write_rule` tool: the rule replaces the editor content and streams in as it is
  written. While the assistant answers, the editor, the name, description and enable
  fields, **Save** and **Replay** are locked; **Esc** stops the answer instead of
  closing the window. If the answer breaks off in the middle of a rule (the model's
  output limit, an error, the turn's time limit), the editor goes back to the last rule
  written in full, or to what it held before the message. **Undo** above the editor
  puts back what was there before the last write. The assistant never saves: in
  this conversation an API write to `/api/edge/guardrails` (or `/api/edge/scanners`) by
  the assistant is refused. Review the rule, save it, and test it in report mode (§4).
- **One answer at a time.** A message sent while the assistant is still answering in the
  same conversation — a second tab or window with the dialog open — gets `409` and the
  panel says "The assistant is still answering in this conversation in another window.
  Send again once it has finished." The answer holds the conversation for 90 seconds
  past its last sign of life, renewed while it runs: if the server restarts mid-answer,
  the conversation is free again within about a minute and a half.

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

## 4. Testing a rule

A rule is tested live, on a small scope, before it blocks anything:

1. **Lint it.** `python3 tools/rulelint.py <dir>` from the public library
   (`aidr-sigma`) catches a category no host produces, a field the engine never fills,
   a removed builtin and a `|re` pattern RE2 cannot compile; a rule contributed to the
   library also ships with its fixtures (`32-detection-rule-authoring.md`, "Fixtures").
2. **Report mode on a small filter.** Save the rule with `action: report` and bind it in
   a filter for one test device or one test user: an endpoint filter for device
   traffic, a gateway filter for traffic through the AI Gateway.
3. **Reproduce** the traffic the rule must catch and the closest legitimate traffic, on
   that device or through the gateway as that user.
4. **Read the result.** An **AI detected** event (Activity, category AI Edge) names the
   rule and carries the matched excerpt and the content; the legitimate traffic must
   produce none. A scripted rule that failed logs `Execute script for rule <id> error: …`
   on the device or the gateway (`13` §4). What the engine recorded is in the peer's
   behaviour graph (the **View** window from the peer page or an activity entry: graph,
   keyword search, Search Results) and in
   `GET /api/aidr/sessions|graph|observations|detections|search?q=&scope=…`; the
   session itself is in Activity → AI Sessions or behind its **Session trajectory
   available** entry → **View session** (Trajectory, MCP Calls).
5. Iterate until the intended traffic, and only that, fires; then change the action
   (§6).

### 4.1 Replay over recorded sessions

Before step 2, a rule can be replayed over sessions that already happened: what would it
have done, step by step? **Replay** (▶) opens from a guardrail's row in the Guardrails
list (that saved guardrail) and from the guardrail window's title bar (the draft in the
editor). Pick up to **3 guardrails** and up to **3 recorded sessions** (search by user,
agent or model; filter by user, agent and period), then **Replay**. Each session is
replayed alone, in the order it happened, so a rule's script sees the session as it was
at that step. Each guardrail is evaluated on its own; on a step the most severe action
wins. Results show, per session, the steps a guardrail would have acted on, with the
guardrail, its action and reason, the matched text in the step's content, and how many
steps had no recorded content.

Facts to state:

- **Content.** Prompts, answers and tool arguments and results come from what the
  session's source captured (the AI Gateway and current Netzilo clients capture them, as
  the guardrails left them).
  A step blocked live never reached the caller, so its content was not captured and
  replay cannot re-evaluate it; such steps are counted as "without recorded content".
- **Cost.** Script rules that call `system_one()` or `llm_call()` and `action: scan`
  rules make real model calls at real cost, one per step they run on. A judge rule over
  a 100-step session can take more than a minute.
- **No other effects.** In a replay a script's `http()` and `webhook()` calls are
  refused (their result carries the error "replay: scripts make no network calls"):
  nothing is called from the server and a rule's notifications are not sent again. A
  rule whose verdict depends on such a call behaves as its error path. The AI judge is
  real (above).
- **Periodic rules** run every 30 seconds of session time, on the session as it stood
  then; across a quiet gap they run at the gap's first and last tick only.
- **Limits are the caller's job.** The dashboard allows 3 × 3; the API (§5) has no count
  limit. Bounded instead: up to 5,000 steps per session (`max_steps`; a larger value is
  treated as 5,000), 500 reported hits per session (the rest counted in `more_hits`),
  4,000 characters of script output and reason per match, 5 minutes per run (sessions
  not reached come back with an error), 2 runs at a time per account (`429`). A run in
  which no guardrail has a rule that loads is refused (`422`).

**When you (an agent) replay:** confirm with the admin which sessions and guardrails;
start with one to three sessions that contain the behaviour in question and the one to
three guardrails being judged; never replay "all sessions" or a whole period; split a
larger question into several small runs and read each before the next; say before
running when a judge rule is involved, since it costs model calls.

---

## 5. API

```
GET/POST /api/edge/guardrails ; GET/PUT/DELETE /api/edge/guardrails/{id}
POST /api/aidr/replay {"sessions":["session://…"],"guardrails":[{"id":"…"},{"name":"Draft","rule_yaml":"…"}],"max_steps":0}
     → {guardrails:[{id,name,rules,failed_rules,error}], sessions:[{id,found,steps,partial,truncated,duration_ms,hits:[{ts,kind,target,request_id,call_id,turn,action,content,partial,matches:[{guardrail,rule_id,rule_name,action,reason,matched,chain,output,error}]}],more_hits,error}], summary}
     (admins and service users, saved guardrails included; with Accept: text/event-stream: "guardrails", one "session" each as it finishes, "done" {summary}, or "error" {message}; 422 when no guardrail has a rule that loads; session ids from GET /api/ai/sessions; keep runs small, §4.1)
GET  /api/support/sessions?kind=guardrail_authoring   → the caller's guardrail threads, newest activity first (kind= lists ordinary ones; no kind lists all)
POST /api/support/sessions {"kind":"guardrail_authoring"}   → a new thread {id, title, kind, model, created_at, updated_at} (admins only; unknown kind 422)
GET  /api/support/sessions/{id}?limit=40&before=<message id>   → the newest <limit> messages (before that id); has_more when older ones remain (a limit above 200 is capped at 200, a non-positive one is 422; before without limit = a page of 200; neither = the whole conversation)
POST /api/support/sessions/{id}/messages {"text":"…","model":"…","editor":{"guardrail_id":"…","name":"…","yaml":"…"}}
     (event stream; the agent's write arrives as rule_delta {text, reset} while it is written and rule {yaml} when complete; 409 while another turn runs in that conversation)
```
Guardrail body: `{"name":"…","description":"…","severity":"high","context":["tool_input"],"rule_yaml":"…","enabled":true}`
— `severity` one of `low|medium|high|critical` (case-insensitive), `context` a list of
which only the first value is stored. Every `PUT` replaces the whole object: `GET` first.

The earlier rule generator (`GET/POST /api/edge/guardrails/generate`, alias
`/api/edge/scanners/generate`), which streamed YAML from the model approved for Threat
Analysis, has been removed; the AI Assistant writes rules instead (§2.1).

Deleting a guardrail does **not** check filters: the filters that bound it drop it
silently at expansion, and the next save of such a filter fails with
`guardrail <id> does not exist` until the id is removed from it.

---

## 6. Lifecycle procedure

1. **Draft** in report mode (`action: report`), by hand or with the AI Assistant in the
   dialog (§2.1), and review what it wrote before saving.
2. **Test** on one device or user in report mode (§4), with the agents and users it targets.
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
| Rule saved, never fires | not bound (Used by = No Filters); the filter does not match the device or user; wrong `logsource.category` for where the content is; bound in a gateway filter but needs an endpoint-only context (process, file, connect); a more severe rule already blocks the same events, so a lower-severity `report` rule is skipped | bind it; check filter targets and type; reproduce the traffic in report mode and read the device or gateway log (§4) |
| Fires far too often | broad `contains`; no exclusions | tighten; `excl` selection + `condition: sel and not excl`; report mode |
| An MCP result redaction rewrote one item, but a pattern spanning two items did not match | each text of an MCP result (content item, resource text, `structuredContent` string) is judged on its own (`10-ai-security-aidr.md` §7) | write the rule for one text's content |
| Redaction not visible | redaction applies to matched content only; a match longer than about 1 KB in a streamed answer has its start released before the rule sees all of it; a Cursor streamed request is blocked instead of redacted | check the event's content |
| AI panel and ✦ button missing from the guardrail dialog | no model approved for **Assistant** (the header's AI Assistant button is missing too), or the user is not an owner or admin | Integrations → Artificial Intelligence → approve a model for Assistant; a Threat Analysis approval does not enable it |
| AI panel: "The assistant is still answering in this conversation in another window" (`409`) | that thread is answering a message sent from another tab or window | wait for that answer, or close the other dialog, then send again |
| The assistant wrote a rule, but the guardrail did not change | the assistant never saves; the rule is only in the editor | review it, **Save**; **Undo** puts back the previous content |
| Editor does not accept typing; Save and Replay greyed out | the assistant is answering; the editor and the dialog's fields are locked until it finishes | wait for the answer, or press **Esc** to stop it |
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
conditions. Prove every exception on a pilot group in report mode (§4).

**The gateway does not inspect every surface** (`27-ai-gateway.md` §1): prompt, answer
and tool-call rules reach the OpenAI chat, Responses and Anthropic Messages surfaces,
streamed or not (a streamed answer is held about 1 KB behind the model so it can be
redacted); embeddings and text completions are counted, not scanned.

**A script is not checked when the guardrail is saved.** The editor validates the YAML,
not the Starlark in `script:`; a script that fails to parse loads and takes its
`on_error` verdict at run time (`32`, Starlark is not Python). After every script edit,
run the rule once on a pilot and read the host's log for `Execute script for rule <id>
error`.

**Judge rules cost a model call per match.** Each `llm_call()` and `system_one()` is a
paid round trip through management, run synchronously on the matched call: scope the
detection tightly (an agent, a tool, a context) and let a cheap check or System One
decide before an `llm_call()`.

**Performance is not instrumented for customers.** No overhead figure and no per-rule
timing are exposed. When AI tools feel slow, narrow the rules and move expensive ones to
report mode, and say plainly that no measurement is available.
