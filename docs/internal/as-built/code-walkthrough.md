# Code walkthrough

Updated: 2026-10-09 (America/Chicago). Source inspected: implementation 256a1b41bcbdb65927153cc8157ba4d8215e2165; reviewed source and both fresh-clone qualification are pinned to this implementation commit. This document describes inspected code and test coverage, not a fresh-clone, browser, live-model or final-review qualification.

Use this navigation aid with the [as-built architecture](architecture.md), [native tasks](../../../specs/001-guarded-scheduling/tasks.md), [decisions](../../product/decisions.md) and [UAT evidence](../uat.md). Native tasks own completion status; UAT owns qualification evidence.

## Find the relevant code

All source and test links below resolve from this document's directory.

| Change or inspection | File and symbols | Relevant tests | Boundary to preserve |
| --- | --- | --- | --- |
| Conversation and authoritative state | [core.py](../../../src/guarded_scheduling/core.py): `SchedulingSession`, `message`, `_advance`, `serialized` | [provider](../../../tests/test_scheduling_provider.py), [identity](../../../tests/test_scheduling_duplicates.py), [consent](../../../tests/test_scheduling_consent.py) | A model suggests intent and public preferences; core verifies identity, validates facts and controls effects under one session lock. |
| Validated values and returned records | [models.py](../../../src/guarded_scheduling/models.py): `PrivateIdentity`, `Preferences`, `Interpretation`, `Proposal`, `View`, `validate_providers`, `validate_slots`, `validate_appointment` | [models](../../../tests/test_scheduling_models.py) | Reject malformed types, extra interpretation fields, duplicate identifiers and foreign patient/search/proposal results before using them. |
| Effect interfaces and safe failures | [ports.py](../../../src/guarded_scheduling/ports.py): `Response`, `ModelPort`, `SchedulingPort`, `ModelFailure`, `SchedulingUnavailable`, `UnknownOutcome` | [HTTP](../../../tests/test_scheduling_http.py), [model](../../../tests/test_scheduling_model.py) | Model output carries no consent or scheduling effect; unavailable reads differ from uncertain writes. |
| Public model input | [privacy.py](../../../src/guarded_scheduling/privacy.py): `project` | [privacy](../../../tests/test_scheduling_privacy.py), [identity](../../../tests/test_scheduling_duplicates.py), [consent](../../../tests/test_scheduling_consent.py) | Suppress mixed/uncertain private input rather than treating regex masking as proof of safety. |
| Genuine interpretation transport | [model_adapter.py](../../../src/guarded_scheduling/model_adapter.py): `ModelAdapter.interpret` | [model](../../../tests/test_scheduling_model.py) | Responses receives only approved public prose and validated public context; strict output is independently validated. |
| Supplied scheduling HTTP | [http_adapter.py](../../../src/guarded_scheduling/http_adapter.py): `HttpAdapter.request` | [HTTP](../../../tests/test_scheduling_http.py) | Loopback origin, bounded requests/replies/timeouts, no redirects/proxies or write retry; no raw URL-bearing errors. |
| CLI entry and feedback | [__main__.py](../../../src/guarded_scheduling/__main__.py): `run`, `main` | [CLI](../../../tests/test_scheduling_cli.py) | Pending acknowledgement precedes work; local commands and separate proposal confirmation delegate to core. |
| Reactive UI event boundary | [ui_adapter.py](../../../src/guarded_scheduling/ui_adapter.py): `UiController.dispatch`, `snapshot`; [Marimo app](../../../apps/scheduling.py) | [UI adapter](../../../tests/test_scheduling_ui.py) | Snapshot/render has no effects; explicit events claim their IDs before dispatch and confirmations bind the displayed proposal. |
| Explicit spelling suggestions | [suggestions.py](../../../src/guarded_scheduling/suggestions.py): `suggest`; core `set_preferences`, `select_provider` | [suggestions](../../../tests/test_scheduling_suggestions.py), [integration](../../../tests/test_scheduling_suggestion_integration.py) | RapidFuzz compares public vocabulary or validated returned provider names; suggestions never silently select or clinically rank. |
| Private diagnostics | [diagnostics.py](../../../src/guarded_scheduling/diagnostics.py): `Diagnostics.__call__`; core `_event`, `_request` | [diagnostics](../../../tests/test_scheduling_diagnostics.py) | Serialize only validated allowlisted values, normalize patient routes and omit identity, raw prompts, exception text and payloads. |
| Owned mock process and repeatable demos | [mock_runner.py](../../../src/guarded_scheduling/mock_runner.py): `MockRunner`; [demo.py](../../../src/guarded_scheduling/demo.py): `run`, `main`, `ScriptedModel` | [runner](../../../tests/test_scheduling_runner.py), [demo](../../../tests/test_scheduling_demo.py), [lookup](../../../tests/test_scheduling_lookup.py) | Python 3.11+, owned ephemeral process, suppressed server output and actual returned-outcome checks. Scripted interpretation is explicitly disclosed. |

