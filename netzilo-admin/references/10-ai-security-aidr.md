# Netzilo — AI Security (AIDR) Administration

**Audience:** an AI operator deploying and running Netzilo's AI Detection & Response
features for a customer: governing coding agents, desktop AI apps, custom agents (SDK),
browser AI use, and MCP tool access; authoring and testing detection rules; and
troubleshooting TLS inspection.

Licensing: Edge Tools, Scanners and Filters require an **Enterprise** subscription
(self-hosted servers run as Enterprise/MSP). Premium (global) scanners show
`locked_reason: "Enterprise subscription required"` otherwise.

---

## 1. Architecture in one page

Every governed AI action produces an **event** and updates a per-device **behaviour
graph** (agents, LLM calls, tool calls, files, processes, hosts, skills). Rules
(**Edge Scanners**) evaluate events and the graph and return a verdict: allow, report,
redact, block (and a few HTTP/model-rewrite actions). Verdicts and events flow to the
dashboard (Activity, Reports, Dashboard → AI Activity, peer **Session Snapshots**).

Three ways traffic enters the engine:

| Surface | How it works | Best for |
|---|---|---|
| **Netzilo client (daemon)** | the daemon runs a TLS-inspecting SOCKS5/HTTP proxy on `127.0.0.1:41339`; per-app traffic is steered into it by the Windows `nwfilter` driver or the macOS system extension for processes listed in an Edge Filter's **Agents**. Parses OpenAI, Anthropic, Gemini, Perplexity, Cursor, Cohere, Bedrock, NVIDIA, Ollama, Telegram, and MCP over HTTP; classifies semantic events (skill acquisition, file upload/download, external messages, automation) | desktop AI apps, IDE assistants, any process on a managed machine |
| **Coding-agent hooks** | `netzilo hook` registered in Claude Code / Codex CLI / Gemini CLI / OpenClaw; each tool call and prompt is POSTed to the daemon's `http://localhost:41336/evaluate` before it runs | CLI coding agents, where the hook can *block* a tool call synchronously |
| **SDK** (`pip install netzilo`, `npm install netzilo`) | the whole client embedded in the agent process; `isAllowed()`/`wrapTool()`/framework adapters; optional **advanced governance** (Linux only) adds in-process TLS interception and syscall probes | agents you build (CrewAI, LangGraph, Strands/AgentCore, LangChain, AutoGen, …) |
| **Browser extension** ("Netzilo Secure Browser") | evaluates prompts to ChatGPT/Claude/Gemini/Perplexity/… in the page, fetches its rules from the server (`/api/edge/filters?os=…`), sends events to `/api/edge/events`; when the desktop client is present it defers LLM governance to the client | browser AI use on managed or BYOD devices |

Central policy objects (Dashboard → **Edge**):

- **Tools** (`/ai-edge/tools`): approved MCP servers/tools (catalog + your own) and
  **Discovered Tools** awaiting approval.
- **Scanners** (`/ai-edge/scanners`): YAML detection rules (Sigma-style); global
  premium ones are read-only.
- **Filters** (`/ai-edge/filters`): the binding — **Groups** + **Operating Systems** +
  **Agents** (process paths) + **Tools** + **Scanners** + **Posture Checks**. Nothing is
  enforced on a device until a filter matches its groups and OS.

---

## 2. Rollout runbook

1. **Prerequisites:** Netzilo client installed and connected on the devices
   (`05-client-install-and-deploy.md`); devices in a group (e.g. `ai-users`); Enterprise
   entitlement.
2. **(Optional) AI provider integration** for AI rule generation, discovered-tool risk
   analysis and AI Smart Search: Integrations → Artificial Intelligence → OpenAI or
   Anthropic API key (usage *All*). Without it `POST /edge/scanners/generate` returns 428.
