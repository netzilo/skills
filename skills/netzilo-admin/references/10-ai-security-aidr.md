---
id: '10'
title: Netzilo — AI Security (AIDR) Administration
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 42668
sections:
- id: '1'
  title: Architecture in one page
  chars: 4228
- id: '2'
  title: Rollout runbook
  chars: 3822
- id: '3'
  title: Client-side mechanics you must know when troubleshooting
  chars: 4273
- id: '4'
  title: Coding-agent hooks (`netzilo hook`)
  chars: 2869
- id: '5'
  title: SDK for custom agents
  chars: 4658
- id: '6'
  title: Browser extension and Enterprise Browser
  chars: 4866
- id: '7'
  title: The AI Gateway and MCP
  chars: 2696
- id: '8'
  title: Writing and testing rules (Guardrails)
  chars: 3571
- id: '9'
  title: Troubleshooting
  chars: 6424
- id: '10'
  title: Reporting and evidence
  chars: 1337
- id: '11'
  title: Constraints to disclose early
  chars: 3289
---
# Netzilo — AI Security (AIDR) Administration

**Audience:** an AI operator deploying and running Netzilo's AI Detection & Response
features for a customer: governing coding agents, desktop AI apps, custom agents (SDK)
and browser AI use on devices; routing agents' model and MCP traffic through the
Netzilo AI Gateway; authoring and testing guardrails; and troubleshooting TLS
inspection.

Self-hosted servers run as Enterprise. On Netzilo Cloud the Edge pages are available to
the account; an upgrade prompt on one of them is explained in
`31-plans-limits-and-billing.md`. Filters and guardrails themselves carry no plan gate.

---

## 1. Architecture in one page

Every governed AI action feeds a per-device or per-user **behaviour graph** (agents, LLM
calls, tool calls, files, processes, hosts, skills). **Guardrails** (YAML rules,
`28-edge-guardrails.md`) evaluate the actions and the graph and return a verdict: allow,
report (detected), redact, block, redirect to another model, a few HTTP rewrites. The
client (TLS inspection) and the AI Gateway also record each model call and MCP call into
an **AI session** — usage, the conversation after the guardrails, the MCP calls — shown in
Activity → **AI Sessions**, the home page's **Agentic Activity** and the AI Usage report
(`30` §1a, §3). Verdicts are `ai.*` events (Activity, Reports); a clean call is never an
event, it is in the session.

Two enforcement points, one rule language, bound by **Filters** of two types
(`29-edge-filters.md`):

| Enforcement point | Filter type | Governs | Identity |
|---|---|---|---|
| **The Netzilo client on a device** | endpoint (groups × OS, Agents, guardrails) | what runs on the device: desktop AI apps through the TLS-inspecting proxy, coding agents through hooks, custom agents through the SDK, the browser extension; records AI sessions (point `endpoint`) of the traffic it inspects | the device and its user; a setup-key peer (no user) owns its sessions as the peer |
| **The Netzilo AI Gateway** (`27-ai-gateway.md`) | gateway (groups, model grants, limits, MCP grants, gateway addresses, guardrails) | what any agent sends to the organisation's LLM providers and MCP servers **through the gateway**: model access, spend and rate limits, guardrails on prompts, answers and tool calls, usage facts; records AI sessions (point `gateway`) | the Netzilo user, from the token the agent presents or the calling peer |

Ways traffic enters the device-side engine:

| Surface | How it works | Best for |
|---|---|---|
| **Netzilo client (daemon)** | a TLS-inspecting proxy on `127.0.0.1:41339`; per-app traffic is steered into it by the Windows `nwfilter` driver or the macOS system extension for processes listed in an endpoint filter's **Agents**. Parses OpenAI, Anthropic, Gemini, Perplexity, Cursor, Cohere, Bedrock, NVIDIA, Ollama, Telegram, OpenShell and MCP over HTTP; classifies semantic events (skill acquisition, file upload/download, external messages, automation) | desktop AI apps, IDE assistants, any process on a managed machine |
| **Coding-agent hooks** | `netzilo hook` registered in Claude Code / Codex CLI / Gemini CLI / OpenClaw; each tool call, prompt and session event is POSTed to the daemon's `http://localhost:41336/evaluate` before it runs | CLI coding agents, where the hook can *block* a tool call or prompt synchronously |
| **SDK** (`pip install netzilo`, `npm install netzilo`, 5.0) | the whole client embedded in the agent process; `is_allowed()`/`wrapTool()`/framework adapters; optional **advanced governance** (Linux only) adds in-process TLS interception and a syscall probe | agents you build (CrewAI, LangGraph, Strands/AgentCore, LangChain, AutoGen, …) |
| **Browser extension** ("Netzilo Secure Browser") | the same engine built for the browser: governs the web AI apps (ChatGPT signed-in and logged-out, claude.ai, Gemini, Perplexity), direct API calls from pages and MCP over WebMCP, keeps a network log (no bodies) and uploads tab sessions to the behaviour graph; reads the endpoint filters whose Operating Systems include **Browser** (`/api/edge/filters?os=browser`) for the signed-in user's groups; stands down when the desktop client on the device governs the browser (`49-browser-extension-aidr.md`) | browser AI use on managed or BYOD devices, and the only browser enforcement point on Linux |

