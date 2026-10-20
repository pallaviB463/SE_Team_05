# Performance and Security Test Results

| Test | Check | Tool | Target | Measured | Pass/Fail |
|---|---|---|---|---|---|
| TC-PERF-01 | Dashboard 95th percentile | JMeter | <= 3 s |  |  |
| TC-REL-01 | Monthly availability | Uptime monitor | ≥ 99% |  |  |
| TC-SEC-03 | TLS version / HTTP redirect | testssl / SSL Labs | TLS ≥ 1.2 |  |  |
| TC-SEC-04 | Password storage | DB inspection | Hashed, no plaintext |  |  |
| TC-SEC-05 | Security event logging | Log review | User ID, event, timestamp |  |  |
| TC-AUD-01 | Retention | Log review | ≥ 12 months |  |  |
| TC-UX-01 | Keyboard + contrast | axe / WAVE | WCAG 2.1 AA |  |  |
