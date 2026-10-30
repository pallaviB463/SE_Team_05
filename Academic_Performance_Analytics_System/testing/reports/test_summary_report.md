# Test Summary Report - APAS v1.0

**Prepared by:** Neha Rastogi (QA Lead / Test Coordinator) | **Reviewed by:** Pallavi B (Project Lead / Approver)
**Execution Date:** 30-10-2026 (Environment: Windows 11, Python 3.13.7, SQLite 3.50.4)

## 1. Scope of testing completed
Full functional, non-functional, and security verification of the APAS reference build across all 25 SRS requirements (15 Functional, 5 Non-Functional, 5 Security) over 2 formal execution cycles and Windows regression verification.

## 2. Execution summary
| Total | Passed | Failed | Blocked | Not Executed |
|---|---|---|---|---|
| 24 (88 sub-cases, 196 runs) | 24 (100%) | 0 | 0 | 0 |

## 3. Defects
- Execution defects (Software): Identified: 2 | Resolved: 2 | Open: 0 | Open critical: 0
  - DEF-001 (Critical - HTTPS spoofing bypass): Closed
  - DEF-002 (Major - Admin overview p95 response time): Closed
- Static review defects (SRS/STP): Identified: 9 (DOC-001 to DOC-009) | Status: Under review

## 4. Requirement coverage
25/25 requirements mapped in RTM; execution status: 100% verified (with documented limitations on NF-001, NF-002, SR-003, F-013).

## 5. Results
- Performance (TC-PERF-01): p95 = 0.687 s overall (worst dashboard 0.724 s; mixed read/write p95 1.311 s) (Target <= 3.0 s) -> Pass
- Reliability (TC-REL-01): 100.00% availability over soak window -> Pass (with soak limitation)
- Security (TC-SEC-01..05): Pass (TLS 1.2+ enforced, PBKDF2-SHA256 600k iterations, RBAC verified, tamper-proof audit logging)
- Audit logging / retention (TC-AUD-01): Pass (12-month minimum retention enforced)
- Accessibility (TC-UX-01): Pass (0 WCAG 2.1 AA structural/contrast issues across 4 web pages)
- Predictive analytics: Linear trend extrapolation, accuracy = 0.863, precision = 0.814, recall = 0.775

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
Ready for Sprint 1 sign-off and progression to Sprint 2.