Central policy objects (Dashboard → **Edge**, in this order): **Providers** (`45`),
**MCP** servers and bundles (`46`), **Guardrails** (`28`), **Limits** (`45`),
**Filters** (`29`). Users meet the gateway side at Workplace → **Agentic Access** (`47`).

What no longer exists, so you never look for it: approved and discovered **Tools**, the
global catalogue of premium rules, posture checks inside filters, the client's local MCP
gateway on port 41338. MCP servers are admin-defined objects served by the AI Gateway.

---

## 2. Rollout runbook

### 2.1 Devices

1. **Prerequisites:** Netzilo client installed and connected on the devices
   (`05-client-install-and-deploy.md`); devices in a group (e.g. `ai-users`).
2. **(Optional) AI provider for the dashboard's own AI features** — the AI judge of
   rules, smart search, the assistant (which also writes rules in the guardrail
   dialog): Integrations → Artificial Intelligence → add a provider and approve a model
   for **Threat Analysis** (the judge) and **Assistant** (the chat panel and the
   guardrail editor's AI panel, `28` §2.1) (`30` §4a). Judge rules
   (LLM-as-judge) use the same providers: `llm_call()` on the Threat Analysis model or a
   model the rule names, and `system_one()` on a **System One** provider (`32`). This is
   not the gateway's provider list (`45`).
3. **Guardrails:** Edge → Guardrails → Add Guardrail; start from the public library
   (`github.com/netzilo/aidr-sigma`) in report mode (`28` §6).
4. **Create an endpoint Filter** (Edge → Filters → Add Filter → Filter Type Endpoint):
   groups `ai-users`, OS (Windows, Darwin…); **Agents**: process paths to intercept,
   wildcards and env vars allowed (`%PROGRAMFILES%\Google\Chrome\Application\chrome.exe`,
   `~/.cursor/**`, `/Applications/Claude.app/**`, `$HOME/.local/bin/claude`; empty = no
   transparent interception, hooks/SDK/extension still work); **Guardrails** (optional
   on the filter, but without one nothing is judged); name; save.
5. **Verify on a device:** the client log shows `Filters applied: N` (debug: `Rules
   updated: N loaded, 0 failed, version=mgmt-sync-…`) with no `Failed rules:` line. Use an
   AI app named in Agents; the session appears in Activity → **AI Sessions** within about
   15 seconds (point `endpoint`), rules
   show as **AI detected / blocked / redacted** events, and the peer has observations
   (`/api/aidr/sessions?scope=source:<peer>`). There are no **AI allowed** events.
6. **Coding agents:** on each dev machine
   `curl -fsSL https://pkg.netzilo.com/download/plugin/install.sh | sh` (Linux installs the
   client if missing; macOS/Windows need the client first), or `netzilo hook install
   --framework=claude-code|codex|gemini|openclaw`, then restart the agent CLI;
   `netzilo hook verify --framework=<x>` → ready.
7. **Custom agents:** developers add the SDK (§5).
8. **Browsers:** an **Enterprise Browser Extension** profile (Endpoint → Profiles) makes
   the client force-install the extension in Chrome/Edge; or deploy via browser policy (§6).
9. **Tune:** run report mode 1–2 weeks, review Activity → Events (category *AI Edge*) and
   Reports → **AI Agent Activity**, then switch high-confidence rules to `block`/`redact`.

### 2.2 Gateway

1. **Install and run the gateway** (`27` §3) with a setup key and a service token; put
   it where callers can reach it: inside the network (tunnel door) and/or published at an
   address (`27` §5).
2. **Providers:** Edge → Providers → Add Provider (type, credential, Refresh models) (`45`).
3. **(Optional) MCP servers and bundles:** Edge → MCP (`46`).
4. **(Optional) Limits:** Edge → Limits (`45` §2).
5. **Create a gateway Filter** (Filter Type Gateway): groups, **Models** (Browse Models;
   at least one required), Limits, **MCP**, **Gateways** (the address users paste — the
   tab is not on the Continue path, open it), Guardrails (optional; recommended), name.
6. **Verify:** `GET /api/edge/filters/effective?type=gateway&user=<id>` lists it;
   `curl <gateway>/v1/models -H "Authorization: Bearer <user token>"` lists the models;
   the Workplace shows the card **Online**; a chat completion appears in Dashboard →
   Agentic Activity after the hourly snapshot (or at once with **Refresh**), and in
   Activity → AI Sessions and the AI Usage report at once.
7. **Tell users** (`47` §6).

---

## 3. Client-side mechanics you must know when troubleshooting

| Item | Value |
|---|---|
| Local ports | 41336 control/hooks HTTP (`/evaluate`, `/ws`), 41337 the same over TLS, 41339 TLS-inspecting SOCKS5/HTTP proxy; macOS extension IPC 17999. Port 41338 (the former local MCP gateway) is no longer used |
| CA | `Netzilo Edge CA` (ECDSA P-256, 10 years) in `/etc/netzilo/netzilo-ca.pem` (`%PROGRAMDATA%\Netzilo\netzilo-ca.pem`); trusted in the OS store at `service install` and every start; `NODE_EXTRA_CA_CERTS` set system-wide; leaf certs 24 h |
| Interception steering | Windows: `nwfilter.exe` (WFP) redirects TCP of matched processes (and their children) to the proxy; macOS: `com.netzilo.NetziloFilter` system extension (needs user approval once); Linux: **no per-app steering** — point apps at `HTTPS_PROXY=http://127.0.0.1:41339` / `ALL_PROXY=socks5h://127.0.0.1:41339`, or use hooks/SDK |
| Skip list | Windows clients fetch `pkg.netzilo.com/download/configs/container.json` (`skip_domains`, e.g. Zoom); pinned/mTLS apps must be excluded there or removed from Agents |
| Parsers | WASM modules hot-loaded hourly from `pkg.netzilo.com/download/llm-parsers` and `…/semantic-classifier` (checksum-verified); an embedded copy ships in the binary; a failed download or checksum keeps the previous version (§9) |
| Rule delivery | management sends the device its **endpoint** filters with guardrails expanded on every sync; the client loads them into its intake host: `Filters applied: N`; a gateway filter never reaches a device |
| Streams | SSE, NDJSON and AWS event streams are inspected before forwarding, event by event: a block ends the stream, a redaction rewrites exactly the events that carried the text, and a redaction that cannot be applied ends the stream (never a partial mix). Cursor's Connect/gRPC responses are block-only, and a redaction on a Cursor request is applied as a block |
| Big and binary bodies | over 10 MB, or opaque binary content: streamed without body inspection; URL, status and header rules still run |
| SigV4 (Bedrock native) | the daemon cannot rewrite a signed body: redactions are suppressed (`redaction SUPPRESSED on SigV4-signed request …`), blocks still work; the embedded SDK re-signs with the agent's own AWS credentials |
| Hook evaluation | `toolCall`, `promptRequest`, `promptResponse` synchronous (can block; a redaction cannot be applied by a hook, so the hook acts only on allow/block); `toolResult`, `sessionStart`, `sessionEnd` fire-and-forget; hooks are **fail-open** by default (`NETZILO_HOOK_POLICY=allow`); set `block` for fail-closed |
| Scan actions | the built-in prompt classifier and the AI judge run through management (15 s timeout on the device); a scan that cannot run is an **error for the rule's `on_error`** (default allow) — not a silent allow, not a block unless `on_error: block` |
| Posture in filters | none; a failing posture check never blocks AI traffic through a filter. Posture gates policies, profiles and published applications (`21`) |
| Verdict events | `ai.blocked` (149), `ai.redacted` (150), `ai.redirected` (151), `ai.detected` (152); `ai.allowed` (148) and `semantic.event` (127) are no longer recorded; `aidr.graph` (129, browser tab sessions only); `aidr.trajectory` (171) is no longer recorded by current servers (older ones announced each new AI session with it; open sessions from Activity → AI Sessions) |
| AI session records | usage and the captured conversation of each model call and HTTP MCP call the proxy inspected, held in memory and sent to management every 15 s, only once management announces it records them (an older server: none). A call sent to the account's AI Gateway is recorded once, by the gateway. Claude Code hooks, SDK runs and the proxy's model calls of the same process land on one session. Not recorded yet: Cursor, Gemini CLI and other Connect-streaming traffic, stdio MCP servers. Cost is 0 on devices |
| MCP tool results | judged text by text (§7) |

To inspect what the engine recorded for a device: `GET /api/aidr/sessions?scope=source:<peerId>`,
`/api/aidr/graph`, `/api/aidr/observations`, `/api/aidr/detections`, `/api/aidr/search?q=`
(admin; `since`/`until`); the **View** window on a peer's page shows the same graph (`28` §4).

---

## 4. Coding-agent hooks (`netzilo hook`)

| Framework | Config written | Events |
|---|---|---|
| `claude-code` (alias `claude`) | `~/.claude/settings.json` (Windows: `%APPDATA%\Claude\settings.json`) | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `SessionStart`, `SessionEnd` (matcher `*`, 10 s) |
| `codex` | `~/.codex/config.toml` (a block between `# <netzilo-hook:codex>` markers) | `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `SessionStart` |
| `gemini` | `~/.gemini/settings.json` | `BeforeTool`, `AfterTool`, `BeforeModel`, `AfterModel`, `SessionStart`, `SessionEnd` |
| `openclaw` | plugin extracted to `~/.netzilo/openclaw-plugin/`, installed with `openclaw plugins install` and configured with `openclaw config set plugins.entries.netzilo.config.*` (needs `openclaw` on PATH) | in-process: `before_tool_call`, `after_tool_call`, `before_agent_run`, `session_end`; `timeout_ms` 200, `timeout_policy` allow|block, a circuit breaker |

Commands: `netzilo hook install|uninstall|verify --framework=<fw> [--url http://localhost:41336/evaluate]`.
Install is idempotent (`registered`, `updated`, `already_current`) and repairs the binary
path after client upgrades; files are written mode 0600. Verify reports `Daemon not
reachable at … — start the Netzilo client.` or `Hook not registered — run 'netzilo hook
install …'` when something is off; its probe is a `__health__` tool call to `/evaluate`.

Runtime env for the hook: `NETZILO_HOOK_URL`, `NETZILO_HOOK_TIMEOUT_MS` (5000),
`NETZILO_HOOK_POLICY` (`allow`|`block`; fail-closed blocks read `Netzilo unavailable
(fail-closed): <err>`), `NETZILO_HOOK_SKIP="Glob Grep LS"`, `NETZILO_HOOK_STATE_DIR`
(`$TMPDIR/netzilo-hook`). Tool output sent for scanning is capped at 8 KB. A block
appears to the agent as the rule's reason, default `Blocked by Netzilo security policy`
(`Prompt blocked by …`, `Response blocked by …`). Claude Code receives a block as
`{"decision":"block"}` with exit code 2; Codex as a permission decision; Gemini as
`{"decision":"deny"}`.

Requirements: the Netzilo client must be running and logged in on that machine (the hook
only talks to `localhost:41336`); the device must be in a group matched by an **endpoint**
filter whose guardrails produce verdicts. Cursor is not a hook framework: it is governed
through the proxy (its executable in Agents).

A coding agent that talks to the **AI Gateway** (Claude Code with
`ANTHROPIC_BASE_URL=<gateway>/anthropic`, Codex with an OpenAI base URL) is identified,
limited, counted and governed there in addition: the gateway filter's guardrails judge
its prompts, answers, the tool calls the model asks for and the tool results sent back
(`27` §1). Keep the hooks for the tool's execution on the machine itself (session
events, commands and files as they run), which the gateway never sees.

---

## 5. SDK for custom agents

Install `pip install netzilo` (extras `netzilo[crewai]`, `[langgraph]`, `[langchain]`,
`[llamaindex]`, `[bedrock]`, `[openai_sdk]`, `[anthropic_sdk]`, `[mcp_client]`, …) or
`npm install netzilo`. Current version **5.0.0** (Python wheels per platform, independent
of the Python version; npm with per-platform optional packages). Linux wheels and
packages ship the probe used by advanced governance.

```python
import netzilo
netzilo.start(server="https://<domain>", setup_key="…", agent_name="orders-agent")   # or pat="nzl_…"
# CrewAI: from netzilo.crewai import govern; govern(config={...}) before kickoff
# LangGraph: netzilo.langgraph.govern(graph, config={...}) before compile(); govern_model(ChatAnthropic(...))
# Strands / Bedrock AgentCore: from netzilo.strands import govern; govern()   # reads NETZILO_* env
# any framework: from netzilo.tools import govern_tool  (decorator) ; blocked → NetziloBlockedError
# raw clients: netzilo.openai_sdk.govern_client(client) / anthropic_sdk / bedrock / gemini / mistral
# direct: netzilo.is_allowed("web_search", args), netzilo.check_prompt(text), netzilo.check_response(text)
netzilo.stop()   # flushes events + graph snapshot
```

```ts
import { start, wrapTool, govern } from "netzilo";
await start({ server: "https://<domain>", pat: "nzl_…", agentName: "orders-agent" });
const safeSearch = wrapTool("web_search", searchFn);
// or: await govern()  — reads NETZILO_SERVER / NETZILO_SETUP_KEY / NETZILO_AGENT_NAME
```

Config keys / env: `server` (`NETZILO_SERVER`, default `https://srv.netzilo.com`;
`management_url` is a legacy alias), `setup_key` (`NETZILO_SETUP_KEY`) or `pat`
(`NETZILO_PAT`), `agent_name` (`NETZILO_AGENT_NAME`, **required**: Python raises
`ValueError`, TypeScript throws and the C/Go entry point returns 2 when it is missing or
blank; there is no hostname fallback — it names the peer and the agent in events,
sessions and AI Gateway records, the embedded client adding `NetziloAgent/<name>` to the
agent's LLM requests' User-Agent), `enable_advanced_governance`
(`NETZILO_ADVANCED`; `govern()` turns it on unless `NETZILO_ADVANCED=0`), `socks5_port`
(auto-picked), `log_level`, `log_file`, `config_path` (`~/.netzilo-sdk/config.json`).
Use a **setup key** whose auto-group is your agents' group so the right endpoint filter
applies. `set_agent_pid(pid)` names the real workload when a supervisor starts the SDK.
An agent that calls its models through the AI Gateway should send its own ID per task in
`x-bf-session-id`, so each task is one session (`27` §1, Sessions); the SDK does not set one,
because one ID per process would merge every task of a long-running agent.

**Breaking change in 5.0.0:** the `mcp_gateway_port` option and function (Python) and
`mcpGatewayPort` (TypeScript) are gone; passing them fails (`TypeError` /
compile error). Governance no longer depends on a local gateway port: the engine always
starts with the SDK, and `Evaluate` is always backed by it. Code written for 4.x that
passed `mcp_gateway_port=0` to "disable governance" must be changed; there is no
disable switch — leave the agent out of any filter instead.

**Advanced governance** (Linux only): adds in-process TLS interception (proxy env + CA
at `~/.netzilo-sdk/netzilo-ca.pem`) and an `LD_PRELOAD` probe for file/process events,
including subprocesses, with a session-end event when the process exits. Limits:
statically linked binaries ignore `LD_PRELOAD`; programs that ignore proxy env variables
bypass interception; Node `fetch` needs `undici`; in containers root is needed to install
the CA. It is turned on by `govern()` by default; turn it off on macOS/Windows.

Known limits: raw-client wrappers do not redact **streaming** responses (prompts are
still gated); LiteLLM integration logs redact verdicts but does not apply them; MCP
clients that cache `call_tool` before `govern_session()` bypass governance; smolagents
sandboxed executors (E2B/Docker) are not governed. Bedrock native Converse (SigV4) is
redacted only in embedded SDK mode; the daemon inspects it read-only. Interactive SSO
login is not supported in the SDK.

Containers: the SDK image pattern sets `NETZILO_SERVER`, `NETZILO_SETUP_KEY`,
`NETZILO_AGENT_NAME`, `NETZILO_LOG_LEVEL`, `NETZILO_PROXY_PORT`, `NETZILO_CONFIG_DIR`,
`NETZILO_EXTRA_NO_PROXY`, `NETZILO_READY_TIMEOUT` (45), and waits for the client to be
ready before starting the agent.

An SDK agent may also call models **through the AI Gateway** (point its OpenAI or
Anthropic client at the gateway with the service user's or the owner's token); the SDK
governs what the agent does, the gateway what it may ask of models.

---

## 6. Browser extension and Enterprise Browser

**Extension ("Netzilo Secure Browser"):** Chrome Web Store id
`kdcpnkonhjcknlkjmjapclhpoamlckji`; Edge Add-ons id `efflopncanncclcfnddajplbnmhoebml`;
Firefox ≥ 128 `netzilo-secure-browser`; Safari through the **Netzilo Secure Browser**
app, App Store `6740890085` (the Safari extension inside it is named **Netzilo Browser**;
enable it under Safari → Settings → Extensions and allow it on all websites). Version
line 5.1.x. Everything below in full, with the diagnosis table, is
`49-browser-extension-aidr.md`.

- Force-install via browser policy: Chrome `ExtensionInstallForcelist` =
  `kdcpnkonhjcknlkjmjapclhpoamlckji;https://clients2.google.com/service/update2/crx`;
  Edge = `efflopncanncclcfnddajplbnmhoebml;https://edge.microsoft.com/extensionwebstorebase/v1/crx`.
  The Netzilo client does this automatically when an **Enterprise Browser Extension**
  profile applies to the device (registry / `/etc/opt/chrome/policies/managed/` /
  `/Library/Managed Preferences/`), and removes it on `service uninstall`.
- **One engine.** The extension runs the same governance engine as the client and the
  AI Gateway; guardrails, the behaviour graph and `ai.*` events are the same. It governs
  the web AI apps (ChatGPT signed-in and logged-out, claude.ai, Gemini, Perplexity),
  direct API calls a page makes to the LLM providers, MCP over WebMCP, and keeps a
  network log of the tab's requests (host, path, method, content type; never bodies).
  Safari has no network log, so rules that `requires: http` are skipped there.
- **Policy:** only **endpoint** filters whose Operating Systems include **Browser**
  (`os: browser`) and whose groups contain the signed-in user; the Agents list is not
  used by the extension. A desktop OS never matches the browser and a browser-only
  filter never reaches a desktop client.
- **Sign-in:** standalone, from the popup's **Login** (the tenant picker at the
  Workplace); the popup shows **Protection: Active / Inactive**. When the desktop client
  on the device governs the browser (browser executable in Agents **and** the AI hosts
  within its inspection), the extension **stands down** after confirming with management
  that the user has a connected device; on Linux the extension is always the browser
  enforcement point.
