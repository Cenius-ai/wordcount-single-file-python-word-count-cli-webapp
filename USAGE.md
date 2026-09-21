# Using wordcount

## Count one file

```sh
python3 wordcount.py report.txt
# 1012
```

The output is exactly the integer and a newline. Nothing else is printed on
success — no filename, no banner, no colour — so the result composes with
pipes, redirection and command substitution:

```sh
python3 wordcount.py report.txt > count.txt
total=$(python3 wordcount.py report.txt)
echo "the report has $total words"
```

## Quote paths that contain spaces

```sh
python3 wordcount.py "draft chapter one.txt"
# 8402
```

The shell hands the quoted path over as one `FILE` argument, so spaces are
fine. For a filename that itself begins with a dash, use `--`:

```sh
python3 wordcount.py -- -draft.txt
```

## Drive your scripts from the exit code

| Code | Meaning | What a script should do |
|---|---|---|
| `0` | counted; the integer is on stdout | read the count |
| `1` | the file could not be read | report the stderr line, skip the file |
| `2` | the command line was wrong | fix the invocation |

```sh
if count=$(python3 wordcount.py "$draft" 2>/dev/null); then
  echo "$draft: $count words"
else
  echo "$draft: skipped (exit $?)"
fi
```

A failing run writes **nothing** to stdout, so a captured variable is never
half-filled with an error message.

## What counts as a word

The rule is "any maximal run of non-whitespace characters". No dictionary and
no locale are consulted, so results are identical on macOS, Linux and WSL.

| Text | Count | Reason |
|---|---|---|
| `the quick brown fox` | 4 | four runs |
| `café olé — naïve` | 4 | accented letters are ordinary characters; `—` is a run of its own |
| `alpha   beta\tgamma\r\ndelta` | 4 | spaces, tabs and CRLF each separate once, however many of them |
| `wait... don't re-enter` | 3 | punctuation, apostrophes and hyphens do not split a word |
| `2025-01-01T09:30` | 1 | a timestamp is a single run |
| a 0-byte file | 0 | there is no run at all |
| a file of only spaces, tabs and newlines | 0 | nothing non-whitespace exists |

Wide whitespace counts as whitespace too: a non-breaking space (`U+00A0`) or a
form feed separates words exactly like an ordinary space.

## Error messages

Every failure is one line on stderr, naming the path and the reason, and the
exit code is `1`. No Python traceback is ever shown to a user.

```console
$ python3 wordcount.py notes.txt
wordcount.py: cannot read 'notes.txt': no such file or directory
$ python3 wordcount.py drafts/
wordcount.py: cannot read 'drafts': it is a directory
$ python3 wordcount.py protected.txt
wordcount.py: cannot read 'protected.txt': permission denied
$ python3 wordcount.py legacy-latin1.txt
wordcount.py: cannot read 'legacy-latin1.txt': not valid UTF-8 text (byte 3)
```

The file must be UTF-8 text. A Latin-1, UTF-16 or binary file is reported with
the byte offset where decoding failed, so you can convert it (for example with
`iconv -f latin1 -t utf8`) and count it after that.

If the file disappears or becomes unreadable between the path being typed and
the read (a race with a `mv`, a `rm` or an unmount), the same one-line message
is printed and the exit code is `1`.

## Usage errors

```console
$ python3 wordcount.py
usage: wordcount.py [-h] [--version] FILE
wordcount.py: error: the following arguments are required: FILE
$ python3 wordcount.py one.txt two.txt
usage: wordcount.py [-h] [--version] FILE
wordcount.py: error: unrecognized arguments: two.txt
```

Both exit `2`; one run sees exactly one file. `--help` exits `0` and prints the
count rule plus a copy-pasteable example, and `--version` prints the version.

## Large files

The file is streamed in 1 MiB chunks, so a 100 MB file counts in about 2.5
seconds with the interpreter's own memory footprint (measured numbers are in
`README.md`), and a multi-gigabyte log does not grow the process. Nothing is
buffered to disk and no temporary file is created.

## Self-check

```sh
bash demo.sh
```

prints the usage block, the counting table over the bundled examples, the
failure table for every error class, and a pass/fail summary; it exits non-zero
if anything moved.
