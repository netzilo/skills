---
id: '50'
title: Admin Skill — Files attached to AI requests (file guardrails)
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 17574
sections:
- id: '1'
  title: Model
  chars: 2336
- id: '2'
  title: When the gateway reads a file
  chars: 718
- id: '3'
  title: What is read
  chars: 2827
- id: '4'
  title: Writing a file rule
  chars: 2967
- id: '5'
  title: What users see
  chars: 2049
- id: '6'
  title: Large requests and fail-open
  chars: 1520
- id: '7'
  title: Evidence
  chars: 1915
- id: '8'
  title: Diagnosis
  chars: 1412
- id: '9'
  title: Limits to state before a customer discovers them
  chars: 844
---
# Admin Skill — Files attached to AI requests (file guardrails)

**Audience:** admins who want guardrails to judge the files people and agents send to a
model (a PDF in Claude Code, a document dropped into a chat, a screenshot a computer-use
tool returns), and the support agent explaining why a file was refused, redacted or let
through. Read with `27-ai-gateway.md` (the gateway that does the work), `28-edge-guardrails.md`
(how a guardrail is created and bound) and `32-detection-rule-authoring.md` (the rule
language).

**Dashboard:** Edge → **Guardrails** (the rule), Edge → **Filters** (who it applies to),
Activity → **Events** (category AI Edge, the file's name in the entry), Activity →
**AI Sessions** (the files of each model call, the `FILE_SENT` / `FILE_RECEIVED` edges in
the behavior graph). **API:** `/api/edge/guardrails`, `/api/edge/filters`,
`/api/ai/sessions/trajectory?id=`. **Who:** admins write and bind the rule; the AI Gateway
reads and judges the files.

---

## 1. Model

A file attached to a model request is judged as its own event, `file_attachment`: its
type facts are fields, its text is the `content`. A guardrail can block the request, redact
the file in place, or report it, exactly as for a prompt.

**Where it happens: the AI Gateway only.** The gateway reads the files in the requests it
serves. The Netzilo client, coding-agent hooks, the SDK and the browser extension do not
produce file events (the extension has its own upload restrictions, `49`). A device whose
AI traffic goes through the gateway is covered; a device calling the provider directly is
not, for files.

**What counts as a file** — every attachment the request carries, whatever the caller:

| Channel (`channel`) | What | Examples |
|---|---|---|
| `llm_attachment` | a file in a message: image, document, file part, audio | a PDF dropped into a chat, an OpenAI `file` part, an Anthropic `document` or `image` block |
| `tool_result` | a file a tool returned to the model | a PDF or image in a tool result, a computer-use screenshot |

**What never arrives as a file.** Anything a client turns into text before sending is
judged as text, on its own surface (`llm_request`, tool results), not as a file:

- **Claude Code** sends a PDF it reads (the Read tool) and images as files. A CSV, a log
  or source code it reads arrives as text in the tool result. It cannot read a DOCX itself;
  if it extracts one with a command, that is text too.
- **Claude Cowork** never sends a file: it reads documents in its own workspace (its
  `pdf-reading` skill extracts the text) and sends the text. A document dragged into
  Cowork is copied into the task's folder and read the same way. File guardrails do not
  see Cowork's files; text guardrails see their text.
- A chat client that uploads a file to the provider first and sends only its id or URL:
  recorded `by_reference` (§3), never fetched or read.

**Naming.** `file_name` is the name the request gives. Anthropic documents often have no
title; a title-less document sent after a tool call whose arguments name a file
(`file_path` or `path`, as Claude Code's Read does) takes that file's base name, in call
order, `/` and `\` paths alike. Otherwise an untitled document is `document.<ext>`; an
image `image`; a screenshot `screenshot`; audio `audio.<format>`.

---

## 2. When the gateway reads a file

- **A file is read only when some guardrail under the caller's filters applies to files**:
  a rule with `category: file_attachment`, or a broad rule (`agent_events`, `all`, no
  category) whose detection does not require another `event_type`. A broad PII rule
  therefore turns file reading on by itself.
- Otherwise every file is still identified (type, size, SHA-256), recorded and judged on
  those facts only, without its text.
- A caller with no filter gets no rule at all (`29`).
- **Prompt guardrails run first.** A request refused for its prompt is not judged for its
  files.
- **The first refused file ends the check**; later files in that request are not judged.

---

## 3. What is read

The true type comes from the bytes; the declared type and the extension never decide what
is read.

| Format | Read | Redact in place |
|---|---|---|
| Text: `text/*`, JSON, XML, NDJSON, JavaScript, YAML, shell, Python, SQL, GeoJSON, JSON-LD, SubRip | the whole text (UTF-8, UTF-8 with BOM, UTF-16 with BOM) | yes, in the same encoding |
| DOCX, XLSX, PPTX | every XML part: paragraphs, shared and inline strings, comments, field codes, tracked deletions, document properties; text of embedded text/Office/PDF documents | paragraphs, strings, comments, field codes, tracked deletions, properties. **Not**: spreadsheet cell values and formulas, attribute text (alt text, tooltips, sheet names, validation prompts), embedded documents |
| PDF | page text, annotations, form-field values, metadata (Title, Author, Subject, Keywords, Creator, Producer) | **never** — a PDF is read-only |
| Anything else: images, audio, video, archives (ZIP), legacy `.doc`/`.xls`/`.ppt`, binaries | not read; type facts only (`unsupported_format`) | — |

There is **no OCR** (an image or a scanned PDF has no text to judge) and no archive
extraction.

`content` is the file's text units, empty ones skipped, joined with a newline: a text file
is one unit; an Office file its paragraphs and strings in part order; a PDF page by page
(page text, then that page's annotations and fields), then the metadata.

**Limits** (fixed, no setting): file 25 MiB · expanded Office content 50 MiB · 10 000 zip
entries · compression ratio 100 · 5 MiB of text per file · 500 PDF pages · two levels of
embedded documents · XML nesting 256 · 20 s per PDF · 30 s per file.

### 3.1 Unscannable reasons

A file that is not read has `scannable: "false"` and `unscannable_reason`:

| `unscannable_reason` | Why |
|---|---|
| `unsupported_format` | not text, Office (DOCX/XLSX/PPTX) or PDF |
| `too_large` | over 25 MiB |
| `encrypted` | the PDF needs a password |
| `no_text_layer` | a PDF without text (a scan) |
| `garbled_text` | the PDF's text does not decode (over 5 % unreadable characters) |
| `embedded_files` | the PDF carries file attachments |
| `too_many_pages` | over 500 PDF pages |
| `too_much_text` | over 5 MiB of text |
| `not_unicode` | a text file in neither UTF-8 nor UTF-16 with a BOM |
| `malformed` | a broken Office or PDF file |
| `too_complex` | too many parts, too much expansion, too deep, or took too long to read |
| `nested_too_deep` | documents embedded more than two levels deep |
| `unreadable_embedded_object` | an embedded object that cannot be read (an OLE object, an encrypted embedded PDF) |
| `undecodable` | the file's encoding in the request does not decode |
| `by_reference` | named by URL or file id; no bytes in the request, never fetched |
| `not_read` | could be read, but not right now (§6) |

---

## 4. Writing a file rule

Target files with `logsource.category: file_attachment`, or `agent_events` with
`event_type: file_attachment` in the detection. Fields (all strings; an empty field is
absent and never matches):

| Field | Value |
|---|---|
| `channel` | `llm_attachment` or `tool_result` |
| `file_name` | the name (§1) |
| `ext` | extension of `file_name`, lower case, no dot; absent for `image`, `screenshot` |
| `declared_type` | the MIME type the request declared, lower case |
| `true_type` | the MIME type sniffed from the bytes; absent when there are no bytes |
| `size` | decoded size in bytes |
| `sha256` | SHA-256 of the decoded bytes; absent when there are no bytes |
| `scannable` | `"true"` or `"false"` |
| `unscannable_reason` | §3.1, only when set |
| `content` | the file's text (§3); empty when it was not read |
| `provider`, `model`, `agent_name` | the model request's |

The tool that returned a `tool_result` file is **not** a rule field (it is on the event).
There is no numeric comparison: `size|gt:` silently becomes `contains`. Compare sizes in a
script (`int(meta["size"])`) or with `|re`.

```yaml
# Refuse executables and scripts sent to a model, whatever their name says
title: Executables attached to AI requests
id: 2f0d6c51-7f0b-4f3e-9c2e-5a1b8e7d3c40
status: stable
level: high
logsource: {product: ai_agent, category: file_attachment}
detection:
  exe:
    true_type:
      - application/vnd.microsoft.portable-executable   # .exe, .dll
      - application/x-mach-binary                       # macOS
      - application/x-elf                               # Linux
      - application/x-executable
      - application/x-sharedlib
  condition: exe
action: block
```

```yaml
# Report files nobody could read, so an encrypted PDF is at least visible
title: Unreadable files sent to AI
id: 6c1e9a7b-3d52-4f0e-8a6d-2b9c4e1f7a03
status: stable
level: medium
logsource: {product: ai_agent, category: file_attachment}
detection:
  locked:
    unscannable_reason: [encrypted, unreadable_embedded_object, nested_too_deep]
  condition: locked
action: report
```

A content rule (a PII regex with `action: redact`) applies to file text as to any text:
written on `agent_events` it covers prompts and files alike.

**Judging what a file is** — a script can send the file's text to a model
(`system_one()`, `llm_call()`, `32`) and decide by kind, for one team: "files unrelated to
development work" on the engineering filter blocks a customer export, an HR record or a
bank statement while code, logs, specifications and test data pass. The script reads
`meta["content"]`, `meta["file_name"]`, `meta["true_type"]`, `meta["scannable"]` and
`meta["unscannable_reason"]`; System One takes at most 512 KiB, so judge a long file on its
start and end. Return a reason that names what the file is: the gateway puts the file's
name in front of it. Answer `report` (not `allow`) for files that could not be judged, so
they stay visible.

---

## 5. What users see

- **Blocked:** the whole request is refused with HTTP 400, error type `netzilo_policy`.
  The message names the file:

  `Netzilo Guardrail: <file name>: <reason>` — e.g.
  `Netzilo Guardrail: account_statement.pdf: financial records, not development material.`
  A rule without its own message gives `Blocked by rule: <rule name>`.

  Claude Code shows it as `API Error: 400 Netzilo Guardrail: …` under the tool call that
  read the file.
- **Redacted:** the request goes on with the file rewritten in place, in the form it came
  (a data URL stays a data URL), and the rewrite is read back before it is sent. **A PDF,
  a spreadsheet cell value, alt text or an embedded document cannot be rewritten**: when a
  redaction touches one, the request is refused instead: `<file>: the file holds content a
  guardrail redacts, and it cannot be redacted in place`. A rewrite that does not read back
  is refused: `Netzilo Guardrail: the file <name> holds content that must be redacted and
  it cannot be rewritten`.
- **Reported:** nothing changes for the user.
- **The conversation goes on after a refusal.** Every verdict is remembered for 24 hours
  per user, policy and session:
  - the same file sent again **with the same prompt** (a retry) is refused again;
  - the file sent **with anything newer** (in history after the model's turn, or with a
    new prompt in the same message, as Claude Code sends it) is replaced by the text
    `[removed by Netzilo Guardrail]` and the request goes through;
  - a computer-use screenshot or an Anthropic document given as text blocks cannot be
    removed and is refused on every later request that carries it: start a new
    conversation;
  - a redacted file sent again gets the same rewrite; a changed policy or a new session
    judges again.
- Models react to refusals: after a refused file a model may decline to read similar files
  in the same conversation ("I expect this will be blocked too"). That is the model, not
  the gateway; a new conversation behaves normally.

---

## 6. Large requests and fail-open

The gateway admits large request bodies and reads files within memory budgets, sized from
the process's memory (the tightest cgroup limit, else the host's):

| Setting | Default | When it is full |
|---|---|---|
| `NZ_AI_BODY_BUDGET_MB` — request bodies of 64 KiB or more held at once | memory ÷ 48, between 32 and 512 MiB | the request waits up to 10 s, then **HTTP 503** `overloaded_error` *"Netzilo AI Gateway: too many large requests at once; retry shortly"*, `Retry-After: 5` |
| `NZ_AI_FILE_BUDGET_MB` — file bytes being read at once | memory ÷ 256, between 16 and 128 MiB | waits up to 2 s, then **fail-open**: the file is judged on its facts only, `unscannable_reason: not_read`, and sent |

Set them in the gateway's environment: a container takes `-e NZ_AI_FILE_BUDGET_MB=64`; the
Linux service takes a systemd drop-in (`sudo systemctl edit netzilo-aigw`, then
`[Service]` / `Environment=NZ_AI_FILE_BUDGET_MB=64`, and `sudo systemctl restart
netzilo-aigw`), which `netzilo-aigw up` leaves in place. `GOMEMLIMIT` overrides the soft
memory limit the gateway sets for itself (80 % of the memory it found).

**File analysis fails open.** A file that cannot be read right now (budget full, readers
busy, request ended) goes to the model unread. To make that visible or strict, write a rule
on `unscannable_reason: not_read`: `report` to count them, `block` where an unread file
must never pass (the user retries). Every other unread reason is final and the same each
time.

---

## 7. Evidence

- **Activity → Events**: one AI Edge event per rule that matched the file —
  `ai.blocked` (149) when the file was refused, `ai.redacted` (150) when it was rewritten,
  `ai.detected` (152) otherwise. The entry reads *User <user> on <gateway>: file
  <name> (<EXT>) to <model> blocked by rule <rule> by filter <filter> — <reason>*; for a
  tool's file, *a tool returned to <model>*. A rule that only matched a file another rule
  refused says *blocked by <that rule>*.
- Event fields: `file_name`, `file_type` (true type), `file_size`, `file_sha256`,
  `channel`, the rule, filter, severity and reason; `tool` and `call_id` for a tool's file;
  `extra` holds every field of §4. **The file text on the event is the text as the
  guardrails left it** (redacted, also when the file was refused), at most 8 KB, shown
  under **show full file text**. The file itself is never stored.
- **AI Sessions**: each model call lists its **Files** — name, type, size, *attached to the
  request* or *returned by the tool*, *not scanned (<reason>)*, and the verdict with the
  rules. The trajectory's `scanned` is the format's readability: a DOCX shows scanned
  even when no file guardrail read it.
- **Behavior graph**: `FILE_SENT` (session → model) for attachments, `FILE_RECEIVED`
  (tool → session) for tool files; the edge's label names the files, and hovering it
  lists each file once with its own verdict and rules. Each file is identified by
  `<request or call id>/<sha256>/<name>`.
- **API**: `GET /api/ai/sessions/trajectory?id=<session>` → each step's `files[]`: `name`,
  `type`, `declared`, `size`, `sha256`, `scanned`, `reason`, `channel`, `node`, `status`
  (`blocked`, `redacted`, `detected`), `severity`, `rules`.
- **Replay** (`28` §4.1) re-judges recorded files on their facts only: their text is not
  kept, so a content rule cannot be replayed on files (the result is marked partial).

---

## 8. Diagnosis

| Symptom | Cause | Do |
|---|---|---|
| A file went through that a rule should stop | the caller does not reach the model through the gateway; or the client sent text, not a file (§1: Claude Code reading a CSV, Cowork); or the rule is not in a filter of the caller's groups | check the session's **Files** list: no file there means no file event; text guardrails apply to the text |
| The file is listed *not scanned* | §3.1 reason | `encrypted` / `no_text_layer`: no text to judge; `not_read`: §6; `by_reference`: the client uploads files to the provider first |
| A PDF with personal data is refused instead of redacted | PDFs are read-only | expected; redact upstream or narrow the redact rule to prompts with `event_type: llm_request` |
| The same refusal again and again in one conversation | a retry with the same prompt, or a screenshot / text-block document that cannot be removed | send a new prompt, or start a new conversation |
| Claude stops reading files after a refusal | the model anticipates the guardrail | a new conversation; it is not a gateway refusal (no `Netzilo Guardrail` message) |
| 503 *too many large requests at once* | the body budget is full | retry; raise `NZ_AI_BODY_BUDGET_MB` or the gateway's memory |
| A file event shows `blocked by <rule>` as its reason | that rule matched a file another rule refused | read the other rule's event for the reason |

---

## 9. Limits to state before a customer discovers them

- **Gateway only.** Files sent from a device straight to a provider, through the browser
  extension, or by a hook or the SDK are not judged as files.
- **Clients that extract text send text.** Claude Code's text files and every Cowork
  document reach the model as text: file guardrails do not see them, text guardrails do.
- **No OCR, no archives.** Images, scans and ZIPs are judged on their type and size only.
- **PDFs and spreadsheet values cannot be redacted**: a redaction there refuses the
  request.
- **File analysis fails open** under memory pressure (§6); a rule on `not_read` makes it
  visible or strict.
- **A file's text is not kept**, so replay judges files on their facts only.
- **Files are fixed at 25 MiB and 5 MiB of text**; larger files are judged on their facts.