- **Enforcement:** a redaction replaces the matched text with the rule's `replace`
  token in the prompt as sent and in the answer as shown; a blocked prompt is refused in
  the chat (ChatGPT shows an error with the reason; claude.ai and Gemini show the answer
  "Netzilo Guardrail: Blocked by rule: <rule name>"); conversation history is governed
  again when reloaded. Streamed answers are held about 1 KB behind the model.
- **`fail_mode`** (browser managed policy, key `fail_mode`): `open` (default) passes
  traffic while the engine cannot judge it; `closed` stops such requests on AI endpoints
  only.
- Events: source `extension`, agent = the site, program = the site origin, session = the
  tab's session; Activity reads "<site> in the browser for <user>". Sessions appear
  under `GET /api/aidr/sources` with `kind: browser`, and a **Session snapshot** entry
  announces the first behaviour of a session.
- Popup → Debug tab is the status screen to ask a user for: state, Protection,
  stand-down, rules version, filters count, rules loaded / failed / skipped with names,
  capabilities, active tabs, `unmapped` counters (traffic on AI endpoints the engine
  could not read — the site changed; report to Netzilo).

**Netzilo Enterprise Browser** (Chromium-based, Windows/macOS/Linux/mobile):
`pkg.netzilo.com/download/windows/browser_setup.exe`, `…/macos/{amd64,arm64}/NetziloEnterpriseBrowser_*.dmg`,
Play `com.netzilo.browser2`, App Store `6747919491`. Windows MSI silent install
(per-machine, system context):
`msiexec /i netzilo_enterprise_browser.msi /qn /norestart TENANT=https://<your Workplace address> SHORTCUTNAME="Acme Browser"`.
Add `FORCETENANT=1` to lock the browser to that Workplace (users can no longer pick
another one on the new tab). Pass the properties on **every** install and upgrade (they
are not remembered), and note that the tenant is also the browser's update host — every
switch, the EXE alternative that keeps update checks working, macOS (DMG only, no tenant)
and uninstall: `48-installer-command-lines.md` §13–16.
It bundles the Netzilo client and its own extension; policy comes from **Enterprise
Browser** profiles (domain restrictions, watermark, clipboard, downloads/uploads,
keylogging, screenshot, extension allow/block, encryption). Updates: users check
`chrome://settings/help` (the check reads `<tenant>/download/windows/browser_updates.json`
unless an update URL was set at install, `48` §13.3); **Share Support Data** there zips the logs. Logs in
`<User Data>/logfile.log` and `netzilo.log`.

