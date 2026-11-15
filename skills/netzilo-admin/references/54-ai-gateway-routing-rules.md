---
id: '54'
title: Admin Skill — AI Gateway Routing Rules
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 27650
sections:
- id: '1'
  title: What a routing rule is, and when to use one
  chars: 1545
- id: '2'
  title: The Routing Rules tab
  chars: 1878
- id: '3'
  title: The rule dialog
  chars: 5902
- id: '4'
  title: How the gateway applies rules
  chars: 2313
- id: '5'
  title: Grants, providers and the rules that hold them
  chars: 2302
- id: '6'
  title: 'Records: what a routed request leaves behind'
  chars: 1047
- id: '7'
  title: API
  chars: 5871
- id: '8'
  title: Procedures
  chars: 1335
- id: '9'
  title: Troubleshooting
  chars: 3568
- id: '10'
  title: Not available
  chars: 822
---
# Admin Skill — AI Gateway Routing Rules

**Dashboard:** Edge → Governance, tab **Routing Rules** (`/ai-edge/governance?tab=routing`);
a gateway filter's **Routing** tab. **API:** `/api/edge/routing-rules`,
`/api/edge/routing-rules/stats`, the `routing_rules` field of a gateway filter.
**Who:** owners and admins; regular users see neither the tab nor the rules.

A **routing rule** sends AI Gateway requests that match its conditions to other
providers and models than the one the caller asked for: by model, provider, header,
query parameter or request type, split by weight across one or more **targets**, with
ordered **fallbacks** when the targets fail. The caller keeps calling the model it
knows; the gateway decides where the request goes.

Related files: `27-ai-gateway.md` (the gateway that applies the rules),
`29-edge-filters.md` §2.2 (the gateway filter that carries them),
`45-ai-gateway-providers-and-limits.md` (the providers and models a rule routes to),
`30-activity-reports-and-integrations.md` §1a (the sessions that show what a rule did).

---

## 1. What a routing rule is, and when to use one

A rule on its own does nothing. It applies once a **gateway filter** carries it, and
then only to the users that filter targets. One rule can be carried by several filters.
**Endpoint filters, including those for the browser extension, carry no routing rules**:
routing is something the AI Gateway does, never the device or the browser.

| Goal | What the rule does |
|---|---|
| **Cost** | sends simple or high-volume traffic (one team, one agent, embeddings) to a cheaper model, or splits a share of it there by weight |
| **Data residency** | sends requests marked as regional data (a header such as `x-data-region: eu`) to a deployment in that region |
| **Resilience** | lists fallbacks tried in order when the target answers with an error (500, 503, 429 and the like) and moves a streamed request on when no first token arrives in time |
| **Moving an agent** | sends one agent's requests (Claude Code, recognised by its `User-Agent`) to another model of the same or another provider, without touching the agent's configuration |
| **Local models** | sends a share of traffic to a self-hosted model server (vLLM, Ollama, SGLang) on the customer's own network (`45` §1.1) |

A routed request is still the caller's request: the guardrails of the caller's filters
judge it, the caller's limits count it, and it is recorded under the caller (§6). A rule
can only send a request to models the filters that carry it grant (§5), so routing never
gives anyone a model their filters do not.

---

## 2. The Routing Rules tab

Edge → Governance, tab **Routing Rules**, next to Filters, Guardrails and Limits.
Page text: "Routing rules send gateway requests to other providers and models: by model,
provider, header or request type, split by weight, with fallbacks. Filters apply them to
their users." With no rule yet the page shows **Create Routing Rule**.

| Column | Shows |
|---|---|
| **Priority** | the number the rules are evaluated by, lowest first (§4) |
| **Name** | the rule's name; a chain icon marks a **Chain Rule** ("Chain rule: the rules are evaluated again after this one routes") |
| **Active** | the rule's switch ("Routing rule enabled" / "Routing rule disabled") |
| **Conditions** | the conditions in short form, or **All requests** when it has none |
| **Targets** | each target's model (or **Requested model**) and weight, and "n fallbacks" |
| **Routed (7 days)** | how many requests the rule routed in the last seven days (§6) |
| **Used By** | the filters that carry it, or **No filters** |

**Add Routing Rule** opens the dialog (§3); a row's **Edit** opens it on that rule.
**Delete** asks "Delete “<name>”? Requests it routes go to the model they ask for. This
cannot be undone." and is disabled while a filter carries the rule (its tooltip: "Used by
n filters"); remove the rule from those filters first. Search: "Search by name...".

