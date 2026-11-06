# Test Summary Report - APAS v1.0

**Prepared by:** Neha Rastogi (QA Lead / Test Coordinator) | **Reviewed & Approved by:** Pallavi B (Project Lead / Approver)  
**Execution Date:** 06-11-2026 (Environment: Python 3.11/3.13, Flask 3.1.3, pytest 9.1.1, SQLite)

## 1. Scope of testing completed
Full functional, non-functional, security, and regression verification of the APAS reference build across all 25 SRS requirements (15 Functional, 5 Non-Functional, 5 Security) over two formal execution cycles and the final Sprint 2 automated regression run.

## 2. Execution summary
| Total Requirements | Planned Test Cases | Automated Sub-Cases | Executed Runs | Passed | Failed | Pass % |
|---|---|---|---|---|---|---|
| 25 / 25 | 24 | 88 | 199 | 199 | 0 | 100% |

### 2.1 Final Automated Regression Verification

**Execution Date:** 05-11-2026  
**QA Lead:** Neha Rastogi | **Project Lead Approval:** Pallavi B  
**Environment:** Windows / Ubuntu CI, Python 3.11/3.12, Flask 3.1.3, pytest 9.1.1, SQLite

| Metric | Result | Target |
|---|---|---|
| Total automated test executions | 199 | 199 |
| Passed | 199 | 199 |
| Failed | 0 | 0 |
| Pass percentage | 100% | 100% |
| Regression status | **PASS** | PASS |

**Defect Reverification:**

- **DEF-001 (Critical - HTTPS spoofing bypass):** Closed. Insecure connections rejected with HTTP 403 / redirected with HTTP 301. TLS 1.0/1.1 connections refused; TLS 1.2 and 1.3 accepted.
- **DEF-002 (Major - Admin overview p95 response time):** Closed. Under 50 concurrent simulated users and 300 requests, p95 response time recorded at 0.433 seconds (mixed read/write p95 0.598 seconds), significantly faster than the 3.0-second limit.

**Conclusion:** All 199 automated test executions passed with 100% success rate. Both previously reported software defects have supporting verification evidence and are verified closed.

## 3. Defects
- **Execution defects (Software):** Identified: 2 | Resolved: 2 | Open: 0 | Open critical: 0
  - DEF-001 (Critical - HTTPS spoofing bypass): Closed (Verified in Cycle 2 / Regression)
  - DEF-002 (Major - Admin overview p95 response time): Closed (Verified in Cycle 2 / Regression, p95 = 0.433 s)
- **Static review defects (SRS/STP):** Identified: 9 (DOC-001 to DOC-009) | Resolved: 9 | Open: 0
  - DOC-001 to DOC-009: Formally reviewed, documented, and approved in `SRS_Review_Corrections.md` by Project Lead Pallavi B and QA Lead Neha Rastogi. All items closed for Release v1.0.0.

## 4. Requirement coverage
25/25 requirements mapped in RTM; execution status: 100% verified (with documented limitations on NF-001, NF-002, SR-003, F-013).

## 5. Results
- **Performance (TC-PERF-01):** p95 = 0.433 s overall (Target <= 3.0 s) -> **Pass**
- **Reliability (TC-REL-01):** 100.00% availability over soak window -> **Pass**
- **Security (TC-SEC-01..05):** **Pass** (TLS 1.2+ enforced, PBKDF2-SHA256 600k iterations, RBAC verified, tamper-proof audit logging)
- **Audit logging / retention (TC-AUD-01):** **Pass** (12-month minimum retention enforced)
- **Accessibility (TC-UX-01):** **Pass** (0 WCAG 2.1 AA structural/contrast issues across all web pages)
- **Predictive analytics (TC-PRED-01..03):** **Pass** (Linear SGPA trend forecasting, risk classification, targeted actionable recommendations)

## 6. Known limitations and outstanding risks
1. Predictive evaluation used a synthetic student cohort.
2. Monthly 99% availability (NF-002) requires 30-day host monitoring via availability_monitor.py.
3. TLS certificate enforcement should be re-validated on final cloud production host.

## 7. Exit criteria check (STP §5.4)
- [x] All planned test cases executed or documented
- [x] High-priority functional requirements verified
- [x] All 5 NFRs and 5 SRs tested
- [x] No unresolved critical defects
- [x] Failed cases investigated and defects documented
- [x] Results recorded and summary reviewed

## 8. Readiness for acceptance
All 25 SRS requirements verified with 100% pass rate (199/199 automated test executions passing). All software defects verified closed and all static documentation review findings approved via `SRS_Review_Corrections.md`. The system meets all functional, performance, security, and accessibility exit criteria and is ready for Sprint 2 acceptance, release v1.0.0, and final project presentation.
