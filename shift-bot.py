import discord
import asyncio

import re
import traceback

from shift.helper import log, get_shift_api_data, load_history, save_history, parse_manual_code, build_embed
from shift.types import PostHistory, ShiftCode, ShiftDataUnavailableError

BORDERLANDS_GUILD_ID = 132671445376565248
COMMAND_CHANNEL_ID = 556796818600755229
NEWS_CHANNEL_ID = 749485616621813841
NEWS_ROLE_ID = 624528614330859520

# Every 15 minutes
UPDATE_DELAY = 900


class ShiftBot(discord.Client):
    __history: PostHistory
    __api_responsive: bool

    __news_channel: discord.TextChannel
    __update_codes_task: asyncio.Task

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__history = load_history()
        self.__api_responsive = True

    async def on_guild_available(self, guild):
        if guild.id == BORDERLANDS_GUILD_ID:
            self.__news_channel = self.get_channel(NEWS_CHANNEL_ID)
            self.__update_codes_task = self.loop.create_task(self.__update_codes_loop())

    async def on_message(self, message: discord.Message):
        if message.channel.id != COMMAND_CHANNEL_ID:
            return
        command = [''.join(match) for match in re.findall(r'"(.+?)"|(\S+)', message.content)]

        try:
            if command[0] == '$post' and len(command) >= 6:
                await self.__post_code(parse_manual_code(command[1:]))
            elif command[0] == '$edit' and len(command) >= 7:
                post = await self.__news_channel.fetch_message(int(command[1]))
                if post is None:
                    message.channel.send("Post ID does not exist.")
                    return

                await self.__edit_code(post, parse_manual_code(command[2:]))
        except ValueError:
            await message.channel.send("Arguments in unrecognised format.")

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
        except ShiftDataUnavailableError:
            if self.__api_responsive:
                log(f'Could not contact API. Will log when connection is reestablished.\n{traceback.format_exc()}')
                self.__api_responsive = False
            return

        if not self.__api_responsive:
            log('Connection reestablished.')
            self.__api_responsive = True

        for code in data.codes:
            if not (code.time_added < self.__history.start_time or code.code in self.__history.codes):
                await self.__post_code(code)

        save_history(self.__history)

    async def __post_code(self, code: ShiftCode):
        message = await self.__news_channel.send(embed=build_embed(code))
        # Leaving this disabled for now, in case edits need to be made before being sent out.
        # await message.publish()
        await self.__news_channel.send(f'<@&{NEWS_ROLE_ID}>')

        self.__history.codes.add(code.code)

    async def __edit_code(self, message: discord.Message, code: ShiftCode):
        await message.edit(embed=build_embed(code))

        self.__history.codes.add(code.code)


def main():
    with open('api_key', 'r') as f:
        api_key = f.read().replace('\n', '')

    client = ShiftBot()
    client.run(api_key)


if __name__ == '__main__':
    main()
