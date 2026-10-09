# Scheduling qualification evidence

Updated: 2026-10-09, America/Chicago. Current qualified implementation revision: 256a1b41bcbdb65927153cc8157ba4d8215e2165. Initial fresh clones qualified 7738727; both were subsequently fast-forwarded from GitHub and requalified as recorded below. Documentation-only changes are identified separately.

Python: candidate .venv 3.11.13, macOS ARM. Current combined suite passed 92 tests in 5.574s after the transport delta; all four supplied-reference demos and both remote-updated qualification clones passed. Initial qualification evidence remains below.

## Actual checks

- Meaningful red-to-green tests cover model schema, fail-closed public projection, private incremental identity and duplicate ZIP, authoritative providers/slots, separate current single-use consent, mixed correction invalidation, conflict, outage and lost/truncated response after a real write.
- Four supplied-reference demos passed: provider, booking, no-match, guards. These explicitly use scripted model interpretation and own isolated ephemeral server processes; they are not live AI evidence.
- Genuine full-application qualification passed with gpt-5.4-mini and an ordinary process environment key: find primary care providers → Downtown refinement → booking intent → local identity verification → current API slot selection → separate confirmation → one validated booking. Three model turn completions: 1.589,0.961,1.094 seconds, single session. No raw identity/request/transcript retained.
- CLI emits and flushes pending acknowledgement before work. A controlled test proves acknowledgement exists before model execution. This does not establish universal 400 ms compliance; model completion is measured separately above.
- Marimo0.25.1 actual HTML export and controller tests pass. Controlled IAB shows local Ochsner branding, disclosure, private controls and preference controls. Rendered IAB provider lookup, private local identity, returned-slot keyboard selection, proposal and separate Confirm button successfully reached API-confirmed booked. Pending spinner was observed; buttons require retained notebook bindings, now covered by an actual-cell regression.

## Remaining qualification

Both required fresh private clones, independent review and rendered IAB booking/no-match qualification are complete. Actual continuous scenario recording is pending coordinated native capture assistance; screenshots are not a video substitute. Actual <=5 minute video remains pending. No unsupported timing/window compliance statement is made.

## Reset and limits

Only owned mock processes are stopped. Restarting a mock resets synthetic state; it never proves an uncertain transaction failed. Unknown outcome locks the current session, with explicit human reconciliation required before another attempt including after restart. This PoC has no persistent reconciliation or production identity service. Keyboard controls exist; no screen-reader certification, exhaustive browser compatibility or measured multi-session/load claim is made.

## Initial fresh private clone reproduction

Implementation7738727a9f2ca97fe999527df20515a016a7332f, private origin git@kenerator-github.com:Kenerator/ochsner-scheduling-enhanced.git. Each trial used an actual authenticated GitHub clone and a new virtual environment, with no copied developer venv or credentials.

| Host | Fresh trial | Interpreter/platform | Outcome |
| --- | --- | --- | --- |
| Mac ARM | /private/tmp/ochsner-enhanced-mac-qualification.BoHZQo/repo | Python 3.11.13, macOS26.7 arm64 |91 tests passed6.003s;4 demos/pip check/Marimo check-export/owned ephemeral HTTP200 passed; tracked clone clean |
| Minty Linux | /tmp/ochsner-enhanced-qualification-MsF5LE/repo | Python 3.12.3, Linux7.0.0-34-generic x86_64 |91 tests passed6.662s;4 demos/pip check/Marimo check-export/owned ephemeral HTTP200 passed; clone clean |

Commands: git clone the private origin; verify git rev-parse HEAD; selected Python -m venv a fresh venv; venv/bin/python -m pip install -e '.[ui]'; PYTHONPATH=src venv/bin/python -m unittest discover -s tests -v; venv/bin/python -m guarded_scheduling.demo --scenario provider, booking, no-match, guards (one command each); venv/bin/python -m pip check; venv/bin/python -m marimo check apps/scheduling.py; venv/bin/python -m marimo export html apps/scheduling.py -o a temporary HTML file. Startup smoke used owned unused loopback ports61233/45923 and stopped only its own process. These startup probes use no key and do not claim browser/live-model interaction; that evidence is separately recorded above.

Both actual architecture Mermaid diagrams were rendered and visually reviewed in controlled IAB using the installed Marimo renderer. The sequence parser punctuation error was corrected before this record.21 README/spec/as-built/product documents had zero broken relative file links. No production, accessibility certification or load claim follows from these checks.

## Post-checkpoint model transport delta

Current qualified implementation: 256a1b41bcbdb65927153cc8157ba4d8215e2165. A mocked standard-library HTTPS redirect reproduced forwarding of a placeholder bearer to a second host; the default Responses opener now refuses redirects. The isolated test made no network call and used no live secret. All92 integrated tests passed locally in 5.574s. Genuine three-turn application qualification again reached providers→Downtown refinement→booking identity→current separate confirmed booking, with model completion1.622/1.622/1.099s. No raw identity/transcript retained.

The original fresh private clones above were incrementally updated by normal fetch and fast-forward-only merge from GitHub to exact256a1b4. They were not claimed as newly created clones: Mac ARM Python 3.11.13 passed 92 tests/all 4 demos/pip check/Marimo check-export; Minty Linux Python 3.12.3 passed 92 tests in 7.323s/all 4 demos/pip check/Marimo check. Both remained clean, reused their declared-dependency virtual environments and did not alter immutable tags. No dependency change occurred. Final code source is256a1b4; later documentation commits do not change that qualified code.

The main controlled IAB UI was restarted to load this exact source; a live provider lookup returned Dr. Elena Brooks and Dr. Marcus King. API 4011 remains a fresh owned synthetic baseline. Actual continuous video remains a separately coordinated follow-on and does not block product or timed checkpoints. No native recorder investigation is performed by the product lane.
