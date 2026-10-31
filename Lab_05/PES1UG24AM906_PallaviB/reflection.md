# Lab 5 – Reflection
## Static Code Analysis

### 1. What is the importance of static code analysis?

Static code analysis helps identify programming errors, security vulnerabilities and coding standard violations without executing the program. It improves code quality, reliability, security and maintainability.

### 2. What did you learn from Pylint, Bandit and Flake8?

- **Pylint:** Helped identify code-quality problems such as unused variables, missing docstrings, mutable default arguments and improper naming conventions.
- **Bandit:** Helped identify potentially insecure coding practices, including the use of `eval()` and broad exception handling.
- **Flake8:** Helped identify formatting violations such as long lines, unused imports, trailing whitespace and missing final newlines.

### 3. What challenges did you face while fixing the issues?

Some challenges included understanding why mutable default arguments are problematic, replacing broad exception handling with specific exceptions, removing unsafe functions without affecting program functionality and correcting formatting violations.

### 4. How does static code analysis improve software development?

Static code analysis helps developers identify problems early, reduce potential bugs, improve security and maintain consistent coding standards. It also makes programs easier to understand, debug and maintain.