3. **Create a Filter** (Edge → Filters → Add Filter):
   - Targets: groups `ai-users`, OS (e.g. Windows, Darwin).
   - Agents: process paths to intercept, wildcards and env vars allowed —
     `%PROGRAMFILES%\Google\Chrome\Application\chrome.exe`, `~/.cursor/**`,
     `/Applications/Claude.app/**`, `$HOME/.local/bin/claude`. Empty = no transparent
     interception (hooks/SDK/extension still work).
   - Tools: browse the catalog; add **Unsanctioned Tools** (wildcard `*`) if you want
     shadow MCP servers to be blocked/recorded.
   - Scanners: browse; start with the premium set (Path Traversal, PII in Tool Output,
     Prompt Injection, API Key & Secret Redaction, SSH Key Exfiltration, System
     Enumeration & CLI Exfiltration) plus report-mode custom rules.
   - Posture Checks: optional (e.g. disk encryption) — evaluated live; failure revokes
     tool access.
   - Enable, name, save. Validation: name, ≥1 OS, ≥1 group, ≥1 tool, ≥1 scanner.
4. **Verify on a device:** log shows `✓ Successfully updated MCP Gateway filters: N filters applied`
   and `Gateway static rules updated: N loaded, 0 failed`. Use an AI app named in Agents;
   Activity shows `tool.detected` / `semantic.event` / `aidr.graph` events and the peer
   page gets **Available Snapshots**.
5. **Coding agents:** on each dev machine `curl -fsSL https://pkg.netzilo.com/download/plugin/install.sh | sh`
   (Linux installs the client if missing; macOS/Windows need the client first), or
   `netzilo hook install --framework=claude-code|codex|gemini|openclaw`, then restart
   the agent CLI. `netzilo hook verify --framework=<x>` → `Status: ready ✓`.
6. **Custom agents:** developers add the SDK (§5).
7. **Browsers:** an **Enterprise Browser Extension** profile (Endpoint → Profiles) makes
   the client force-install the extension in Chrome/Edge; or deploy via browser policy
   (§6).
8. **Tune:** run report-mode for 1–2 weeks, review Activity → Events (category *AI Edge*,
   *Policy Violation*) and Reports → **AI Activity**, then switch high-confidence rules
   to `block`/`redact`.

---

## 3. Client-side mechanics you must know when troubleshooting

| Item | Value |
|---|---|
| Local ports | 41336 control/hooks HTTP (`/evaluate`, `/ws`), 41337 WSS, 41338 MCP gateway (`http://127.0.0.1:41338/mcp`, `/sse`), 41339 TLS-inspecting proxy; macOS extension IPC 17998/17999 |
| CA | `Netzilo Edge CA` (ECDSA P-256, 10 years) in `/etc/netzilo/netzilo-ca.pem` (`%PROGRAMDATA%\Netzilo\netzilo-ca.pem`); trusted in the OS store at `service install` and every start; `NODE_EXTRA_CA_CERTS` set system-wide; leaf certs 24 h |
| Interception steering | Windows: `nwfilter.exe` (WFP) redirects TCP of matched processes (and their children) to the proxy; macOS: `com.netzilo.NetziloFilter` system extension (needs user approval once); Linux: **no per-app steering** — point apps at `HTTPS_PROXY=http://127.0.0.1:41339` / `ALL_PROXY=socks5h://127.0.0.1:41339`, or use hooks/SDK |
| Skip list | Windows clients fetch `pkg.netzilo.com/download/configs/container.json` (`skip_domains`, e.g. Zoom); pinned/mTLS apps must be excluded there or removed from Agents |
| Parsers | WASM modules hot-loaded hourly from `pkg.netzilo.com/download/llm-parsers` and `…/semantic-classifier` (checksum-verified); an embedded copy ships in the binary |
| Rule delivery | management pushes expanded filters (tools, scanners, posture) to the peer on sync; log `Gateway static rules updated` |
| Hook evaluation | `toolCall` is synchronous (can block); `toolResult` fire-and-forget; hooks are **fail-open** by default (`NETZILO_HOOK_POLICY=allow`); set `block` for fail-closed |
| Verdict logging | `tool.allowed` (123), `tool.blocked` (124), `tool.sanctioned` (125), `tool.explicitly_blocked` (126), `semantic.event` (127), `tool.detected` (128), `aidr.graph` (129) |

To inspect what the engine recorded for a device, open the peer in the dashboard →
**Available Snapshots** → **View session snapshot** (behaviour graph, event search,
scanner replay).

