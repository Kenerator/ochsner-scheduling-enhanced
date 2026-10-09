"""Bounded Responses transport: interpretation suggestions never grant authority."""
import json
import os
from urllib.request import Request, urlopen
from .models import Interpretation, INTENTS, SPECIALTIES, LOCATIONS
from .ports import ModelFailure
from .privacy import project

_SCHEMA = {'type':'object','properties':{
    'intent':{'type':'string','enum':list(INTENTS)},
    'specialty':{'type':['string','null']},'location':{'type':['string','null']},
    'clear_specialty':{'type':'boolean'},'clear_location':{'type':'boolean'}},
    'required':['intent','specialty','location','clear_specialty','clear_location'],
    'additionalProperties':False}
_INSTRUCTIONS = '''Interpret public appointment scheduling language only. Return intent and public specialty/location suggestions. Supported specialties: primary_care, dermatology. Supported locations: downtown, uptown, lakeside. Preserve previous public preferences when omitted. Explicit removal sets the respective clear flag. Unsupported requests or preferences must be unsupported, never silently substituted. Clinical requests are medical_advice; requests for human help are human_help. Ambiguity is clarify. Never produce identifiers, patient facts, choices, confirmations, or booking outcomes.'''

class ModelAdapter:
    def __init__(self, model='gpt-5.4-mini', api_key=None, timeout=30, opener=None):
        self.model=os.environ.get('OPENAI_MODEL',model)
        self._api_key=api_key if api_key is not None else os.environ.get('OPENAI_API_KEY')
        self.timeout=timeout
        self._opener=opener or urlopen

    def interpret(self,text,context):
        safe=project(text)
        if safe is None or not isinstance(context,dict) or not self._api_key:
            raise ModelFailure('Model interpretation unavailable.')
        # Context must be public validated values, never a copied session/history.
        allowed={'specialty':SPECIALTIES,'location':LOCATIONS,'intent':INTENTS,
                 'state':('idle','providers','collecting_identity','collecting_preferences','slots','proposed','booked','help'),
                 'stage':('idle','providers','collecting_identity','collecting_preferences','slots','proposed','booked','help')}
        if any(k not in allowed or (v is not None and (not isinstance(v,str) or v not in allowed[k])) for k,v in context.items()):
            raise ModelFailure('Model interpretation unavailable.')
        payload={'model':self.model,'store':False,'instructions':_INSTRUCTIONS,
                 'input':json.dumps({'message':safe,'public_context':context}),
                 'max_output_tokens':300,
                 'text':{'format':{'type':'json_schema','name':'scheduling_interpretation','strict':True,'schema':_SCHEMA}}}
        try:
            request=Request('https://api.openai.com/v1/responses',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+self._api_key,'Content-Type':'application/json'},method='POST')
            with self._opener(request,timeout=self.timeout) as stream:
                raw=stream.read(65537)
            if len(raw)>65536: raise ValueError()
            result=json.loads(raw)
            if not isinstance(result,dict) or result.get('status')!='completed': raise ValueError()
            output=result.get('output')
            if not isinstance(output,list): raise ValueError()
            texts=[]
            for item in output:
                if not isinstance(item,dict): raise ValueError()
                if item.get('type')=='reasoning': continue
                if item.get('type')!='message' or item.get('role')!='assistant': raise ValueError()
                content=item.get('content')
                if not isinstance(content,list): raise ValueError()
                for part in content:
                    if not isinstance(part,dict) or part.get('type')!='output_text' or not isinstance(part.get('text'),str): raise ValueError()
                    texts.append(part['text'])
            if len(texts)!=1: raise ValueError()
            # Duplicate JSON keys are invalid too, not last-value-wins authority.
            def unique(pairs):
                data={}
                for key,value in pairs:
                    if key in data: raise ValueError()
                    data[key]=value
                return data
            return Interpretation.from_dict(json.loads(texts[0],object_pairs_hook=unique))
        except Exception:
            # Never retain transport URL/body/credential or model output in errors.
            raise ModelFailure('Model interpretation unavailable.') from None