---

## 7. The AI Gateway and MCP

Everything an agent sends to the organisation's LLM providers and MCP servers can go
through the **Netzilo AI Gateway** instead of straight to the vendor. The gateway holds
the provider keys, identifies the caller as a Netzilo user, applies the user's gateway
filters (model grants, limits, MCP grants, guardrails) and records usage facts.

- Install, run, expose, identity, refusals, logs: `27-ai-gateway.md`.
- Providers (the model catalogue) and Limits: `45-ai-gateway-providers-and-limits.md`.
- MCP servers and bundles, admin and per-user sign-ins, MCP clients that sign in through
  OAuth: `46-ai-gateway-mcp-servers-and-bundles.md`.
- What users see and paste at Workplace → Agentic Access: `47-agentic-access-workplace.md`.
- Usage: Dashboard → Agentic Activity and the **AI Usage** report
  (`30-activity-reports-and-integrations.md` §2–3).

The two enforcement points complement each other: the device engine sees everything a
governed process does (files, processes, every provider it talks to), the gateway sees
every user's model and MCP traffic wherever the agent runs, holds the keys and the
budgets, and is the only place MCP servers are served. Use both for developer
workstations; the gateway alone for CI, servers and unmanaged devices. Both record into
the same AI sessions (`point` `endpoint`, `gateway` or `endpoint,gateway`); a call a
device sends through the gateway is recorded once, by the gateway.