---

## 4. Coding-agent hooks (`netzilo hook`)

| Framework | Config written | Events |
|---|---|---|
| `claude-code` | `~/.claude/settings.json` (Windows `%APPDATA%\Claude\settings.json`) | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit` (matcher `*`, 10 s) |
| `codex` | `~/.codex/config.toml` | `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit` |
| `gemini` | `~/.gemini/settings.json` | `BeforeTool`, `AfterTool`, `BeforeModel`, `AfterModel` |
| `openclaw` | plugin extracted to `~/.netzilo/openclaw-plugin/` and enabled with `openclaw config set plugins.entries.netzilo.*` (needs `openclaw` on PATH) | in-process |

Commands: `netzilo hook install|uninstall|verify --framework=<fw> [--url http://localhost:41336/evaluate]`.
Install is idempotent and repairs the binary path after client upgrades. Output ends with
`Restart <framework> for the hook to take effect.` and warns if the daemon is down.

Runtime env for the hook: `NETZILO_HOOK_URL`, `NETZILO_HOOK_TIMEOUT_MS` (5000),
`NETZILO_HOOK_POLICY` (`allow`|`block`), `NETZILO_HOOK_SKIP="Glob Grep LS"`,
`NETZILO_HOOK_STATE_DIR`. A block appears to the agent as
`[netzilo hook] blocked <tool>: <reason>` (default reason
`Blocked by Netzilo security policy`).

Requirements: the Netzilo client must be running and logged in on that machine (the hook
only talks to `localhost:41336`); the device must be in a group matched by a filter whose
scanners produce verdicts.

---

## 5. SDK for custom agents

Install `pip install netzilo` (extras `netzilo[crewai]`, `[llamaindex]`, `[bedrock]`) or
`npm install netzilo`.

```python
import netzilo
netzilo.start(server="https://<domain>", setup_key="…", agent_name="orders-agent")   # or pat="nzl_…"
# CrewAI: from netzilo.crewai import govern; govern(config={...}) before kickoff
# LangGraph: netzilo.langgraph.govern(graph, config={...}) before compile(); govern_model(ChatAnthropic(...))
# Strands / Bedrock AgentCore: from netzilo.strands import govern; govern()   # reads NETZILO_* env
# any framework: from netzilo.tools import govern_tool  (decorator) ; blocked → NetziloBlockedError
netzilo.stop()   # flushes events + graph snapshot
```

```ts
import { start, wrapTool, govern } from "netzilo";
await start({ server: "https://<domain>", pat: "nzl_…", agentName: "orders-agent" });
const safeSearch = wrapTool("web_search", searchFn);
// or: await govern()  — reads NETZILO_SERVER / NETZILO_SETUP_KEY / NETZILO_AGENT_NAME
```

Config keys / env: `server` (`NETZILO_SERVER`, default `https://srv.netzilo.com`),
`setup_key` (`NETZILO_SETUP_KEY`) or `pat` (`NETZILO_PAT`), `agent_name`
(`NETZILO_AGENT_NAME`), `enable_advanced_governance` (`NETZILO_ADVANCED`, `govern()`
enables it by default), `log_level`, `log_file`, `config_path` (`~/.netzilo-sdk/config.json`),
`mcp_gateway_port` (`0` disables). Use a **setup key** whose auto-group is your agents'
group so the right filter applies.

**Advanced governance** (Linux only): adds in-process TLS interception (proxy env +
CA at `~/.netzilo-sdk/netzilo-ca.pem`) and an `LD_PRELOAD` probe for file/process
events, including subprocesses. Limits: statically linked binaries ignore `LD_PRELOAD`;
programs that ignore proxy env variables bypass interception; Node `fetch` needs
`undici`; in containers root is needed to install the CA. Leave it off on macOS/Windows.

Known limits: raw-client wrappers do not redact **streaming** responses (prompts are
still gated); LiteLLM integration logs redact verdicts but does not apply them; MCP
clients that cache `call_tool` before `govern_session()` bypass governance; smolagents
sandboxed executors (E2B/Docker) are not governed. Bedrock native Converse (SigV4)
can be redacted only in embedded SDK mode; the daemon inspects it read-only.

Containers: the SDK image pattern sets `NETZILO_SERVER`, `NETZILO_SETUP_KEY`,
`NETZILO_AGENT_NAME`, `NETZILO_LOG_LEVEL`, `NETZILO_PROXY_PORT`, `NETZILO_CONFIG_DIR`,
`NETZILO_EXTRA_NO_PROXY`, and waits for the log line `Rules updated` before starting
the agent.

---

## 6. Browser extension and Enterprise Browser

**Extension ("Netzilo Secure Browser"):** Chrome Web Store id
`kdcpnkonhjcknlkjmjapclhpoamlckji`; Edge Add-ons id `efflopncanncclcfnddajplbnmhoebml`;
Firefox `netzilo-secure-browser`; Safari App Store `6740890085`.

- Force-install via browser policy: Chrome `ExtensionInstallForcelist` =
  `kdcpnkonhjcknlkjmjapclhpoamlckji;https://clients2.google.com/service/update2/crx`;
  Edge = `efflopncanncclcfnddajplbnmhoebml;https://edge.microsoft.com/extensionwebstorebase/v1/crx`.
  The Netzilo client does this automatically when an **Enterprise Browser Extension**
  profile applies to the device (registry / `/etc/opt/chrome/policies/managed/` /
  `/Library/Managed Preferences/`), and removes it on `service uninstall`.
- Standalone mode (no client): the user signs in at the dashboard; the extension stores
  `nz_cloud_url` + `nz_auth_token` and refreshes rules every 5 minutes from
  `GET /api/edge/filters?os=…` — only filters whose **Agents** list matches the browser
  name ("Google Chrome", "Microsoft Edge", "Mozilla Firefox", "Apple Safari") apply.
- Enforcement: a blocked prompt returns HTTP 403 "Blocked by policy" to the web app;
  redactions rewrite the request body silently; responses are logged, not blocked. The
  `Prevent LLM Prompt Injections` domain setting in a profile enables prompt scanning via
  `POST /api/ai/scanprompt`.
- Popup → Debug tab shows `LLM Guard: ENABLED (standalone mode)` / `DISABLED (client mode)`,
  and pills `SW DOWN`, `INIT ERR`, `RULES:n`, `OK R:n`. Console prefixes `[Netzilo]`, `[LLMGuard]`.

**Netzilo Enterprise Browser** (Chromium-based, Windows/macOS/Linux/mobile):
`pkg.netzilo.com/download/windows/browser_setup.exe`, `…/macos/{amd64,arm64}/NetziloEnterpriseBrowser_*.dmg`,
Play `com.netzilo.browser2`, App Store `6747919491`. Windows MSI silent install:
`msiexec /i netzilo_enterprise_browser.msi /qn TENANT=https://<tenant-dashboard> SHORTCUTNAME="Acme Browser"`.
It bundles the Netzilo client and its own extension; policy comes from **Enterprise
Browser** profiles (domain restrictions, watermark, clipboard, downloads/uploads,
keylogging, screenshot, extension allow/block, encryption). No auto-update: users check
`chrome://settings/help`; **Share Support Data** there zips the logs. Logs in
`<User Data>/logfile.log` and `netzilo.log`.

---

## 7. Edge Tools and MCP

- **Approved tools**: name, transport (`stdio` command/args/env, `sse`/`streamable_http` URL + headers), categories (≥1), icon URL, enabled. Bind to filters. Disabling a tool blocks it everywhere immediately.
- **Discovered tools**: MCP servers seen on devices but not approved → **Pending Review**; **Approve** (creates a tool and sanctions it), **Dismiss**, **Analyze** (AI risk, needs an AI integration). Usage shows peers/users, allowed/blocked calls.
- **Unsanctioned Tools** wildcard in a filter: any MCP tool not approved is matched → blocked and reported as `Unsanctioned tools are not allowed`.
- **Using the gateway from IDEs**: Workplace → Tools → **Use Tools** gives deep links and config for Cursor (`~/.cursor/mcp.json`), VS Code (`.vscode/mcp.json`) and generic clients pointing at `http://localhost:41338/mcp` (HTTP) / `/sse`. Direct MCP-over-HTTPS from intercepted apps is also parsed by the proxy.

---

## 8. Writing and testing rules (Edge Scanners)

For authoring beyond the basics below (multi-event Starlark scripts over the behaviour
graph, false-positive discipline, the complete field, modifier, action and builtin
reference), load `32-detection-rule-authoring.md` — it is the dedicated rule-author skill. This section
covers what an administrator needs to deploy, test and troubleshoot rules.

Format is Sigma with Netzilo extensions (the AI rule generator and the public corpus
`github.com/netzilo/aidr-sigma` use it; the older `match/except` syntax in some docs is
legacy). Minimal rule:

```yaml
title: Block obvious prompt-injection phrases
id: 7d3a2f1e-6b2c-4c1b-9d5e-0a1b2c3d4e5f
status: experimental
level: high
description: Blocks tool inputs containing classic instruction-override phrases.
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

- `logsource.category` (routing context): `tool_request|tool_response|tool_input|tool_output|llm_request|llm_response|http_request`; semantic `skill_acquired|llm_reasoning|external_message|file_upload|file_download|do_automation|llm_tool_call|llm_tool_result`; syscall `execute_process|connects|file_read|file_write|file_create|file_delete|file_rename|file_op`; `agent_events|all`; `periodic` (30 s background scripts).
- Fields: `event_type, tool_name, server, provider, model, host, path, method, url.full, content, command, file_path, response, message.content, system_prompt, source, agent_name`. Modifiers: `|contains`, `|startswith`, `|endswith`, `|re` (RE2), `|all`, `|base64`, `|cidr`, `|windash`.
- `level`: `low|medium|high|critical` (default action when `action` absent: high/critical → block, else report).
- `action`: `block` (403 to the agent), `allow` (skip remaining rules), `report`, `redact` (`replace`, `keep_first`, `keep_last`), `scan` (ML/AI classifier; `prompt:` for an LLM judge; `on_timeout`, `on_error`), `blockmodel`/`allowmodel`/`replacemodel` (model governance), `redirect`, `inject`, `replace` (HTTP rewrites), `execute` (Starlark script over the behaviour graph: `graph()`, `node()`, `edges()`, `search()`, `re`, `http`, `webhook`, `meta`, `netzilo` identity, `store_*`; 30 s timeout; fail-open unless `on_error: block`; must assign `result`).
- Semantic payloads are `key=value` lines (`content|contains: "host=evil.example"`).
- Ordering: first firing rule wins; put explicit `allow` rules first.

Authoring in the dashboard: Edge → Scanners → **Add Scanner** → YAML editor (name and
description sync from `title`/`description`); the sparkle button streams an AI-generated
rule from a prose description when an AI integration exists. **Replay** tests the rule
against a peer's recorded session snapshot (`Peer` → `Snapshot` → **Play**) and shows
`new_block / new_redact / new_detection / unchanged`. Session snapshots also offer **Run
Scanners** to replay several catalog rules.

Lint locally: clone `https://github.com/netzilo/aidr-sigma`,
`pip install pyyaml && python3 tools/rulelint.py <dir>`.

Best practices: report before block; anchor regexes; add exclusions for legitimate use;
keep `scan` rules narrow (latency); scope graph traversals to the current agent.

---

## 9. Troubleshooting

| Symptom | Check | Fix |
|---|---|---|
| No AI events for a device | device in a group of an **enabled** filter with matching OS? filter has tools+scanners? | fix filter; `netzilo refresh`; log `Successfully updated MCP Gateway filters` |
| Desktop app not intercepted (no `[aidr] IngestHTTPRequest` at debug level) | app path in filter **Agents**? Windows `nwfilter.exe` running (`NWFilter: started`)? macOS extension approved (`MacFilter` errors)? Linux (no steering) — app must use the proxy env or hooks | adjust Agents; approve extension; on Linux set `HTTPS_PROXY`/`ALL_PROXY` for the app |
| App shows TLS/certificate errors | app not using OS trust store; pinning | Python/curl: `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE=/etc/netzilo/netzilo-ca.pem`; Java `keytool -importcert … cacerts`; Firefox `ImportEnterpriseRoots` policy or `certutil -A -d sql:<profile>`; pinned/mTLS apps → exclude domain (Netzilo skip list) or remove from Agents |
| `MITM: CA trust install failed` / cancelled dialog | | manual trust commands in `07-client-troubleshooting.md` §9 |
| Hook installed but nothing happens | `netzilo hook verify`; daemon running? device filtered? | start client; check filter; `NETZILO_HOOK_POLICY=block` to fail closed while testing |
| Hook blocks everything when client is down | `NETZILO_HOOK_POLICY=block` set | expected fail-closed; start the client |
| Rule never fires | wrong `logsource.category`; earlier `allow`; content not where expected | Replay against a snapshot and use its event search to see the real payload; move the rule up |
| Too many false positives | | tighten regex, add exclusion selection + `condition: sel and not excl`, switch to `report` |
| AI rule generation returns 428 | no OpenAI/Anthropic integration | Integrations → Artificial Intelligence |
| Discovered tool has risk "Unknown" and no Analyze button | no AI integration | same |
| `Enterprise subscription required` on premium scanners | plan | upgrade / MSP mode on self-hosted |
| Browser extension `DISABLED (client mode)` in plain Chrome with the client installed | by design: client MITM handles LLM traffic | ensure Chrome path is in filter Agents (Windows/macOS) |
| Bedrock traffic visible but not redacted | SigV4-signed requests cannot be rewritten by the daemon | use SDK embedded mode, or Bedrock's OpenAI-compatible bearer endpoint |
| Events show `peer="edge.netzilo.extension"` | events from the browser extension in standalone mode | normal |

Log prefixes to search for on a device: `MITM:`, `Gateway static rules updated`, `NWFilter:`, `MacFilter:`,
`[aidr]`, `[evaluate]`, `hook`.

---

## 10. Reporting and evidence

- Dashboard → **AI Activity** panel (top agents, models, policy violations over 7 days).
- Activity → Events filtered by category *AI Edge* / *Policy Violation*; each event carries
  agent, tool/server, verdict, rule; kill-chain and session-snapshot viewers open from the
  row.
- Reports → **AI Activity** report (agents, models, servers, top calls, violations,
  per-user graphs).
- API: `GET /api/events/paginated?code=tool.blocked&…`, `GET /api/peers/{id}/aidr-snapshot`.
- Stream everything to S3/Min.io for SIEM (Integrations → Event Streaming).

## 11. Constraints to disclose early

**Excluding a domain from inspection is not self-service.** Applications that pin
certificates or require mutual authentication break under inspection, and the list of
domains passed through uninspected is maintained centrally by Netzilo, not per tenant.
There is no dashboard or API field for it. The self-service options are to remove the
application from the filter's agent list, which loses visibility for that application
entirely, or to request the addition. Say this plainly rather than searching for a
setting that does not exist.

**Certificate trust varies by runtime, not by operating system.** Installing the
inspection authority in the system store covers most applications. Runtimes that ship
their own trust store do not read it: Python, Java and Firefox each need their own step,
covered in `07-client-troubleshooting.md`. Applications written in Go normally follow the
system store and need nothing extra, which is worth stating because it is the first thing
people ask about after the other three.

**Provider coverage is broader than the named list.** Traffic is matched first by
recognised hostname and then, failing that, by the shape of the request body, so many
services with an OpenAI-compatible interface are parsed even when they are not named
anywhere. The way to answer "is this provider supported" is to run the tool once and look
for its activity in the dashboard, not to consult a list.

**Reading the behaviour graph.** Node colour encodes node type and is consistent across
every graph view. Clustered nodes carry a count badge and appear when several nodes of
the same type share the same parent. A node ringed in grey is the action that triggered
the rule, which is separate from the kill-chain stage colours. Time-window controls and
node and edge type filters sit in the graph toolbar. Tell an admin this before their
first look at a graph; without it the picture is not interpretable.
