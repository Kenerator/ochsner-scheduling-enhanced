import io
import json
import socket
import unittest
from urllib.request import Request, urlopen
from guarded_scheduling.ports import SchedulingUnavailable, UnknownOutcome
from test_scheduling_helpers import ReferenceServer

try:
    from guarded_scheduling.http_adapter import HttpAdapter
except ImportError:
    HttpAdapter = None

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(HttpAdapter, 'HTTP adapter behavior not implemented')

    def test_supplied_read_routes_and_fixed_offset(self):
        with ReferenceServer() as server:
            adapter = HttpAdapter(server.base_url)
            providers = adapter.request('GET','/providers', {'specialty':'primary_care','location':'downtown'})
            self.assertEqual(providers.status, 200)
            self.assertTrue(providers.data['providers'])
            matches = adapter.request('GET','/patients/search',{'phone':'555-0101','dob':'1985-04-12'}).data['matches']
            self.assertEqual([p['patientId'] for p in matches], ['pat_1001'])
            slots = adapter.request('GET','/availability',{'patientId':'pat_1001','specialty':'primary_care','location':'downtown'}).data['slots']
            self.assertTrue(slots)
            self.assertTrue(all(s['startTime'].endswith('-05:00') for s in slots))
            self.assertTrue(adapter.request('GET','/patients/pat_1001/appointments').data['appointments'])
        self.assertEqual(len(server.events), 4)

    def test_definite_rejections_and_success_change_reference_state(self):
        with ReferenceServer() as server:
            adapter=HttpAdapter(server.base_url)
            body={'patientId':'pat_1001','slotId':'slot_4001','confirmed':False}
            self.assertEqual(adapter.request('POST','/appointments',body=body).status,400)
            body['confirmed']=True
            self.assertEqual(adapter.request('POST','/appointments',body=body).status,201)
            self.assertEqual(adapter.request('POST','/appointments',body=body).status,409)
            self.assertEqual(len(server.store.appointments),3)
        self.assertEqual(len(server.events),3)

    def test_outage_header_persists_to_handoff(self):
        with ReferenceServer() as server:
            adapter=HttpAdapter(server.base_url,scenario='api_failure')
            self.assertEqual(adapter.request('GET','/providers').status,503)
            result=adapter.request('POST','/handoffs',body={'reason':'api_failure','summary':'Scheduling unavailable.'})
            self.assertEqual(result.status,503)
            self.assertEqual(server.store.handoffs,[])

    def test_lost_response_after_real_write_is_unknown_without_retry(self):
        def drop_response(handler):
            original=handler.respond
            def respond(self,status,payload):
                if self.command=='POST' and self.path=='/appointments' and status==201:
                    self.close_connection=True
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                else:
                    original(self,status,payload)
            handler.respond=respond
        with ReferenceServer(drop_response) as server:
            with self.assertRaises(UnknownOutcome):
                HttpAdapter(server.base_url).request('POST','/appointments',body={'patientId':'pat_1001','slotId':'slot_4001','confirmed':True})
            self.assertEqual(len(server.store.appointments),3)
        self.assertEqual(sum(e[0]=='POST' for e in server.events),1)

    def test_rejects_nonloopback_urls_and_zip_parameter_before_dispatch(self):
        for url in ['https://127.0.0.1:4011','http://example.com','http://127.0.0.1.evil.test','http://user:secret@127.0.0.1','http://127.0.0.1/?secret=x','http://127.0.0.1/other']:
            with self.subTest(url=url), self.assertRaises(ValueError): HttpAdapter(url)
        with ReferenceServer() as server:
            with self.assertRaises(ValueError):
                HttpAdapter(server.base_url).request('GET','/patients/search',{'phone':'555-0101','dob':'1985-04-12','zip':'00000'})
        self.assertEqual(server.events,[])

    def test_transport_and_malformed_bounds_fail_safely_without_sensitive_error(self):
        class Reply(io.BytesIO):
            status=201
        for payload in [b'{', b'[]', b'x'*(1024*1024+1)]:
            calls=[]
            def opener(request,timeout):
                calls.append(request)
                return Reply(payload)
            with self.assertRaises(UnknownOutcome) as caught:
                HttpAdapter(opener=opener).request('POST','/appointments',body={'patientId':'pat_1001','slotId':'slot_4001','confirmed':True})
            self.assertEqual(len(calls),1)
            self.assertNotIn('pat_1001',str(caught.exception))
        def broken(request,timeout): raise OSError('phone=private-secret')
        with self.assertRaises(SchedulingUnavailable) as caught:
            HttpAdapter(opener=broken).request('GET','/providers')
        self.assertNotIn('private-secret',str(caught.exception))

    def test_unexpected_write_server_error_is_unknown(self):
        def failing(handler):
            def route(self,method,parsed): return 500, {'code':'internal_error','message':'private'}
            handler.route=route
        with ReferenceServer(failing) as server:
            with self.assertRaises(UnknownOutcome):
                HttpAdapter(server.base_url).request('POST','/handoffs',body={'reason':'other','summary':'Help needed.'})
        self.assertEqual(len(server.events),1)

    def test_truncated_content_length_after_write_is_unknown(self):
        def truncated(handler):
            original=handler.respond
            def respond(self,status,payload):
                if self.command=='POST' and status==201:
                    raw=json.dumps(payload).encode()
                    self.send_response(status)
                    self.send_header('Content-Length',str(len(raw)+10))
                    self.end_headers()
                    self.wfile.write(raw)
                    self.wfile.flush()
                    self.close_connection=True
                else: original(self,status,payload)
            handler.respond=respond
        with ReferenceServer(truncated) as server:
            with self.assertRaises(UnknownOutcome):
                HttpAdapter(server.base_url).request('POST','/appointments',body={'patientId':'pat_1001','slotId':'slot_4001','confirmed':True})
            self.assertEqual(len(server.store.appointments),3)
