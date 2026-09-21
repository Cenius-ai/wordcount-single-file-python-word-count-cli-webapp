"""Tests for wordcount.py.

Development-only: this file is not part of the shipped artifact.  Run it with
either of the standard runners from the repository root:

    python3 -m unittest -v
    python3 -m pytest -q
"""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import wordcount

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(REPO_ROOT, "wordcount.py")


def run_cli(*args, text=True):
    """Run the real command in a child process, exactly as a user would."""
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=text,
        cwd=REPO_ROOT,
        check=False,
    )


class TempFileMixin:
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmpdir = self._tmp.name

    def write(self, name, data, encoding="utf-8"):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w", encoding=encoding, newline="") as handle:
            handle.write(data)
        return path

    def write_bytes(self, name, data):
        path = os.path.join(self.tmpdir, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path


class TestCountRule(unittest.TestCase):
    """The counting rule itself, exercised in-process."""

    def count(self, text):
        return wordcount.count_words(io.StringIO(text))

    def test_maximal_run_of_non_whitespace_is_one_word(self):
        self.assertEqual(self.count("the quick brown fox"), 4)

    def test_empty_text_is_zero(self):
        self.assertEqual(self.count(""), 0)

    def test_whitespace_only_text_is_zero(self):
        self.assertEqual(self.count(" \t\n\r\n   \t "), 0)

    def test_non_ascii_words_follow_the_same_rule(self):
        self.assertEqual(self.count("café olé — naïve résumé"), 5)

    def test_whitespace_runs_separate_words_only_once(self):
        # Tabs, repeated spaces, CRLF and a form feed all count as one break.
        self.assertEqual(self.count("alpha   beta\tgamma\r\ndelta\x0cepsilon"), 5)

    def test_punctuation_only_token_is_a_word(self):
        # The rule is whitespace-delimited, not dictionary-based, so punctuation
        # and hyphenated or elided forms each stay a single word.
        self.assertEqual(self.count("wait... don't re-enter"), 3)

    def test_word_split_across_a_chunk_boundary_is_counted_once(self):
        # A tiny chunk size forces the streaming correction path to run.
        with mock.patch.object(wordcount, "CHUNK_SIZE", 4):
            self.assertEqual(self.count("word"), 1)
            self.assertEqual(self.count("two words"), 2)
            self.assertEqual(self.count("many many many words"), 4)
            self.assertEqual(self.count("trailing space "), 2)
            self.assertEqual(self.count("   "), 0)


class TestCommandLine(TempFileMixin, unittest.TestCase):
    """End-to-end runs of the real command."""

    def test_normal_file_prints_the_count(self):
        path = self.write("fox.txt", "the quick brown fox\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "4\n")
        self.assertEqual(result.stderr, "")

    def test_stdout_bytes_are_exactly_the_number_and_a_newline(self):
        path = self.write("fox.txt", "the quick brown fox\n")
        result = run_cli(path, text=False)
        self.assertEqual(result.stdout, b"4\n")
        self.assertEqual(result.stderr, b"")

    def test_empty_file_prints_zero(self):
        path = self.write("empty.txt", "")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "0\n")

    def test_whitespace_only_file_prints_zero(self):
        path = self.write("blank.txt", "  \n\t\n \r\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "0\n")

    def test_non_ascii_words_are_counted(self):
        path = self.write("cafe.txt", "café olé\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "2\n")

    def test_filename_with_spaces_is_one_argument(self):
        path = self.write("a file with spaces.txt", "one two three\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "3\n")

    def test_mixed_whitespace_and_crlf_do_not_add_phantom_words(self):
        path = self.write("mixed.txt", "alpha   beta\tgamma\r\ndelta\r\n\r\nepsilon")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "5\n")

    def test_missing_argument_is_a_usage_error(self):
        result = run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("FILE", result.stderr)

    def test_extra_argument_is_a_usage_error(self):
        first = self.write("a.txt", "one\n")
        second = self.write("b.txt", "two\n")
        result = run_cli(first, second)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn(second, result.stderr)

    def test_help_documents_file_argument_rule_and_example(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("wordcount.py", result.stdout)
        self.assertIn("FILE", result.stdout)
        self.assertIn("non-whitespace", result.stdout)
        self.assertIn("python wordcount.py notes.txt", result.stdout)

    def test_version_exits_zero(self):
        result = run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn(wordcount.__version__, result.stdout)

    def test_success_output_carries_no_banner_or_ansi_escapes(self):
        path = self.write("fox.txt", "the quick brown fox\n")
        result = run_cli(path)
        self.assertNotIn("\x1b", result.stdout)
        self.assertNotIn("\x1b", result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), 1)


class TestFileProblems(TempFileMixin, unittest.TestCase):
    """Every realistic file problem: one stderr line, exit 1, empty stdout."""

    def test_missing_path_names_the_path(self):
        missing = os.path.join(self.tmpdir, "missing.txt")
        result = run_cli(missing)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn(missing, result.stderr)
        self.assertIn("no such file", result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1)

    def test_directory_path_is_rejected(self):
        result = run_cli(self.tmpdir)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("directory", result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1)

    def test_invalid_utf8_names_the_file_and_the_encoding(self):
        path = self.write_bytes("latin1.txt", b"caf\xe9 ol\xe9\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn(path, result.stderr)
        self.assertIn("UTF-8", result.stderr)

    def test_unreadable_file_is_reported_without_a_traceback(self):
        path = self.write("secret.txt", "one two\n")
        with mock.patch(
            "builtins.open", side_effect=PermissionError(13, "Permission denied")
        ):
            result = self._run_in_process([path])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("permission denied", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    @unittest.skipIf(
        hasattr(os, "geteuid") and os.geteuid() == 0,
        "root bypasses file permissions, so a 0-mode file stays readable",
    )
    def test_unreadable_file_on_disk(self):  # pragma: no cover - skipped as root
        path = self.write("locked.txt", "one two\n")
        os.chmod(path, 0o000)
        self.addCleanup(os.chmod, path, 0o600)
        result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("permission denied", result.stderr)

    def test_file_deleted_before_the_read_is_reported_cleanly(self):
        path = self.write("gone.txt", "one two\n")
        with mock.patch(
            "builtins.open", side_effect=FileNotFoundError(2, "No such file")
        ):
            result = self._run_in_process([path])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("no such file", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def _run_in_process(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = wordcount.main(argv)
        return subprocess.CompletedProcess(argv, code, out.getvalue(), err.getvalue())


class TestLargeFile(unittest.TestCase):
    """The 100 MB measurement, gated so the default suite stays fast.

    Run it with:  WORDCOUNT_PERF=1 python3 -m unittest -v
    """

    LINE = "alpha beta gamma delta epsilon zeta eta theta iota kappa\n"
    TARGET_BYTES = 100 * 1024 * 1024

    @unittest.skipUnless(
        os.environ.get("WORDCOUNT_PERF") == "1",
        "set WORDCOUNT_PERF=1 to run the measured 100 MB run",
    )
    def test_hundred_megabyte_file_counts_in_under_ten_seconds(
        self,
    ):  # pragma: no cover
        import resource
        import time

        payload = self.LINE.encode("utf-8")
        words_per_line = len(self.LINE.split())
        lines = self.TARGET_BYTES // len(payload)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "big.txt")
            # Written line by line so this test process stays small: a parent
            # holding the whole 100 MB would inflate the child's forked RSS.
            with open(path, "wb") as handle:
                for _ in range(lines):
                    handle.write(payload)
            before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            started = time.monotonic()
            result = run_cli(path)
            elapsed = time.monotonic() - started
            peak_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss - before
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, f"{lines * words_per_line}\n")
        self.assertLess(elapsed, 10.0, f"100 MB took {elapsed:.2f}s")
        # Bounded memory: the peak is the interpreter, not the file.
        self.assertLess(
            peak_kb * 1024, self.TARGET_BYTES // 2, f"peak RSS {peak_kb} kB"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