**MCP tool results are judged text by text**, on the client (HTTP MCP answers, JSON-RPC
incl. SSE and batches) and on the gateway (its MCP endpoints, tool execution and tool
calls in a chat agent loop): every text a model or user can read — the content items'
text, embedded resource text, text resource blobs (decoded and re-encoded), resource
links, and every string in `structuredContent` — is a text of its own; images, audio,
binary blobs and shape fields (`type`, `mimeType`) are not judged. A rewrite goes back to
the exact place and the result keeps its shape (`isError`, `structuredContent`, item
order); if the guardrails hand back a different number of texts, the result is refused
(fail closed). Tool-call arguments are judged too, on the request side.

**Files attached to model requests are judged at the gateway only** (`file_attachment`):
documents, images, file parts and files a tool returned, read when a file rule applies to
the user (text, DOCX/XLSX/PPTX, PDF; no OCR). The device engine, hooks, the SDK and the
browser extension do not judge files as files; text a client extracts from a file
(Claude Code reading a CSV, Claude Cowork reading any document) is judged as text.
`50-ai-gateway-file-guardrails.md`.

---

## 8. Writing and testing rules (Guardrails)

For authoring beyond the basics (multi-event Starlark scripts over the behaviour graph,
false-positive discipline, the complete field, modifier, action and builtin reference),
load `32-detection-rule-authoring.md` — it is the dedicated rule-author skill.
`28-edge-guardrails.md` covers what an administrator needs to deploy, test and
troubleshoot rules: the dialog, the minimal template and its vocabulary, testing in
report mode, the lifecycle, the limits (no version history, no per-group exemption inside a rule, which
surfaces the gateway scans).

