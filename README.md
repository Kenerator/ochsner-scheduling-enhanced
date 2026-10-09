# Enhanced scheduling PoC

A model interprets public scheduling language across turns. Python owns identity verification, returned provider/slot facts, confirmation and HTTP effects. The unchanged supplied server uses synthetic records. This is a local demonstration; mock matching is not production authentication and a queued mock handoff is not delivered human assistance.

Contents: [Run](#run) · [Verify](#verify) · [Boundaries](#boundaries) · [Specification](specs/001-guarded-scheduling/spec.md) · [Plan](specs/001-guarded-scheduling/plan.md) · [Tasks](specs/001-guarded-scheduling/tasks.md) · [Decisions](docs/product/decisions.md) · [Architecture](docs/internal/as-built/architecture.md) · [Walkthrough](docs/internal/as-built/code-walkthrough.md) · [UAT evidence](docs/internal/uat.md) · [Next steps](docs/product/next-steps.md) · [Video notes](docs/internal/video-notes.md).

## Run

Repository: [Kenerator/ochsner-scheduling-enhanced](https://github.com/Kenerator/ochsner-scheduling-enhanced) (private; reviewers need access). Use your normal GitHub HTTPS or SSH authentication. Verify your selected interpreter is Python 3.11 or newer; on macOS the system python3 may be older.

```sh
git clone https://github.com/Kenerator/ochsner-scheduling-enhanced.git
cd ochsner-scheduling-enhanced
python3.11 -c 'import sys; print(sys.version); assert sys.version_info >= (3, 11)'
python3.11 -m venv .venv
.venv/bin/python -m pip install -e '.[ui]'
```

On Linux select a verified Python 3.11+ executable, for example python3.12. Supply OPENAI_API_KEY through your shell's protected environment and optionally OPENAI_MODEL (default gpt-5.4-mini). The application has no credential-vault dependency. Keys are never command-line arguments or project files. Model API calls require network access and account capability.

Terminal 1 starts the unchanged reference server with audit output suppressed:

```sh
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.mock_runner --port 4011
```

Terminal 2 starts the conversation:

```sh
PYTHONPATH=src .venv/bin/python -m guarded_scheduling --api-url http://127.0.0.1:4011
```

For the local browser interface:

```sh
PYTHONPATH=src .venv/bin/marimo run apps/scheduling.py --host 127.0.0.1 --port 28181
```

Use free ports; never stop an unrelated service. Find primary care providers downtown, or ask to book primary care downtown. In the CLI, `identity` opens hidden local prompts; synthetic fixture phone 555-0101 and DOB 1985-04-12 match one patient. Choose a returned option number, inspect the exact proposal, then separately type `confirm PROPOSAL-ID`. Ordinary yes does not submit. Use private controls in the browser. For spelling help, enter `specialty dermatolgy`, `location downtwon`, or `provider NAME`; suggestions require an explicit corrected command and never select automatically. `phone VALUE`, `dob YYYY-MM-DD` and `zip VALUE` are local commands for scripted synthetic trials. Do not enter real patient information.

Stop only your owned processes with Ctrl-C. Restarting the mock resets synthetic appointments/handoffs. A local conversation reset or process restart never proves that an uncertain booking failed: reconcile with a human before trying again.

## Verify

Tests need no model key. Demos use the real supplied server and explicitly labeled deterministic model doubles.

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario provider
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario booking
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario no-match
PYTHONPATH=src .venv/bin/python -m guarded_scheduling.demo --scenario guards
```

See [UAT](docs/internal/uat.md) for actual verification and remaining qualification. A passing double is not live AI evidence. The recorded live generation probe is distinct from full-application qualification. Fresh private Mac ARM and Minty Linux clones passed91tests/all4demos and dependency/Marimo checks at7738727. Actual <=5 minute video remains pending coordinated native capture assistance. No unsupported three-hour compliance statement is made.

## Boundaries

Phone, DOB, ZIP, returned patient records and raw history stay outside model requests. A conservative public-language projection suppresses unfamiliar or mixed identity wording; restate only the scheduling request and use local identity controls. Model output cannot authorize effects. Only current API slots can be proposed; separate current consent permits one booking attempt. Identity/preference corrections invalidate earlier consent. Unknown write outcomes lock further booking; no automatic POST retry or cross-process idempotency guarantee exists.

The mock has fixed-offset fixture timestamps, limited specialties/locations and no cancellation/rescheduling endpoint. This assistant gives no medical advice, triage or clinical eligibility decisions. During injected api_failure every request, including handoff, fails; the assistant cannot truthfully claim a queue. Local diagnostics contain only normalized state/route/status/reason/latency fields. Required branding assets are local and indexed in [UI assets](docs/internal/ui-assets.md).

The reusable core and thin adapters sit beside retained template tooling. Original private intake, coordination notes, credentials and raw transcripts are excluded from Git. Approved server/data/schema provenance is in [reference](vendor/reference/PROVENANCE.md). Product priorities: [backlog](docs/product/backlog.md), [roadmap](docs/product/roadmap.md), [sprint planning](docs/product/sprint-planning.md).
