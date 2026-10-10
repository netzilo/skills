---
id: '45'
title: Admin Skill — AI Gateway Providers, Models and Limits
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 13932
sections:
- id: '1'
  title: Providers
  chars: 6109
- id: '2'
  title: Limits
  chars: 2635
- id: '3'
  title: Procedures
  chars: 1309
- id: '4'
  title: Diagnosis
  chars: 1829
- id: '5'
  title: Limits to state before a customer discovers them
  chars: 768
---
# Admin Skill — AI Gateway Providers, Models and Limits

**Dashboard:** Edge → **Providers** (`/ai-edge/providers`), Edge → **Limits**
(`/ai-edge/limits`). **API:** `/api/edge/providers`, `/api/edge/providers/discover`,
`/api/edge/limits`. **Who:** admins and owners; regular users see neither page.

A **Provider** is a model vendor or a model server the AI Gateway can call, with the
credential the gateway uses and the **catalogue** of models it serves. A **Limit** is a
spend budget, a token quota and/or a request quota, applied per user. Neither reaches a
user on its own: a **gateway filter** (`29-edge-filters.md` §2.2) grants models from
providers and attaches limits to the users of its groups. The gateway
(`27-ai-gateway.md`) pulls providers and keys with its service token and enforces the
grants and limits per request.

**Not the same thing as Integrations → Artificial Intelligence.** That page
(`30-activity-reports-and-integrations.md` §4a, `/api/ai/providers`) holds the AI
provider management itself uses for the dashboard assistant, log analysis and
threat analysis (guardrail generation, prompt scanning). Edge → Providers are what
users' agents talk to through the gateway. The two lists are independent; a key
entered in one is not known to the other.

---

## 1. Providers

### 1.1 Model

| Field | Rule |
|---|---|
| Name | required; unique in the account, case-insensitive (409 `a provider named "…" exists`) |
| Provider type | one of: `openai, anthropic, azure, bedrock, bedrock_mantle, cohere, vertex, mistral, ollama, opencode-go, opencode-zen, groq, sgl, parasail, perplexity, cerebras, deepseek, gemini, openrouter, elevenlabs, huggingface, nebius, xai, replicate, vllm, runway, runware, fireworks, sarvam, wafer, github-copilot, databricks, typesafe` (dashboard labels: OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, AWS Bedrock Mantle, Cohere, DeepSeek, Vertex AI, Mistral AI, Ollama, OpenCode Go, OpenCode Zen, Groq, Parasail, ElevenLabs, Perplexity, SGLang, Cerebras, Gemini, OpenRouter, Hugging Face, Nebius Token Factory, xAI, Replicate, vLLM, Runway, Runware, Fireworks AI, Sarvam AI, Wafer, Databricks, GitHub Copilot, Typesafe) |
| Endpoint (`base_url`) | optional http(s) URL; empty = the vendor's own API. **Required** for `ollama`, `vllm`, `sgl` ("An endpoint is required for this type"). Must be reachable **from the gateway host**, through the gateway peer's routes first and the host network second — not from the admin's browser or from management |
| Credential | fields depend on the type (§1.2); write-only; the API returns `••••` plus the last 4 characters; sending the mask or an empty value keeps the stored value, **unless the type changed** (then the stored credential is discarded) |
| Extra headers | sent with every request to the provider (an organisation id, for example) |
| Skip TLS Verification (`insecure_skip_verify`) | accept the endpoint's certificate unverified: for a local or internal endpoint with its own CA |
| Models | the **catalogue**: `name` (no spaces, unique in the provider, "model name … must not contain spaces", "model … is listed twice"), optional display name, enabled switch. A model's id is `<providerId>/<name>` |
| Enable Provider | "A disabled provider is removed from every gateway; filters that grant its models grant nothing from it." |

Catalogue versus grants: the provider's model list says what **exists**; a filter's
Models tab says what a group **may use**. Removing a model from the catalogue removes
that model from every filter grant that named it; a filter left with no grant still
exists and refuses its users (§3 of `29`). A provider cannot be deleted while a filter
grants anything from it (412 `provider is used by filter(s): …`).

### 1.2 Credential fields per type

| Type | Fields (dashboard label) |
|---|---|
| `azure` | `endpoint` (Endpoint, `https://<resource>.openai.azure.com`), `api_key` (API key) |
| `vertex` | `project_id` (Project ID), `region` (Region, e.g. `us-central1`), `auth_credentials` (Service account JSON) |
| `bedrock`, `bedrock_mantle` | `access_key`, `secret_key`, `region` (e.g. `us-east-1`) |
| `databricks` | `workspace_url` (Workspace URL), `api_key` |
| `github-copilot` | `app_id`, `installation_id`, `repository_id`, `private_key` (Private key, PEM) |
| `ollama`, `vllm`, `sgl` | none (keyless; the endpoint is required instead) |
| every other type | `api_key` |

