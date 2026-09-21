#!/usr/bin/env python3
"""Render the management API's request schemas as a runbook reference.

    scripts/gen-api-schemas.py path/to/openapi.yml > netzilo-admin/references/33-api-request-schemas.md

The source of truth is the OpenAPI description shipped inside Netzilo Server
(served to admins at GET /api/support/openapi.yml). This file is the offline
copy for operators without a live server; regenerate it when the API changes.
"""

import sys
from datetime import date

import yaml

METHODS = ("get", "post", "put", "patch", "delete")


def resolve(spec, node, depth=0):
    if depth > 8 or not isinstance(node, dict):
        return node
    if "$ref" in node:
        target = spec
        for part in node["$ref"].lstrip("#/").split("/"):
            target = target.get(part, {}) if isinstance(target, dict) else {}
        return resolve(spec, target, depth + 1)
    out = {}
    for k, v in node.items():
        if isinstance(v, dict):
            out[k] = resolve(spec, v, depth + 1)
        elif isinstance(v, list):
            out[k] = [resolve(spec, i, depth + 1) for i in v]
        else:
            out[k] = v
    return out


def merge_allof(schema):
    if not isinstance(schema, dict) or "allOf" not in schema:
        return schema
    merged = {"type": "object", "properties": {}, "required": []}
    for part in schema["allOf"]:
        part = merge_allof(part)
        merged["properties"].update(part.get("properties") or {})
        merged["required"] += part.get("required") or []
    return merged


def fmt_type(s):
    if not isinstance(s, dict):
        return "?"
    t = s.get("type", "object" if "properties" in s else "?")
    if t == "array":
        return f"array of {fmt_type(s.get('items', {}))}"
    if "enum" in s:
        return t + " (" + " | ".join(str(e) for e in s["enum"]) + ")"
    if s.get("format"):
        return f"{t} ({s['format']})"
    return t


def render_body(schema, indent=0, depth=0):
    schema = merge_allof(schema)
    lines = []
    if not isinstance(schema, dict):
        return lines
    required = set(schema.get("required") or [])
    props = schema.get("properties") or {}
    if not props and schema.get("type") == "array":
        lines.append(" " * indent + f"- array of {fmt_type(schema.get('items', {}))}")
        return lines
    for name, p in props.items():
        p = merge_allof(p)
        tag = "**required**" if name in required else "optional"
        desc = (p.get("description") or "").strip().replace("\n", " ")
        ex = f" — e.g. `{p['example']}`" if "example" in p else ""
        lines.append(" " * indent + f"- `{name}` ({fmt_type(p)}, {tag}){': ' + desc if desc else ''}{ex}")
        sub = p.get("items") if p.get("type") == "array" else p
        if isinstance(sub, dict) and sub.get("properties") and depth < 3:
            lines += render_body(sub, indent + 2, depth + 1)
    return lines


def main(path):
    spec = yaml.safe_load(open(path))
    paths = spec.get("paths") or {}
    out = [
        "# API request schemas",
        "",
        f"Generated from Netzilo Server's OpenAPI description on {date.today().isoformat()} by `scripts/gen-api-schemas.py`.",
        "",
        "**Read the schema before any write.** Every `POST`/`PUT`/`PATCH`/`DELETE` below lists the",
        "required fields; a body missing one is rejected with 422. The live, version-exact copy is",
        "served to admins at `GET /api/support/openapi.yml`; the Netzilo dashboard's AI assistant",
        "reads it with its `netzilo_api_schema` tool before proposing a change. Use this file when",
        "you have no server to ask.",
        "",
        "Base URL: `https://<server>/api`; every path below is relative to `https://<server>`.",
        "",
    ]
    for p in sorted(paths):
        ops = paths[p] or {}
        for m in METHODS:
            if m not in ops:
                continue
            op = resolve(spec, ops[m])
            out.append(f"## `{m.upper()} {p}`")
            if op.get("summary") or op.get("description"):
                out.append("")
                out.append((op.get("summary") or op.get("description") or "").strip())
            params = [x for x in op.get("parameters", []) if isinstance(x, dict)]
            if params:
                out.append("")
                out.append("Parameters:")
                for x in params:
                    out.append(f"- `{x.get('name')}` ({x.get('in')}, {'required' if x.get('required') else 'optional'}){': ' + x['description'].strip() if x.get('description') else ''}")
            body = ((op.get("requestBody") or {}).get("content") or {}).get("application/json", {}).get("schema")
            if body:
                out.append("")
                out.append("Request body (JSON):")
                out += render_body(body) or ["- (object, see live spec)"]
            responses = op.get("responses") or {}
            if responses:
                out.append("")
                out.append("Responses: " + ", ".join(
                    f"`{code}` {r.get('description', '').strip() if isinstance(r, dict) else r}" for code, r in responses.items()
                ))
            out.append("")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
