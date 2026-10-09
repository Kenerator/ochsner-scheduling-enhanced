"""Explicit UI events delegate authority to core; rendering never performs effects."""
import os
import threading
from .core import SchedulingSession
from .http_adapter import HttpAdapter
from .model_adapter import ModelAdapter

DISCLOSURE = ('AI scheduling prototype • Supplied synthetic patients and mock scheduling API. '
              'Identity stays local and is not sent to the model. A mock handoff is not delivered human help.')

class UiController:
    def __init__(self,session):
        self.session=session
        self._seen=set()
        self._lock=threading.RLock()

    @classmethod
    def from_environment(cls):
        api=HttpAdapter(os.environ.get('SCHEDULING_API_URL','http://127.0.0.1:4011'),
                        scenario=os.environ.get('SCHEDULING_MOCK_SCENARIO') or None)
        return cls(SchedulingSession(api,ModelAdapter()))

    def snapshot(self):
        with self._lock:
            view=self.session.view
            # Render public facts only; patient/slot/provider identifiers are unnecessary here.
            fields=('specialty','location','startTime','status')
            return {'state':view.state,'message':view.message,'disclosure':DISCLOSURE,
                    'requested_fields':list(view.requested_fields),
                    'providers':[{k:p[k] for k in ('name','specialty','locations','modalities') if k in p} for p in view.providers],
                    'slots':[{k:s[k] for k in fields if k in s} for s in view.slots],
                    'appointments':[{k:a[k] for k in fields if k in a} for a in view.appointments],
                    'proposal_id':view.proposal_id,'proposal':dict(view.proposal) if view.proposal else None}

    def dispatch(self,event_id,action,payload=None):
        if not isinstance(event_id,str) or not 1<=len(event_id)<=100:
            raise ValueError('Invalid UI event.')
        if payload is None:payload={}
        if not isinstance(payload,dict):raise ValueError('Invalid UI event.')
        with self._lock:
            if event_id in self._seen:return self.snapshot()
            if self.session.view.state=='unresolved':return self.snapshot()
            actions={'message':lambda:self.session.message(payload.get('text')),
                     'identity':lambda:self.session.set_identity(**payload),
                     'preferences':lambda:self.session.set_preferences(**payload),
                     'choose':lambda:self.session.choose(payload.get('index')),
                     'confirm':lambda:self.session.confirm(payload.get('proposal_id')),
                     'refresh':self.session.refresh,'decline':self.session.decline,'reset':self.session.reset}
            if action not in actions:raise ValueError('Unsupported UI event.')
            # Claim an event before calling the core; a reactive replay cannot resubmit it.
            self._seen.add(event_id)
            actions[action]()
            return self.snapshot()


def action_buttons(mo, emit, proposal_id=None, disabled=False):
    """Return real controls for direct notebook bindings, not anonymous layout-only widgets.

    The app must bind each returned UIElement to a cell variable so Marimo retains
    its registered object across frontend updates. The exact proposal is captured
    now; a stale rendered click cannot confirm a newer proposal.
    """
    def button(label,action,payload=None,**options):
        return mo.ui.button(value=0,on_click=lambda value:value+1,
                            on_change=lambda value:emit(action,payload),
                            label=label,disabled=disabled,**options)
    confirm=button('Confirm this exact appointment','confirm',{'proposal_id':proposal_id},kind='success')
    decline=button('Decline','decline')
    refresh=button('Refresh current options','refresh')
    reset=button('Reset local conversation','reset')
    return confirm,decline,refresh,reset
