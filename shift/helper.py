import discord
from typing import List

from datetime import datetime
import aiohttp
import jsonschema

from shift.types import ShiftData, ShiftMetadata, ShiftCode, ShiftDataUnavailableError, ShiftDataInvalidError
from shift.schema import SHIFT_API_SCHEMA


SHIFT_API_URL = 'https://shift.orcicorn.com/shift-code/index.json'

GOLDEN_KEY_EMOJI = '<:GoldenKey:273763771929853962>'


def log(text: str) -> None:
    print(f'[{datetime.now()}] {text}')


async def get_shift_api_data() -> ShiftData:
    async with aiohttp.ClientSession() as session:
        try:
            json = await __get_shift_api_json(session)
        except aiohttp.ServerConnectionError as e:
            raise ShiftDataUnavailableError from e

    try:
        jsonschema.validate(json, SHIFT_API_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ShiftDataInvalidError from e

    data = json[0]

    return ShiftData(
        metadata=__parse_shift_metadata(data['meta']),
        codes=__parse_shift_codes(data['codes'])
    )


def build_embed(code: ShiftCode) -> discord.Embed:
    if code.expires is not None:
        # The %e option is seemingly nonstandard and prints the day without the trailing 0.
        expires = datetime.strftime(code.expires, '%e %B, %Y')
    else:
        expires = 'Unknown'

    title = f'{GOLDEN_KEY_EMOJI} {code.game}: {code.reward}'
    description = (f'Platform: {code.platform}\n'
                   f'Expires: {expires}.```\n'
                   f'{code.code}```Redeem on the [website](https://shift.gearboxsoftware.com/rewards) or in game.\n\n'
                   f'[Source]({code.source})')
    colour = discord.Colour(0xF4C410)

    return discord.Embed(title=title, description=description, colour=colour)


async def __get_shift_api_json(session: aiohttp.ClientSession):
    async with session.get(SHIFT_API_URL) as response:
        if response.status != 200:
            raise ShiftDataUnavailableError(f'API server responded with non-200 error code: {response.status}.')

        try:
            # Ignore content type checks, they're useless for actual integrity.
            # We check the JSON formatting later anyway.
            json = await response.json(content_type=None)
        except json.decoder.JSONDecodeError as e:
            raise ShiftDataInvalidError from e

    return json


def __parse_shift_metadata(json) -> ShiftMetadata:
    return ShiftMetadata()


def __parse_shift_codes(json) -> List[ShiftCode]:
    return [__parse_shift_code(code_json) for code_json in json]


def __parse_shift_code(json) -> ShiftCode:
    try:
        time_added = datetime.strptime(json['archived'], '%d %b %Y %H:%M:%S %z')

        if json['expires'] == 'Unknown':
            expires = None
        else:
            expires = datetime.strptime(json['expires'], '%d %b %Y %H:%M:%S %z')
    except ValueError as e:
        raise ShiftDataInvalidError from e

    return ShiftCode(
        code=json['code'],
        game=json['game'],
        platform=json['platform'],
        reward=json['reward'],
        time_added=time_added,
        expires=expires,
        source=json['link']
    )
