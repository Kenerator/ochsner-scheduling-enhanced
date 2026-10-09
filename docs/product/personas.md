# Selected personas

Updated:2026-10-09. Exact supplied hypothesis pins adopted after RC-1; no bootstrap or historical launch personas arrays were rewritten. These are design hypotheses, not real-user validation, demographic inference, clinical suitability or permissions. Language and actual channel availability remain unknown.

Retained [catalog](../../reference/personas/catalog.json) contains selected records with all retained revisions and required ancestors; [exact selections](../../reference/personas/selected.json) and [generated cards](../../reference/personas/selected-cards.md) make clean clones standalone. Source catalog SHA256: `18ca4ae40b88320a2acb4fcc48ba581c4721b6670dba9ef3234dacb90a5837d9`. Shared catalog was not edited; no identities allocated.

| Persona | Exact pin | Native stories | Constraint and actual status |
| --- | --- | --- | --- |
| Jules | `poc-template-seed-v1:56e6af21-d1e4-4698-8485-83a341d77031@1` | 1–2 | Exact proposal and separate current confirmation; concise next action. Verified existing booking behavior. |
| Ellie-Rae | `poc-template-seed-v1:cb706720-85fb-42ef-9318-2bcec4c2b621@1` | 2–3 | Numbered keyboard choices; invalid input keeps context; no repeated fields. Valid selection verified; signed/oversized invalid-number repair tested in RC-2. |
| Billy-June | `poc-template-seed-v1:0de53f87-1856-40ac-84fe-ec4d890e3770@1` | 2–4 | Location/date constraints; corrections invalidate consent; explain unsupported hours. Existing date/location guards verified; unsupported time-of-day repair tested in RC-2. |
| Nina-Jean | `poc-template-seed-v1:5d4d7083-1479-4637-90cd-5e841bfe080d@1` | 1–4 | Useful clarification, plain labels and visible correction. Existing authority/correction guards; plain specialty labels and canonical submission verified in IAB. |
| Amy-Lou | `poc-template-seed-v1:aae4b004-4bbf-4ac5-b532-2d7af776e168@1` | 3,5 | No email demand; truthful assistance and browser limitation. No email requirement verified; assisted-access wording repair tested in RC-2. |
| Morgan-Rae (human support) | `poc-template-seed-v1:657aedfe-4a4a-4ec4-83c0-52614111f07c@1` | 3,5 | Known/missing/unknown outcome context; no false delivery. Queue/outage/unknown truth verified; allowlisted known/missing/booking-outcome summary regression passed. |
| Sam-Rae (AGENT QA) | `poc-template-seed-v1:98e1dcd5-8ee9-4b2b-b7fe-2045d389b9b4@1` | 2–3,6 | Replayed consent and uncertain effects cannot authorize retry. Existing replay/unknown guards verified; no persona permission. |

[Native stories](../../specs/001-guarded-scheduling/spec.md) own accepted requirements; [story index](user-stories.md) links them. Relevant seven-person set includes core Jules/Ellie-Rae/Morgan-Rae/Sam-Rae and focused Billy-June/Nina-Jean/Amy-Lou constraints. Support/Admin coverage is Morgan-Rae’s factual support needs; no admin console or representative delivery is implied. Basic-phone service is not implemented. Focused regression/UI evidence is recorded in existing [UAT](../internal/uat.md) and [video notes](../internal/video-notes.md).
