# Skill metadata and build scripts

**Who this folder is for.** These scripts maintain the skill; they are not part of
operating Netzilo. An agent following the runbooks never has to run them — what it
consumes is their output, the front matter at the top of each reference file. Run them
when you change a reference, add one, or want to rebuild the API schema reference from a
server. The one script with a use outside maintenance is `gen-api-schemas.py`, which
turns any Netzilo Server's own OpenAPI description into readable per-endpoint
documentation.

The `netzilo-admin` skill is loaded by agents that do not all have the same
reach: one has only the REST API, one has shells on the server and the device,
one is a human who can also click the dashboard and the IdP console. Every
reference file therefore carries machine-readable front matter saying what its
procedures need and who can actually run them.

The front matter is generated, never hand-edited. The only hand-edited piece is
`capabilities.json`.

## Front matter contract

Written by `gen-frontmatter.py` at the top of every `netzilo-admin/references/*.md`:

| Field | Meaning |
|---|---|
| `id` | the file's two-digit prefix, e.g. `20` |
| `title` | the file's H1, copied verbatim |
| `requires` | capabilities needed to **execute** the procedures — curated, from `capabilities.json` |
| `executable_on` | derived from `requires`: the surfaces that hold every required capability |
| `chars` | body size, so an agent can budget context before loading |
| `sections` | one entry per `## ` heading: `id`, `title`, `chars`, and `requires` when a section differs from the file |

`sections` exists so a 180 KB file can be loaded in parts. A section `id` is the
heading's leading number (`## 3. API` → `3`), or a slug of its text when the
heading is unnumbered.

## Capability vocabulary

Defined once in `skillmeta.py` (`CAPABILITIES`):

| Capability | What it means |
|---|---|
| `api` | the Netzilo management REST API with an admin token |
| `dashboard-ui` | a browser session in the Netzilo dashboard |
| `server-shell` | a shell on the Netzilo Server host (docker, systemd, files) |
| `client-device` | a shell or OS access on a device running the Netzilo client |
| `idp-console` | the identity provider's own admin console |
| `device-tools` | the support device tools through management: read a peer's tool catalog and run its tools remotely |

`requires` records what a procedure needs to be **run**, not what the prose
mentions. A page that explains a `docker compose` command without asking anyone
to run it does not require `server-shell`.

## Surfaces and the executable-vs-advisory rule

`skillmeta.SURFACES`:

| Surface | Has |
|---|---|
| `dashboard-assistant` | `api`, `device-tools` |
| `netzilo-harness` | `api`, `server-shell`, `client-device`, `device-tools` |
| `human-operator` | all six |

A reference is **executable** on a surface when the surface holds every
capability in `requires`; that is the whole of `executable_on`. Otherwise the
reference is **advisory** there: the agent explains the procedure and a human
performs it. This is why a file that carries shell steps but declares only
`api` is a build error — it tells an API-only agent it can run something it
cannot.

## Adding a reference file

1. Write `netzilo-admin/references/NN-name.md` with an H1 and `## ` sections.
2. Add an entry to `capabilities.json`:
   ```json
   "NN-name.md": {"requires": ["api"], "sections": {"7": ["server-shell"]}}
   ```
   `sections` is optional; use it when a few sections need more than the file does.
3. Link to it from `SKILL.md` (an unlinked reference is reported as an orphan).
4. Run `scripts/build.sh` and commit the generated front matter with the file.

## Regenerating

```bash
scripts/build.sh                      # front matter, then validate
scripts/build.sh path/to/openapi.yml  # also regenerate 33-api-request-schemas.md
scripts/build.sh https://<server>/api/support/openapi.yml   # …straight from a server
```

Individually: `gen-frontmatter.py` (add `--check` to fail instead of write),
`gen-api-schemas.py <openapi.yml | URL> [--token …]` (prints to stdout), `check-skills.py`.

The OpenAPI description comes from a running server: `GET /api/support/openapi.yml`.
It is not in this repository, so the default build never needs it.

## What CI enforces

`.github/workflows/validate-skills.yml` runs `gen-frontmatter.py --check` and
`check-skills.py` on every push and pull request. `check-skills.py` fails on:

- front matter missing or stale against the file it describes;
- `capabilities.json` not covering exactly the reference files, an unknown
  capability name, or a section override whose id matches no heading;
- shell or device commands in a file that declares no shell capability and no
  section override (other curation-versus-prose mismatches are warnings);
- a version that differs between `VERSION`, `SKILL.md` front matter, the
  `This copy is version …` and `Compare its version: with …` lines, `manifest.json`,
  `CHANGELOG.md` and the `README.md` table;
- a `references/NN-*.md` link or `#section` anchor that does not resolve;
- an H1 that disagrees with the front-matter title.

It warns, without failing, about orphaned references and about files over 60 KB
with fewer than five sections.

A second job, `api-schema-drift`, is manual (`workflow_dispatch` with an
`openapi_url` input). It regenerates `33-api-request-schemas.md` from a live
spec and fails if the committed copy differs.