Format is Sigma with Netzilo extensions (the AI Assistant and the public corpus
`github.com/netzilo/aidr-sigma` use it; the older `match/except` syntax in some docs is
legacy). Evaluation order: most severe `level` first, then rule `id`; the most severe
matching rule decides and is named as the blocker; after a block only `redact` and
`execute` rules still run; an `allow` rule is not an exemption; position has no effect.

Authoring in the dashboard: Edge → Guardrails → **Add Guardrail** → YAML editor (name and
description sync from `title`/`description`); the AI panel beside the editor is the AI
Assistant (shown when a model is approved for Assistant): it writes the whole rule into
the editor from a prose description, in guardrail authoring threads the admin starts or continues,
and the admin reviews and saves (`28` §2.1). Test a new rule in report mode on a pilot
device or user before it blocks (`28` §4).

Lint locally: clone `https://github.com/netzilo/aidr-sigma`,
`pip install pyyaml && python3 tools/rulelint.py <dir>`.

Best practices: report before block; anchor regexes; add exclusions for legitimate use;
keep `scan` rules narrow (latency); scope graph traversals to the current agent; decide
per rule whether a scan failure should block (`on_error: block`).

**Background rules and session verdicts.** A scripted rule can run inline (`mode: sync`,
the default: the call waits for it and it can refuse that call) or in the background
(`mode: async`: the call goes on at once). What an administrator sees from a background
rule:

- its `block` or `report` on the call it judged is an **AI detected** event (marked
  `execute_async`) — that call was already allowed;
- to stop what follows, the rule sets a **session verdict**: the session's later
  matching calls are blocked (or reported) before any rule runs on them, with the
  rule's reason, and each is an **AI blocked** / **AI detected** event naming that rule.
  The verdict lasts until the session ends or its time runs out; there is no dashboard
  control to lift it — the rule lifts it, or the user starts a new session;
- a rule can make the session's next calls wait briefly (at most 2 s, only while
  background work is pending), so a verdict being computed still applies.

