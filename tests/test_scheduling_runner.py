import subprocess
import sys
import unittest
from unittest.mock import patch
from guarded_scheduling.ports import SchedulingUnavailable
try:
    from guarded_scheduling.mock_runner import MockRunner
except ImportError:
    MockRunner=None

class RunnerTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(MockRunner,'Owned mock runner not implemented')
    def test_readiness_isolation_and_owned_cleanup(self):
        from guarded_scheduling.http_adapter import HttpAdapter
        with MockRunner(python_executable=sys.executable) as first, MockRunner(python_executable=sys.executable) as second:
            self.assertNotEqual(first.base_url,second.base_url)
            self.assertEqual(HttpAdapter(first.base_url).request('POST','/appointments',body={'patientId':'pat_1001','slotId':'slot_4001','confirmed':True}).status,201)
            self.assertEqual(HttpAdapter(second.base_url).request('POST','/appointments',body={'patientId':'pat_1001','slotId':'slot_4001','confirmed':True}).status,201)
            process=first.process
        self.assertIsNotNone(process.poll())
        with self.assertRaises(SchedulingUnavailable): HttpAdapter(first.base_url,timeout=.1).request('GET','/providers')
    def test_occupied_port_is_rejected_without_touching_occupant(self):
        from test_scheduling_helpers import ReferenceServer
        from guarded_scheduling.http_adapter import HttpAdapter
        with ReferenceServer() as other:
            port=other.server.server_port
            with self.assertRaises(RuntimeError):
                with MockRunner(sys.executable,port=port): pass
            self.assertEqual(HttpAdapter(other.base_url).request('GET','/providers').status,200)
    def test_missing_interpreter_is_sanitized(self):
        with self.assertRaises(RuntimeError) as caught:
            with MockRunner('/not-present/private-identifier'): pass
        self.assertNotIn('private-identifier',str(caught.exception))
    def test_old_interpreter_is_rejected(self):
        with patch('guarded_scheduling.mock_runner.subprocess.run',return_value=subprocess.CompletedProcess([],0,'3.10\n','')):
            with self.assertRaises(RuntimeError):
                with MockRunner(sys.executable): pass
    def test_subprocess_output_is_suppressed(self):
        original=subprocess.Popen
        observed=[]
        def capture(*args,**kwargs):
            if args and '--port' in args[0]: observed.append(kwargs)
            return original(*args,**kwargs)
        with patch('guarded_scheduling.mock_runner.subprocess.Popen',side_effect=capture):
            with MockRunner(sys.executable): pass
        self.assertEqual(len(observed),1)
        self.assertEqual(observed[0]['stdout'],subprocess.DEVNULL)
        self.assertEqual(observed[0]['stderr'],subprocess.DEVNULL)
