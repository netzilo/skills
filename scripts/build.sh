#!/usr/bin/env bash
#
# Regenerate every generated artefact in this repository, then validate it.
#
#     scripts/build.sh [path/to/openapi.yml | https://<server>/api/support/openapi.yml]
#
# With an argument, references/33-api-request-schemas.md is regenerated from
# that Netzilo Server OpenAPI description first — a local file, or the URL the
# server itself serves to admins (set NETZILO_API_TOKEN for the token). Without
# one, 33 is left as committed and the build needs nothing but this checkout.
#
# Order matters: the API schemas change section headings and file size, so
# front matter must be regenerated after them, and validated last.
#
# Requires: python3 with PyYAML.

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(dirname "$here")"
schemas="$repo/netzilo-admin/references/33-api-request-schemas.md"

if [ "$#" -gt 1 ]; then
    echo "usage: scripts/build.sh [path/to/openapi.yml | https://<server>/api/support/openapi.yml]" >&2
    exit 2
fi

if [ "$#" -eq 1 ]; then
    spec="$1"
    case "$spec" in
        http://*|https://*) ;;
        *) [ -f "$spec" ] || { echo "no such OpenAPI file: $spec" >&2; exit 2; } ;;
    esac
    echo "==> generating references/33-api-request-schemas.md from $spec"
    tmp="$(mktemp)"
    trap 'rm -f "$tmp"' EXIT
    python3 "$here/gen-api-schemas.py" "$spec" > "$tmp"
    mv "$tmp" "$schemas"
    trap - EXIT
else
    echo "==> no OpenAPI description given; keeping references/33-api-request-schemas.md as committed"
fi

echo "==> writing reference front matter"
python3 "$here/gen-frontmatter.py"

echo "==> validating"
python3 "$here/check-skills.py"