Rules share state within a session (`32`, "Session State"), so one rule can follow a
session and another decide on it — for example Netzilo's **Agent Intent Chain** (follows
an agent session in the background and reports when it drifts from what the user asked)
and **Agent Intent Gate** (judges risky tool calls inline against the session and blocks
harmful ones); both need a System One provider. `mode`, `timeout_ms` and the session
builtins need a current engine on the host: an older client, gateway or browser
extension runs a background rule inline and fails a script that uses the session
builtins (it takes its `on_error` verdict). Bind such rules only to filters whose hosts
run a current version.

---

## 9. Troubleshooting

| Symptom | Check | Fix |
|---|---|---|
| No AI events for a device | device in a group of an **enabled endpoint** filter with matching OS? guardrails bound? | fix the filter; `netzilo refresh`; log `Filters applied: N` |
| Desktop app not intercepted (no `[aidr] IngestHTTPRequest` at debug level) | app path in filter **Agents**? Windows `nwfilter.exe` running (`NWFilter: started`)? macOS extension approved (`MacFilter` errors)? Linux (no steering) — app must use the proxy env or hooks | adjust Agents; approve the extension; on Linux set `HTTPS_PROXY`/`ALL_PROXY` for the app |
| App shows TLS/certificate errors | app not using the OS trust store; pinning | Python/curl: `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE=/etc/netzilo/netzilo-ca.pem`; Java `keytool -importcert … cacerts`; Firefox `ImportEnterpriseRoots` policy or `certutil -A -d sql:<profile>`; pinned/mTLS apps → exclude the domain (Netzilo skip list) or remove from Agents |
| `MITM: CA trust install failed` / cancelled dialog | | manual trust commands in `07-client-troubleshooting.md` §9 |
| Hook installed but nothing happens | `netzilo hook verify`; daemon running? device filtered? | start the client; check the filter; `NETZILO_HOOK_POLICY=block` to fail closed while testing |
| Hook blocks everything when the client is down | `NETZILO_HOOK_POLICY=block` set | expected fail-closed; start the client |
| Rule never fires | wrong `logsource.category`; content not where expected; a more severe rule already blocks the same events; a gateway filter with an endpoint-only context | reproduce it in report mode and read the event and host log; `28` §4, §7 |
| Too many false positives | | tighten the regex, add `excl` + `condition: sel and not excl`, switch to `report` |
| A rule reports a call but does not block it, though its script answers `block` | the rule is `mode: async`: a background rule never refuses the call it judged | expected; it must set a session verdict to stop later calls, or run inline (`32`, "Sync and async rules") |
| Calls of one session are blocked by a rule that did not match them | a **session verdict** set earlier in the session by that rule (event reason names it) | expected until the session ends or the verdict expires; the user starts a new session, or the rule is changed |
| Host log `Execute script for rule <id> error: … undefined: session_get` (or another `session_…` name) | the host's engine predates the session builtins | update the client, gateway or extension; until then the rule takes its `on_error` verdict |
| No AI panel in the guardrail dialog | no model approved for Assistant, or not an admin | Integrations → Artificial Intelligence → approve a model for Assistant (`28` §2.1) |
| Browser extension stands down ("the desktop client governs this browser") with the client installed | by design on Windows/macOS when the browser executable is in the filter's Agents and the AI hosts are within the client's inspection; events then come with source `mitm` | nothing, unless the client does not inspect the AI sites: then remove the browser from Agents so the extension governs it (`49` §3, §10) |
| Browser extension **Protection: Inactive** / no browser events | not signed in from the popup; no enabled endpoint filter with OS **Browser** for the user's groups; a failed guardrail | `49` §10; the popup's Debug tab names the cause |
| Bedrock traffic visible but not redacted | SigV4-signed requests cannot be rewritten by the daemon | use SDK embedded mode, or Bedrock's OpenAI-compatible bearer endpoint, or route through the AI Gateway |
| Events with source `extension` and agent = a site (`chatgpt.com`, `claude.ai`, …) | events from the browser extension; Activity reads "<site> in the browser for <user>" | normal |
| An agent gets 400 (`netzilo_policy`)/401/405/429 from the **gateway** | `27` §6 and `47` §5 | |
| A user has no **Agentic Access** tab | no gateway filter grants them an address or MCP server | `29` §5.2 |

**Degradation lines in the client log.** Each means a part of AI governance is running in
a reduced mode. None stops the client; each has a specific fix.

| Log line | What it means | What to do |
|---|---|---|
| `MITM: engine init failed (…) — falling back to HTTP/1.1-only interception` | the HTTP/2-capable inspection engine did not start; traffic is inspected over HTTP/1.1 only; some streaming AI tools that rely on HTTP/2 can stall | restart the client service (with consent); if it returns, collect an anonymized debug bundle (`netzilo debug bundle -A`) and follow `12-escalation-package.md` |
| `WASM [<name>]: download HTTP <code> from <url>` | a parser or classifier update could not be downloaded; the previous version stays | check that the device reaches `pkg.netzilo.com` through its proxy and firewall; retried hourly |
| `WASM [<name>]: checksum mismatch (got …, want …) — skipping update` | the download did not match its published checksum and was discarded | a proxy or content filter altering the download: exempt the host from rewriting |
| `Failed rules: [<rule-id>, …]` (often after `[partition] rule <rule-id>: parse error: …`) | the named guardrails did not load on this device; all others did | open each named guardrail, fix its YAML, save |
| `Failed to load rules into the intake host: <reason>` / `Failed to apply filters, will retry on next sync` | the device did not accept the rule update | `netzilo refresh`, re-check the log; a service restart only with consent |
| `[intake] scanner skipped: …` / `[intake] semantic classifier skipped: …` | a pipeline stage failed to start; that stage's governance is off (fail-open) on this device | restart the client (consent); escalate with the line if it repeats |
| `redaction SUPPRESSED on SigV4-signed request …` | a redact verdict on a Bedrock-signed body could not be applied; the request went through unredacted (a block would have applied) | expected on the daemon; SDK embedded mode or the gateway |
| `[evaluate] hook request missing caller_pid — AIDR graph edge will not be created …` | a hook call without the caller's pid; governed, but not linked in the graph | an old hook registration: `netzilo hook install --framework=<x>` again |

