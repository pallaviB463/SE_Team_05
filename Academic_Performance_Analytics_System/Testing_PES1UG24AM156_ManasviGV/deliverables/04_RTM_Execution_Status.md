# Requirements Traceability Matrix with Execution Status

**Project:** Academic Performance Analytics System (APAS) v1.0  
**Prepared by:** Manasvi G V (PES1UG24AM156), Test Engineer, Team 05  
**Reference documents:** APAS SRS v1.0, APAS SAD v1.0, APAS STP v1.0  
**Final execution run:** 2026-10-20T12:24:34+05:30 to 2026-10-20T12:26:10+05:30  
**Generated:** 20-10-2026 12:26


| Requirement | Description | Planned TC (STP 13.2) | Executed test cases | Passed | Verdict |
|---|---|---|---|---|---|
| APAS-F-001 | User authentication and login | TC-AUTH-01 | TC-AUTH-01.1, TC-AUTH-01.2, TC-AUTH-01.3, TC-AUTH-01.4, TC-AUTH-01.5, TC-AUTH-01.6, TC-AUTH-01.7, TC-AUTH-01.8 | 8/8 | **Verified** |
| APAS-F-002 | Role-based access control | TC-AUTH-02 | TC-AUTH-02.1, TC-AUTH-02.2 | 2/2 | **Verified** |
| APAS-F-003 | Secure logout and session termination | TC-AUTH-03 | TC-AUTH-03.1, TC-AUTH-03.2, TC-AUTH-03.3, TC-AUTH-03.4 | 4/4 | **Verified** |
| APAS-F-004 | Student academic profile management | TC-REC-01 | TC-REC-01.1, TC-REC-01.2, TC-REC-01.3, TC-REC-01.4 | 4/4 | **Verified** |
| APAS-F-005 | Grade entry and update | TC-REC-02 | TC-REC-02.1, TC-REC-02.2, TC-REC-02.3, TC-REC-02.4, TC-REC-02.5, TC-REC-02.6 | 6/6 | **Verified** |
| APAS-F-006 | Attendance tracking and percentage calculation | TC-REC-03 | TC-REC-03.1, TC-REC-03.2, TC-REC-03.3, TC-REC-03.4, TC-REC-03.5 | 5/5 | **Verified** |
| APAS-F-007 | Overall academic performance calculation | TC-ANA-01 | TC-ANA-01.1, TC-ANA-01.2, TC-ANA-01.3, TC-ANA-01.4, TC-ANA-01.5 | 5/5 | **Verified** |
| APAS-F-008 | Subject-wise and semester-wise performance analysis | TC-ANA-02 | TC-ANA-02.1, TC-ANA-02.2, TC-ANA-02.3 | 3/3 | **Verified** |
| APAS-F-009 | Identification of low performance / attendance below thresholds | TC-ANA-03 | TC-ANA-03.1, TC-ANA-03.2, TC-ANA-03.3 | 3/3 | **Verified** |
| APAS-F-010 | Dashboard display | TC-VIS-01 | TC-VIS-01.1, TC-VIS-01.2, TC-VIS-01.3, TC-VIS-01.4, TC-VIS-01.5 | 5/5 | **Verified** |
| APAS-F-011 | Graphical performance trends | TC-VIS-02 | TC-VIS-02.1, TC-VIS-02.2, TC-VIS-02.3, TC-VIS-02.4 | 4/4 | **Verified** |
| APAS-F-012 | Report generation and download | TC-REP-01 | TC-REP-01.1, TC-REP-01.2, TC-REP-01.3 | 3/3 | **Verified** |
| APAS-F-013 | Prediction using historical academic records | TC-PRED-01 | TC-PRED-01.1, TC-PRED-01.2, TC-PRED-01.3, TC-PRED-01.4 | 4/4 | **Verified with limitation** |
| APAS-F-014 | Identification of academically at-risk students | TC-PRED-02 | TC-PRED-02.1, TC-PRED-02.2 | 2/2 | **Verified** |
| APAS-F-015 | Academic insights and recommendations | TC-PRED-03 | TC-PRED-03.1, TC-PRED-03.2, TC-PRED-03.3 | 3/3 | **Verified** |
| APAS-NF-001 | Dashboard response time <= 3 s for 95% of requests | TC-PERF-01 | TC-VIS-01.5, TC-PERF-01.1, TC-PERF-01.2 | 3/3 | **Verified with limitation** |
| APAS-NF-002 | Monthly availability >= 99% | TC-REL-01 | TC-REL-01.1, TC-REL-01.2 | 2/2 | **Verified with limitation** |
| APAS-NF-003 | Access restrictions based on authenticated roles | TC-SEC-01 | TC-SEC-01.1, TC-SEC-01.2, TC-SEC-05.4 | 3/3 | **Verified** |
| APAS-NF-004 | Timestamped audit logs retained >= 12 months | TC-AUD-01 | TC-AUD-01.1, TC-AUD-01.2, TC-AUD-01.3, TC-AUD-01.4 | 4/4 | **Verified** |
| APAS-NF-005 | Accessibility: keyboard navigation and contrast (WCAG 2.1 AA) | TC-UX-01 | TC-UX-01.1, TC-UX-01.2, TC-UX-01.3, TC-UX-01.4 | 4/4 | **Verified** |
| APAS-SR-001 | Valid credentials required for protected access | TC-SEC-01 | TC-AUTH-01.6, TC-AUTH-01.8, TC-SEC-01.1, TC-SEC-01.2 | 4/4 | **Verified** |
| APAS-SR-002 | Role-based access restrictions | TC-SEC-02 | TC-SEC-02.1, TC-SEC-02.2, TC-SEC-02.3 | 3/3 | **Verified** |
| APAS-SR-003 | HTTPS with TLS 1.2 or higher | TC-SEC-03 | TC-SEC-03.1, TC-SEC-03.2, TC-SEC-03.3 | 3/3 | **Verified with limitation** |
| APAS-SR-004 | Secure password hashing; no plaintext storage | TC-SEC-04 | TC-SEC-04.1, TC-SEC-04.2, TC-SEC-04.3 | 3/3 | **Verified** |
| APAS-SR-005 | Timestamped security logs (logins, record changes) | TC-SEC-05 | TC-SEC-05.1, TC-SEC-05.2, TC-SEC-05.3, TC-SEC-05.4 | 4/4 | **Verified** |

Coverage: 25/25 requirements have at least one executed test case.


## Limitations affecting verdicts

- **APAS-F-013**: Evaluation uses a synthetic cohort; results describe the method's behaviour, not real-world accuracy. No accuracy threshold is asserted because the SRS does not define one (STP 15.1).
- **APAS-NF-001**: 'Normal operating conditions' are not quantified in the SRS; load profile taken from team test data TD-12 (50 concurrent users), cohort of 306 students, single developer laptop. Repeat on the deployment infrastructure.
- **APAS-NF-001**: Same load assumptions as TC-PERF-01.1. Write rate (1 grade update per 10 requests) is an assumption representing faculty entering marks while others view dashboards.
- **APAS-NF-002**: Monthly availability (>= 99%) can only be confirmed by monitoring a deployed instance for a full calendar month (tools/availability_monitor.py). This run covers a short soak test with fault injection.
- **APAS-SR-003**: Executed against the local test server; the deployed environment's TLS configuration must be re-checked (e.g. SSL Labs / testssl.sh) once a hosting platform is chosen (SAD 4.6.1 open issue 3).
