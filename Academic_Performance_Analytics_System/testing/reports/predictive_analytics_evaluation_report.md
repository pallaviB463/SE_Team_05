# Test Summary Report - APAS v1.0

**Prepared by:** Neha Rastogi (QA Lead / Test Coordinator) | **Reviewed by:** Pallavi B (Project Lead / Approver)

## 1. Scope of testing completed
Full functional, non-functional, and security verification of the APAS reference build against all 25 SRS requirements across 2 execution cycles.

## 2. Execution summary
| Total | Passed | Failed | Blocked | Not Executed |
|---|---|---|---|---|
| 24 (88 sub-cases, 196 runs) | 24 (100%) | 0 | 0 | 0 |

## 3. Defects
- Execution defects: Identified: 2 | Resolved: 2 | Open: 0 | Open critical: 0 (DEF-001 Closed, DEF-002 Closed)
- Static review defects: Identified: 9 (DOC-001 to DOC-009) | In progress

## 4. Requirement coverage
25/25 requirements mapped in RTM; execution status: 100% verified (with documented limitations on NF-001, NF-002, SR-003, F-013).

## 5. Results
- Performance (TC-PERF-01): p95 = 0.475 s overall (target <= 3 s) -> Pass
- Reliability (TC-REL-01): 100.00% availability -> Pass
- Security (TC-SEC-01..05): Pass (TLS 1.2+ enforced, PBKDF2-SHA256 600k iterations, RBAC verified)
- Audit logging (TC-AUD-01): Pass (12-month retention enforced)
- Accessibility (TC-UX-01): Pass (0 WCAG 2.1 AA structural/contrast issues)
- Predictive analytics: Linear trend extrapolation, accuracy = 0.863, precision = 0.814, recall = 0.775

## 6. Known limitations and outstanding risks
1. Predictive evaluation used a synthetic student cohort.
2. Monthly 99% availability (NF-002) requires 30-day host monitoring.
3. TLS certificate enforcement should be re-validated on final cloud host.

## 7. Exit criteria check (STP §5.4)
- [x] All planned test cases executed or documented
- [x] High-priority functional requirements verified
- [x] All 5 NFRs and 5 SRs tested
- [x] No unresolved critical defects
- [x] Failed cases investigated and defects documented
- [x] Results recorded and summary reviewed

## 8. Readiness for acceptance
Ready for Sprint 1 sign-off.