A missing field is refused with `credential field "…" is required for <type>`.

### 1.3 Add Provider (dialog)

Tabs **Connection | Models | Name & Description**; in create mode **Continue** walks
them in order and stays disabled on Connection until the connection is valid.

1. **Connection:** Provider type, Endpoint, Credential, Extra headers, Skip TLS
   Verification, Enable Provider.
2. **Models:** **Add Model ▾** → **Custom** (type a model name and display name) or
   **Refresh** (ask the provider for its model list, `POST /api/edge/providers/discover`;
   a picker with checkboxes; "Add (n)"). Types that cannot list their models and must be
   typed by hand: `bedrock`, `bedrock_mantle`, `vertex`, `github-copilot`, `replicate`,
   `runway`, `runware`, `sarvam`, `wafer`, `opencode-go`, `opencode-zen`. Picker errors:
   "This provider does not list its models", "Could not list the models".
3. **Name & Description.**

Discovery runs on management (20 s timeout) with the credential typed or stored; its
answers name the cause: `the provider rejected the credential (HTTP 401)`, `the provider
answered HTTP …`, `the answer is not a model list`, `the provider listed no models`, `an
endpoint is required to list the models of <type>`. A self-hosted endpoint must be
reachable from management for discovery and from the gateway host for use; those can
differ.

### 1.4 API

```
GET/POST /api/edge/providers ; GET/PUT/DELETE /api/edge/providers/{id} ; POST /api/edge/providers/discover
```
```json
{"name":"Anthropic production","description":"","enabled":true,"type":"anthropic",
 "base_url":"","credential":{"api_key":"sk-ant-…"},"extra_headers":{},
 "insecure_skip_verify":false,
 "models":[{"name":"claude-sonnet-4-6","display_name":"Claude Sonnet 4.6","enabled":true}]}
```

Every `PUT` replaces the whole object: `GET` first, change one thing, `PUT`, `GET` again.
Keep `credential` out of a `PUT` body (or send the mask) to keep the stored key. The
discover body is the same object plus an optional `id` (the stored credential then fills
empty fields); the answer is `{supported, models[], error?}` — `supported:false` means the
type cannot list models, a provider-side failure comes back as HTTP 200 with `error`.

Events: **Provider created / updated / deleted** (`gateway_provider.created|updated|deleted`;
meta `name, type, enabled, base_url, models_count`, never a credential).

### 1.5 What the gateway does with a provider

The gateway pulls the enabled providers with their enabled models and keys
(`GET /api/ai-gateway/providers`, ETag) at start, every `--ai-policy-refresh` (60 s) and
on every policy change, and applies the difference to its built-in upstream: the first
provider of a type keeps the type's own name there, further ones become `nz-<id>`; a
changed provider is removed and re-added; keyless types get no key. The key is held by
the gateway process and never reaches a caller. The gateway is the only writer of its
upstream's providers.

---

## 2. Limits

### 2.1 Model

