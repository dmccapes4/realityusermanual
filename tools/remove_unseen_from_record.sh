#!/usr/bin/env bash
# Walk one markdown file; strip formatting symbols the renderer hides (the unseen).
set -euo pipefail

echo "systematically removing the unseen from the record"

root="$(cd "$(dirname "$0")/.." && pwd)"
md="${1:-$root/src/phase2/-25.md}"
work="$root/.REMOVING_UNSEEN_FROM_RECORD"
out="$work/plain_record.txt"
unseen="$work/unseen_symbols.txt"

mkdir -p "$work"
: >"$out"
: >"$unseen"

while IFS= read -r line || [[ -n $line ]]; do
    # Visible text: peel markdown adornment, leave the spoken record.
    plain=$(
        printf '%s\n' "$line" | sed -E \
            -e 's/^#{1,6}[[:space:]]+//' \
            -e 's/^>[[:space:]]?//' \
            -e 's/^[-*+][[:space:]]+//' \
            -e 's/^[0-9]+[.)][[:space:]]+//' \
            -e 's/\*\*([^*]*)\*\*/\1/g' \
            -e 's/\*([^*]*)\*/\1/g' \
            -e 's/`([^`]*)`/\1/g' \
            -e 's/^\|//' -e 's/\|$//' -e 's/[|]//g' \
            -e 's/^```.*$//'
    )
    printf '%s\n' "$plain" >>"$out"

    # Unseen layer: symbols that structured the line but do not render as words.
    symbols=$(printf '%s' "$line" | tr -cd '#>*`|[]_-')
    if [[ -n $symbols ]]; then
        printf '%s\n' "$symbols" >>"$unseen"
    fi
done <"$md"

echo "lines: $(wc -l <"$out" | tr -d ' ')"
