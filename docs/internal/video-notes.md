# Video notes

Updated: 2026-10-09. **Actual recording pending**; this is a script from tested flows, not a finished video. Target duration4:30, maximum5:00. Use only controlled IAB and synthetic records; mask private fields and exclude credentials, terminal environment and raw logs.

0:00–0:30: AI/synthetic disclosure and local branding; no production authentication/clinical care. 0:30–1:10: provider lookup and Downtown refinement with actual returned facts. 1:10–2:30: private synthetic identity, returned options, exact proposal and separate confirmation; choosing is not booking. 2:30–3:10: reset local conversation, no-match failure and honest next step. 3:10–4:00: [actual architecture](as-built/architecture.md), model only interprets public intent/preferences, core owns effects, unknown outcome locks retry. 4:00–4:30: [UAT evidence and limits](uat.md), conservative vocabulary, no real handoff delivery, no cancel/reschedule/reconciliation endpoint, [next steps](../product/next-steps.md).

Primary/Support/Admin Persona pins remain unresolved in [personas](../product/personas.md). Native [spec](../../specs/001-guarded-scheduling/spec.md), [tasks](../../specs/001-guarded-scheduling/tasks.md) and [walkthrough](as-built/code-walkthrough.md) are canonical. No three-hour compliance statement is supported or asserted. Operator owns effort/window trade-offs. Reviewed commit/tag and final recording artifact must be added after they exist.

## Recording coordination

Earlier scenario qualification was reported to SM/media; the later full-control rehearsal requirement supersedes that readiness statement. CAPTURE-READY is not yet declared. No global capture has started and no reconstructed montage is accepted. Operator-assisted native recording/slot is pending. UI http://127.0.0.1:28181, API 4011; repository Kenerator/ochsner-scheduling-enhanced; implementation7738727a9f2ca97fe999527df20515a016a7332f. External originals destination: `/Volumes/Seagate Backup Plus Drive/nxus-media-studio/source-media/oscar-poc-engineering-review/assignment-captures/enhanced/20261009/`. Names: OSCAR__enhanced__provider-lookup__7738727a__T01, booking-happy, failure-no-match and supported-handoff, native MOV/MP4/WebM extension; increment takes, never overwrite. Media owns catalog/hash/derivatives. Actual path/time/outcome/reset state are filled only after a real take exists.

Actual UI qualification: provider lookup returned Dr. Elena Brooks/Dr. Marcus King; primary-care Downtown booking retained returned2026-10-16T09:00:00-05:00 and current separate Confirm reached API-confirmed booked. Local reset disclosed that backend state remains; unmatched synthetic identity reached private failure and actual queued mock handoff with no human-delivery claim. No raw identity logs retained. For a recording reset, stop/restart only owned mock and UI processes as [README](../../README.md#run) describes; never treat reset as unknown-transaction reconciliation.

Current candidate: **RC-1**, source `a20ab9c0334993d399b826dc09fabf50edf2da22`, whose implementation matches qualified transport source256a1b4. Planned filenames use commit8 `a20ab9c0`. No earlier take exists or is relabeled. The +2h snapshot acdd0b6 was captured00:42:11.471751CDT,70.472s late; tags are not rewritten for later polish. Operator clarified actual video may continue after01:41:01CDT; product attention does not investigate recorder methods, which media owns. No time-window compliance or recording completion is claimed.


## Recording-off rehearsal checklist

Updated 2026-10-09, RC-1 `a20ab9c0334993d399b826dc09fabf50edf2da22`, controlled IAB28181, supplied synthetic API4011, real configured model. Recording is OFF. This checklist records actual observed outcomes; it does not claim completed video or full rehearsal readiness.

- [x] Request field and Send: live booking intent reaches private identity; pending spinner remains distinct from completed response.
- [x] Private identity accordion, phone/DOB/ZIP fields and Apply: password fields; duplicate match requests ZIP without candidate details; local ZIP reaches available options; no-match reaches truthful mock queue.
- [x] Preferences accordion, specialty/location dropdowns, both date fields and Apply: primary_care/downtown and2026-10-16 through2026-10-17 accepted; subsequent booking returns bounded options.
- [x] Returned-slot dropdown and Review: exact API time retained; choice creates proposal and performs no booking.
- [x] Confirm and Decline: separate Confirm reaches actual API-confirmed booking; Decline reports no submission and returns choices.
- [x] Refresh and Reset: refresh returns current options; reset explicitly leaves backend state unchanged.
- [x] Conflict scenario: actual409 reports not booked, clears proposal; Refresh, new choice and separate new Confirm successfully book09:00 with returned-05:00 offset.
- [ ] Rehearse public provider lookup/refinement and explicit authoritative suggestion selection on this exact filming configuration (prior source qualification exists).
- [ ] Rehearse adopted appointment lookup, medical/unsupported/human boundaries, empty availability, privacy mixed input and outage outputs in controlled IAB on the filming configuration. Tests/demos already qualify product guards; they are not a substitute for this rehearsal.
- [ ] Inspect any notebook shell menu used in the take; there are no product tabs, toggles or inspectors in the scheduling UI. Do not introduce unrelated shell interactions into product coverage.
- [ ] Recheck expected disabled controls in unresolved state using the documented controlled test method; never create an unknown outcome by interfering with real transactions.
- [ ] Complete all required scenario coverage, reset only owned synthetic processes to documented fresh state, and notify SM CAPTURE-READY before recording.
- [ ] Record real clip paths and scenario/control timestamps after capture. No clips exist yet; media owns final<=5min edit and disclosure of omitted coverage.

Evidence from this rehearsal: `/private/tmp/ochsner-rc1-booked.jpg`, `/private/tmp/ochsner-rc1-no-match.jpg`, and native controlled-IAB observations. These are screenshots, not continuous video. Relevant product changes require affected rehearsal repeats and a new immutable RC; old tags/footage retain their original identity.
