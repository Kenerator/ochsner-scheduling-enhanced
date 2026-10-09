"""Effects return status/data; interpretation never carries IDs or consent."""
from dataclasses import dataclass
from typing import Protocol
from .models import Interpretation

@dataclass(frozen=True)
class Response:
    status: int
    data: dict

class SchedulingUnavailable(RuntimeError):
    pass

class UnknownOutcome(RuntimeError):
    pass

class ModelFailure(RuntimeError):
    pass

class SchedulingPort(Protocol):
    def request(self, method: str, path: str, params: dict | None = None, body: dict | None = None) -> Response: ...

class ModelPort(Protocol):
    def interpret(self, text: str, context: dict) -> Interpretation: ...
