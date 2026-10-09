"""Typo suggestions for public vocabulary or validated API provider names only.

Callers own provenance: never pass patient records, identity values or model-made
options. Returned labels require explicit user selection; this module performs
no lookup, preference update, clinical ranking or booking action.
"""
from rapidfuzz import fuzz

from .models import ValidationError


def _label(value):
    return (type(value) is str and 0 < len(value) <= 200 and bool(value.strip())
            and all(char.isalnum() or char in " _-.,'’()" for char in value))


def _normalize(value):
    return ' '.join(value.casefold().replace('_', ' ').split())


def suggest(value, candidates):
    """Return at most three close, original labels; exact matches need no fix.

    Similarity is spelling distance, never provider suitability. A conservative
    ratio cutoff and five-point best-match band avoid token/partial matching
    and distant alternatives that could recommend unrelated labels. Collection/label bounds keep untrusted API input finite and inert.
    """
    if (type(value) is not str or len(value) > 200
            or any(not (char.isalnum() or char in " _-.,'’()") for char in value)):
        raise ValidationError('Invalid public suggestion value.')
    if (type(candidates) not in (list, tuple) or len(candidates) > 1000
            or any(not _label(candidate) for candidate in candidates)):
        raise ValidationError('Invalid public suggestion candidates.')
    query = _normalize(value)
    if not query or any(query == _normalize(candidate) for candidate in candidates):
        return []
    ranked = []
    for candidate in set(candidates):
        score = fuzz.ratio(query, _normalize(candidate))
        if score >= 80:
            ranked.append((score, candidate))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].casefold(), pair[1]))
    if not ranked:
        return []
    closest = ranked[0][0]
    return [candidate for score, candidate in ranked[:3] if score >= closest - 5]
