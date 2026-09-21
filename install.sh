#!/usr/bin/env bash
# Setup for wordcount.
#
# The tool is standard-library Python, so there is nothing to download: this
# script checks the interpreter, verifies the module, installs the optional
# `wordcount` console script, runs a smoke test, and EXITS.  It never starts a
# long-running process and never installs a system package.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "wordcount: '$PYTHON' is not on PATH; install Python 3.9+ (see INSTALL.md)" >&2
  exit 1
fi

echo "==> checking the interpreter"
"$PYTHON" - <<'PY'
import sys

if sys.version_info < (3, 9):
    sys.exit("wordcount: Python 3.9+ is required, found %s" % sys.version.split()[0])
print("    %s" % sys.version.split()[0])
PY

echo "==> checking the shipped module compiles and imports"
"$PYTHON" -m py_compile wordcount.py
"$PYTHON" -c "import wordcount"

echo "==> installing the optional 'wordcount' console script"
# Offline and build-isolation free: the fallback below is the plain module run.
if "$PYTHON" -m pip install --quiet --disable-pip-version-check \
        --no-build-isolation --no-index -e . 2>/dev/null; then
  echo "    console script ready: wordcount FILE"
else
  echo "    note: console script not installed; 'python3 wordcount.py FILE' works as-is" >&2
fi

echo "==> smoke test"
smoke_file="$(mktemp)"
trap 'rm -f "$smoke_file"' EXIT
printf 'the quick brown fox\n' > "$smoke_file"
count="$("$PYTHON" wordcount.py "$smoke_file")"
if [ "$count" != "4" ]; then
  echo "wordcount: smoke test failed: expected 4, got '$count'" >&2
  exit 1
fi
echo "    counted 4 words, exit 0"

echo
echo "Setup complete."
echo "  count a file : python3 wordcount.py FILE"
echo "  see the demo : bash demo.sh"
echo "  run the tests: python3 -m unittest -v"
