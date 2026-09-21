#!/usr/bin/env python3
"""wordcount - count the words in one text file.

A word is any maximal run of non-whitespace characters, so spaces, tabs and
newlines all separate words and a run of them separates only once.  The file is
read as UTF-8 text and streamed in fixed-size chunks, so memory stays bounded
even for very large files.

Usage:
    python wordcount.py FILE

Exit codes:
    0  the file was counted and the total was written to stdout
    1  the file could not be read (missing, directory, permission, bad UTF-8)
    2  the command line itself was wrong (missing or extra FILE argument)
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from typing import IO, Optional

__version__ = "1.0.0"

PROGRAM = "wordcount"

# 1 MiB of characters per read: bounded memory on huge files, few syscalls.
CHUNK_SIZE = 1 << 20

EXIT_OK = 0
EXIT_FILE_ERROR = 1
EXIT_USAGE_ERROR = 2

DESCRIPTION = "Count the words in one text file."

EPILOG = """\
count rule:
  a word is any maximal run of non-whitespace characters, so spaces, tabs and
  newlines all separate words, and a run of them separates only once; a 0-byte
  or whitespace-only file counts as 0

example:
  $ python wordcount.py notes.txt
  4

exit codes:
  0 counted   1 file problem   2 usage problem
"""


class FileProblem(Exception):
    """The input file cannot be used.  The message goes to stderr, exit code 1."""


def build_parser(prog: str) -> argparse.ArgumentParser:
    """Build the command-line parser: one positional FILE argument and --help."""
    parser = argparse.ArgumentParser(
        prog=prog,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        help="path of the text file whose words should be counted",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    return parser


def count_words(stream: IO[str]) -> int:
    """Count words in a text stream, reading it in bounded chunks.

    The chunking must not change the answer: a word split across a chunk
    boundary is counted once per half and then corrected down by one.
    """
    total = 0
    word_is_open = False  # True when the previous chunk ended inside a word
    while True:
        chunk = stream.read(CHUNK_SIZE)
        if not chunk:
            return total
        total += len(chunk.split())
        if word_is_open and not chunk[0].isspace():
            total -= 1  # the word that started in the previous chunk ends here
        word_is_open = not chunk[-1].isspace()


def count_file(path: str) -> int:
    """Count the words in the file at *path*.

    Raises FileProblem with a short reason when the file cannot be read; no
    OSError ever escapes, so a normal user never sees a traceback.
    """
    try:
        with open(path, "r", encoding="utf-8") as stream:
            return count_words(stream)
    except UnicodeDecodeError as exc:
        raise FileProblem(f"not valid UTF-8 text (byte {exc.start})") from exc
    except IsADirectoryError as exc:
        raise FileProblem("it is a directory") from exc
    except FileNotFoundError as exc:
        raise FileProblem("no such file or directory") from exc
    except PermissionError as exc:
        raise FileProblem("permission denied") from exc
    except OSError as exc:
        raise FileProblem(exc.strerror or exc.__class__.__name__) from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the tool; return the process exit code."""
    prog = os.path.basename(sys.argv[0]) or PROGRAM
    # argparse writes the usage error to stderr and exits 2 by itself.
    args = build_parser(prog).parse_args(argv)
    try:
        total = count_file(args.file)
    except FileProblem as problem:
        print(f"{prog}: cannot read {args.file!r}: {problem}", file=sys.stderr)
        return EXIT_FILE_ERROR
    print(total)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
