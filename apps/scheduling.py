"""Run with: marimo run apps/scheduling.py --host 127.0.0.1 --port 28181.

Start the supplied mock independently on port4011. OPENAI_API_KEY / OPENAI_MODEL
configure the real interpreter; SCHEDULING_API_URL configures the loopback mock.
"""
import marimo

__generated_with = '0.25.1'
app = marimo.App(width='medium', app_title='Ochsner scheduling prototype')

@app.cell
def _():
    import base64
    import html
    from pathlib import Path
    import uuid
    import marimo as mo
    from guarded_scheduling.ui_adapter import UiController, action_buttons
    return Path, UiController, action_buttons, base64, html, mo, uuid

@app.cell
def _(UiController, mo, uuid):
    controller = UiController.from_environment()
    get_snapshot, set_snapshot = mo.state(controller.snapshot())
    def emit(action, payload=None):
        # This function runs only from explicit UI callbacks, never during cell evaluation.
        with mo.status.spinner(title='Checking scheduling…', subtitle='No completed result yet.'):
            set_snapshot(controller.dispatch(uuid.uuid4().hex, action, payload))
    return controller, emit, get_snapshot

@app.cell
def _(Path, base64, mo):
    _root = Path(__file__).resolve().parents[1]
    _theme = (_root / 'assets/ui/theme.css').read_text()
    _logo = base64.b64encode((_root / 'assets/ui/ochsner-health.svg').read_bytes()).decode()
    mo.Html('<style>'+_theme+'\nh1,h2,h3 {color:var(--brand-primary)} button:focus-visible {outline:3px solid var(--brand-accent);outline-offset:3px}</style>'
            +'<div style="padding:1rem 0;border-bottom:4px solid var(--brand-accent)"><img alt="Ochsner Health" width="222" height="26" src="data:image/svg+xml;base64,'+_logo+'"/><h1>Scheduling assistant</h1><p>Internal review prototype</p></div>')
    return

@app.cell
def _(get_snapshot, html, mo):
    snapshot = get_snapshot()
    mo.vstack([mo.callout(mo.md(snapshot['disclosure']),kind='info'),
               mo.Html('<section aria-live="polite"><h2>Current step: '+html.escape(snapshot['state'].replace('_',' '))+'</h2><p style="white-space:pre-wrap">'+html.escape(snapshot['message'])+'</p></section>')])
    return (snapshot,)

@app.cell
def _(action_buttons, controller, emit, mo, snapshot):
    _locked = snapshot['state']=='unresolved'
    _request = mo.ui.text_area(label='Your scheduling request',placeholder='Find primary care providers downtown, or help me book.',max_length=4000,disabled=_locked,full_width=True).form(
        submit_button_label='Send request',clear_on_submit=True,submit_button_disabled=_locked,
        on_change=lambda value: emit('message',{'text':value}) if value else None)
    _identity = mo.ui.batch(mo.md('**Private identity** — enter only for booking or appointment lookup. These fields stay outside model requests.\n\nPhone: {phone}\n\nDate of birth (YYYY-MM-DD): {dob}\n\nZIP (only when requested): {zip_code}'),
        {'phone':mo.ui.text(kind='password',max_length=25,disabled=_locked,label='Phone'),
         'dob':mo.ui.text(kind='password',max_length=10,disabled=_locked,label='Date of birth'),
         'zip_code':mo.ui.text(kind='password',max_length=5,disabled=_locked,label='ZIP')}).form(
        submit_button_label='Apply private identity',clear_on_submit=True,submit_button_disabled=_locked,
        on_change=lambda values: emit('identity',{key:value for key,value in values.items() if value}) if values and any(values.values()) else None)
    _prefs = controller.session.preferences
    _preferences = mo.ui.batch(mo.md('**Preferences and corrections**\n\n{specialty}\n\n{location}\n\n{start_date}\n\n{end_date}'),
        {'specialty':mo.ui.dropdown(['primary_care','dermatology'],value=_prefs.specialty,allow_select_none=True,label='Specialty',disabled=_locked),
         'location':mo.ui.dropdown(['downtown','uptown','lakeside'],value=_prefs.location,allow_select_none=True,label='Location (optional)',disabled=_locked),
         'start_date':mo.ui.text(value=_prefs.start_date or '',label='From date (optional YYYY-MM-DD)',disabled=_locked,max_length=10),
         'end_date':mo.ui.text(value=_prefs.end_date or '',label='Through date (optional YYYY-MM-DD)',disabled=_locked,max_length=10)}).form(
        submit_button_label='Apply preferences',submit_button_disabled=_locked,
        on_change=lambda values:emit('preferences',{key:(value or None) for key,value in values.items()}) if values else None)
    # Direct cell bindings keep button registrations alive across frontend events.
    action_widgets = action_buttons(mo, emit, snapshot['proposal_id'], _locked)
    confirm_button, decline_button, refresh_button, reset_button = action_widgets
    _parts=[_request,mo.accordion({'Private identity':_identity,'Preferences and corrections':_preferences})]
    if snapshot['slots']:
        _choices={str(i)+'. '+slot['specialty'].replace('_',' ')+' — '+slot['location']+' — '+slot['startTime']:i for i,slot in enumerate(snapshot['slots'],1)}
        _choice=mo.ui.dropdown(_choices,label='Choose an API-returned appointment',allow_select_none=True,disabled=_locked).form(
            submit_button_label='Review selected appointment',submit_button_disabled=_locked,
            on_change=lambda value:emit('choose',{'index':value}) if value else None)
        _parts.append(_choice)
    if snapshot['proposal_id'] and not _locked:
        _proposal_id=snapshot['proposal_id']
        _parts.append(mo.callout(mo.md('Review the exact appointment above. Choosing does not book. Confirm only if it is the appointment you want.'),kind='warn'))
        _parts.append(mo.hstack([confirm_button, decline_button]))
    _parts.append(mo.hstack([refresh_button, reset_button]))
    mo.vstack(_parts)
    return action_widgets, confirm_button, decline_button, refresh_button, reset_button

if __name__ == '__main__':
    app.run()
