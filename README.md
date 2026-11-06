# Academic Performance Analytics System (APAS) — SE Team 05

A comprehensive student performance tracking system that analyzes grades, attendance, and assignment submissions, and generates predictive insights about academic outcomes.

---

## 📌 Project Management & Sprint Tracking

* **Jira Workspace:** [APAS Jira Scrum Board](https://pallavibasavarajappa01-1791177333816.atlassian.net/jira/software/projects/APAS/boards/35/backlog?atlOrigin=eyJpIjoiN2U1Y2E3OGIyOWQ2NGJhNjgzZWI0MTllYTE1ODU3YTYiLCJwIjoiaiJ9)
* **Sprint Burndown Reports:** [APAS Burndown Chart](https://pallavibasavarajappa01-1791177333816.atlassian.net/jira/software/projects/APAS/boards/35/reports/burndown?source=overview&atlOrigin=eyJpIjoiMDVhN2ZkMmU1M2ZhNDYyNTlmZmQ5MTM2NTdjYjgxZTEiLCJwIjoiaiJ9)
* **CI/CD Status:** [![APAS CI Pipeline](https://github.com/pallaviB463/SE_Team_05/actions/workflows/ci.yml/badge.svg)](https://github.com/pallaviB463/SE_Team_05/actions/workflows/ci.yml)
* **Release:** [![GitHub release](https://img.shields.io/badge/release-v1.0.0-blue.svg)](https://github.com/pallaviB463/SE_Team_05/releases/tag/v1.0.0)

---

## 👥 Team 05 Members & Roles

| SRN | Name | Role | Responsibilities |
|---|---|---|---|
| **PES1UG24AM906** | **Pallavi B** | Project Lead / Repo Owner | Project coordination, architecture approval, demo recordings, UI dashboards |
| **PES1UG24AM152** | **Madhuri Ravikumar** | Developer | Backend API development, data models, business logic, bug fixes |
| **PES1UG24AM156** | **Manasvi G V** | Test Engineer | Automated test suite (88 test cases), performance & security testing |
| **PES1UG24AM175** | **Neha Rastogi** | QA Lead / Test Coordinator | Test planning, RTM verification, QA summary reports |

---

## 🚀 Sprint Deliverables

### Sprint 1 (Oct 27 – Oct 31, 2026) — 100% Complete ✅
* **Scope:** 31 Story Points (10 Work Items) — 0 points remaining (Burned down to 0).
* **CI/CD Pipeline:** Fully automated GitHub Actions workflow verifying all 88 test cases on every push/PR.
* **Sprint 1 Demo Video:** [`Academic_Performance_Analytics_System/Sprint_1_demo.mp4`](Academic_Performance_Analytics_System/Sprint_1_demo.mp4)
* **Deliverable Documents:**
  * [Software Requirements Specification (SRS)](Academic_Performance_Analytics_System/SRS.pdf)
  * [Software Architecture Document (SAD)](Academic_Performance_Analytics_System/SAD.pdf)
  * [Software Test Plan (STP)](Academic_Performance_Analytics_System/Test_Plan.pdf)
  * [Test Summary Report](Academic_Performance_Analytics_System/testing/reports/test_summary_report.md)

### Sprint 2 (Nov 02 – Nov 07, 2026) — 100% Complete ✅
* **Scope:** 31 Story Points (9 Work Items) — 0 points remaining (Burned down to 0).
* **Key Implementations:**
  * **Predictive Analytics & Risk Classification:** Linear SGPA trajectory forecasting, risk classification badge (`HIGH RISK` / `MEDIUM RISK` / `LOW RISK`), and actionable targeted academic advisory recommendations (`APAS-F-013`, `APAS-F-014`, `APAS-F-015`).
  * **Interactive Modern UI & Dashboards:** Elevated responsive dashboards with role-based views (Admin, Faculty, Student), colorful KPI cards, and trend charts (`APAS-F-010`, `APAS-F-011`).
  * **Student Audit Report Export:** Dynamic CSV report generation and download endpoint `/reports/download/<student_id>` (`APAS-F-012`).
  * **QA & Verification:** Full automated regression run (199/199 passing tests, 100% pass rate), performance stress-testing (p95 = 0.433 s against 3.0 s target), TLS 1.2+ security enforcement, and DEF-001 / DEF-002 defect verification.
  * **Static Review Approvals:** Formal sign-off on 9 documentation review findings documented in [`SRS_Review_Corrections.md`](Academic_Performance_Analytics_System/SRS_Review_Corrections.md).
* **Sprint 2 Demo Video:** [`Academic_Performance_Analytics_System/Sprint_2_demo.mp4`](Academic_Performance_Analytics_System/Sprint_2_demo.mp4)
* **Official Release:** [`v1.0.0`](https://github.com/pallaviB463/SE_Team_05/releases/tag/v1.0.0)
* **Final Presentation:** Ready for presentations starting Nov 09, 2026.

---

## 💻 Local Setup & Execution

### Prerequisites
- Python 3.10+
- Dependencies: `pip install flask pytest requests cryptography python-docx`

### Running the Application
```bash
cd Academic_Performance_Analytics_System/Testing_PES1UG24AM156_ManasviGV
python run_app.py
```
Open **`http://127.0.0.1:5000`** in your browser. Demo credentials:
- **Admin:** `admin` / `Admin@APAS2026` (Cohort overview with 306 students)
- **Faculty:** `fac.rao` / `Faculty@Rao2026` (Department grades & student drill-down)
- **Student:** `aarav` / `Student@0001` (Low Risk profile) or `diya` / `Student@0002` (High Risk profile with advisory recommendations)

### Running Automated Test Suites
```bash
cd Academic_Performance_Analytics_System/Testing_PES1UG24AM156_ManasviGV
python -m pytest
```
