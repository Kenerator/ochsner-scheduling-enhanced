# Data model

Updated: 2026-10-08. Proposed in-memory entities, no database/migrations. See [workflow](contracts/workflow.md) and [adapters](contracts/adapters.md).

| Entity | Fields / relationships | Validation and privacy |
|---|---|---|
| Session | random ID, intent/state, generations, private verification, preferences, returned catalogs, proposal/outcome | Serialized events; no persisted transcript; diagnostic labels only |
| PrivateIdentity | phone, DOB, optional ZIP, extraction status | Supported nonempty phone format; real ISO DOB; ZIP string retains zeros, duplicates only. Never model/log fields |
| Verification | state, identity generation, local returned matches, selected patient ID | unverified/needs_zip/verified/unresolved; exactly one valid returned candidate. Records local; establishedPatient not eligibility |
| Preferences | specialty, optional location/startDate/endDate, revision | Supported enums, real ordered ISO dates. Omission differs from explicit clearing. Public projection excludes identity/collisions |
| Provider | providerId/name/specialty/locations[]/modalities[] | Typed returned public facts only; no fabricated display or clinical ranking |
| SlotCatalog | identity/preference/catalog generations, slots[] | After verification only; stale context cannot be selected |
| Slot | slotId/providerId/specialty/location/startTime/available | Returned available actual boolean true, unique IDs, matching context/date bounds; exact returned offset/time; no fixture internals |
| Proposal | opaque ID, private patient binding, generations, returned slot snapshot, display summary, lifecycle | Current validated catalog only; active/invalidated/consumed. Local verified patient context + specialty/location/time; never model/diagnostic identity |
| ConsentEvent | proposal ID, generation binding, explicit action | Current exact proposal only; selection/model flag/ambiguous yes insufficient |
| Submission | proposal/attempt IDs, status, appointment or rejection/unknown reason | submitting/booked/rejected/unresolved; consume consent before single request; no retry; local attempt ID not server idempotency |
| Appointment | appointmentId/patientId/providerId/specialty/location/startTime/status | Valid service response bound to selected proposal; no slotId in schema. Optional lookup patient-bound only |
| RecoveryContext | allowed reason, minimized template summary, optional actual queue result | No identity/transcript. Valid 201/handoffId/queued required for queue claim, never delivered-human claim |
| DiagnosticEvent | random session ID, normalized state/intent/route, status/reason/source, duration | Whitelist only; no sensitive identifiers, URL/query/body/prompt/history |

## State transitions

Provider lookup works without verification and never triggers patient search. Patient-specific intent: collecting identity → verifying → needs ZIP (duplicates only), verified or unresolved. Verified + valid preferences → availability → returned options → active proposal → explicit confirmation → submitting → booked/rejected/unresolved. Empty availability, unsupported scope, clinical request and unavailable service lead to truthful recovery.

Identity changes increment identity generation and clear verification/matches/catalog/proposal/consent. Preference changes increment revision and clear affected catalog/proposal/consent, retaining valid identity. Choice changes invalidate old proposal/consent before a new proposal. Responses carrying obsolete generations cannot restore stale results. A possibly completed obsolete write remains unresolved, never discarded as failure.

Conflict rejection invalidates consent/catalog; refresh and new exact confirmation are needed. Booked consumes proposal permanently; repeat confirmation can display known result but cannot write. Unresolved locks further booking in that session and tells users to reconcile before another attempt, including after restart. Reset clears synthetic local state only, never certifies failed effect or reconciliation. No unavailable reconciliation endpoint is invented.
