import discord
import asyncio

import traceback

from shift.helper import log, load_history, save_history, get_shift_api_data, build_embed
from shift.types import PostHistory, ShiftDataUnavailableError


BORDERLANDS_GUILD_ID = 132671445376565248
NEWS_CHANNEL_ID = 749485616621813841
NEWS_ROLE_ID = 624528614330859520

# Every 15 minutes
UPDATE_DELAY = 900


class ShiftBot(discord.Client):
    __history: PostHistory
    __api_responsive: bool

    __update_codes_task: asyncio.Task

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__history = load_history()
        self.__api_responsive = True

    async def on_guild_available(self, guild):
        if guild.id == BORDERLANDS_GUILD_ID:
            self.__update_codes_task = self.loop.create_task(self.__update_codes_loop())

    async def __update_codes_loop(self):
        await self.wait_until_ready()

        while True:
            # We need to log exceptions here because otherwise the Task eats it
            # noinspection PyBroadException
            try:
                await self.__update_codes()
            except Exception:
                log(f'Error occurred in Task. Exiting.\n{traceback.format_exc()}')
                break

            await asyncio.sleep(UPDATE_DELAY)

        await self.close()

    async def __update_codes(self):
        try:
            data = await get_shift_api_data()
        except ShiftDataUnavailableError as e:
            if self.__api_responsive:
                log(f'Could not contact API. Will log when connection is reestablished.\n{traceback.format_exc()}')
                self.__api_responsive = False
            return

        if not self.__api_responsive:
            log('Connection reestablished.')
            self.__api_responsive = True

        channel = self.get_channel(NEWS_CHANNEL_ID)

        for code in data.codes:
            if not (code.time_added < self.__history.start_time or code.code in self.__history.codes):
                message = await channel.send(embed=build_embed(code))
                await message.publish()
                await channel.send(f'<@&{NEWS_ROLE_ID}>')

                self.__history.codes.add(code.code)

        save_history(self.__history)


def main():
    with open('api_key', 'r') as f:
        api_key = f.read().replace('\n', '')

    client = ShiftBot()
    client.run(api_key)


if __name__ == '__main__':
    main()
