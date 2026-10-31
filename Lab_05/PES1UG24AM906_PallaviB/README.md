# Lab 5: Static Code Analysis — Support Ticket Tracker

**Your file:** `support_ticket_tracker.py`

Follow the lab handout for the full instructions.

## About the program

A support ticket tracker. It creates tickets with a priority and category, assigns them to agents, updates their status, searches and reports on them, and saves them to a JSON file.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:
   ```bash
   python support_ticket_tracker.py
   ```
   It asks one question. Press Enter to skip, then try a few inputs of your own (for example a ticket id that does not exist). Not every problem in this file is something a tool will flag, so pay attention to output that looks wrong.

2. **Install the tools:**
   ```bash
   python -m pip install pylint bandit flake8
   ```

3. **Run the analysis** and save the reports:
   ```bash
   python -m pylint support_ticket_tracker.py > pylint_report.txt
   python -m bandit -r support_ticket_tracker.py > bandit_report.txt
   python -m flake8 support_ticket_tracker.py > flake8_report.txt
   ```

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | ... | ... | ... | ... | ... |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

1. `support_ticket_tracker.py`: your cleaned version, with at least 4 issues fixed.
2. `issues.md`: the completed issue table.
3. `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.
