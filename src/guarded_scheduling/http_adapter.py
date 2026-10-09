"""Bounded loopback transport; it never retries an uncertain scheduling write."""
import ipaddress
import json
import re
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from .ports import Response, SchedulingUnavailable, UnknownOutcome

_MAX_RESPONSE = 1024 * 1024
_MAX_REQUEST = 64 * 1024
_ROUTES = {
    ('GET', '/providers'): {'specialty','location'},
    ('GET', '/patients/search'): {'phone','dob'},
    ('GET', '/availability'): {'patientId','specialty','location','startDate','endDate'},
    ('POST', '/appointments'): set(),
    ('POST', '/handoffs'): set(),
}

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HttpAdapter:
    def __init__(self, base_url='http://127.0.0.1:4011', scenario=None, timeout=5, opener=None):
        try:
            parsed = urlsplit(base_url)
            host = parsed.hostname
            loopback = host == 'localhost' or ipaddress.ip_address(host).is_loopback
            valid = (parsed.scheme == 'http' and loopback and not parsed.username and not parsed.password
                     and parsed.path in ('','/') and not parsed.query and not parsed.fragment
                     and (parsed.port is None or 0 < parsed.port < 65536))
        except (ValueError, TypeError):
            valid = False
        if not valid:
            raise ValueError('Scheduling base URL must be an HTTP loopback origin.')
        if scenario not in (None, 'api_failure'):
            raise ValueError('Unsupported mock scenario.')
        if not isinstance(timeout,(int,float)) or not 0 < timeout <= 60:
            raise ValueError('Use a bounded scheduling timeout.')
        self.base_url = base_url.rstrip('/')
        self.scenario = scenario
        self.timeout = timeout
        # Disable environment proxies and redirects: private requests stay at the approved origin.
        self.opener = opener or build_opener(ProxyHandler({}), _NoRedirect()).open

    def request(self, method, path, params=None, body=None):
        allowed = _ROUTES.get((method,path))
        if allowed is None and method == 'GET' and isinstance(path,str) and re.fullmatch(r'/patients/[A-Za-z0-9_-]{1,200}/appointments',path):
            allowed = set()
        if allowed is None or (params is not None and (not isinstance(params,dict) or not set(params) <= allowed)):
            raise ValueError('Unsupported scheduling operation or parameter.')
        if method == 'GET' and body is not None:
            raise ValueError('Scheduling reads do not accept a body.')
        if body is not None and not isinstance(body,dict):
            raise ValueError('Scheduling body must be an object.')
        try:
            raw = json.dumps(body,allow_nan=False).encode('utf-8') if body is not None else None
            if raw is not None and len(raw) > _MAX_REQUEST:
                raise ValueError
            query = urlencode(params or {})
        except (ValueError,TypeError,UnicodeError):
            raise ValueError('Invalid scheduling request.') from None
        url = self.base_url + path + ('?' + query if query else '')
        headers = {'Accept':'application/json'}
        if raw is not None: headers['Content-Type'] = 'application/json'
        if self.scenario: headers['X-Mock-Scenario'] = self.scenario
        request = Request(url,data=raw,headers=headers,method=method)
        uncertain = UnknownOutcome if method == 'POST' else SchedulingUnavailable
        response = None
        try:
            try:
                open_call = self.opener.open if hasattr(self.opener,'open') else self.opener
                response = open_call(request,timeout=self.timeout)
            except HTTPError as error:
                response = error
            status = response.status
            length = getattr(response,'headers',{}).get('Content-Length')
            expected = int(length) if length is not None else None
            if expected is not None and not 0 <= expected <= _MAX_RESPONSE:
                raise ValueError
            payload = response.read(_MAX_RESPONSE + 1)
            if len(payload) > _MAX_RESPONSE or (expected is not None and len(payload) != expected):
                raise ValueError
            data = json.loads(payload)
            if not isinstance(data,dict):
                raise ValueError
            if method == 'POST':
                definite = status in (201,400,409) or (status == 503 and self.scenario == 'api_failure')
                if not definite: raise ValueError
            elif not (200 <= status < 500 or (status == 503 and self.scenario == 'api_failure')):
                raise ValueError
            return Response(status,data)
        except Exception:
            # Never expose URL-bearing exceptions or response content. Every write is single-shot.
            raise uncertain('Scheduling write outcome is unresolved.' if method == 'POST' else 'Scheduling service is unavailable.') from None
        finally:
            if response is not None:
                try: response.close()
                except Exception: pass
