# Scheduling qualification evidence

Updated: 2026-10-09, America/Chicago. Qualified implementation revision: 7738727a9f2ca97fe999527df20515a016a7332f. Both fresh private GitHub clones resolved this exact HEAD; later documentation-only changes are identified separately.

Python: candidate .venv 3.11.13, macOS ARM. Combined suite passed91 tests in6.027s after final integration and independent review fixes; all four supplied-reference demo commands passed. Final fresh-clone reruns remain required.

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

## Fresh private clone reproduction

Implementation7738727a9f2ca97fe999527df20515a016a7332f, private origin git@kenerator-github.com:Kenerator/ochsner-scheduling-enhanced.git. Each trial used an actual authenticated GitHub clone and a new virtual environment, with no copied developer venv or credentials.

| Host | Fresh trial | Interpreter/platform | Outcome |
| --- | --- | --- | --- |
| Mac ARM | /private/tmp/ochsner-enhanced-mac-qualification.BoHZQo/repo | Python3.11.13, macOS26.7 arm64 |91tests passed6.003s;4demos/pipcheck/Marimo check-export/owned ephemeral HTTP200 passed; tracked clone clean |
| Minty Linux | /tmp/ochsner-enhanced-qualification-MsF5LE/repo | Python3.12.3, Linux7.0.0-34-generic x86_64 |91tests passed6.662s;4demos/pipcheck/Marimo check-export/owned ephemeral HTTP200 passed; clone clean |

Commands: git clone the private origin; verify git rev-parse HEAD; selected Python -m venv a fresh venv; venv/bin/python -m pip install -e '.[ui]'; PYTHONPATH=src venv/bin/python -m unittest discover -s tests -v; venv/bin/python -m guarded_scheduling.demo --scenario provider, booking, no-match, guards (one command each); venv/bin/python -m pip check; venv/bin/python -m marimo check apps/scheduling.py; venv/bin/python -m marimo export html apps/scheduling.py -o a temporary HTML file. Startup smoke used owned unused loopback ports61233/45923 and stopped only its own process. These startup probes use no key and do not claim browser/live-model interaction; that evidence is separately recorded above.

Both actual architecture Mermaid diagrams were rendered and visually reviewed in controlled IAB using the installed Marimo renderer. The sequence parser punctuation error was corrected before this record.21 README/spec/as-built/product documents had zero broken relative file links. No production, accessibility certification or load claim follows from these checks.
