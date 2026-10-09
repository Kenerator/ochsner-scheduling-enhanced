"""Repeatable real-reference flows with explicitly scripted interpretation.

These demos qualify deterministic guards and supplied HTTP behavior, not live AI.
Each run launches and stops its own ephemeral supplied mock process.
"""
import argparse
import json
import sys
import time
import platform
from .core import SchedulingSession
from .http_adapter import HttpAdapter
from .mock_runner import MockRunner
from .models import Interpretation

class DemoFailure(RuntimeError):
    pass

class ScriptedModel:
    """A disclosed finite interpretation script; never pretend this is live AI."""
    def __init__(self,*values):self._values=iter(values)
    def interpret(self,text,context):return next(self._values)

def _require(condition):
    if not condition:raise DemoFailure('Demo outcome did not satisfy its checks.')

def _booking(api,phone='555-0101',dob='1985-04-12'):
    session=SchedulingSession(api,ScriptedModel(Interpretation('book','primary_care','downtown')))
    _require(session.message('Book primary care downtown').state=='needs_identity')
    session.set_identity(phone=phone,dob=dob)
    return session

def run(scenario,python_executable=sys.executable):
    if scenario not in ('provider','booking','no-match','guards'):raise ValueError('Unknown demo scenario.')
    started=time.monotonic()
    checks=[]
    with MockRunner(python_executable=python_executable,port=0) as runner:
        api=HttpAdapter(runner.base_url)
        if scenario=='provider':
            session=SchedulingSession(api,ScriptedModel(Interpretation('provider_lookup','primary_care','downtown')))
            view=session.message('Which primary care providers are downtown?')
            actual=api.request('GET','/providers',{'specialty':'primary_care','location':'downtown'}).data['providers']
            _require(view.state=='providers' and bool(view.providers) and view.providers==actual and not view.requested_fields)
            _require(not any(e.get('route')=='/patients/search' for e in session.events))
            checks+=['returned_provider_facts','no_identity_search']
        elif scenario=='booking':
            session=_booking(api);_require(session.view.state=='options')
            before=api.request('GET','/patients/pat_1001/appointments').data['appointments']
            proposal=session.choose(1);_require(proposal.state=='proposal')
            _require(len(api.request('GET','/patients/pat_1001/appointments').data['appointments'])==len(before))
            _require(session.confirm(proposal.proposal_id).state=='booked')
            after=api.request('GET','/patients/pat_1001/appointments').data['appointments']
            _require(len(after)==len(before)+1)
            _require(any(all(row[k]==proposal.proposal[k] for k in ('specialty','location','startTime')) for row in after if row not in before))
            session.confirm(proposal.proposal_id)
            _require(len(api.request('GET','/patients/pat_1001/appointments').data['appointments'])==len(after))
            checks+=['selection_does_not_book','exact_returned_booking','single_use_confirmation']
        elif scenario=='no-match':
            session=_booking(api,phone='555-0999');_require(session.view.state=='handoff')
            _require('could not verify' in session.view.message.lower())
            _require(not any(e.get('route') in ('/availability','/appointments') for e in session.events))
            checks+=['no_match_private_handoff','no_availability_or_booking']
        else:
            duplicate=_booking(api,phone='555-0130',dob='1978-09-22')
            _require(duplicate.view.state=='needs_zip' and not duplicate.view.slots)
            _require(duplicate.set_identity(zip_code='70115').state=='options')
            checks+=['duplicate_private_zip']
            # This scenario chooses the third currently returned option, as a user
            # would; no fixture-only conflict flags are used by the application.
            conflict=_booking(api);_require(len(conflict.view.slots)>=3)
            proposal=conflict.choose(3);_require(conflict.confirm(proposal.proposal_id).state=='conflict')
            _require(conflict.confirm(proposal.proposal_id).state!='booked')
            checks+=['conflict_requires_fresh_consent']
            outage=SchedulingSession(HttpAdapter(runner.base_url,scenario='api_failure'),ScriptedModel(Interpretation('provider_lookup')))
            view=outage.message('Find providers');_require('unavailable' in view.message.lower() and 'queued' not in view.message.lower())
            checks+=['outage_no_false_queue']
            medical=SchedulingSession(api,ScriptedModel(Interpretation('medical_advice')))
            view=medical.message('I have chest pain, should I wait?')
            _require('cannot provide medical advice' in view.message.lower() and 'mock' in view.message.lower())
            checks+=['medical_boundary_mock_handoff']
    return {'scenario':scenario,'passed':True,'simulation':True,'model':'scripted','backend':'supplied_reference','checks':checks,'seconds':round(time.monotonic()-started,3),'python':platform.python_version(),'platform':platform.system()+' '+platform.machine(),'load':'single_session','feedback_target':'not_measured_by_noninteractive_demo'}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario',nargs='?',choices=('provider','booking','no-match','guards'))
    parser.add_argument('--scenario',dest='scenario_option',choices=('provider','booking','no-match','guards'))
    parser.add_argument('--python',default=sys.executable)
    args=parser.parse_args(argv)
    if bool(args.scenario)==bool(args.scenario_option):parser.error('Specify one scenario.')
    args.scenario=args.scenario or args.scenario_option
    try:result=run(args.scenario,args.python)
    except Exception:
        # No raw exception, private path, identity, or HTTP query is printed.
        print(json.dumps({'scenario':args.scenario,'passed':False,'simulation':True,'error':'Demo could not verify its outcome.'}))
        return 1
    print(json.dumps(result,sort_keys=True));return 0

if __name__=='__main__':raise SystemExit(main())
