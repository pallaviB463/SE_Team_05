# SRS Review Corrections — APAS

## DOC-001: Risk and Performance Thresholds

**Existing requirement:** APAS-F-009 identifies students below configured academic performance or attendance thresholds.

**Proposed clarification:**
- Academic marks below 50% trigger a low-performance alert.
- Attendance below 75% triggers a low-attendance alert.
- Dashboard response-time acceptance criterion remains p95 ≤ 3 seconds, as specified in APAS-NF-001.

**Status:** Proposed clarification, pending requirement-owner confirmation.

## DOC-003: Normal Operating Conditions

**Existing requirement:** APAS-NF-001 specifies dashboard response time under normal operating conditions.

**Proposed clarification:**
For the current reference-build performance test, the operating workload consists of:
- 50 concurrent users
- 300 dashboard requests
- 306 student records in the test database
- A dashboard p95 response-time target of ≤ 3 seconds

These parameters describe the tested workload and should be approved before being adopted as the formal definition of normal operating conditions.

**Status:** Proposed clarification, pending requirement-owner confirmation.

## DOC-009: Inconsistent Document Metadata

**Issue:** The SRS revision history contains an outdated template entry dated 18-08-2025, attributed to Instructor, while the actual APAS SRS is dated 12-10-2026 and authored by Team 05.

**Required correction:**
- Version: 1.0
- Date: 12-10-2026
- Author: Team 05
- Change summary: Initial APAS Software Requirements Specification
- Approval: Pending

Remove the outdated instructor/template revision entry from the SRS revision history when updating the source document.

**Status:** Correction identified and documented; pending application to the SRS source document and approval.