From a gateway filter, the **Routing** tab ("Route the requests of this filter's users to
other providers and models.") lists the rules the filter carries ("Evaluated by priority;
the first match routes the request.") with **Browse Routing Rules** (pick existing rules)
and **Add Routing Rule** (create one and add it to this filter). An empty tab reads "No
routing rules yet — Requests of this filter's users go to the model they ask for." The
rule is added to the filter when the filter is saved (§5).

---

## 3. The rule dialog

**Create Routing Rule** / **Edit Routing Rule** ("Send matching gateway requests to the
providers and models you choose."), tabs **Conditions | Targets | Fallbacks | Name**.

### 3.1 Conditions

"The requests this rule applies to. Without conditions it applies to all of them."
Choose **Builder** or **CEL**.

**Builder.** A group joins its conditions with **AND** or **OR**; **Add Condition** adds a
condition, **Add Group** a nested group (groups nest at most 3 levels; a group needs at
least one condition). A live CEL preview shows below. Without conditions the dialog reads
"No conditions: the rule applies to every request."

| Field | Operators | Value |
|---|---|---|
| **Model** | equals, does not equal, is in list, is not in list, contains, begins with, ends with, matches (regex) | a model name as the provider's catalogue lists it, typed or picked from the providers' catalogues |
| **Provider** | equals, does not equal, is in list, is not in list, matches (regex), does not exist, exists | providers, shown by name and stored by their **slug** — the value the provider dialog labels **ID** (`45` §1.1) and `GET /api/edge/providers` returns as `slug`, e.g. `anthropic-production`. Never the provider's record `id` (e.g. `db4scbta5gic73bpm1p0`): that is refused with 422 `no provider is named "…"` |
| **Request Type** | equals, does not equal, is in list, is not in list, matches (regex) | Chat Completion, Chat Completion (Streaming), Responses, Responses (Streaming), Text Completion, Text Completion (Streaming), Embeddings, Image Generation, Image Generation (Streaming), Image Edit, Image Edit (Streaming), Image Variation, Speech, Speech (Streaming), Transcription, Transcription (Streaming), Count Tokens, Rerank, Decisions, Video Generation. A streamed request is its own value: "Chat Completion" does not match a streamed chat |
| **Header** | equals, does not equal, contains, begins with, ends with, matches (regex), does not exist, exists | a header name, written in lowercase (it matches the header however the caller capitalises it), and a value; values are compared case-sensitively |
| **Query Parameter** | as Header | a parameter name and a value |

Limits the dialog and the server enforce: at most 50 conditions per rule; a list holds at
most 100 values; a value is at most 1024 characters; a header or parameter name uses
lowercase letters, digits, dots, dashes and underscores, up to 128 characters; names
starting `x-netzilo-` or `x-bf-` are reserved for the gateway; regular expressions
support neither lookarounds nor backreferences. An incomplete condition is highlighted
("Fix the highlighted conditions.") and blocks saving and the switch to CEL.

**CEL.** A hand-written expression over `model`, `provider`, `request_type`, `headers`
and `params` that is true or false, at most 4096 characters. Headers are read by a
constant name: `headers["x-team"] == "data"`, `"x-team" in headers`. The server refuses:

| Refusal | Why |
|---|---|
| `headers must be read by a constant name` | a header name built at run time |
| `header "x-netzilo-…" is reserved: headers starting x-netzilo- or x-bf- belong to the gateway` | reserved names |
| `complexity routing is not available yet` | `complexity_tier` (§10) |
| `<variable> cannot be tested: filters decide who a rule applies to` | `user_id`, `team_id`, `team_name`, `virtual_key_id`, `virtual_key_name`, `customer_id`, `customer_name`: who a rule applies to is the filters' job, never the condition's |
| `<variable> cannot be tested: the gateway keeps no provider budgets or rate limits` | `budget_used`, `tokens_used`, `request`; use Limits (`45` §2) for budgets |
| `CEL condition does not compile: …` / `a CEL condition must be true or false, not …` | syntax or type |
| `a CEL condition is required; leave the builder empty to match every request` | CEL mode with nothing typed |

Switching from CEL back to the builder asks "Switch to the builder? The expression you
wrote is replaced by the builder's conditions."

**Enable Rule** ("Matching requests are routed while the rule is enabled.") sits on this
tab. A disabled rule stays on its filters and routes nothing.

### 3.2 Targets

**Browse Models** picks the targets: a model of a provider, or **Requested model** ("The
model the request names, sent to this provider") to keep the model the caller asked for
and only change the provider. "Requests are spread over the targets by weight; the
weights add up to 100 %."

| Column | Rule |
|---|---|
| **Model** | the target |
| **Weight** | whole percent, 1 to 100; all targets add up to 100 ("Total n %"); targets added together are split evenly, then adjusted by hand |
| **First token timeout** | milliseconds, 0 or empty = **Off**, at most 300000. For a streamed request only: when no first token arrives in that time, the request moves on to the fallbacks |

A rule has 1 to 10 targets; a target is listed once. **Chain Rule** ("After this rule
matches, the rules are evaluated again with the routed provider and model.") lets a
second rule refine where this one sent the request (§4).

### 3.3 Fallbacks

"Tried in order when the targets fail." Pick models with **Browse Models** and order them
with the arrows. A fallback names a model (no **Requested model**); 0 to 10 per rule, each
listed once.

### 3.4 Name

**Name of the Routing Rule** (required, 1 to 255 characters, unique in the account,
placeholder "e.g., Keep EU requests in Azure EU"), **Description** (up to 1000
characters) and **Priority** (0 to 9999; "Rules are evaluated from the lowest number up;
the first match routes the request."). An account holds at most 200 routing rules.

Save errors the dialog shows: "Routing rule name is required", "Weights are whole numbers
from 1 to 100 that add up to 100 %.", "Enter whole milliseconds from 0 to 300000.", and the
server's message for anything else (§5).

---

## 4. How the gateway applies rules

1. **Which rules a request meets.** The gateway knows the caller and the caller's gateway
   filters (`29` §1). The rules it tests are the enabled rules carried by those filters,
   all of them together. A user in several gateway filters gets every rule those filters
   carry. A rule never matches a user of a filter that does not carry it, and a caller
   cannot claim another filter's rules: the gateway sets the caller's filters itself.
2. **In priority order.** Lowest **Priority** first; at equal priority the older rule
   first. The **first** rule whose conditions match routes the request; later rules are
   not consulted, unless that rule is a **Chain Rule**.
3. **Chain Rule.** After a chain rule routes, the rules are evaluated again with the
   routed provider and model as the request's, so a second rule can refine the result
   (for example one rule moves a team to a provider, a second one picks the model there).
4. **Targets.** The request goes to one target, chosen by weight: with 80/20, about four
   in five matching requests go to the first target. A **Requested model** target sends
   the model the caller asked for to that target's provider.
5. **Fallbacks.** When the chosen target fails (an error answer such as 500, 503 or 429,
   or a first token timeout on a streamed request), the fallbacks are tried in order. The
   prompt is judged by the guardrails once; a fallback attempt carries the same verdict.
   A fallback the gateway cannot serve at the moment (its provider disabled) is skipped;
   the rule still routes to its targets.
6. **Guardrails win.** When a guardrail rule changes the model of a request (its
   `replacemodel` action, `32`, Actions), routing rules and fallbacks do not apply to
   that request: the guardrail decided where it goes.
7. **No match.** A request no rule matches goes to the model it asked for, as before.

**When a change takes effect.** Rule and filter changes reach the AI Gateways within
about a minute: gateways pull the rules from management (`GET /api/ai-gateway/routing-rules`)
on every policy change and every `--ai-policy-refresh` (60 s), like every other gateway
setting (`27` §7). A gateway restart keeps the rules. A gateway older than routing rules
applies none: upgrade it (`27` §3.4).

---

## 5. Grants, providers and the rules that hold them

A routed request must be one the gateway may serve, so the server keeps rules, filters
and providers consistent. Every refusal names the rule, the filter or the model.

| Rule | Refusal |
|---|---|
| Conditions name providers by slug | 422 `no provider is named "<value>"` — the value is not a provider's slug (typically the record `id` was used); use `slug` from `GET /api/edge/providers` |
| Targets and fallbacks exist and are **enabled** models of **enabled** providers | 422 `provider <id> does not exist` (typically the slug was used where the record `id` belongs), `provider <name> is disabled`, `<provider> has no model <model>`, `model <model> of <provider> is disabled`, `fallback "…" must be provider/model` |
| Every filter that carries the rule **grants** every target and every fallback (Models tab, `29` §2.2); a **Requested model** target needs the whole provider granted (**All models**, `provider/*`) | 422 `filter "<filter>" does not grant <provider>/<model>, a target of routing rule "<rule>"` (or `… a fallback of …`, or `<provider> (requested model)`). Raised when the filter is saved with the rule, and when the rule is changed while filters carry it |
| A filter cannot drop a grant one of its rules needs | the same 422, on the filter's save: remove the rule from the filter, or change its targets, first |
| A rule carried by a filter cannot be deleted | 412 `routing rule is used by filter(s): <names>` |
| A model a rule targets or falls back to cannot be removed from the provider's catalogue, nor disabled | 412 `model <model> is used by routing rule "<rule>"` |
| A provider a rule targets, falls back to or names in its conditions cannot be deleted | 412 `provider is used by routing rule "<rule>"` |
| Names are unique; an account holds at most 200 rules | 409 `a routing rule named "…" exists`; 412 `an account has at most 200 routing rules` |

**Disabling a whole provider is allowed** — it is the incident off-switch. Its rules
then stop applying until the provider is enabled again, and a rule that targets it cannot
be saved (422 `provider <name> is disabled`) until the provider is back or the targets
change. A filter changed to the Endpoint type loses its routing rules with its other
gateway fields.

---

## 6. Records: what a routed request leaves behind

- **AI usage.** Every routed call is recorded with the rule that routed it, next to the
  model asked for and the model served (`27` §8).
- **Routed (7 days)** in the grid counts those records per rule (`GET
  /api/edge/routing-rules/stats`, §7). It follows the gateway's usage uploads (every
  15 s), so a test request shows within a minute.
- **Sessions.** In a session's **Trajectory** (Edge → Sessions, `30` §1a), a model step a
  rule routed shows **Model** (what served it), **Asked for** (what the caller named,
  when different), **Provider** and **Routed by** (the rule's current name; "A deleted
  routing rule" when it has since been deleted).
- **Activity.** **Routing rule created / updated / deleted**
  (`gateway_routing_rule.created|updated|deleted`, category *Administration*; meta
  `name, enabled, priority, chain_rule, condition` (the CEL), `targets`
  (`<provider record id>/<model>:<weight>`), `fallbacks`). Adding a rule to a filter is a
  **Filter updated** event.

---

## 7. API

Admin token (`SKILL.md` "First things first"; the `nz` helper there). Schemas:
`33-api-request-schemas.md`.

**Two provider identifiers — use the right one.** `GET /api/edge/providers` returns both:

| Identifier | Looks like | Used in |
|---|---|---|
| `slug` (the dialog's **ID**) | `anthropic-production` | a **Provider** condition's `value`, `provider == "…"` in CEL, and the model name clients send (`<slug>/<model>`) |
| `id` (record id) | `db4scbta5gic73bpm1p0` | `targets[].provider_id`, `fallbacks` (`"<id>/<model>"`) and filter grants (`"<id>/<model>"`, `"<id>/*"`) |

A condition written with the record id is refused (422 `no provider is named "<id>"`); a
target or fallback written with the slug is refused (422 `provider <slug> does not exist`).

```
GET/POST /api/edge/routing-rules ; GET/PUT/DELETE /api/edge/routing-rules/{ruleId}
GET /api/edge/routing-rules/stats?days=7        → [{"rule_id","requests"}]   (days 1–90; only rules that routed)
PUT /api/edge/filters/{id}                       → "routing_rules": ["<rule id>", …] on a gateway filter
```

Body (`POST`, and every `PUT`, which replaces the whole rule):

| Field | Rule |
|---|---|
| `name` | required |
| `description` | optional |
| `enabled` | **false when omitted** — a `PUT` without it disables the rule |
| `priority` | 0–9999, lower first |
| `chain_rule` | boolean |
| `condition_mode` | `builder` (default) or `cel` |
| `condition` | builder: `{"id","combinator":"and"\|"or","rules":[…]}`; a condition is `{"id","field","operator","key","value"}` with `field` `model`, `provider`, `request_type`, `headers`, `params`; `operator` `=`, `!=`, `in`, `notIn`, `contains`, `beginsWith`, `endsWith`, `matches`, `null` (does not exist), `notNull` (exists); `key` the header or parameter name; `value` a string, a list for `in`/`notIn`, none for `null`/`notNull`; `provider` values are provider **slugs** (`slug`, never the record `id`); a nested group is an object with `rules`. The server computes `cel_expression` from it |
| `cel_expression` | `cel` mode only |
| `targets` | `[{"provider_id","model","weight","ttft_timeout_ms"}]`; `provider_id` the provider's record `id` (not the slug); `model` empty = **Requested model** |
| `fallbacks` | `["<provider record id>/<model>", …]`, in order |

Which filters carry a rule: the `routing_rules` of `GET /api/edge/filters`. On a filter
`PUT`, an omitted `routing_rules` keeps the filter's rules; an empty list removes them.

**Worked example** — keep EU data in the EU, for the `developers` gateway filter:

1. Find the EU provider's record `id` (for targets and fallbacks), its `slug` (for a
   Provider condition, if you add one) and model names, and the filter:
   ```bash
   nz /edge/providers | jq '.[] | {id, slug, name, enabled, models: [.models[] | select(.enabled) | .name]}'
   nz /edge/filters | jq '.[] | select(.type == "gateway") | {id, name, models, routing_rules}'
   ```
   The filter's `models` must grant the targets and fallbacks below
   (`"<eu-provider-id>/*"`, or each model). To limit the rule to requests for that
   provider, add a condition
   `{"id": "c2", "field": "provider", "operator": "=", "value": "<eu-provider-slug>"}` —
   the slug, not the id.
2. Create the rule:
   ```bash
   nz /edge/routing-rules -X POST --data '{
     "name": "EU data stays in the EU",
     "description": "Requests marked x-data-region: eu go to the EU deployment",
     "enabled": true, "priority": 0, "chain_rule": false,
     "condition_mode": "builder",
     "condition": {"id": "root", "combinator": "and", "rules": [
       {"id": "c1", "field": "headers", "operator": "=", "key": "x-data-region", "value": "eu"}]},
     "targets": [{"provider_id": "<eu-provider-id>", "model": "gpt-5.1-mini", "weight": 100, "ttft_timeout_ms": 4000}],
     "fallbacks": ["<eu-provider-id>/gpt-5.1"]
   }' | jq '{id, name, enabled, cel_expression}'
   ```
3. Add it to the filter: read the filter, add the id, write the whole filter back, read
   the answer:
   ```bash
   FILTER=<filter-id> RULE=<rule-id>
   nz /edge/filters/$FILTER \
     | jq --arg r "$RULE" '.routing_rules = ((.routing_rules // []) + [$r] | unique)' \
     | nz /edge/filters/$FILTER -X PUT --data @- | jq '{name, models, routing_rules}'
   ```
   A 422 here names the grant the filter is missing (§5).
4. After a minute, send a test request as a member of that filter (§9) and read the count:
   ```bash
   nz '/edge/routing-rules/stats?days=1' | jq --arg r "$RULE" '.[] | select(.rule_id == $r)'
   ```

**Other conditions and targets** (the `condition` / `targets` / `fallbacks` part only):

```json
{"condition_mode":"builder","condition":{"id":"root","combinator":"and","rules":[]},
 "targets":[{"provider_id":"<anthropic-id>","model":"claude-sonnet-4-6","weight":80},
            {"provider_id":"<anthropic-id>","model":"claude-haiku-4-5","weight":20}]}
```
An 80/20 split of every request of the filter's users. Add a condition (for example
`request_type` `in` the chat values) to narrow it.

```json
{"condition_mode":"cel","cel_expression":"headers[\"user-agent\"].contains(\"claude-cli\")",
 "targets":[{"provider_id":"<anthropic-id>","model":"claude-haiku-4-5","weight":100}]}
```
Claude Code's requests to a cheaper Anthropic model: Claude Code sends a `User-Agent`
starting `claude-cli/`. The filter must grant the target model.

```json
{"condition_mode":"builder","condition":{"id":"root","combinator":"and","rules":[
   {"id":"c1","field":"model","operator":"=","value":"gpt-5.1"}]},
 "targets":[{"provider_id":"<openai-id>","model":"","weight":100,"ttft_timeout_ms":5000}],
 "fallbacks":["<azure-id>/gpt-5.1","<openai-id>/gpt-5.1-mini"]}
```
A fallback chain: the requested model at OpenAI, then the same model at Azure, then a
smaller model. The filter must grant all of OpenAI (`<openai-id>/*`) for the **Requested
model** target.

---

## 8. Procedures

**Create a rule and apply it to a team.**

1. Check the target models exist and are enabled under Edge → Providers (`45` §1).
2. Check the team's gateway filter grants them (Models tab); add them if not.
3. Edge → Governance → **Routing Rules** → **Add Routing Rule**: Conditions (or none),
   **Enable Rule**; Targets (weights, first token timeout); Fallbacks; Name and Priority.
   Save.
4. Edge → Governance → Filters → the team's gateway filter → **Routing** → **Browse
   Routing Rules** → pick the rule → save the filter. (Or start from the filter's Routing
   tab with **Add Routing Rule**.)
5. Wait a minute, send a test request, and read **Routed by** in the session (§9).

**Take a rule out of service.** Switch **Active** off in the grid (it stays on its
filters and routes nothing), or remove it from a filter's Routing tab for that filter
only. To delete it, remove it from every filter first.

**Change the order.** Lower the **Priority** of the rule that must win. Two rules at the
same priority are evaluated oldest first; give them distinct numbers rather than relying
on that.

**Incident: a provider is failing.** Disable the provider (Edge → Providers): its rules
stop applying until it is enabled again. Better before an incident: give the rules that matter a fallback on another provider.

---

## 9. Troubleshooting

**Verify a rule with one request.** As a user the filter targets (their gateway token,
`47` §2), send a request the rule should match, for example with the header of the
worked example:

```bash
curl -sS https://<gateway>/v1/chat/completions \
  -H "Authorization: Bearer <user's gateway token>" -H 'Content-Type: application/json' \
  -H 'x-data-region: eu' \
  -d '{"model":"<provider slug>/gpt-5.1","messages":[{"role":"user","content":"Say hi"}]}'
```

Then open the user's latest session in Edge → Sessions: the step's **Routed by** names the
rule, **Model** the target. Within a minute **Routed (7 days)** counts it.

| Symptom | Cause | Fix |
|---|---|---|
| Rule never routes; **Routed (7 days)** stays 0 | no filter carries it (**Used By**: No filters); the filter that carries it is an endpoint filter (endpoint and browser filters have no Routing tab) or disabled; the user is in none of that filter's groups | add it to the user's **gateway** filter; check `GET /api/edge/filters/effective?type=gateway&user=<id>` (`29` §5.2) |
| Rule is carried but does not route | the rule is disabled (**Active** off); a rule with a lower Priority (or the same priority and older) matches first and is not a Chain Rule; the conditions do not match the request (a header value differing in case, a streamed request against a non-streaming Request Type, a Model value written with the provider slug in front: the model is compared without it) | switch it on; read the grid by Priority and the conditions of the rules above it; test the condition values against the request |
| Changed a rule, the old behaviour continues | propagation: gateways apply changes within about a minute | wait a minute, send the test request again |
| Rule stopped applying | a target's provider was disabled (§5); the gateway logs `gateway ai: routing rule "<name>" not applied: provider … is not served by this gateway yet` or `… model … of … is not enabled` (`journalctl -u netzilo-aigw`, `27` §9.2) | enable the provider, or point the rule elsewhere |
| A request a guardrail changed the model of ignores the routing rules | expected: guardrails win (§4) | — |
| No rule applies on one gateway, others route | that gateway is older than routing rules; its log says `gateway ai: routing: management has no routing rules` when management is the old one | upgrade the gateway or management (`27` §3.4, `02-server-operations.md`) |
| Saving a filter fails: `filter "…" does not grant …, a target of routing rule "…"` | the filter carries a rule whose target or fallback it does not grant, or the save removes such a grant | grant the model (or the whole provider for a Requested model target), or remove the rule from the filter |
| Cannot delete a rule (button disabled, 412) | filters carry it | remove it from those filters first |
| Cannot remove or disable a model, or delete a provider (412 `… is used by routing rule "…"`) | a rule targets it, falls back to it or names the provider in its conditions | change or delete that rule first; to stop a provider at once, disable it instead |
| Fallbacks never used | the target answered; a first token timeout applies to streamed requests only; the fallback's provider is disabled | check the session; set a timeout; enable the provider |

**Before escalating:** the rule (`GET /api/edge/routing-rules/{id}`), the filter
(`GET /api/edge/filters/{id}`), the user's effective gateway filters, the test request
(no token) with the time it was sent, the session id, and the gateway's `gateway ai:
routing` log lines.

---

## 10. Not available

- **Routing by the request's complexity** (send simple prompts to a small model and hard
  ones to a large one) is not available yet; a condition on `complexity_tier` is refused
  ("complexity routing is not available yet"). When it comes, the classifier will be one
  of the models defined under Integrations → Artificial Intelligence and approved for
  **Log Analysis** (`30` §4a).
- **Adaptive routing** (choosing targets from measured latency or error rates) is not
  available; weights are fixed and fallbacks are the way to react to failures.
- **Routing on devices or in the browser**: none; routing rules are an AI Gateway
  feature (§1).
- **Per-user conditions**: a condition cannot name a user or a team; put those users in a
  group and carry the rule on a gateway filter for that group.
