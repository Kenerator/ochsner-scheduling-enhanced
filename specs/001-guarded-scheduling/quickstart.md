# Quickstart validation guide

Updated: 2026-10-08. **Implementation qualification update**:7738727 passed91tests/all4demos from fresh private Mac ARM and Minty Linux clones. Genuine application model and IAB booking/no-match checks passed separately. Use the canonical [README](../../README.md) and [UAT](../../docs/internal/uat.md); remaining actual video is explicit.

## Prerequisites

Final reproduction requires fresh authenticated private GitHub clones on both Mac ARM and Minty Linux. Local working-tree evidence does not satisfy that check. Verify Python 3.11+ before launch:

```bash
python3 -c 'import sys; print(sys.version); assert sys.version_info >= (3, 11)'
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[ui]'
```

If version check fails, select explicit compatible executable; no global tooling changes. Stdlib transports need no SDK. Reviewer baseline needs neither Bitwarden nor Marimo. Separately authorized genuine AI qualification uses approved process environment OPENAI_API_KEY and explicit OPENAI_MODEL, without pasting keys into commands/docs, copying secrets or debug output. Tests need neither key nor generation.

## Run/reset commands

Terminal 1 starts unchanged vendored reference via output-suppressing runner:

```bash
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.mock_runner --port 4011
```

No --log-file/raw audit retained. Runner verifies actual public providers readiness. Terminal 2:

```bash
PYTHONPATH=src .venv/bin/python -m guarded_scheduling --api-url http://127.0.0.1:4011
```

Assistant discloses AI/synthetic API and privately collects identity locally. Reset: Ctrl-C owned mock process and restart runner to reset synthetic bookings/handoffs; restart assistant for new session. Reset never proves uncertain write failed. Independent trials use separate processes/ports.

## Required verification after implementation

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario provider
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario booking
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario no-match
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario guards
```

Suite includes existing scaffold plus meaningful scheduling tests. Demos own isolated resettable real reference processes, suppress raw mock output and label model doubles synthetic. Genuine AI qualification separately records actual generation and intent/behavior evidence; listing HTTP 200 is insufficient. Product commands above were qualified against the implementation revision; tests and demos need no real model key.

## Acceptance scenarios

| Flow/story | Input/action | Expected observation |
|---|---|---|
| Provider/1 | Which primary care providers are downtown? Refine across turns | Qualified genuine interpretation, GET providers only, returned facts; no identity/patient search |
| Booking/2 | Book primary care; private phone 555-0101 and DOB 1985-04-12 across turns; choose returned option, inspect proposal, confirm current ID | Choice never writes; one POST after current explicit consent; valid returned appointment drives booked |
| No match/3 | Private 555-9999 and 1990-01-01 | No disclosure/availability/write; private correction or scheduling-team next step |
| Duplicate/3 | Private 555-0130 and 1978-09-22 then private synthetic ZIP | Local filtering only, no candidate disclosure; zero/multiple unresolved; exactly one permits continuation |
| Conflict/3 | Test harness chooses returned conflict fixture and confirms | 409 rejected; old consent invalid; refreshed alternative needs new confirmation; no assistant trap-ID branch |
| Empty/outage/3 | Dermatology/lakeside; separately api_failure header | No fabricated slots; accurate issue/next step; injection persists on optional handoff |
| Medical/unsupported/3 | Supplied clinical/human request and unsupported filter/scope | No advice/triage/invented eligibility/contact/endpoint; truthful boundary and help |
| Unknown effect/3 | Harness lets real server write then loses response | Unresolved, zero blind POST retry, human reconciliation; no false failed/booked/reset claim |
| Stale/adversarial/2 | Correct identity/filter/choice, repeat stale confirm, forged model IDs/confirmed or malformed/refusal output | Zero unauthorized writes/disclosures; useful correction/fresh confirmation |
| Privacy/2,5 | Capture actual serialized model requests for initial/mixed/correction/ZIP turns and allowlisted logs | Zero phone/DOB/ZIP/patient records in model input; zero excluded diagnostic fields; unsafe separation suppresses request |
| Optional Enhanced/4,5 | Verified appointment lookup, returned typo suggestion, actual mock handoff if adopted | Patient-bound facts, explicit suggestion selection; queued only on valid response, never delivered-human claim |
| Optional UI | Rerun/double click/correction/restart while pending | No repeated POST/consent revival; pending/unresolved remain distinct |

Values above are synthetic data. Harness may inspect trap fixture to select scenario; assistant logic may use only returned API facts. See [entities](data-model.md) and [contracts](contracts/README.md).

## Evidence and handoff

Record Python/platform/model configuration without secrets, single-session load, feedback/completion latency and target misses. Record fresh-clone evidence separately for each required platform. Sanitize retained screenshots/logs. <=5 minute actual-flow video includes provider, confirmed booking and no-match plus authority/architecture/limitations. Three-hour claim requires actual timing evidence; optional adoption status explicit. Near-final as-built docs use actual reviewed source revision and verified links/diagrams; tasks own completion progress. This Plan does not produce video/as-built qualification.
