#!/usr/bin/env bash
# wordcount demo - a non-interactive tour of the whole tool.
#
# It runs the real command over the bundled examples and the edge cases, shows
# every result as an aligned column row, and exits non-zero if any observed
# behaviour drifts from what the tool documents.  Nothing here is interactive
# and nothing outside this checkout is touched.
#
# Design tokens - the CLI equivalent of a CSS :root block:
#   --accent   oklch(0.58 0.12 201)  ==  #008e97  ==  ANSI truecolor 38;2;0;142;151
#   --surface  terminal dark: body text keeps the terminal's own foreground
#   --type     system monospace, one compact ramp, aligned columns
#   --signal   the accent never travels alone; each accented cell carries a
#              glyph (pass/fail) so the signal survives a monochrome terminal
set -uo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
RULE_WIDTH=76

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  ACCENT=$'\033[38;2;0;142;151m'
  BOLD=$'\033[1m'
  DIM=$'\033[2m'
  OFF=$'\033[0m'
else
  ACCENT=""; BOLD=""; DIM=""; OFF=""
fi

work="$(mktemp -d)"
err_file="$work/stderr.txt"
trap 'rm -rf "$work"' EXIT

rule() {
  local i
  for ((i = 0; i < RULE_WIDTH; i++)); do printf '%s' "─"; done
  printf '\n'
}

heading() {
  printf '\n%s%s%s\n' "$BOLD" "$1" "$OFF"
  printf '%s' "$DIM"; rule; printf '%s' "$OFF"
}

row() {  # row <mark> <case> <exit> <stdout> <stderr>
  printf '  %-34s %s %-4s %-8s %s\n' "$2" "$1" "$3" "$4" "$5" | sed 's/[[:space:]]*$//'
}

columns() {
  printf '%s  %-34s %-6s %-8s %s%s\n' "$DIM" "case" "exit" "stdout" "stderr (first line)" "$OFF"
}

pass=0
total=0
failed=""

# check <case> <expected stdout> <expected exit> -- <command...>
check() {
  local case_label="$1" want_out="$2" want_code="$3"
  shift 4
  local out err code
  code=0
  out="$("$@" 2>"$err_file")" || code=$?
  err="$(head -n 1 "$err_file" | cut -c1-30)"
  total=$((total + 1))
  if [ "$out" = "$want_out" ] && [ "$code" = "$want_code" ]; then
    pass=$((pass + 1))
    row "${ACCENT}✓${OFF}" "$case_label" "$code" "${out:-—}" "$err"
  else
    failed="$failed [$case_label]"
    row "${ACCENT}✗${OFF}" "$case_label" "$code≠$want_code" "want ${want_out:-—}" "$err"
  fi
}

# --- fixtures -----------------------------------------------------------------
printf 'alpha   beta\tgamma\r\ndelta\r\n\r\nepsilon' > "$work/mixed.txt"
printf '   \n\t\n \r\n' > "$work/whitespace.txt"
printf 'one two three\n' > "$work/a file with spaces.txt"
printf 'caf\351 ol\351\n' > "$work/latin1.txt"   # 0xE9 is not valid UTF-8

printf '%swordcount%s %s\n' "$BOLD" "$OFF" "one file in, one integer out"
printf '%s  a word is any maximal run of non-whitespace characters%s\n' "$DIM" "$OFF"

heading "usage - python3 wordcount.py --help"
"$PYTHON" wordcount.py --help | sed -e 's/^/  /' -e 's/[[:space:]]*$//'

heading "counting - the bundled examples"
columns
check "notes.txt"                 "24" 0 -- "$PYTHON" wordcount.py examples/notes.txt
check "cafe.txt (non-ASCII)"      "7"  0 -- "$PYTHON" wordcount.py examples/cafe.txt
check "empty.txt (0 bytes)"       "0"  0 -- "$PYTHON" wordcount.py examples/empty.txt
check "whitespace-only.txt"       "0"  0 -- "$PYTHON" wordcount.py "$work/whitespace.txt"
check "mixed tabs + CRLF"         "5"  0 -- "$PYTHON" wordcount.py "$work/mixed.txt"
check "a file with spaces.txt"    "3"  0 -- "$PYTHON" wordcount.py "$work/a file with spaces.txt"

heading "failure handling - one stderr line, no traceback"
columns
check "missing path"              ""   1 -- "$PYTHON" wordcount.py "$work/missing.txt"
check "directory path"            ""   1 -- "$PYTHON" wordcount.py examples
check "not valid UTF-8"           ""   1 -- "$PYTHON" wordcount.py "$work/latin1.txt"
check "no FILE argument"          ""   2 -- "$PYTHON" wordcount.py
check "two FILE arguments"        ""   2 -- "$PYTHON" wordcount.py examples/notes.txt examples/cafe.txt

printf '\n%s' "$DIM"; rule; printf '%s' "$OFF"
if [ -z "$failed" ]; then
  printf '  %swordcount%s %s every case matched%s   %s✓%s %s/%s checks\n' \
    "$BOLD" "$OFF" "$DIM" "$OFF" "$ACCENT" "$OFF" "$pass" "$total"
  exit 0
fi
printf '  %swordcount%s%s unexpected results:%s %s\n' "$BOLD" "$OFF" "$DIM" "$OFF" "$failed"
exit 1
