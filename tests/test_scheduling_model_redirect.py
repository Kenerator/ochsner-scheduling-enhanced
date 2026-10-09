import io
import json
import unittest
from email.message import Message
from urllib.response import addinfourl
from unittest.mock import patch
from guarded_scheduling.model_adapter import ModelAdapter
from guarded_scheduling.ports import ModelFailure

class ModelRedirectTest(unittest.TestCase):
    def test_redirect_cannot_forward_credential_or_prompt_to_another_host(self):
        requests=[]
        def respond(handler,request):
            requests.append(request)
            headers=Message()
            if len(requests)==1:
                headers['Location']='https://other.example/collect'
                reply=addinfourl(io.BytesIO(b''),headers,request.full_url,302);reply.msg='Found'
                return reply
            payload={'status':'completed','output':[{'type':'message','role':'assistant','content':[{'type':'output_text','text':json.dumps({'intent':'provider_lookup','specialty':None,'location':None,'clear_specialty':False,'clear_location':False})}]}]}
            reply=addinfourl(io.BytesIO(json.dumps(payload).encode()),headers,request.full_url,200);reply.msg='OK'
            return reply
        with patch('urllib.request.HTTPSHandler.https_open',respond):
            with self.assertRaises(ModelFailure):ModelAdapter(api_key='placeholder').interpret('Find providers',{})
        self.assertEqual(len(requests),1)
        self.assertEqual(requests[0].full_url,'https://api.openai.com/v1/responses')
