from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class URLStatus(Enum):
    SUCCESS = auto()
    ERROR = auto()
    SKIPPED = auto()

@dataclass
class ExpansionResult:
    original_url: str
    expanded_url: str
    status: URLStatus
    error: Optional[str] = None