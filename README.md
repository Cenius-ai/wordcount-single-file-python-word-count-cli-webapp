# wordcount — single-file Python word-count CLI — complete Full-stack app command-line tool example app

A Full-stack app command-line tool, open-source and ready to self-host: that's **wordcount — single-file Python word-count CLI**. We'll build wordcount.py, a single-file, standard-library-only Python 3 command-line tool that counts the words in one text file. wordcount — single-file Python word-count CLI ships complete — source, design assets, seed data — under the Apache-2.0 license; no cloud account needed. [Remix wordcount — single-file Python word-count CLI on cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp) for a custom build.


[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Stack](https://img.shields.io/badge/Stack-Full--stack%20app-3b82f6) [![Built with cenius.ai](https://img.shields.io/badge/Built%20with-cenius.ai-8b5cf6)](https://cenius.ai)

[![Open in cenius.ai](https://img.shields.io/badge/▶%20Open%20%26%20edit%20in-cenius.ai-8b5cf6?style=for-the-badge)](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp)

> **▶ [Open & edit in cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp)** — one click to an editable workspace: describe changes in plain English, get an instant preview, one-click deploy and host. Modifications made on the platform come with full rebrand & relicense rights.

_Local clone? See [Quick start](#quick-start) below. cenius.ai is the zero-setup path._

## Demo

![wordcount — single-file Python word-count CLI demo — command-line tool built with Full-stack app](.github/media/hero.gif)

▶ **[Video walkthrough](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp)** — see the app in action on the cenius.ai project page · [MP4 file](.github/media/demo.mp4)

## Quick start

```bash
./install.sh   # installs dependencies + seeds demo data
```

See [`INSTALL.md`](INSTALL.md) for full setup and usage instructions.

## Usage guide

### Count one file

```sh
python3 wordcount.py report.txt
## 1012
```

The output is exactly the integer and a newline. Nothing else is printed on
success — no filename, no banner, no colour — so the result composes with
pipes, redirection and command substitution:

```sh
python3 wordcount.py report.txt > count.txt
total=$(python3 wordcount.py report.txt)
echo "the report has $total words"
```

### Quote paths that contain spaces

```sh
python3 wordcount.py "draft chapter one.txt"
## 8402
```

The shell hands the quoted path over as one `FILE` argument, so spaces are
fine. For a filename that itself begins with a dash, use `--`:

```sh
python3 wordcount.py -- -draft.txt
```

### Drive your scripts from the exit code

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

### What counts as a word

The rule is "any maximal run of non-whitespace characters". No dictionary and
no locale are consulted, so results are identical on macOS, Linux and WSL.

_Full guide: [`USAGE.md`](USAGE.md)_

## Features

- Count words in one file
- Input validation and error reporting
- Command-line interface and help

## Architecture

Folder layout: `examples/`. The setup script (`install.sh`) installs runtime dependencies and loads a starter dataset so the app is immediately usable. Built in Full-stack app (16 files). Installation walkthrough: [`INSTALL.md`](INSTALL.md).

## FAQ

### How do I self-host wordcount — single-file Python word-count CLI?

Pull the repo, run `./install.sh`, and you are up — the script installs packages and pre-seeds the database. [`INSTALL.md`](INSTALL.md) covers any platform-specific tweaks.

### How do I customise wordcount — single-file Python word-count CLI's branding?

Rebranding is straightforward under the MIT license — change what you want in the source. Or [open it on cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp): the platform handles the changes and grants full rebrand rights on the result.

### Can non-developers customise wordcount — single-file Python word-count CLI?

Non-developers can use [cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp) to make changes. Describe your goal in everyday language and the platform delivers an updated, ready-to-run project — zero coding on your part.

### How is wordcount — single-file Python word-count CLI built technically?

The app is built with Full-stack app. What you see in this repo is the full production source, demo data included. Highlights include count words in one file.

### Is it OK to ship wordcount — single-file Python word-count CLI as part of a product?

Yes — Apache-2.0-licensed, so commercial use, modification, and distribution are all permitted. Read the full terms in [LICENSE](LICENSE).

## License & rebranding

Released under the [Apache License 2.0](LICENSE) (© 2026 Cenius AI) — free for personal and commercial use. The Cenius name/logo are trademarks (see NOTICE).

**Need a customized version?** [Remix this app on cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp) — modifications made on the platform come with **full rebrand & relicense rights** over your derivative.

## Built with cenius.ai

This entire application — code, design, seeded demo data — was generated on **[cenius.ai](https://cenius.ai)** from a plain-English description.

- 🚀 [Build your own app on cenius.ai](https://cenius.ai)
- 🎛️ [Remix wordcount — single-file Python word-count CLI on the marketplace](https://cenius.ai/marketplace/p/wordcount-single-file-python-word-count-cli?ref=gh&utm_campaign=wordcount-single-file-python-word-count-cli-webapp) — open it in a workspace, prompt for changes, and ship your own version.

More open-source apps: [the Cenius-ai catalog](https://github.com/Cenius-ai) · [showcase index](https://github.com/Cenius-ai/showcase)
