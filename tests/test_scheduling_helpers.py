"""Isolated supplied-reference test utilities; never a replacement backend."""
import importlib.util
from pathlib import Path
import threading
from http.server import ThreadingHTTPServer

_PATH = Path(__file__).resolve().parents[1] / 'vendor/reference/mock-api/server.py'
_SPEC = importlib.util.spec_from_file_location('supplied_scheduling_reference', _PATH)
reference = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(reference)


class ReferenceServer:
    def __init__(self, handler_modifier=None):
        self.store = reference.Store()
        self.events = []
        owner = self
        class IsolatedHandler(reference.Handler):
            store = owner.store
            log_fh = None
            def audit(self, method, path, status, ms):
                route = '/patients/{patientId}/appointments' if path.startswith('/patients/') and path.endswith('/appointments') else path
                owner.events.append((method, route, status))
        if handler_modifier:
            handler_modifier(IsolatedHandler)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), IsolatedHandler)
        self.base_url = 'http://127.0.0.1:' + str(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
    def __enter__(self):
        self.thread.start()
        return self
    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class ScriptedModel:
    def __init__(self, *interpretations):
        self.values = iter(interpretations)
        self.calls = []
    def interpret(self, text, context):
        self.calls.append((text, dict(context)))
        value = next(self.values)
        if isinstance(value, Exception):
            raise value
        return value
