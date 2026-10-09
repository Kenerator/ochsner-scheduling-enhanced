# Local operations and support

Updated: 2026-10-09. Run only synthetic data on loopback. The supplied mock runner suppresses its identity-bearing raw audit output and stops only its own process. Each test/demo gets isolated mutable state.

Identity is locally verified against phone/DOB matches, with private ZIP only for returned duplicate candidates. This is fixture matching, not production authentication. Diagnostic context contains random session label, normalized route/state/intent/status/reason/latency; no patient IDs, query/body, prompt/history or raw errors. The CLI reports unexpected exception class only and stops. No new support console or access permission is introduced.

A valid bound201 means booked;409 means rejected and needs fresh returned options/confirmation. A lost/malformed/uncertain write response locks booking and requires human reconciliation before another attempt, including after restart. Reset never certifies failure. The API has no reconciliation/idempotency endpoint.

A mock handoff queues only on actual valid201 with queued status and identifier. api_failure injection persists on every request, so it cannot queue help. Use your usual scheduling contact when service/help is unavailable; this prototype invents no phone number or delivery channel. See [UAT](uat.md), [README](../../README.md) and [walkthrough](as-built/code-walkthrough.md).
