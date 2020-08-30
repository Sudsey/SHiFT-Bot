import discord
from typing import List

from datetime import datetime
import requests
import jsonschema

from shift.types import ShiftData, ShiftMetadata, ShiftCode, ShiftDataUnavailableError, ShiftDataInvalidError
from shift.schema import SHIFT_API_SCHEMA


SHIFT_API_URL = 'https://shift.orcicorn.com/shift-code/index.json'

GOLDEN_KEY_EMOJI = '<:GoldenKey:273763771929853962>'


def log(text: str) -> None:
    print(f'[{datetime.now()}] {text}')


def get_shift_api_data() -> ShiftData:
    response = requests.get(SHIFT_API_URL)
    if response.status_code != 200:
        raise ShiftDataUnavailableError

    try:
        json = response.json()
    except ValueError:
        raise ShiftDataUnavailableError

    try:
        jsonschema.validate(json, SHIFT_API_SCHEMA)
    except jsonschema.ValidationError:
        raise ShiftDataInvalidError

    data = json[0]

    return ShiftData(
        metadata=__parse_shift_metadata(data['meta']),
        codes=__parse_shift_codes(data['codes'])
    )


def build_embed(code: ShiftCode) -> discord.Embed:
    title = f'{GOLDEN_KEY_EMOJI} {code.game}: {code.reward}'
    description = (f'Platform: {code.platform}\n'
                   f'Expires: {datetime.strftime(code.expires, "%e %B, %Y")}.```\n'
                   f'{code.code}```Redeem on the [website](https://shift.gearboxsoftware.com/rewards) or in game.\n\n'
                   f'[Source]({code.source})')
    colour = discord.Colour(0xF4C410)

    return discord.Embed(title=title, description=description, colour=colour)


def __parse_shift_metadata(json) -> ShiftMetadata:
    try:
        updated = datetime.strptime(json['generated']['human'], '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        raise ShiftDataInvalidError

    return ShiftMetadata(
        updated=updated
    )


def __parse_shift_codes(json) -> List[ShiftCode]:
    return [__parse_shift_code(code_json) for code_json in json]


def __parse_shift_code(json) -> ShiftCode:
    if json['expires'] == 'Unknown':
        expires = None
    else:
        try:
            expires = datetime.strptime(json['expires'], '%d %b %Y %H:%M:%S %z')
        except ValueError:
            raise ShiftDataInvalidError

    return ShiftCode(
        code=json['code'],
        game=json['game'],
        platform=json['platform'],
        reward=json['reward'],
        expires=expires,
        source=json['link']
    )
