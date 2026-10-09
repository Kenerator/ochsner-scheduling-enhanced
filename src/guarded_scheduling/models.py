"""Small validated values at the model/API-to-authority boundary."""
from dataclasses import dataclass, field
from datetime import date, datetime
import re

SPECIALTIES = ('primary_care', 'dermatology')
LOCATIONS = ('downtown', 'uptown', 'lakeside')
INTENTS = ('provider_lookup', 'book', 'appointment_lookup', 'human_help', 'medical_advice', 'unsupported', 'clarify')

class ValidationError(ValueError):
    """A static label is safe to show; never include the rejected value."""

def calendar(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        raise ValidationError('Use a calendar date in YYYY-MM-DD format.')
    try: date.fromisoformat(value)
    except ValueError: raise ValidationError('Use a valid calendar date.') from None
    return value

def nonempty(value):
    return isinstance(value,str) and 0 < len(value) <= 200

@dataclass(frozen=True, repr=False)
class PrivateIdentity:
    phone: str
    dob: str
    zip_code: str | None = None
    def __post_init__(self):
        if not isinstance(self.phone,str) or not re.fullmatch(r'[+()\d .-]{7,25}',self.phone) or not 7 <= len(re.sub(r'\D','',self.phone)) <= 15:
            raise ValidationError('Use a supported phone format in the private identity control.')
        calendar(self.dob)
        if self.zip_code is not None and (not isinstance(self.zip_code,str) or not re.fullmatch(r'\d{5}',self.zip_code)):
            raise ValidationError('Use a five-digit ZIP in the private identity control.')
    def __repr__(self): return 'PrivateIdentity(<private>)'

@dataclass(frozen=True)
class Preferences:
    specialty: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    provider_id: str | None = None
    def __post_init__(self):
        if self.specialty is not None and self.specialty not in SPECIALTIES: raise ValidationError('Unsupported specialty.')
        if self.location is not None and self.location not in LOCATIONS: raise ValidationError('Unsupported location.')
        for value in (self.start_date,self.end_date):
            if value is not None: calendar(value)
        if self.start_date and self.end_date and self.start_date > self.end_date: raise ValidationError('Start date must be on or before end date.')
        if self.provider_id is not None and not nonempty(self.provider_id): raise ValidationError('Invalid provider choice.')

@dataclass(frozen=True)
class Interpretation:
    intent: str
    specialty: str | None = None
    location: str | None = None
    clear_specialty: bool = False
    clear_location: bool = False
    def __post_init__(self):
        if self.intent not in INTENTS: raise ValidationError('Invalid model intent.')
        if type(self.clear_specialty) is not bool or type(self.clear_location) is not bool: raise ValidationError('Invalid model clearing flag.')
        for value in (self.specialty,self.location):
            if value is not None and (not nonempty(value) or len(value)>100): raise ValidationError('Invalid model preference.')
    @classmethod
    def from_dict(cls, value):
        if not isinstance(value,dict) or set(value)!=set(cls.__dataclass_fields__): raise ValidationError('Invalid model fields.')
        return cls(**value)

@dataclass
class View:
    state: str
    message: str
    providers: list = field(default_factory=list)
    slots: list = field(default_factory=list)
    appointments: list = field(default_factory=list)
    proposal_id: str | None = None
    proposal: dict | None = None
    requested_fields: list = field(default_factory=list)

@dataclass(frozen=True, repr=False)
class Proposal:
    proposal_id: str
    patient_id: str
    slot: dict
    revision: int


def collection(value, key, required):
    if not isinstance(value,dict) or not isinstance(value.get(key),list): raise ValidationError('Invalid scheduling response.')
    rows=value[key]
    if len(rows)>1000: raise ValidationError('Scheduling response is too large.')
    for row in rows:
        if not isinstance(row,dict) or any(not nonempty(row.get(k)) for k in required): raise ValidationError('Invalid scheduling record.')
    return [dict(row) for row in rows]


def validate_providers(value):
    rows=collection(value,'providers',('providerId','name','specialty'))
    if len({p['providerId'] for p in rows})!=len(rows): raise ValidationError('Duplicate provider identifiers.')
    for p in rows:
        if p['specialty'] not in SPECIALTIES: raise ValidationError('Invalid provider specialty.')
        for key in ('locations','modalities'):
            if not isinstance(p.get(key),list) or not p[key] or any(not nonempty(v) for v in p[key]): raise ValidationError('Invalid provider facts.')
        if any(v not in LOCATIONS for v in p['locations']): raise ValidationError('Invalid provider location.')
    return rows


def timestamp(value):
    if not nonempty(value): raise ValidationError('Invalid returned time.')
    try: parsed=datetime.fromisoformat(value)
    except ValueError: raise ValidationError('Invalid returned time.') from None
    if parsed.tzinfo is None: raise ValidationError('Returned time must include its offset.')
    return parsed


def validate_slots(value, preferences):
    rows=collection(value,'slots',('slotId','providerId','specialty','location','startTime'))
    if len({s['slotId'] for s in rows})!=len(rows): raise ValidationError('Duplicate slot identifiers.')
    for slot in rows:
        timestamp(slot['startTime'])
        if slot.get('available') is not True: raise ValidationError('Slot is not available.')
        if slot['specialty']!=preferences.specialty or slot['location'] not in LOCATIONS: raise ValidationError('Slot does not match the search.')
        if preferences.location and slot['location']!=preferences.location: raise ValidationError('Slot does not match the location.')
        if preferences.provider_id and slot['providerId']!=preferences.provider_id: raise ValidationError('Slot does not match the provider.')
        day=slot['startTime'][:10]
        if preferences.start_date and day<preferences.start_date or preferences.end_date and day>preferences.end_date: raise ValidationError('Slot does not match the date range.')
    return rows


def validate_appointment(value, patient_id, slot=None):
    if not isinstance(value,dict) or not isinstance(value.get('appointment'),dict): raise ValidationError('Invalid appointment result.')
    a=dict(value['appointment'])
    if any(not nonempty(a.get(k)) for k in ('appointmentId','patientId','providerId','specialty','location','startTime','status')): raise ValidationError('Incomplete appointment result.')
    timestamp(a['startTime'])
    if a['patientId']!=patient_id or a['status']!='scheduled': raise ValidationError('Appointment does not match the verified request.')
    if slot and any(a[k]!=slot[k] for k in ('providerId','specialty','location','startTime')): raise ValidationError('Appointment does not match the proposal.')
    if a['specialty'] not in SPECIALTIES or a['location'] not in LOCATIONS: raise ValidationError('Invalid appointment facts.')
    return a
