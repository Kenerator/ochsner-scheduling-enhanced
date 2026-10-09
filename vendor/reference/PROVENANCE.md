# Supplied reference provenance

Updated: 2026-10-08 (America/Chicago).

These files are unchanged selective copies from the supplied patient appointment assignment package at `/Users/ken/codeRepos/PoC-RFP/patient_appointment_project`. They are included under the Operator-approved private reviewer repository scope for reproducible local setup and testing. This record does not claim an open-source license or permission for public redistribution. All patient/provider/slot/appointment fixtures are supplied synthetic data.

Included: the standard-library reference mock server, four JSON fixture files, and the canonical OpenAPI contract. Assignment text, policies, scenarios, email, intake metadata, and credentials are excluded.

| Relative file | SHA-256 of original and copied bytes |
| --- | --- |
| `mock-api/server.py` | `9597f92fe3ec19c16e08b1491fbac12e1ffed87bd41c137be1e638addac2d1f1` |
| `data/appointments.json` | `02be083e7d1d5841b29a4bb1fb663ba49f6c3d9ed47c236fa67545e8432d0d65` |
| `data/patients.json` | `4bc471bef84eccee513b2ae15127cbf532b6aa47f151831ff7c2a6b832889d48` |
| `data/providers.json` | `0745b592a15821474ebee45f868c3ed90d4bf24846903a17e7da0b210a3d92d6` |
| `data/slots.json` | `340bb75c9c737281de2e48b7c299141ce4c27e41001c0172c4e8f0927cf0ce9b` |
| `openapi/scheduling-api.yaml` | `62e17d269d924d1a3832c16a262cb85f78ebbceb078cdb73e759a91bf40fa735` |

The server loads fixtures relative to its source directory, binds loopback, and keeps mutable booking/handoff state in memory. Restart its own process to reset. Tests should instantiate independent server/store instances on OS-assigned ephemeral ports; the review demo uses its separately assigned port. Do not share booking state between tests or candidates. Returned timestamps use the supplied fixed `-05:00` fixture semantics.

The unchanged reference request audit includes patient IDs in appointment-lookup paths. Application logs must redact those IDs and must never include request queries, identity fields, credentials, model prompts, or transcripts. Route mock stdout to a private transient sink or suppress it in automated tests; do not publish raw request logs.
