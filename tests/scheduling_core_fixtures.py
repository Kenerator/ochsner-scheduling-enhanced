from guarded_scheduling.models import Interpretation
from guarded_scheduling.ports import Response, UnknownOutcome

PATIENT = dict(patientId='patient1', firstName='Synthetic', lastName='Patient',dateOfBirth='1985-04-12',phone='555-0101',zipCode='70112',establishedPatient=True)
SLOTS = [dict(slotId='slot1',providerId='provider1',specialty='primary_care',location='downtown',startTime='2026-10-10T09:00:00-05:00',available=True),dict(slotId='slot2',providerId='provider1',specialty='primary_care',location='downtown',startTime='2026-10-11T10:00:00-05:00',available=True)]
PROVIDER = dict(providerId='provider1',name='Dr. Example',specialty='primary_care',locations=['downtown'],modalities=['in_person'])

class ScriptModel:
    def __init__(self, results=None): self.results=list(results or []);self.inputs=[]
    def interpret(self,text,context):
        self.inputs.append((text,dict(context)))
        return self.results.pop(0) if self.results else Interpretation('book')

class MemoryApi:
    def __init__(self):
        self.calls=[];self.matches=[dict(PATIENT)];self.slots=[dict(s) for s in SLOTS];self.bookings=[];self.handoffs=[];self.booking_status=201;self.unknown=False;self.outage=False
    def request(self,method,path,params=None,body=None):
        self.calls.append((method,path,params,body))
        if self.outage:return Response(503,{'code':'downstream_unavailable'})
        if path=='/providers':return Response(200,{'providers':[dict(PROVIDER)]})
        if path=='/patients/search':return Response(200,{'matches':self.matches})
        if path=='/availability':return Response(200,{'slots':self.slots})
        if path.endswith('/appointments') and method=='GET':return Response(200,{'appointments':self.bookings})
        if path=='/handoffs':
            self.handoffs.append(body);return Response(201,{'handoffId':'h1','status':'queued'})
        if path=='/appointments':
            if self.unknown:raise UnknownOutcome('unresolved')
            if self.booking_status!=201:return Response(self.booking_status,{'code':'slot_taken'})
            slot=next(s for s in self.slots if s['slotId']==body['slotId'])
            appointment=dict(appointmentId='appointment1',patientId=body['patientId'],providerId=slot['providerId'],specialty=slot['specialty'],location=slot['location'],startTime=slot['startTime'],status='scheduled')
            self.bookings.append(appointment);return Response(201,{'appointment':appointment})
        raise AssertionError('Unexpected API route')

def ready(session):
    session.message('Book primary care downtown')
    session.set_identity(phone='555-0101')
    return session.set_identity(dob='1985-04-12')
