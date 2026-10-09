"""Thin interactive adapter; the core alone owns verification and effects."""
import argparse
import getpass
import sys
from .core import SchedulingSession
from .http_adapter import HttpAdapter
from .model_adapter import ModelAdapter

DISCLOSURE = ('AI scheduling assistant using synthetic patient data and a local mock API. '
              'This is a demonstration, not production authentication or clinical care. '
              'Identity stays local; uncertain wording may require restatement.\n'
              'Ask to find providers, book, look up appointments, or get human help.\n'
              'Private commands: phone VALUE, dob YYYY-MM-DD, zip VALUE; identity opens hidden prompts.\n'
              'Select a returned option number, then separately confirm PROPOSAL-ID. '
              'Other commands: date START END, refresh, decline, reset, quit.\n'
              'Reset/restart never reconciles an uncertain booking.\n')

def run(session, source=sys.stdin, output=sys.stdout):
    output.write(DISCLOSURE);output.flush()
    for line in source:
        text=line.strip()
        if text.lower() in ('quit','exit'):break
        if not text:continue
        output.write('Working — interpreting or checking the scheduling service; no completed result yet.\n');output.flush()
        try:
            if text.lower()=='identity' and source is sys.stdin:
                phone=getpass.getpass('Synthetic phone (local): ')
                dob=getpass.getpass('DOB YYYY-MM-DD (local): ')
                view=session.set_identity(phone=phone,dob=dob)
            elif text.lower().startswith('date '):
                values=text.split()
                if len(values)!=3:
                    output.write('Use date YYYY-MM-DD YYYY-MM-DD.\n');continue
                view=session.set_preferences(start_date=values[1],end_date=values[2])
            else:view=session.message(text)
            output.write(view.message+'\n');output.flush()
        except Exception as exc:
            # Class only: exception messages and frames can carry identity or requests.
            output.write('Unexpected internal error ('+type(exc).__name__+'). Stop this session and ask the reviewer for help; reconcile any pending booking before retrying.\n');output.flush()
            break
    return 0

def main(argv=None):
    parser=argparse.ArgumentParser(description='Guarded synthetic scheduling conversation')
    parser.add_argument('--api-url',default='http://127.0.0.1:4011')
    parser.add_argument('--scenario',choices=['api_failure'],default=None)
    args=parser.parse_args(argv)
    try:
        session=SchedulingSession(HttpAdapter(args.api_url,scenario=args.scenario),ModelAdapter())
        return run(session)
    except (ValueError,RuntimeError):
        print('Unable to configure the local scheduling assistant. Check the loopback API URL and environment model/key.',file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
