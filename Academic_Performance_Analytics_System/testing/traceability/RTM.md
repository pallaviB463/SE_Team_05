# Requirements Traceability Matrix (APAS)

| Requirement ID | Description | Type | Priority | Test Case ID | Executed sub-cases | Execution status | Defects |
|---|---|---|---|---|---|---|---|
| APAS-F-001 | User authentication and login | Functional | High | TC-AUTH-01 | 8 (8 passed) | Pass | - |
| APAS-F-002 | Role-based access to system functions | Functional | High | TC-AUTH-02 | 2 (2 passed) | Pass | - |
| APAS-F-003 | Secure logout and session termination | Functional | High | TC-AUTH-03 | 4 (4 passed) | Pass | - |
| APAS-F-004 | Student academic profile management | Functional | High | TC-REC-01 | 4 (4 passed) | Pass | - |
| APAS-F-005 | Grade entry and updating | Functional | High | TC-REC-02 | 6 (6 passed) | Pass | - |
| APAS-F-006 | Attendance recording and % calculation | Functional | High | TC-REC-03 | 5 (5 passed) | Pass | - |
| APAS-F-007 | Overall academic performance calculation | Functional | High | TC-ANA-01 | 5 (5 passed) | Pass | - |
| APAS-F-008 | Subject/semester-wise analysis | Functional | High | TC-ANA-02 | 3 (3 passed) | Pass | - |
| APAS-F-009 | Below-threshold identification | Functional | High | TC-ANA-03 | 3 (3 passed) | Pass | - |
| APAS-F-010 | Academic performance dashboard | Functional | High | TC-VIS-01 | 5 (5 passed) | Pass | - |
| APAS-F-011 | Graphical trends | Functional | Medium | TC-VIS-02 | 4 (4 passed) | Pass | - |
| APAS-F-012 | Report generation and download | Functional | High | TC-REP-01 | 3 (3 passed) | Pass | - |
| APAS-F-013 | Future performance prediction | Functional | High | TC-PRED-01 | 4 (4 passed) | Pass (with limitation) | - |
| APAS-F-014 | At-risk student identification | Functional | High | TC-PRED-02 | 2 (2 passed) | Pass | - |
| APAS-F-015 | Insights and recommendations | Functional | Medium | TC-PRED-03 | 3 (3 passed) | Pass | - |
| APAS-NF-001 | Dashboard response time | Non-Functional | High | TC-PERF-01 | 3 (3 passed) | Pass (with limitation) | DEF-002 (closed) |
| APAS-NF-002 | Monthly availability | Non-Functional | High | TC-REL-01 | 2 (2 passed) | Pass (with limitation) | - |
| APAS-NF-003 | Access restrictions for records | Non-Functional | High | TC-SEC-01 | 3 (3 passed) | Pass | - |
| APAS-NF-004 | Audit logging and retention | Non-Functional | High | TC-AUD-01 | 4 (4 passed) | Pass | - |
| APAS-NF-005 | UI accessibility | Non-Functional | Medium | TC-UX-01 | 4 (4 passed) | Pass | - |
| APAS-SR-001 | Secure user authentication | Security | High | TC-SEC-01 | 4 (4 passed) | Pass | - |
| APAS-SR-002 | Role-based access control | Security | High | TC-SEC-02 | 3 (3 passed) | Pass | - |
| APAS-SR-003 | TLS 1.2+ transmission | Security | High | TC-SEC-03 | 3 (3 passed) | Pass (with limitation) | DEF-001 (closed) |
| APAS-SR-004 | Secure password hashing | Security | High | TC-SEC-04 | 3 (3 passed) | Pass | - |
| APAS-SR-005 | Security event audit logging | Security | High | TC-SEC-05 | 4 (4 passed) | Pass | - |

All 25 requirements (15 functional, 5 non-functional, 5 security) map to at least one test case. TC-SEC-01 covers APAS-NF-003 and APAS-SR-001.

Execution status added by Manasvi G V from the cycle 2 run (2026-10-20). Sub-case counts include supporting cases mapped to the requirement (e.g. TC-SEC-05.4 also covers APAS-NF-003). Review note DOC-005: APAS-NF-003 is also exercised by TC-SEC-02 (role checks).
