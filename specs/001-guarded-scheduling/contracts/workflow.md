# Workflow and user contract

Updated: 2026-10-08. FR-001–012 and privacy/reproduction guards mandatory; optional FR-013–014 apply when adopted.

## Local event boundary

Core receives typed message/set_identity/set_preferences/choose/confirm/decline/reset_session events. Adapters cannot write independently. A message passes private local extraction and safe public projection before model interpretation. Unsafe/empty projection asks for private correction without transmission. Identity controls never become model messages; dates/choice indexes are local events. Model suggests only intent/public preferences. Structured views render validated service facts and fixed explanations, not model patient/slot narratives.

View: state, useful message, permitted returned providers/options/appointments, requested missing fields, current opaque proposal ID/exact summary when applicable. No candidate records/disclosure before exactly-one verification. Public lookup requests no identity. Invalid optional fields prompt useful correction, not identification. Preserve unrelated valid context; omitted update differs from explicit clearing.

## Consequential action

1. Verify exactly one patient and choose a current validated returned available slot.
2. Display exact patient-bound proposal, specialty/location/returned time. Choice does not write.
3. CLI accepts `confirm <proposal-id>` against the displayed proposal; UI emits explicit current confirm event. Explain syntax/action. Bare yes, model confirmed, stale/unknown ID, consumed consent or mismatched generations cannot authorize effects.
4. Serialize mutation; consume consent and set submitting before sole POST. Reject parallel events/disable changing controls while write pending. Reruns never restore consent.
5. Booked requires valid bound 201. Conflict invalidates old consent and requires refreshed options/fresh confirmation. A possible write without trustworthy result is unresolved; zero automatic retry.

Correction invalidates affected state even in an input containing an affirmative statement. Confirm must be a separate action without concurrent changes. A pending acknowledgement remains distinct from completion. Read responses with stale generations never revive choices; pending write uncertainty cannot be erased by view reset.

## Truthful recovery

No match: private correction or contact scheduling team. Duplicates: private ZIP filtering over already returned candidates, no names/ZIP alternatives. Empty availability: no matching returned slots, supported preference correction/human step. Unsupported scope/filter/type, reschedule/cancel, human request or clinical request: explain boundary/reachable human next step, no medical advice/triage/invented eligibility/contact details.

Outage: truthful downstream unavailability and retry-later/contact step, no loops/false queued handoff. Unknown submission: booking result could not be confirmed; contact scheduling team to reconcile before booking again. Restart/reset is not reconciliation. Failed model interpretation cannot authorize effects/disclosure.

Optional queued handoff uses minimized normalized facts/reason. Queued requires actual valid 201; mock queue is not delivered help. Failure injection stays active on handoff as well.

## Thin optional UI

AI/mock disclosure, private identity controls, readable labels, keyboard-operable choice/confirmation, clear missing fields and reachable help support current needs without claiming accessibility validation. Marimo reruns refresh views, never submit effects. One core session with event/proposal revision checks prevents replay. Browser refresh/restart says nothing about prior write outcome. No admin console.
