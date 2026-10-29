# Manual Accessibility Checklist: TC-UX-01 (APAS-NF-005)

Automated checks (TC-UX-01.1 to 01.4) cover structure, labels, contrast and focus styles. The checks below need
a person and should be completed before final acceptance. Start the app with `python run_app.py`
and log in with the accounts in `test_data/apas_test_data.json`.

**Tester:** Manasvi G V (Test Engineer) **Browser / AT:** __________ **Date:** __________

| # | WCAG 2.1 criterion | Check | Pages | Result (Pass/Fail) | Notes |
|---|---|---|---|---|---|
| M1 | 2.1.1 Keyboard | Every link, button and form field can be reached and used with Tab / Shift+Tab / Enter only | Login, dashboards | | |
| M2 | 2.1.2 No keyboard trap | Focus never gets stuck; it can always move away from charts and tables | All | | |
| M3 | 2.4.1 Bypass blocks | First Tab shows "Skip to main content"; Enter moves focus to the main region | All | | |
| M4 | 2.4.3 Focus order | Focus order follows the visual order (header, then main content) | All | | |
| M5 | 2.4.7 Focus visible | A clearly visible orange outline appears on every focused element | All | | |
| M6 | 1.4.4 Resize text | At 200% browser zoom all text is readable and nothing is cut off | Dashboards | | |
| M7 | 1.4.10 Reflow | At 320 px width there is no horizontal page scrolling (tables scroll inside their container) | Dashboards | | |
| M8 | 1.1.1 / 4.1.2 Screen reader | VoiceOver/NVDA announces chart titles ("Bar chart of subject percentages...") and the data tables | Student dashboard | | |
| M9 | 3.3.1 Error identification | Screen reader announces the login error message on failed login | Login | | |
| M10 | 1.4.1 Use of colour | "Below threshold" status is conveyed by text, not colour alone | Overview dashboard | | |
| M11 | 2.4.2 Page titled | Each page has a descriptive title (e.g. "Log in - Academic Performance Analytics System") | All | | |
| M12 | 3.1.1 Language | Screen reader uses an English voice (html lang="en") | All | | |
