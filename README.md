# Temp Mail Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Mail.tm API](https://img.shields.io/badge/Mail.tm-API-green)
![CI](https://github.com/A-z-exe/temp-mail-generator/actions/workflows/ci.yml/badge.svg)

Creates a disposable inbox through the [Mail.tm](https://mail.tm) API, watches it for
a while, and pulls verification codes out of incoming mail. Useful for testing your
own sign-up flows without handing out a real address.

## Features

- Creates a fresh Mail.tm address and a random password per run
- Polls the inbox and prints each new message
- Extracts verification codes with ordered regex rules (subject and body)
- Saves codes to `codes.txt` and the account to `account_info.json`
- Optional `--open` hands the inbox to the Mail.tm web UI

## Requirements

- Python 3.9+
- `requests`, `colorama` (see `requirements.txt`)

## Install

```bash
git clone https://github.com/A-z-exe/temp-mail-generator.git
cd temp-mail-generator
python -m pip install -r requirements.txt
```

## Usage

```bash
# watch the inbox for 60 seconds, checking every 5 seconds
python temp-mail-no-browser.py

# longer window, faster polling, open the web inbox afterwards
python temp-mail-no-browser.py --wait 300 --interval 3 --open
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--wait` | `60` | Seconds to keep watching for new mail |
| `--interval` | `5` | Seconds between inbox checks |
| `--open` | off | Open `mail.tm` in the browser after creating the inbox |

## Output

- `codes.txt` — one `address: code` line per detected code
- `account_info.json` — address, password, token and creation time

Both files are git-ignored.

## Notes

- Mail.tm is a third-party service with its own rate limits; the tool stops with a
  clear message if the API is unreachable.
- The standalone-code fallback matches six-character alphanumeric tokens, so a code
  can be missed when a provider formats it differently. When that happens, open the
  inbox with `--open` and read the message yourself.
- Only use disposable inboxes for services where this is allowed, and never for
  accounts you need to keep.

## License

MIT — see [LICENSE](LICENSE).

Author: [AmirHossein Zarei](https://a-z-exe.github.io/) · [GitHub](https://github.com/A-z-exe)