Log prefixes to search for on a device: `MITM:`, `Filters applied`, `Rules updated`,
`Failed rules`, `[intake]`, `WASM [`, `NWFilter:`, `MacFilter:`, `[aidr]`, `[evaluate]`,
`hook`. Gateway log lines: `27` §9.2.

---

## 10. Reporting and evidence

- Dashboard → **Agentic Activity** (Last 24 Hours | Last 7 Days | Last 30 Days; Overview /
  Agents / MCP tabs; Top Teams, Guardrails, Agents, Models, Servers, Tools), recomputed
  hourly or on **Refresh**; its window drills from teams to a single AI session's
  (device or gateway) trajectory, MCP calls and behavior graph, with kill chains marked
  (`30` §3).
- Activity → **AI Sessions**: every recorded session, LLM and MCP tabs, word-prefix
  search, server-side sort (`30` §1a).
- Activity → Events filtered by category *AI Edge*: each `ai.*` event carries the agent,
  surface, model or tool, verdict, rule and filter, source (`mitm`, `hook`, `extension`,
  `gateway`), and the kill chain where a script built one.
- Reports → **AI Agent Activity** (agents, models, servers, top calls, violations per
  user, and per setup-key peer under **Agents**) and **AI Usage** (usage recorded by
  gateways and devices: requests, tokens, cost, latency, MCP calls; by model, user,
  provider, gateway, server, tool).
- API: `GET /api/events/paginated?code=ai.blocked&…`, `GET /api/aidr/…`,
  `GET /api/stats`, `GET /api/ai/activity`, `GET /api/ai/sessions…`,
  `POST /api/reports {report_type: ai_activity|ai_usage}` (`09` §2).
- Stream everything to S3/Min.io for SIEM (Integrations → Event Streaming).

---

## 11. Constraints to disclose early

**Excluding a domain from inspection is not self-service.** Applications that pin
certificates or require mutual authentication break under inspection, and the list of
domains passed through uninspected is maintained centrally by Netzilo, not per tenant.
There is no dashboard or API field for it. The self-service options are to remove the
application from the endpoint filter's Agents, which loses visibility for that
application, or to request the addition. Say this plainly rather than searching for a
setting that does not exist.

**Certificate trust varies by runtime, not by operating system.** Installing the
inspection authority in the system store covers most applications. Runtimes that ship
their own trust store do not read it: Python, Java and Firefox each need their own step,
covered in `07-client-troubleshooting.md`. Applications written in Go normally follow the
system store and need nothing extra.

**Provider coverage is broader than the named list.** Traffic is matched first by
recognised hostname and then, failing that, by the shape of the request body, so many
services with an OpenAI-compatible interface are parsed even when they are not named
anywhere. The way to answer "is this provider supported" is to run the tool once and look
for its activity in the dashboard, not to consult a list.

**The gateway governs by API surface** (`27` §1): model grants and guardrails cover the
OpenAI chat surface, the Responses API and the Anthropic Messages surface (Claude Code,
Claude Desktop), streamed or not; embeddings and text completions are identified,
limited by the virtual key and recorded, not inspected.

**Streamed answers are held back.** On every enforcement point — the client, the
browser extension and the gateway — streamed answer text is released about 1 KB behind
the model so that a match can be redacted before it is shown. Users see a short delay on
long answers, and short answers appear at once at the end. Say this before a user
reports "the AI got slower" after a redaction rule was bound.

**Old clients.** A client from before this release still receives its endpoint filters
with guardrails and enforces them; it reports its verdicts with activity codes the server
no longer knows (`tool.allowed`, `tool.blocked`, `tool.detected`), which the Activity page
shows as an unknown activity and the AI reports do not count. Upgrade clients to see their
AI events again. Their local MCP gateway receives no tool catalogue any more. A client
older than AI session recording records no sessions; the `ai.allowed` events it still
sends are dropped by the server, so its clean calls appear nowhere until it is upgraded.

**Not recorded on devices yet:** Cursor, Gemini CLI and other Connect-streaming traffic,
and stdio MCP servers; device sessions carry tokens (cached and reasoning included) but
cost 0.

**Reading the behaviour graph.** Node colour encodes node type and is consistent across
every graph view. Clustered nodes carry a count badge and appear when several nodes of
the same type share the same parent. A node ringed in grey is the action that triggered
the rule, which is separate from the kill-chain stage colours. Time-window controls and
node and edge type filters sit in the graph toolbar.