## Follow a request through the code

`python -m guarded_scheduling` constructs the HTTP and real model adapters and a `SchedulingSession`. The CLI writes a pending acknowledgement before invoking the core. Its `identity` command uses hidden local prompts; phone/DOB/ZIP commands, date bounds, current choice numbers and `confirm PROPOSAL-ID` are parsed locally. The Marimo app builds explicit request, private identity, preference, choice and confirmation controls over the same session authority. Its branding/theme entry points are [theme.css](../../../assets/ui/theme.css) and [ochsner-health.svg](../../../assets/ui/ochsner-health.svg); provenance and permitted usage belong in the [asset index](../ui-assets.md).

`SchedulingSession.message` handles local commands before `project`. The projection accepts conservative ASCII public prose, rejects numeric/structured/unknown input and checks caller-known private values for collisions. While identity or ZIP is expected, conversational projection is suppressed. Phone, DOB, ZIP, returned patient records, dates, choice indexes and raw history do not become model context. An unsafe message invalidates the earlier proposal and identity-derived state before asking for local correction.

`ModelAdapter.interpret` rechecks projection and validates context keys/values. It sends a bounded Responses request with `store:false`, no tools and a strict five-field schema: `intent`, nullable `specialty`/`location`, and boolean `clear_specialty`/`clear_location`. It requires completed output, rejects refusal/incomplete/malformed content and duplicate JSON keys, and constructs `Interpretation.from_dict`. Transport and validation failures become a static `ModelFailure` without raw exception text. Neither schema nor core interpretation grants patient IDs, slot IDs, confirmation or outcome prose.

For public lookup, `_advance` requests `/providers` without identity search. It displays validated returned provider facts. For booking or appointment lookup, missing phone/DOB causes a local identity request. `_advance` validates `PrivateIdentity`, calls `/patients/search`, and permits patient-specific work only after exactly one match. Duplicate matches require local ZIP filtering over the already returned candidates; ZIP is not added to the HTTP search query and candidate names/alternatives are not displayed. Identity corrections invalidate patient-bound choices and require verification again.

Booking retrieves `/availability` only for the verified patient and accepted preferences. `validate_slots` checks available flags, unique IDs, specialty/location/date bounds and timezone-aware returned timestamps; a selected authoritative provider is filtered locally after validating the broad API response. Times retain the supplied fixed offset; the application does not reinterpret fixture-relative dates itself. Appointment lookup requests `/patients/{patientId}/appointments`, validates each result against the verified patient and renders only public appointment display fields. [Lookup tests](../../../tests/test_scheduling_lookup.py) exercise verification and correction against an isolated actual reference server.

## Follow authority and failure

`choose` selects only a current returned option and creates an opaque `Proposal` bound to patient and context revision. Selection causes no booking request. `confirm` accepts the current proposal ID, consumes the proposal before dispatch, sets `submitting`, and sends one `/appointments` POST with the bound patient/slot and explicit `confirmed:true`. Model-generated confirmation, bare yes, stale IDs and replayed UI events cannot supply this authority. A valid bound 201 is required for the `booked` view; the appointment is checked against the proposed patient, provider, specialty, location and exact returned time.

