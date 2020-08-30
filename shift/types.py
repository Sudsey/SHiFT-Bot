from typing import Optional, List

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ShiftMetadata:
    updated: datetime


@dataclass
class ShiftCode:
    code: str
    game: str
    platform: str
    reward: str
    expires: Optional[datetime]
    source: str


@dataclass
class ShiftData:
    metadata: ShiftMetadata
    codes: List[ShiftCode]


class ShiftDataUnavailableError(Exception):
    pass


class ShiftDataInvalidError(Exception):
    pass
