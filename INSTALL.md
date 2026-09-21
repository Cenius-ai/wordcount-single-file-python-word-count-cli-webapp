# Installing and running wordcount

`wordcount.py` is standard-library Python. There is nothing to download, no
database, no service and no build step — a fresh checkout runs immediately.

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.9 or newer | `python3 --version`; already present on macOS, most Linux distributions and WSL |
| A POSIX shell | `bash`/`sh` for `demo.sh` and `install.sh` |
| `pip` (optional) | only used to install the optional `wordcount` console script |

Nothing is installed system-wide. `install.sh` never calls `sudo`, `apt`,
`brew` or any other package manager, and the tool needs no network at any
point.

## 1. Set up (one command, then it exits)

```sh
bash install.sh
```

It checks the interpreter, byte-compiles and imports `wordcount.py`, installs
the optional console script (`pip install -e .`, offline and without build
isolation), runs a smoke test, prints what to do next and **exits**. It does
not start a long-running process. If `pip` is unavailable the script says so
and continues — `python3 wordcount.py FILE` needs no install at all.

It is safe to re-run.

## 2. Count a file

```sh
python3 wordcount.py FILE
```

`FILE` is one path; quote it if it contains spaces. The output is one bare
integer on stdout. `--help` prints the usage block, the count rule and an
example. If `install.sh` installed the console script you can also run:

```sh
wordcount FILE
```

## 3. See it work end to end

```sh
bash demo.sh
```

Non-interactive: it runs the real command over the bundled examples and the
edge cases, prints an aligned table of results, and exits non-zero if any
observed behaviour drifts from what the tool documents. It creates its
fixtures in a temporary directory and removes them on exit.

## 4. Run the tests (development only)

The shipped tool has no dependencies, so the suite runs on the standard
library alone:

```sh
python3 -m unittest -v
```

`pytest` works too, if you prefer it:

```sh
pip3 install -r requirements-dev.txt    # pytest==8.3.4
python3 -m pytest -q
```

The 100 MB measurement is gated so the default run stays fast:

```sh
WORDCOUNT_PERF=1 python3 -m unittest test_wordcount.py -v
```

## Configuration

None. The tool reads **no environment variables** and no config file, so there
is deliberately no `.env.example`: `requirements.txt` documents that the
runtime is standard library only, and the only optional settings are the
`PYTHON` variable that `install.sh`/`demo.sh` use to pick an interpreter and
the `NO_COLOR` convention that `demo.sh` honours.

## Uninstalling

Nothing is placed outside the checkout except the optional console script:

```sh
pip3 uninstall wordcount
```

and delete the directory. `python3 wordcount.py FILE` keeps working from the
checkout either way.
