from typing import Set, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone
import jsonschema
import json

from shift.schema import GUILD_CONFIG_SCHEMA, POST_HISTORY_SCHEMA, SHIFT_API_DATA_SCHEMA, SHIFT_API_METADATA_SCHEMA, \
    SHIFT_API_CODE_SCHEMA


@dataclass
class GuildConfig:
    game_pattern: str

    guild_id: int
    command_channel_id: int
    news_channel_id: int
    news_role_id: int
    embed_emoji: str

    @staticmethod
    def parse_json(data) -> 'GuildConfig':
        try:
            jsonschema.validate(data, GUILD_CONFIG_SCHEMA)
        except jsonschema.ValidationError as e:
            raise GuildConfigsInvalidError from e

        return GuildConfig(
            game_pattern=data['game_pattern'],
            guild_id=data['guild_id'],
            command_channel_id=data['command_channel_id'],
            news_channel_id=data['news_channel_id'],
            news_role_id=data['news_role_id'],
            embed_emoji=data['embed_emoji']
        )


class PostHistory:
    start_time: datetime
    codes: Set[str]

    def __init__(self, start_time: datetime = None, codes: Set[str] = None):
        if start_time is None:
            start_time = datetime.now(timezone.utc)
        if codes is None:
            codes = set()

        self.start_time = start_time
        self.codes = codes

    @staticmethod
    def parse_json(data) -> 'PostHistory':
        try:
            jsonschema.validate(data, POST_HISTORY_SCHEMA)
        except jsonschema.ValidationError as e:
            raise PostHistoryInvalidError from e

        try:
            start_time = datetime.strptime(data['start_time'], '%d %b %Y %H:%M:%S %z')
        except ValueError as e:
            raise PostHistoryInvalidError from e

        codes = set(data['codes'])

        return PostHistory(start_time=start_time, codes=codes)

    def get_json(self):
        start_time = datetime.strftime(self.start_time, '%d %b %Y %H:%M:%S %z')
        codes = list(self.codes)

        return json.dumps({'start_time': start_time, 'codes': codes})


@dataclass
class ShiftMetadata:
    @staticmethod
    def parse_json(data) -> 'ShiftMetadata':
        try:
            jsonschema.validate(data, SHIFT_API_METADATA_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ShiftDataInvalidError from e

        return ShiftMetadata()


@dataclass
class ShiftCode:
    code: str
    game: str
    platform: str
    reward: str
    time_added: datetime
    expires: Optional[datetime]
    source: Optional[str]

    @staticmethod
    def parse_json(data) -> 'ShiftCode':
        try:
            jsonschema.validate(data, SHIFT_API_CODE_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ShiftDataInvalidError from e

        try:
            time_added = datetime.strptime(data['archived'], '%d %b %Y %H:%M:%S %z')

            if data['expires'] == 'Unknown':
                expires = None
            else:
                expires = datetime.strptime(data['expires'], '%d %b %Y %H:%M:%S %z')
        except ValueError as e:
            raise ShiftDataInvalidError from e

        return ShiftCode(
            code=data['code'],
            game=data['game'],
            platform=data['platform'],
            reward=data['reward'],
            time_added=time_added,
            expires=expires,
            source=data['link']
        )


@dataclass
class ShiftData:
    metadata: ShiftMetadata
    codes: List[ShiftCode]

    @staticmethod
    def parse_json(data) -> 'ShiftData':
        try:
            jsonschema.validate(data, SHIFT_API_DATA_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ShiftDataInvalidError from e

        return ShiftData(
            metadata=ShiftMetadata.parse_json(data['meta']),
            codes=[ShiftCode.parse_json(code_json) for code_json in data['codes']]
        )


class GuildConfigsInvalidError(Exception):
    def __init__(self, message='Guild configs format was incorrect. Repair.', *args, **kwargs):
        super().__init__(message, args, kwargs)


class PostHistoryInvalidError(Exception):
    def __init__(self, message='History file was corrupt. Repair or delete to regenerate.', *args, **kwargs):
        super().__init__(message, args, kwargs)


class ShiftDataUnavailableError(Exception):
    def __init__(self, message='Could not contact API.', *args, **kwargs):
        super().__init__(message, args, kwargs)


class ShiftDataInvalidError(Exception):
    def __init__(self, message='Received invalid data from API. Check for updates.', *args, **kwargs):
        super().__init__(message, args, kwargs)