| Field | Rule |
|---|---|
| Name | required; unique, case-insensitive (409 `a limit named "…" exists`) |
| Spend (`budget`) | `max_usd` > 0 (US dollars, from the gateway's pricing catalogue), `reset` window |
| Tokens (`tokens`) | `max` > 0, prompt and completion tokens together, `reset` window |
| Requests (`requests`) | `max` > 0, `reset` window |
| `reset` | `hourly`, `daily`, `weekly`, `monthly`, `yearly` (dialog: per Hour / Day / Week / Month / Year, default Month) |
| Enable Limit | "A disabled limit is not applied by the filters that carry it." |

At least one of the three blocks is required ("Switch on a spend budget, a token quota or
a request quota"; API 422 `a limit needs a budget, a token quota or a request quota`).

**Semantics, to state exactly:**

- A limit has **no scope of its own**. It applies to every user of every gateway filter
  that carries it, **each user with their own counters**. There is no team pool.
- When several filters apply to one user, the **lowest value of each kind** wins
  (lowest budget, lowest token quota, lowest request quota, each taken separately).
- Counters live on the gateway, per user **per gateway**: two gateways count
  separately. They **restart** whenever the user's grants or limits change (the gateway
  re-issues the user's virtual key).
- The window resets at its boundary (`1h`, `1d`, `1w`, `1M`, `1Y` in the upstream).
- A limit cannot be deleted while a filter carries it (412 `limit is used by filter(s): …`).

### 2.2 What a user sees when a limit is hit

HTTP 429 or 402 from the gateway with the upstream's governance error (`budget_exceeded`,
`rate_limited`, `token_limited`, `request_limited`); recorded in usage with status
`limited`; reported as an **AI blocked** event (`ai.blocked`, engine `limit`, source
`gateway`, surface `llm_request`, the user as actor, reason = the upstream message). The
Workplace card does not show remaining quota; there is no per-user counter view in the
dashboard. To lift a block before the window ends: raise the limit (restarts counters)
or move the user to a filter without it.

### 2.3 API

```
GET/POST /api/edge/limits ; GET/PUT/DELETE /api/edge/limits/{id}
```
```json
{"name":"Developers monthly","description":"","enabled":true,
 "budget":{"max_usd":200,"reset":"monthly"},
 "tokens":{"max":5000000,"reset":"daily"},
 "requests":{"max":500,"reset":"hourly"}}
```

Blocks not set are omitted in responses. Events: **Limit created / updated / deleted**
(`gateway_limit.*`; meta `name, enabled, budget_usd, budget_reset, tokens_max, tokens_reset,
requests_max, requests_reset`).

---

## 3. Procedures

- **First provider:** Edge → Providers → Add Provider → type, credential, Models →
  Refresh → tick the models → Name → save. Then Edge → Filters → a **gateway** filter →
  Models → **Browse Models** → the models or "All models" of the provider → save. Then
  check `GET /api/edge/filters/effective?type=gateway&user=<id>` lists the filter for a
  member and `GET <gateway>/v1/models` with that user's token lists the models.
- **Private endpoint (Ollama, vLLM, SGLang):** type, Endpoint `http://<host>:<port>`
  (an in-network name `<peer>.netzilo.network` works when the gateway peer has a policy
  to it; a LAN address works when the gateway host reaches it with `--egress public`
  and, for private ranges, `--egress-allow`), no credential; Refresh lists the models.
- **Rotate a provider key:** edit the provider, type the new key, save; the gateway
  applies it at its next refresh (≤60 s) with no user impact; users' counters are kept.
- **Cap a team's spend:** Add Limit (Spend per Month) → the team's gateway filter →
  Limits → Browse Limits → save. Tell the admin the cap is **per user**, not for the team.
- **Give one user more:** put them in an extra filter? No — the **lowest** value wins
  across filters. Instead, remove them from the capped group or raise the limit.

---

## 4. Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Refresh lists nothing / "Could not list the models" | wrong key; endpoint unreachable **from management**; type cannot list | check the error text; type the models by hand (Custom) |
| Models listed but users get 403 `model X is not granted to this user` | no gateway filter grants it; the grant names another provider of the same type; model disabled in the catalogue | `29` §2.2 |
| Users get 403 `no model is granted to this user` | user in no group a gateway filter targets, or the filter grants no model | fix the filter's groups/Models |
| 502 / provider errors through the gateway for one provider | endpoint unreachable **from the gateway host**; TLS (private CA) → Skip TLS Verification or add the CA; wrong `base_url` form (`/v1` is not appended twice) | `journalctl -u netzilo-aigw` shows the upstream error at `--ai-upstream-log-level debug` |
| Provider deleted/disabled, users still see its models in the Workplace | the Workplace card lists what the gateway answered at its last probe (30 s) | wait, or reload |
| Cannot delete a provider / limit (412) | referenced by filters | edit the filters first |
| Limit refuses on the first request | the user's counters carried over from before the limit was lowered? No: changing a limit restarts counters. Check the window (`hourly` with a small `max`) and other filters with a lower value | `GET /api/edge/filters/effective?type=gateway&user=` then each filter's `limits` |
| Costs look wrong | cost is the upstream's pricing catalogue, in USD, at the time of the request; self-hosted models cost 0 | — |

Before escalating: the provider's type and endpoint (no key), the discover error, and
the gateway's `providers …: N provider(s) from management` / `applied to the upstream as …`
lines (`27` §9.2).

---

## 5. Limits to state before a customer discovers them

- **No team or account pool.** Limits are per user; a "department budget" is each
  member's budget.
- **No counter view.** Remaining budget is not shown anywhere; the AI Usage report
  (`30` §2) shows spend after the fact.
- **No cost for local models** and no custom price list; cost comes from the
  gateway's built-in pricing catalogue.
- **Only the OpenAI chat surface is model-gated by Netzilo's own refusal** (`27` §1);
  the Responses and Anthropic surfaces are limited and counted through the virtual key.
- **A key is stored on the server** (write-only through the API, masked in the
  dashboard, clear to the gateway's service token). Treat the gateway's service user as
  holding every provider key.