Corrections invalidate consent. A 409 clears the old proposal and requires refresh, selection and new confirmation. Invalid/unavailable model output cannot cause a booking. Medical, unsupported and human-help requests become fixed boundary explanations and minimized `/handoffs` requests. A queued claim requires a valid actual mock 201; the text explicitly says a mock queue is not delivered human help. Outage injection is HTTP-adapter configuration and remains active for handoff requests, so outage does not become a false queue claim.

`HttpAdapter` distinguishes unavailable reads from writes that may have taken effect. Transport loss, truncated/malformed replies and unexpected write responses become `UnknownOutcome`; core also treats an unusable/unbound successful booking response as unresolved. `_unresolved` locks booking in the current session. `reset` cannot clear that lock, and the UI refuses further dispatch while unresolved. [Demo tests](../../../tests/test_scheduling_demo.py) drop a response after an actual reference-server write and assert one POST, changed server state and persistent unresolved reset/confirmation behavior.

The unresolved lock is **in-memory and session-only**. A newly constructed process/session does not recover it. CLI and core warnings explicitly say reset/restart is not reconciliation; the supplied API has no reconciliation endpoint. Do not turn a new session or restarted mock into evidence that an earlier uncertain transaction failed. Durable transaction recovery and production identity/authentication remain outside this PoC.

## Read the verification evidence correctly

The tests use `MemoryApi`/scripted interpretations for focused core cases and [ReferenceServer](../../../tests/test_scheduling_helpers.py) for isolated supplied-server HTTP behavior. `ReferenceServer` gives each test its own store, ephemeral port and suppressed audit handling. Its deliberate dropped/truncated responses are test-only fault injection, not a changed supplied server or production transport feature.

The four `guarded_scheduling.demo` commands are `provider`, `booking`, `no-match` and `guards`. Each owns a `MockRunner` process and reports scripted interpretation plus supplied-reference backend. Provider checks returned facts and absence of identity lookup; booking compares actual appointment state before/after exact separate confirmation; no-match prevents availability/booking; guards covers duplicate ZIP, real conflict, injected outage and medical boundaries. These runs do not qualify genuine model behavior or browser accessibility.

Use an explicit compatible project interpreter:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo provider
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo booking
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo no-match
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo guards
```

The public vocabulary is intentionally conservative: unfamiliar wording, non-ASCII prose or mixed identity may require restatement/local controls. It is not general-purpose de-identification. Model doubles do not prove live AI; UI-controller tests do not prove full browser/rerun/accessibility behavior; process restart resets synthetic mock state and does not reconcile uncertainty. See [UAT](../uat.md), [video notes](../video-notes.md) and [next steps](../../product/next-steps.md) for actual evidence and remaining work rather than inferring readiness from this walkthrough.

## Small team-review change

A useful bounded exercise is adding one ordinary public scheduling phrase to `privacy.project` without admitting identity. First add a literal phrase case in [privacy tests](../../../tests/test_scheduling_privacy.py), observe rejection, then adjust only the public vocabulary and verify mixed identity/number-word/known-value collision cases still suppress transmission. Run the full suite and four demos above. Preserve local identity, dates, choice and separate current confirmation; do not solve a phrase failure by forwarding arbitrary raw messages or weakening model schema validation.

For a different exercise, extend [suggestion tests](../../../tests/test_scheduling_suggestions.py) with a genuine spelling-distance boundary before changing `suggest`; preserve authoritative candidate provenance and explicit selection. Packaging pins and launch details are in [pyproject.toml](../../../pyproject.toml) and [development](../development.md). Reviewed commit/tag evidence belongs in [milestones](../milestones.md).

Model transport delta: the default Responses opener rejects redirects before bearer credentials can leave the fixed API origin. A mocked stdlib redirect regression reproduced the earlier forwarding and now passes; no actual credential/network was used in that test. Genuine application qualification and both remote-updated qualification clones passed after this change.
