"""Fail-closed public language boundary; identity and local commands stay local.

This deliberately accepts a documented public vocabulary rather than attempting
regex masking of arbitrary personal text. Unknown words require a private/local
correction. No claim of general-purpose de-identification is made.
"""
import re
import unicodedata

_PUBLIC = set('''a an the i me my we us our you your it its this that these those
is are was were be been am do does did can could would should will want wants
need needs like looking look find search show list tell which what where who
when how about for from to at in on of with without and or but please thanks
thank hello hi any all only other another more less also available availability
appointment appointments book booking schedule scheduling scheduled visit visits
provider providers doctor doctors physician physicians clinician clinicians care
primary family general dermatology dermatologist dermatologists cardiology
cardiologist cardiologists neurology neurologist neurology pediatrics pediatric
pediatrician oncology oncologist orthopedics orthopedic specialty specialties
location locations downtown uptown lakeside clinic hospital near nearby remote
virtual telehealth office person consultation new existing earliest latest soon
morning afternoon evening weekday weekend preference preferences change update
remove clear reset no not don't doesn't isn't anywhere fine either instead
cancel cancellation reschedule move check view upcoming past human help support
someone team contact speak talk assistance medical advice diagnosis diagnose
treatment medicine medication medications take stop chest pain headache rash
symptom symptoms fever emergency urgent refill prescription insurance cost costs
price billing payment eligibility question questions explain recommend possible
shouldn't cannot can't won't let let's get have has had out something anything
nothing different same first next available openings opening times time day days wait again now
'''.split())
_LOCAL_ONLY = {'yes','no','okay','ok','confirm','confirmed','decline'}

def project(text, private_values=(), expecting_identity=False):
    """Return approved public text unchanged, or None without transmitting it.

    Mixed private/public input is suppressed as a whole: absence of a recognized
    phone format never proves that an arbitrary fragment is safe. Caller-known
    private values override public vocabulary collisions, even ordinary words.
    """
    if expecting_identity or not isinstance(text, str) or not text.strip() or len(text)>2000:
        return None
    normalized=unicodedata.normalize('NFKC',text).casefold()
    for value in private_values:
        if isinstance(value,str) and value and unicodedata.normalize('NFKC',value).casefold() in normalized:
            return None
    # Only simple prose punctuation is accepted; digits, identifiers, records,
    # Unicode encodings and structured content cannot cross this boundary.
    if any(not (c.isascii() and (c.isalpha() or c.isspace() or c in "',?.!-")) for c in text):
        return None
    words=re.findall(r"[a-z]+(?:'[a-z]+)?",normalized)
    if not words or set(words)<=_LOCAL_ONLY or any(word not in _PUBLIC for word in words):
        return None
    return text
