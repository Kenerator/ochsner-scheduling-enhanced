"""Deterministic identity, returned facts and single-use consent authority.

The model suggests public intent/preferences. It never supplies patient/slot IDs,
consent or outcome prose. One session lock serializes all mutations and reads.
"""
from dataclasses import asdict, replace
from functools import wraps
import re
import threading
import time
import uuid
from .models import (Interpretation, Preferences, PrivateIdentity, Proposal, View,
                     ValidationError, collection, validate_providers, validate_slots,
                     validate_appointment, SPECIALTIES, LOCATIONS)
from .ports import ModelFailure, SchedulingUnavailable, UnknownOutcome

def serialized(method):
    @wraps(method)
    def run(self,*args,**kwargs):
        with self._lock:return method(self,*args,**kwargs)
    return run

class SchedulingSession:
    def __init__(self, api, model, diagnostics=None):
        self.api=api;self.model=model;self._lock=threading.RLock();self.session_id=uuid.uuid4().hex
        self.intent='clarify';self.preferences=Preferences();self._identity={};self._patient=None;self._matches=[]
        self._slots=[];self._proposal=None;self._revision=0;self._unknown=False;self._appointment=None
        self._handoffs={};self.events=[];self._diagnostics=diagnostics
        self.view=View('clarify','I am an AI scheduling prototype using synthetic data. Find providers, book, or look up appointments. Identity stays local.')

    def _event(self, **event):
        allowed={'session','state','intent','route','status','reason','duration_ms'}
        safe={k:v for k,v in dict(session=self.session_id,state=self.view.state,intent=self.intent,**event).items() if k in allowed}
        self.events.append(safe)
        if self._diagnostics:self._diagnostics(safe)

    def _show(self,state,message,**data):
        self.view=View(state,message,**data);self._event();return self.view

    def _invalidate(self, identity=False):
        self._revision+=1;self._slots=[];self._proposal=None
        if identity:self._patient=None;self._matches=[]

    def _request(self,method,path,params=None,body=None):
        started=time.monotonic();route=re.sub(r'/patients/[^/]+/appointments','/patients/{patientId}/appointments',path)
        try:
            response=self.api.request(method,path,params,body)
            self._event(route=route,status=response.status,duration_ms=round((time.monotonic()-started)*1000,2))
            return response
        except (SchedulingUnavailable,UnknownOutcome):
            self._event(route=route,status='unresolved' if method=='POST' else 'unavailable',duration_ms=round((time.monotonic()-started)*1000,2));raise

    def _unresolved(self):
        self._unknown=True;self._invalidate()
        return self._show('unresolved','The booking outcome is unknown. Do not book again or treat reset/restart as failure. Contact the scheduling team through your usual channel to reconcile the appointment first.')

    def _support_summary(self, reason):
        # Allowlisted state only: never patient IDs, identity values or user/model prose.
        known=[]
        for field in ('specialty','location','start_date','end_date'):
            value=getattr(self.preferences,field)
            if value:known.append(field+'='+value)
        missing=[]
        if not self.preferences.specialty:missing.append('specialty')
        if not self._patient:missing.append('identity_verification')
        statuses=[event.get('status') for event in self.events if event.get('route')=='/appointments']
        if self._unknown:outcome='unresolved'
        elif self._appointment:outcome='previous_api_confirmed'
        elif statuses:outcome={409:'rejected_conflict',400:'rejected',503:'not_confirmed'}.get(statuses[-1],'not_submitted')
        else:outcome='not_submitted'
        return ('Scheduling prototype requires human assistance: '+reason.replace('_',' ')+'. '
                +'Known scheduling preferences: '+(', '.join(known) or 'none')+'. '
                +'Missing information: '+(', '.join(missing) or 'none for current scheduling request')+'. '
                +'Booking outcome: '+outcome+'. No identity or transcript included.')

    def _handoff(self,reason,message):
        self._proposal=None
        key=(reason,self._revision)
        if key not in self._handoffs:
            try:
                result=self._request('POST','/handoffs',body={'reason':reason,'summary':self._support_summary(reason)})
                queued=(result.status==201 and isinstance(result.data.get('handoffId'),str) and bool(re.fullmatch(r'[A-Za-z0-9_-]{1,200}',result.data['handoffId'])) and result.data.get('status')=='queued')
                self._handoffs[key]='queued' if queued else 'failed'
            except (UnknownOutcome,SchedulingUnavailable):self._handoffs[key]='unknown'
        status=self._handoffs[key]
        if status=='queued':message+=' A request is queued in the supplied mock; this does not mean a human has received it.'
        elif status=='unknown':message+=' The handoff outcome is unknown; contact the scheduling team directly through your usual channel.'
        else:message+=' The handoff could not be created. Contact the scheduling team through your usual channel or try later.'
        self._event(reason=reason)
        return self._show('handoff',message)

    def _failure(self):
        return self._handoff('api_failure','The scheduling service is unavailable. No scheduling result can be confirmed.')

    @serialized
    def message(self,text):
        if self._unknown:return self._unresolved()
        if not isinstance(text,str) or not text.strip() or len(text)>4000:return self._show('clarify','Please enter a short scheduling request.')
        text=text.strip()
        # Local commands are intentionally parsed before the model privacy boundary.
        match=re.fullmatch(r'confirm\s+([a-f0-9]{12})',text,re.I)
        if match:return self.confirm(match.group(1))
        if text.lower() in ('yes','yes please','confirm') and self._proposal:
            return self._show('proposal','Use the separate current confirmation action or type confirm '+self._proposal.proposal_id+'.',proposal_id=self._proposal.proposal_id,proposal=self._public_proposal())
        match=re.fullmatch(r'(phone|dob|zip)\s+(.+)',text,re.I)
        if match:return self.set_identity(**{{'phone':'phone','dob':'dob','zip':'zip_code'}[match.group(1).lower()]:match.group(2).strip()})
        match=re.fullmatch(r'identity\s+(\S+)\s+(\S+)(?:\s+(\S+))?',text,re.I)
        if match:return self.set_identity(phone=match.group(1),dob=match.group(2),zip_code=match.group(3))
        # Invalid numeric choices stay local and retain verified options, even signed/long input.
        if re.fullmatch(r'[+-]?\d+',text) and self._slots:return self.choose(int(text))
        if text.lower().rstrip('.?!') in ('i need human help','i want human help','human help','please help me contact scheduling'):
            return self._handoff('user_requested','You requested human assistance.')
        if text.lower().rstrip('.?!') in ('i have no email','i only have a basic phone','i do not have email','i have no smartphone'):
            return self._handoff('user_requested','Email is not required. This prototype needs a browser or CLI; it does not provide a basic-phone service. Ask the scheduling team through your usual channel for assisted scheduling.')
        if text.lower()=='refresh':return self.refresh()
        if text.lower() in ('decline','no'):return self.decline()
        if text.lower()=='reset':return self.reset()
        match=re.fullmatch(r'(specialty|location|provider)\s+(.+)',text,re.I)
        if match:
            field,value=match.group(1).lower(),match.group(2).strip()
            if field=='provider':return self.select_provider(value)
            return self.set_preferences(**{field:value.lower().replace(' ','_')})
        try:
            from .privacy import project
            public=project(text,private_values=tuple(self._identity.values()),expecting_identity=self.view.state in ('needs_identity','needs_zip'))
            if not public:
                # Unseparated private corrections cannot leave earlier consent valid.
                self._invalidate(identity=True)
                return self._show('clarify','Keep identity in the private controls or use phone, dob and zip commands. Please restate only the scheduling request; no identity was sent to the model.')
            started=time.monotonic()
            context={'intent':self.intent,'specialty':self.preferences.specialty,'location':self.preferences.location}
            result=self.model.interpret(public,context)
            self._event(duration_ms=round((time.monotonic()-started)*1000,2))
            if isinstance(result,dict):result=Interpretation.from_dict(result)
            if not isinstance(result,Interpretation):raise ModelFailure('Invalid interpretation.')
        except (ModelFailure,ValidationError,ValueError,TypeError):
            self._proposal=None
            return self._show('clarify','The AI interpretation is unavailable or invalid. No booking was submitted. Please restate your scheduling request.')
        if result.intent in ('human_help','medical_advice','unsupported'):
            reason={'human_help':'user_requested','medical_advice':'medical_advice','unsupported':'unsupported_request'}[result.intent]
            message={'human_help':'You requested human assistance.','medical_advice':'I cannot provide medical advice or triage. Contact a qualified healthcare professional directly.','unsupported':'That request is outside the supported scheduling scope. Rescheduling and cancellation are not implemented.'}[result.intent]
            return self._handoff(reason,message)
        # The current API supports calendar dates, not hour/weekday filters. Never silently waive one.
        if re.search(r'\b(morning|afternoon|evening|weekday|weekdays|weekend|weekends)\b',public,re.I):
            self._invalidate();self.intent='clarify'
            return self._show('clarify','Time-of-day and weekday/weekend filters are not supported. Use the preference controls for location and calendar dates, then restate the scheduling request without those time limits, or ask the scheduling team for help.')
        updates={}
        if result.clear_specialty:updates['specialty']=None
        elif result.specialty is not None:updates['specialty']=result.specialty
        if result.clear_location:updates['location']=None
        elif result.location is not None:updates['location']=result.location
        if result.intent!='clarify':
            if result.intent!=self.intent:self._invalidate()
            self.intent=result.intent
        if updates:
            return self.set_preferences(**updates)
        return self._advance()

    @serialized
    def set_preferences(self,**updates):
        if self._unknown:return self._unresolved()
        if any(k not in ('specialty','location','start_date','end_date','provider_id') for k in updates):return self._show('clarify','Unsupported preference field.')
        if any(getattr(self.preferences,k)!=v for k,v in updates.items()):self._invalidate()
        try:self.preferences=replace(self.preferences,**updates)
        except ValidationError as exc:
            from .suggestions import suggest
            hints=[]
            for field,allowed in (('specialty',SPECIALTIES),('location',LOCATIONS)):
                if field in updates and isinstance(updates[field],str):
                    try:hints.extend(field+' '+item for item in suggest(updates[field],allowed))
                    except ValidationError:pass
            hint=' Possible spelling corrections: '+', '.join(hints)+'. Enter a correction explicitly.' if hints else ''
            return self._show('clarify',str(exc)+' Please choose a supported value; the old proposal is invalid.'+hint)

        return self._advance()

    @serialized
    def select_provider(self,name):
        if self._unknown:return self._unresolved()
        self._invalidate()
        try:
            from .suggestions import suggest
            response=self._request('GET','/providers')
            if response.status!=200:return self._failure()
            providers=validate_providers(response.data)
            exact=[p for p in providers if p['name'].casefold()==name.casefold()]
            if len(exact)==1:return self.set_preferences(provider_id=exact[0]['providerId'],specialty=exact[0]['specialty'])
            names=suggest(name,[p['name'] for p in providers])
            message='No single exact provider was selected.'
            if names:message+=' Possible spelling corrections from returned providers: '+', '.join(names)+'. Enter provider NAME explicitly.'
            return self._show('clarify',message)
        except (ValidationError,SchedulingUnavailable):return self._show('clarify','Provider selection is unavailable or invalid; no provider was selected.')

    @serialized
    def set_identity(self,**fields):
        if self._unknown:return self._unresolved()
        if any(k not in ('phone','dob','zip_code') for k in fields):return self._show('clarify','Use the supported private identity controls.')
        changed=any(self._identity.get(k)!=v for k,v in fields.items())
        # ZIP disambiguates cached returned candidates; it is never a server parameter.
        zip_only=set(fields)=={'zip_code'} and bool(self._matches) and self._patient is None
        if changed and not zip_only:self._invalidate(identity=True)
        elif changed:self._revision+=1;self._proposal=None;self._slots=[]
        self._identity.update({k:v for k,v in fields.items() if v is not None})
        return self._advance()

    def _advance(self):
        if self._unknown:return self._unresolved()
        try:
            if self.intent=='provider_lookup':
                params={k:v for k,v in (('specialty',self.preferences.specialty),('location',self.preferences.location)) if v}
                response=self._request('GET','/providers',params=params)
                if response.status!=200:return self._failure()
                providers=validate_providers(response.data)
                message='Providers returned by the scheduling API:\n'+'\n'.join(p['name']+' — '+p['specialty'].replace('_',' ')+', '+', '.join(p['locations']) for p in providers) if providers else 'No providers match these filters. Change your preferences or request human help.'
                return self._show('providers',message,providers=providers)
            if self.intent not in ('book','appointment_lookup'):return self._show('clarify','Would you like to find providers, book an appointment, or look up your appointments?')
            missing=[k for k in ('phone','dob') if not self._identity.get(k)]
            if missing:return self._show('needs_identity','Enter your '+('phone and date of birth' if len(missing)==2 else 'phone' if missing[0]=='phone' else 'date of birth')+' in the private controls. CLI: phone VALUE; dob YYYY-MM-DD.',requested_fields=missing)
            try:identity=PrivateIdentity(self._identity['phone'],self._identity['dob'],self._identity.get('zip_code'))
            except ValidationError:
                return self._show('needs_identity','Enter a valid phone, real calendar DOB (YYYY-MM-DD), and five-digit ZIP when requested, using private controls.',requested_fields=['phone','dob'])
            if self._patient is None:
                if not self._matches:
                    response=self._request('GET','/patients/search',params={'phone':identity.phone,'dob':identity.dob})
                    if response.status!=200:return self._failure()
                    candidates=collection(response.data,'matches',('patientId','phone','dateOfBirth','zipCode'))
                    if any(p['phone']!=identity.phone or p['dateOfBirth']!=identity.dob for p in candidates):raise ValidationError('Unusable identity result.')
                    if len({p['patientId'] for p in candidates})!=len(candidates):raise ValidationError('Unusable identity result.')
                    self._matches=candidates
                if not self._matches:return self._handoff('identity_unclear','I could not verify a patient match. Correct your details privately or ask the scheduling team for help.')
                matches=self._matches
                if len(matches)>1:
                    if not identity.zip_code:return self._show('needs_zip','More information is needed to verify identity. Enter your five-digit ZIP privately; no candidate details will be shown.',requested_fields=['zip_code'])
                    matches=[p for p in matches if p['zipCode']==identity.zip_code]
                if len(matches)!=1:return self._handoff('identity_unclear','I could not verify exactly one patient. Ask the scheduling team for private assistance.')
                self._patient=matches[0]['patientId'];self._matches=[]
            if self.intent=='appointment_lookup':
                response=self._request('GET','/patients/'+self._patient+'/appointments')
                if response.status!=200:return self._failure()
                rows=collection(response.data,'appointments',('appointmentId','patientId','providerId','specialty','location','startTime','status'))
                appointments=[validate_appointment({'appointment':a},self._patient) for a in rows]
                public=[{k:a[k] for k in ('specialty','location','startTime','status')} for a in appointments]
                message='Your returned appointments:\n'+'\n'.join(a['specialty'].replace('_',' ')+' — '+a['location']+' — '+a['startTime']+' — '+a['status'] for a in public) if public else 'No existing appointments were returned for the verified patient.'
                return self._show('appointments',message,appointments=public)
            if not self.preferences.specialty:return self._show('needs_preferences','Which specialty: primary care or dermatology?',requested_fields=['specialty'])
            response=self._request('GET','/availability',params={k:v for k,v in (('patientId',self._patient),('specialty',self.preferences.specialty),('location',self.preferences.location),('startDate',self.preferences.start_date),('endDate',self.preferences.end_date)) if v})
            if response.status!=200:return self._failure()
            self._slots=validate_slots(response.data,replace(self.preferences,provider_id=None))
            if self.preferences.provider_id:self._slots=[slot for slot in self._slots if slot['providerId']==self.preferences.provider_id]
            if not self._slots:return self._handoff('no_availability','No available appointments were returned for these preferences. Change the search or contact scheduling.')
            self._proposal=None
            return self._show('options','Available appointments from the API (times retain the returned offset):\n'+'\n'.join(str(i)+'. '+s['specialty'].replace('_',' ')+' — '+s['location']+' — '+s['startTime'] for i,s in enumerate(self._slots,1))+'\nChoose a number. Selection does not book.',slots=list(self._slots))
        except SchedulingUnavailable:return self._failure()
        except ValidationError:return self._handoff('api_failure','The scheduling service returned unusable data. No booking was submitted.')

    def _public_proposal(self):
        if not self._proposal:return None
        return {k:self._proposal.slot[k] for k in ('specialty','location','startTime')}

    @serialized
    def choose(self,index):
        if self._unknown:return self._unresolved()
        self._proposal=None
        if type(index) is not int or not 1<=index<=len(self._slots) or not self._patient:return self._show('clarify','Choose a number from the current returned options; refresh if the options changed.',slots=list(self._slots))
        self._proposal=Proposal(uuid.uuid4().hex[:12],self._patient,dict(self._slots[index-1]),self._revision)
        summary=self._public_proposal()
        return self._show('proposal','For the verified patient: '+summary['specialty'].replace('_',' ')+' — '+summary['location']+' — '+summary['startTime']+'. To book this exact appointment, use Confirm or type confirm '+self._proposal.proposal_id+'.',proposal_id=self._proposal.proposal_id,proposal=summary,slots=list(self._slots))

    @serialized
    def confirm(self,proposal_id):
        if self._unknown:return self._unresolved()
        proposal=self._proposal
        if not proposal or proposal_id!=proposal.proposal_id or proposal.revision!=self._revision or proposal.patient_id!=self._patient:
            if self._appointment:return self._show('booked','The previously confirmed appointment is already booked. No additional request was sent.')
            return self._show('clarify','That confirmation is stale or invalid. Choose a current returned option and confirm its new proposal.')
        self._proposal=None  # Consume before the sole request, including exceptions.
        self._show('submitting','Submitting the exact confirmed appointment; outcome is pending.')
        try:response=self._request('POST','/appointments',body={'patientId':proposal.patient_id,'slotId':proposal.slot['slotId'],'confirmed':True})
        except (UnknownOutcome,SchedulingUnavailable):return self._unresolved()
        if response.status==201:
            try:self._appointment=validate_appointment(response.data,proposal.patient_id,proposal.slot)
            except ValidationError:return self._unresolved()
            self._slots=[]
            return self._show('booked','Booked: '+self._appointment['specialty'].replace('_',' ')+' — '+self._appointment['location']+' — '+self._appointment['startTime']+'. Confirmed by the scheduling API.')
        if response.status==409:
            self._invalidate();return self._show('conflict','That appointment was not booked because the slot is no longer available. Refresh for current options, then make a fresh choice and confirmation.')
        if response.status in (400,503):
            self._invalidate();return self._failure() if response.status==503 else self._show('rejected','The scheduling API rejected this booking. No appointment was confirmed; refresh or request human help.')
        return self._unresolved()

    @serialized
    def refresh(self):
        if self._unknown:return self._unresolved()
        self._invalidate();return self._advance()

    @serialized
    def decline(self):
        if self._unknown:return self._unresolved()
        self._proposal=None
        return self._show('options','No booking was submitted. Choose another current option or change your preferences.',slots=list(self._slots))

    @serialized
    def reset(self):
        if self._unknown:return self._unresolved()
        self._invalidate(identity=True);self._identity={};self.preferences=Preferences();self.intent='clarify';self._appointment=None
        return self._show('clarify','Local conversation reset. This does not reset the supplied API or reconcile any prior transaction.')
