# Reflection

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 style issues (missing spaces, inline comment spacing, blank lines) and the Pylint docstring and naming warnings. The tool gives the exact line and the fix is mechanical. Renaming to snake_case took a little care because every call in `main()` had to be renamed too.

The hardest was the mutable default argument (`guests=[]`). Pylint only says "dangerous default value". The real effect only shows when you run the program: Alumni Dinner said it was full and refused Meena even though nobody had registered for it, because both events shared one list. Understanding why took longer than fixing it. Replacing `os.system` was also tricky: I had to keep the function working while removing the shell, and `subprocess` still causes Bandit warnings that had to be checked and justified.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes, partly. Bandit flags `import subprocess` (B404) and `subprocess.run` (B603) even when no shell is used and the input is validated. In my final code that use is safe, so I marked those two lines with `# nosec` and a comment explaining why. Bandit's B311 warning about `random.choice` is also borderline for a lucky draw at a small event, but switching to `secrets.choice` cost nothing, so I fixed it anyway. Some Pylint "convention" messages, like missing docstrings, are not bugs. They are style preferences that help readability.

### 3. How would you integrate static analysis tools into your actual software development workflow?

I would run Flake8 and Pylint in the editor while coding and add all three tools as pre-commit hooks, so problems are caught before a commit. In CI (for example GitHub Actions), every push or pull request would run Pylint with a minimum score (like `--fail-under=9.5`), Flake8, and Bandit, and the build would fail on any High or Medium Bandit issue. Shared config files (`.pylintrc`, `.flake8`) would keep the rules the same for the whole team.

### 4. What tangible improvements did you observe in code quality, readability, or potential robustness after applying the fixes?

- **Correctness:** the shared-guest-list bug is gone. Each event now has its own list, and the seat counts and "full" messages are right.
- **Security:** there is no shell injection risk in `print_badges`, and saved data is loaded with `json` instead of `pickle`, so a tampered file can't run code.
- **Readability:** snake_case names and docstrings make each function's purpose clear. `guest_report` now actually uses its `sort_order` argument.
- **Robustness:** the file can be imported without running the demo, thanks to the `__main__` guard.
- **Scores:** Pylint went from 4.64 to 10.00/10, and both Bandit and Flake8 went from 4 issues each to 0.
