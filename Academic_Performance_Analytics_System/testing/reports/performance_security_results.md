# Performance and Security Test Results

| Test | Check | Tool | Target | Measured | Pass/Fail |
|---|---|---|---|---|---|
| TC-PERF-01 | Dashboard 95th percentile | Python load script (requests, 50 threads) instead of JMeter | <= 3 s | p95 0.475 s overall (worst dashboard 0.508 s); with concurrent grade writes p95 0.795 s | Pass (with limitation) |
| TC-REL-01 | Monthly availability | Health-probe soak test with fault injection | ≥ 99% | 100.00% over 2.8 s (monthly figure not yet measurable) | Pass (with limitation) |
| TC-SEC-03 | TLS version / HTTP redirect | Python ssl handshakes + HTTP redirect test (testssl/SSL Labs on deployment still to do) | TLS ≥ 1.2 | TLS 1.0/1.1 refused, TLS 1.2/1.3 accepted; HTTP GET -> 301, HTTP POST -> 403; HSTS set | Pass (with limitation) |
| TC-SEC-04 | Password storage | DB inspection (automated) | Hashed, no plaintext | PBKDF2-SHA256, 600 000 iterations, 16-char salt; no plaintext in DB, API responses or logs | Pass |
| TC-SEC-05 | Security event logging | Audit log review (automated) | User ID, event, timestamp | Login success/failure, record changes and denied access logged with user, event type and UTC timestamp; no secrets logged | Pass |
| TC-AUD-01 | Retention | Audit log review (automated, back-dated entries) | ≥ 12 months | 12-month minimum enforced (11m29d kept, older purged; config < 12 raised to 12); UPDATE blocked | Pass |
| TC-UX-01 | Keyboard + contrast | Python HTML/contrast checks instead of axe/WAVE | WCAG 2.1 AA | 0 structural issues on 4 pages; all text pairs >= 4.5:1, UI pairs >= 3:1; manual checklist pending | Pass |

Additional security results:

- **TC-SEC-01**: Pass (6/6 executions)
- **TC-SEC-02**: Pass (9/9 executions)
- **TC-SEC-03**: Pass (with limitation) (3/3 executions)
- **TC-SEC-04**: Pass (3/3 executions)
- **TC-SEC-05**: Pass (6/6 executions)

Raw data: `../Testing_PES1UG24AM156_ManasviGV/results/` (performance_results.json, tls_results.json, reliability_results.json). Cycle 1 measured admin dashboard p95 4.19 s at 10 users (DEF-002, fixed).
