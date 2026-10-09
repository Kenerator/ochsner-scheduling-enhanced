# Development

Updated: 2026-10-09. Candidate .venv uses Python3.11.13; verify3.11+ before setup. Install editable with ` .venv/bin/python -m pip install -e '.[ui]' ` after creating the venv with an explicit compatible interpreter. Tested UI dependencies are in [lock](../../requirements-ui.lock); application code is [guarded_scheduling](../../src/guarded_scheduling).

Keep deterministic authority in the core, thin UI/CLI and bounded HTTP/model ports. Run `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v` and all four [demo commands](../../README.md#verify). Templates/bootstrap helpers are retained unchanged. Never put vault access in reviewer runtime, log raw inputs or use real patient records.

## Team modification exercise

Add a meaningful date-bound test to [models tests](../../tests/test_scheduling_models.py) before changing behavior: reject a reversed range and preserve exact returned fixed-offset time at a valid bound. Observe a failing behavioral assertion, change shared validation only if justified, run models/core/HTTP tests and all demos. Do not invent a new specialty/filter absent from the supplied API. Preference corrections must still invalidate old confirmation.

Changes needing a new API capability belong in a separately accepted design. Unknown outcomes remain locked, even if a UI exercise resets the local conversation. See [architecture](as-built/architecture.md) and [security](security.md) before committing. Native Spec-Kit stages are recorded under [feature](../../specs/001-guarded-scheduling/plan.md); no stages run concurrently on the same native state.
