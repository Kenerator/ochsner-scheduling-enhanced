"""Consumer routing evidence uses the installed runtime and real app constructors.

Adapter routing uses fake HTTPS. Lifecycle tests start only owned synthetic
vendor and harmless model-canary children. No vault lookup or paid model request
is permitted by these tests.
"""
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import shutil
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'tools' / 'poc-runtime'
STALE = 'stale-synthetic-key'


class RuntimeLauncherTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((RUNTIME / 'launch.py').is_file(),
                        'Reviewed shared runtime has not been installed.')
        self.assertTrue((ROOT / 'poc-launch.json').is_file(),
                        'Enhanced launcher configuration has not been integrated.')
        self.path = patch.object(sys, 'path', [str(RUNTIME), *sys.path])
        self.path.start()
        self.addCleanup(self.path.stop)
        for name in ('launch', 'adapters', 'credentials', 'processes'):
            previous = sys.modules.pop(name, None)
            def restore(name=name, previous=previous):
                sys.modules.pop(name, None)
                if previous is not None:
                    sys.modules[name] = previous
            self.addCleanup(restore)
        self.launch = importlib.import_module('launch')
        self.adapters = importlib.import_module('adapters')
        self.credentials = importlib.import_module('credentials')
        self.processes = importlib.import_module('processes')
        self.config = self.launch.load_config(ROOT / 'poc-launch.json')

    def model_spec(self, interface, model=None, environ=None):
        arguments = ['--interface', interface]
        if model:
            arguments += ['--model', model]
        with patch.dict(os.environ, environ or {}, clear=True):
            request = self.launch.resolve_request(self.config, arguments, os.environ)
            specs = self.adapters.process_specs(ROOT, self.config, request,
                                              key='synthetic-launcher-canary')
        hosts = [spec for spec in specs if spec.role == 'model']
        self.assertEqual(1, len(hosts))
        for spec in specs:
            self.assertNotIn('synthetic-launcher-canary', ' '.join(spec.argv))
            self.assertNotIn('BW_SESSION', spec.environment)
            if spec.role != 'model':
                self.assertNotIn('OPENAI_API_KEY', spec.environment)
        return request, hosts[0]

    def assert_actual_constructor(self, interface, expected_model, environ=None, override=None):
        from guarded_scheduling import __main__ as cli
        from guarded_scheduling.model_adapter import ModelAdapter
        from guarded_scheduling.ui_adapter import UiController
        request, host = self.model_spec(interface, override, environ)
        captured = []
        def opener(req, timeout):
            captured.append(json.loads(req.data))
            response = {'status': 'completed', 'output': [{'type': 'message',
                'role': 'assistant', 'content': [{'type': 'output_text', 'text': json.dumps({
                    'intent': 'provider_lookup', 'specialty': 'primary_care',
                    'location': 'downtown', 'clear_specialty': False, 'clear_location': False})}]}]}
            return io.BytesIO(json.dumps(response).encode())
        def constructor():
            return ModelAdapter(opener=opener)
        with patch.dict(os.environ, host.environment, clear=True):
            if interface == 'cli':
                self.assertEqual(('-m', 'guarded_scheduling'), host.argv[1:3])
                with patch.object(cli, 'ModelAdapter', constructor), patch.object(cli, 'run', return_value=0) as run:
                    self.assertEqual(0, cli.main(list(host.argv[3:])))
                    adapter = run.call_args.args[0].model
            else:
                self.assertEqual(('-m', 'marimo', 'run'), host.argv[1:4])
                self.assertIn(str(ROOT / 'apps/scheduling.py'), host.argv)
                self.assertIn('--headless', host.argv)
                with patch('guarded_scheduling.ui_adapter.ModelAdapter', constructor):
                    controller = UiController.from_environment()
                    self.assertEqual(host.environment['SCHEDULING_API_URL'], controller.session.api.base_url)
                    adapter = controller.session.model
            result = adapter.interpret('Find primary care downtown', {})
        self.assertEqual('model', request.mode)
        self.assertEqual('provider_lookup', result.intent)
        self.assertEqual(expected_model, captured[0]['model'])
        self.assertFalse(captured[0]['store'])

    def test_cli_and_browser_construct_real_default_adapter(self):
        for interface in ('cli', 'browser'):
            with self.subTest(interface=interface):
                self.assert_actual_constructor(interface, 'gpt-5.4-mini')

    def test_environment_model_and_explicit_override_reach_real_adapter(self):
        for interface in ('cli', 'browser'):
            with self.subTest(interface=interface):
                self.assert_actual_constructor(interface, 'configured-model',
                                               {'OPENAI_MODEL': 'configured-model'})
                self.assert_actual_constructor(interface, 'explicit-model',
                                               {'OPENAI_MODEL': 'configured-model'}, 'explicit-model')

    def test_exact_credential_reference_and_no_inherited_key(self):
        self.assertEqual('[Env] (Ochsner PoC) OPENAI_API_KEY', self.config['credential']['item'])
        _, host = self.model_spec('cli', environ={
            'OPENAI_API_KEY': STALE, 'BW_SESSION': 'synthetic-session'})
        self.assertEqual('synthetic-launcher-canary', host.environment['OPENAI_API_KEY'])
        self.assertNotIn('stale-synthetic-key', repr(host))
        self.assertNotIn('synthetic-launcher-canary', repr(host))

    def test_help_neither_resolves_credentials_nor_starts_children(self):
        with (patch.object(self.credentials, 'resolve_key', side_effect=AssertionError('vault called')),
             patch.object(self.processes, 'run_owned', side_effect=AssertionError('children started')),
             patch('sys.stdout', new_callable=io.StringIO)):
            self.assertEqual(0, self.launch.main(['--help']))

    def test_unsupported_interactive_offline_fails_without_substitution(self):
        with self.assertRaises(self.launch.LaunchError):
            self.launch.resolve_request(self.config, ['--offline'], {})

    def test_reviewed_manifest_matches_all_installed_module_bytes(self):
        manifest = json.loads((RUNTIME / 'export-manifest.json').read_text())
        self.assertEqual('b7875452e3a999ca69ce170822c66e7f679b4442', manifest['source_revision'])
        self.assertEqual('clean', manifest['source_worktree_state'])
        expected = {'adapters.py', 'credentials.py', 'launch.py', 'processes.py'}
        self.assertEqual(expected, {Path(p).name for p in manifest['files']})
        for relative, digest in manifest['files'].items():
            self.assertEqual(digest, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())
        self.assertEqual('enhanced', self.config['adapter'])
        self.assertEqual('cli', self.config['default_interface'])
        self.assertEqual('notes', self.config['credential']['field'])

    def free_port(self):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            return probe.getsockname()[1]

    def test_doctor_has_no_vault_process_or_model_operation(self):
        # Only executable discovery is allowed: this harmless executable is never run.
        helper = str(Path(shutil.which('true')).resolve())
        with (patch.dict(os.environ, {'POC_SECRET_HELPER': helper}),
              patch.object(self.credentials, 'resolve_key', side_effect=AssertionError('vault called')),
              patch.object(self.processes, 'run_owned', side_effect=AssertionError('children started')),
              patch('guarded_scheduling.model_adapter.ModelAdapter.interpret', side_effect=AssertionError('model called')),
              patch('sys.stdout', new_callable=io.StringIO) as output):
            self.assertEqual(0, self.launch.main(['--config', str(ROOT / 'poc-launch.json'),
                '--doctor', '--api-port', str(self.free_port())]))
        self.assertIn('no credentials retrieved or model request made', output.getvalue())

    def test_invalid_ports_modes_and_models_fail_without_fallback(self):
        for arguments in (['--api-port', '0'], ['--api-port', '65536'],
                          ['--model', ''], ['--model', 'two names'], ['--unexpected']):
            with self.subTest(arguments=arguments), self.assertRaises(self.launch.LaunchError):
                self.launch.resolve_request(self.config, arguments, {})
        for arguments in (['--api-port', '29001', '--ui-port', '29001', '--interface', 'browser'],
                          ['--transport-port', '29002'], ['--ui-port', '29002']):
            request = self.launch.resolve_request(self.config, arguments, {})
            with self.subTest(arguments=arguments), self.assertRaises(self.launch.LaunchError):
                self.adapters.process_specs(ROOT, self.config, request, key='synthetic-canary')

    def test_missing_browser_dependency_is_safe_preflight_failure(self):
        request = self.launch.resolve_request(self.config, ['--interface', 'browser'], {})
        with patch.object(self.adapters.importlib.util, 'find_spec', return_value=None):
            with self.assertRaisesRegex(self.launch.LaunchError, 'browser dependency is missing'):
                self.adapters.preflight(ROOT, self.config, request)

    def test_configuration_errors_precede_credential_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config.json'
            config.write_text('{"schema_version":1,"schema_version":1}')
            with (patch.object(self.credentials, 'resolve_key', side_effect=AssertionError('vault called')),
                  patch.object(self.processes, 'run_owned', side_effect=AssertionError('children started')),
                  patch('sys.stderr', new_callable=io.StringIO)):
                self.assertEqual(2, self.launch.main(['--config', str(config)]))

    def test_normal_entrypoint_routes_named_key_and_override_to_model_only(self):
        with (patch.object(self.credentials, 'resolve_key', return_value='synthetic-entry-canary') as resolve,
              patch.object(self.processes, 'run_owned', return_value=0) as run,
              patch.dict(os.environ, {'OPENAI_API_KEY': STALE, 'OPENAI_MODEL': 'inherited-model'})):
            self.assertEqual(0, self.launch.main(['--config', str(ROOT / 'poc-launch.json'),
                '--api-port', str(self.free_port()), '--model', 'explicit-model']))
        resolve.assert_called_once_with(self.config['credential'])
        specs = run.call_args.args[0]
        self.assertEqual(['mock', 'model'], [s.role for s in specs])
        self.assertNotIn('OPENAI_API_KEY', specs[0].environment)
        self.assertEqual('synthetic-entry-canary', specs[1].environment['OPENAI_API_KEY'])
        self.assertEqual('explicit-model', specs[1].environment['OPENAI_MODEL'])

    def test_credential_failure_starts_no_child_and_does_not_fallback(self):
        with (patch.object(self.credentials, 'resolve_key', side_effect=self.launch.LaunchError('Credential unavailable.')),
              patch.object(self.processes, 'run_owned', side_effect=AssertionError('fallback started')),
              patch.dict(os.environ, {'OPENAI_API_KEY': STALE}),
              patch('sys.stderr', new_callable=io.StringIO) as output):
            self.assertEqual(2, self.launch.main(['--config', str(ROOT / 'poc-launch.json'),
                '--api-port', str(self.free_port())]))
        self.assertIn('Credential unavailable.', output.getvalue())
        self.assertNotIn('stale-synthetic-key', output.getvalue())

    def test_occupied_foreign_listener_survives_preflight(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            port = listener.getsockname()[1]
            request = self.launch.resolve_request(self.config, ['--api-port', str(port)], {})
            with self.assertRaisesRegex(self.launch.LaunchError, 'occupied'):
                self.adapters.preflight(ROOT, self.config, request)
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                pass

    def run_owned_probe(self, cancel=False):
        request = self.launch.resolve_request(self.config, ['--api-port', str(self.free_port())], {})
        with patch.dict(os.environ, {'GH_TOKEN': 'synthetic-token', 'BW_SESSION': 'synthetic-session'}):
            specs = self.adapters.process_specs(ROOT, self.config, request, key='synthetic-canary')
        # Run the real unchanged vendor process; replace only the model host with
        # a harmless local canary, so lifecycle qualification incurs no model call.
        model = specs[-1]
        canary = (sys.executable, '-c',
            'import os; assert "OPENAI_API_KEY" in os.environ; assert "BW_SESSION" not in os.environ; assert "GH_TOKEN" not in os.environ')
        specs[-1] = self.processes.ProcessSpec('model', canary, model.environment)
        children = []
        def popen(argv, **kwargs):
            if len(children) == 0:
                self.assertNotIn('OPENAI_API_KEY', kwargs['env'])
                self.assertNotIn('BW_SESSION', kwargs['env'])
                self.assertNotIn('GH_TOKEN', kwargs['env'])
                self.assertEqual(subprocess.DEVNULL, kwargs['stdout'])
                self.assertEqual(subprocess.DEVNULL, kwargs['stderr'])
            child = subprocess.Popen(argv, **kwargs)
            children.append(child)
            return child
        if cancel:
            with patch.object(self.processes, 'wait_for_selected_application', side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    self.processes.run_owned(specs, popen=popen)
        else:
            self.assertEqual(0, self.processes.run_owned(specs, popen=popen))
        self.assertEqual(2, len(children))
        self.assertTrue(all(child.poll() is not None for child in children))
        self.adapters.check_ports([request.api_port])

    def test_actual_vendor_child_is_secret_free_owned_and_reaped(self):
        self.run_owned_probe()

    def test_cancellation_reaps_owned_vendor_and_model_children(self):
        self.run_owned_probe(cancel=True)
