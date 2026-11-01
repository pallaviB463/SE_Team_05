# Issues Found and Fixed

Line numbers refer to the **original** `event_manager.py`. Before/after reports are in `reports/before/` and `reports/after/`.

**Results:** Pylint 4.64/10 → 10.00/10 · Bandit 4 issues → 0 · Flake8 4 issues → 0

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command injection (Bandit B605) | Security – High | 56 | `os.system("lp badges_" + eventName + ".txt")` runs a shell command built from the event name, so a name like `x; rm -rf ~` would run extra commands. | Replaced with `subprocess.run([lp_path, file_name], check=True)`: list arguments and no shell. The event name is checked with a regex first, and `lp` is found with `shutil.which`. |
| Mutable default argument (Pylint W0102) | Bug – High | 9 | `guests=[]` makes one list that every call shares. Both events used the same guest list, so Alumni Dinner said it was full and refused Meena while having no guests of its own. | Changed the default to `guests=None` and create a new `[]` inside the function. Now each event gets its own list, and Alumni Dinner shows 1 seat left. |
| Unsafe deserialisation with pickle (Bandit B301, B403) | Security – Medium | 2, 51 | `pickle.load` can run arbitrary code if `events.pkl` is changed or comes from someone else. | Switched saving and loading to `json` (`events.json`), which only reads data. Files are opened with `encoding="utf-8"`. |
| Weak random generator (Bandit B311) | Security – Low | 72 | `random.choice` is not meant for anything that needs to be fair or unpredictable, like a prize draw. | Used `secrets.choice` instead. |
| Unused argument (Pylint W0613) | Bug / Code quality – Medium | 39 | `guestReport` took a `sortOrder` argument but never used it, so passing it did nothing. | Implemented it: `"name"` sorts A–Z, `"reverse"` sorts Z–A, anything else raises `ValueError`. |
| Non-snake_case names (Pylint C0103) | Style – Low | 9–59 | Functions and arguments used camelCase (`createEvent`, `eventName`, …), which goes against PEP 8. | Renamed everything to snake_case (`create_event`, `event_name`, …). |
| Missing docstrings (Pylint C0114, C0116) | Documentation – Low | 1, 9–59 | The module and functions had no docstrings. | Added a module docstring and one for every function. |
| Unnecessary `else` after `return` (Pylint R1705) | Code quality – Low | 33–36 | `else` is not needed after a `return`. | Removed the `else` and moved the second `return` back one level. |
| `main()` runs on import | Code quality – Low | 79 | `main()` was called at module level, so just importing the file would run the demo. | Wrapped it in `if __name__ == "__main__":`. |
| Missing whitespace after comma (Flake8 E231) | Style – Low | 61 | `"Rooftop",2` | Added a space: `"Rooftop", 2`. |
| Missing whitespace around operator (Flake8 E225) | Style – Low | 66 | `left=seatsLeft(...)` | Changed to `left = seats_left(...)`. |
| Inline comment spacing (Flake8 E261) | Style – Low | 75 | Only one space before `# reload ...`. | Used two spaces before the inline comment. |
| Blank lines after function (Flake8 E305) | Style – Low | 79 | Only one blank line between the last function and top-level code. | Used two blank lines before the `if __name__` guard. |

## Commits

1. `Fix Bandit security issues`: B605, B301/B403, B311
2. `Fix Pylint issues (score 4.64 -> 10.00)`: W0102, C0103, C0114/C0116, W0613, R1705, main guard
3. `Fix Flake8 style issues`: E231, E225, E261, E305
