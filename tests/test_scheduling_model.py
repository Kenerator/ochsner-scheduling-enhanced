import io,json,os,unittest
from unittest.mock import patch
from guarded_scheduling.model_adapter import ModelAdapter
from guarded_scheduling.ports import ModelFailure
VALID=dict(intent='provider_lookup',specialty='primary_care',location='downtown',clear_specialty=False,clear_location=False)
def response(value=VALID,**updates):
    reply=dict(status='completed',output=[dict(type='message',role='assistant',content=[dict(type='output_text',text=json.dumps(value))])]);reply.update(updates);return reply
class ModelTests(unittest.TestCase):
    def adapter(self,reply,calls):
        def opener(req,timeout): calls.append((req,timeout));return io.BytesIO(json.dumps(reply).encode())
        return ModelAdapter(api_key='placeholder',opener=opener)
    def test_strict_public_request(self):
        calls=[];result=self.adapter(response(),calls).interpret('Which primary care doctors are downtown?',{'specialty':'primary_care','location':None})
        self.assertEqual(result.intent,'provider_lookup');req,timeout=calls[0];payload=json.loads(req.data)
        self.assertEqual(req.full_url,'https://api.openai.com/v1/responses');self.assertFalse(payload['store']);self.assertNotIn('tools',payload)
        schema=payload['text']['format'];self.assertTrue(schema['strict']);self.assertFalse(schema['schema']['additionalProperties']);self.assertEqual(set(schema['schema']['required']),set(VALID));self.assertEqual(set(schema['schema']['properties']),set(VALID));self.assertEqual(timeout,30)
    def test_environment_configuration(self):
        calls=[]
        with patch.dict(os.environ,{'OPENAI_API_KEY':'placeholder','OPENAI_MODEL':'configured-model'},clear=True):
            adapter=ModelAdapter(opener=lambda req,timeout:(calls.append(req) or io.BytesIO(json.dumps(response()).encode())));adapter.interpret('Find doctors',{})
        self.assertEqual(json.loads(calls[0].data)['model'],'configured-model')
    def test_rejects_invalid_output(self):
        for value in [{**VALID,'confirmed':True},{**VALID,'clear_location':1},{**VALID,'intent':'book_now'},{**VALID,'specialty':[]},{'intent':'book'},[]]:
            with self.subTest(value=value),self.assertRaises(ModelFailure):self.adapter(response(value),[]).interpret('Find doctors',{})
        for reply in [response(status='incomplete'),response(output=[]),response(output=[{'type':'message','content':[{'type':'refusal','refusal':'private'}]}]),response(output=[{'type':'message','content':[{'type':'output_text','text':'bad json'}]}])]:
            with self.subTest(reply=reply),self.assertRaises(ModelFailure):self.adapter(reply,[]).interpret('Find doctors',{})
    def test_private_inputs_suppress_transport(self):
        for text,context in [('Find doctors, phone 5045550100',{}),('Find doctors',{'patientId':'private'}),('Find doctors',{'specialty':'private-name'}),('Find doctors',{'history':['private']})]:
            calls=[]
            with self.subTest(text=text),self.assertRaises(ModelFailure):self.adapter(response(),calls).interpret(text,context)
            self.assertEqual(calls,[])
    def test_failure_is_static_without_retry(self):
        calls=[]
        def fail(req,timeout):calls.append(req);raise RuntimeError('secret URL and body')
        with self.assertRaises(ModelFailure) as caught:ModelAdapter(api_key='placeholder',opener=fail).interpret('Find doctors',{})
        self.assertNotIn('secret',str(caught.exception));self.assertEqual(len(calls),1)
    def test_missing_credentials(self):
        with patch.dict(os.environ,{},clear=True),self.assertRaises(ModelFailure):ModelAdapter().interpret('Find doctors',{})
