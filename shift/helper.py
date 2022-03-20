import discord

from typing import List
from datetime import datetime, timezone
import dateutil.parser
import aiohttp
import jsonschema
import json

from shift.types import PostHistory, ShiftData, ShiftCode, ShiftDataUnavailableError, ShiftDataInvalidError
from shift.schema import SHIFT_API_SCHEMA


SHIFT_API_URL = 'https://shift.orcicorn.com/shift-code/index.json'

GOLDEN_KEY_EMOJI = '<:GoldenKey:273763771929853962>'


def log(text: str):
    print(f'[{datetime.now()}] {text}')


async def get_shift_api_data() -> ShiftData:
    async with aiohttp.ClientSession() as session:
        try:
            data = await __get_shift_api_json(session)
        except aiohttp.ServerConnectionError as e:
            raise ShiftDataUnavailableError from e

    try:
        jsonschema.validate(data, SHIFT_API_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ShiftDataInvalidError from e

    return ShiftData.parse_json(data[0])


def load_history() -> PostHistory:
    try:
        with open('history', 'r') as f:
            return PostHistory.parse_json(json.loads(f.read()))
    except FileNotFoundError:
        return PostHistory()


def save_history(history: PostHistory):
    with open('history', 'w') as f:
        f.write(history.get_json())


def parse_manual_code(args: List[str]) -> ShiftCode:
    if args[3] == 'Unknown':
        expires = None
    else:
        expires = dateutil.parser.parse(args[3])

    return ShiftCode(
        game=args[0],
        reward=args[1],
        platform=args[2],
        expires=expires,
        code=args[4],
        time_added=datetime.now(timezone.utc),
        source=None
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
                   f'{code.code}```Redeem on the [website](https://shift.gearboxsoftware.com/rewards) or in game.')
    if code.source is not None:
        description += f'\n\n[Source]({code.source})'
    colour = discord.Colour(0xF4C410)

    return discord.Embed(title=title, description=description, colour=colour)


async def __get_shift_api_json(session: aiohttp.ClientSession):
    async with session.get(SHIFT_API_URL) as response:
        if response.status != 200:
            raise ShiftDataUnavailableError(f'API server responded with non-200 error code: {response.status}.')

        try:
            # Ignore content type checks, they're useless for actual integrity.
            # We check the JSON formatting later anyway.
            data = await response.json(content_type=None)
        except json.decoder.JSONDecodeError as e:
            raise ShiftDataInvalidError from e

    return data
