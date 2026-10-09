"""Allowlisted diagnostic serialization; never copy event payloads wholesale."""
import json
import math
import re
from .models import INTENTS

_STATES={'clarify','needs_identity','needs_zip','needs_preferences','providers','appointments','options','proposal','submitting','booked','conflict','rejected','unresolved','handoff'}
_ROUTES={'/providers','/patients/search','/availability','/appointments','/handoffs','/patients/{patientId}/appointments'}
_REASONS={'user_requested','identity_unclear','unsupported_request','medical_advice','api_failure','no_availability','other'}

class Diagnostics:
    def __init__(self,stream=None):
        self.stream=stream
        self.events=[]

    def __call__(self,event):
        if not isinstance(event,dict):return
        safe={}
        for key,allowed in (('intent',INTENTS),('state',_STATES),('reason',_REASONS),('source',{'Identity','Booking','Scope','Safety','Handoff','Failure'})):
            value=event.get(key)
            if isinstance(value,str) and value in allowed:safe[key]=value
        session=event.get('session')
        if isinstance(session,str) and re.fullmatch(r'[a-f0-9]{32}',session):safe['session']=session
        route=event.get('route')
        if isinstance(route,str):
            route=re.sub(r'^/patients/[A-Za-z0-9_-]{1,200}/appointments$','/patients/{patientId}/appointments',route)
            if route in _ROUTES:safe['route']=route
        status=event.get('status')
        if type(status) is int and 100<=status<=599 or isinstance(status,str) and status in ('unavailable','unresolved'):
            safe['status']=status
        duration=event.get('duration_ms')
        if type(duration) in (int,float) and math.isfinite(duration) and 0<=duration<=3600000:safe['duration_ms']=duration
        self.events.append(safe)
        if self.stream is not None:
            self.stream.write(json.dumps(safe,allow_nan=False,sort_keys=True)+'\n')
            self.stream.flush()
