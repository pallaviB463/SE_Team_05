# SRS Review Corrections & Formal Approvals — APAS

**Project:** Academic Performance Analytics System (APAS)  
**Document Reference:** SRS v1.0 Addendum / Engineering Change Notice (ECN)  
**Author:** Neha Rastogi (QA Lead)  
**Reviewed & Approved by:** Pallavi B (Project Lead / Repo Owner, PES1UG24AM906)  
**Approval Date:** 06-11-2026  
**Status:** Formally Approved & Accepted for Release v1.0.0

---

## 1. Overview
During verification and static document reviews across Sprint 1 and Sprint 2, 9 documentation defects (DOC-001 through DOC-009) were identified. Rather than modifying submitted baseline foundation artifacts (`SRS.pdf`), this addendum formally resolves, clarifies, and approves the requirements for the v1.0.0 release.

---

## 2. Documented Resolutions & Approvals

### DOC-001: Risk and Performance Thresholds
- **Requirement:** APAS-F-009, APAS-F-014
- **Approved Resolution:**
  - Academic marks $< 50\%$ trigger a low-performance alert.
  - Attendance $< 75\%$ triggers a low-attendance alert.
  - High risk threshold: Predicted SGPA $< 5.0$ OR Attendance $< 65\%$.
  - Medium risk threshold: Predicted SGPA $< 6.0$ OR Attendance $< 75\%$.
  - Acceptance criterion: Dashboard response-time target remains p95 $\le 3$ seconds (APAS-NF-001).
- **Status:** **Closed / Approved**

### DOC-002: Assignment Submission Tracking Scope Clarification
- **Requirement:** SRS §1.2 & §2.2
- **Approved Resolution:**
  - Current v1.0 reference release evaluates academic examinations (ISA and ESA assessments).
  - Continuous assignment submission and LMS file tracking is formally designated for the post-v1.0 product backlog.
- **Status:** **Closed / Approved**

### DOC-003: Definition of Normal Operating Conditions
- **Requirement:** APAS-NF-001, STP §5.2
- **Approved Resolution:**
  - Normal operating workload is formally defined as:
    - 50 concurrent simulated users.
    - 300 dashboard requests (mix of admin, faculty, and student dashboards).
    - Database cohort of 306 students (~42,000 academic records).
    - p95 response time target $\le 3.0\text{ s}$ (Observed in QA: $0.433\text{ s}$ - 100% within target).
- **Status:** **Closed / Approved**

### DOC-004: Prediction Quality Acceptance Criteria
- **Requirement:** APAS-F-013, STP §15.1
- **Approved Resolution:**
  - Linear SGPA trend forecasting serves as an informational academic advisory tool.
  - Evaluation results (Accuracy = 86.3%, Precision = 81.4%, Recall = 77.5%) meet advisory benchmarks; no artificial cutoff imposed.
- **Status:** **Closed / Approved**

### DOC-005: RTM Mapping for Access Control & Authentication
- **Requirement:** APAS-NF-003, APAS-SR-001
- **Approved Resolution:**
  - APAS-NF-003 (Role-based access restriction) maps directly to TC-SEC-01 and TC-SEC-02.
  - APAS-SR-001 (Credential authentication) maps to TC-SEC-01.
  - Traceability matrix updated and verified in `RTM.md`.
- **Status:** **Closed / Approved**

### DOC-006: Plain HTTP vs. HTTPS Deployment Policy
- **Requirement:** SRS §3.4, APAS-SR-003
- **Approved Resolution:**
  - Plain HTTP is permitted strictly in local offline developer environments (`run_app.py` default).
  - HTTPS with TLS 1.2+ minimum is strictly enforced on all external and deployed environments (verified via DEF-001 closure).
- **Status:** **Closed / Approved**

### DOC-007: Session Timeout and Account Lockout Policy
- **Requirement:** APAS-F-003, APAS-SR-001
- **Approved Resolution:**
  - Standard session idle timeout: 30 minutes.
  - Brute-force account lockout policy: 15-minute temporary lock after 5 consecutive failed login attempts (verified via TC-AUTH-01.6).
- **Status:** **Closed / Approved**

### DOC-008: PDF Formatting & Layout Refinement
- **Requirement:** SRS §4.1, §4.4
- **Approved Resolution:**
  - Formally noted minor column text truncation in PDF table rendering; full unclipped text maintained in markdown specifications.
- **Status:** **Closed / Approved**

### DOC-009: Document Metadata and Approval Table Alignment
- **Requirement:** SRS Revision History, STP §15.3
- **Approved Resolution:**
  - SRS Version: 1.0, Release Date: 12-10-2026.
  - Author: Team 05.
  - Sign-off Authorities: Neha Rastogi (QA Lead) and Pallavi B (Project Lead).
- **Status:** **Closed / Approved**

---

## 3. Formal Sign-Off
- **Project Lead:** Pallavi B (`PES1UG24AM906`) — **Approved**
- **QA Lead:** Neha Rastogi (`PES1UG24AM175`) — **Verified**
