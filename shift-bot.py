import discord
import asyncio

from typing import List, Set
import os
import re
import traceback

from shift.helper import log, get_shift_api_data, load_guild_configs, load_history, save_history, parse_manual_code, \
    build_embed
from shift.types import GuildConfig, PostHistory, ShiftCode, ShiftDataUnavailableError


# Every 15 minutes
UPDATE_DELAY = 900


class ShiftBot(discord.Client):
    __guild_configs: List[GuildConfig]
    __history: PostHistory

    __api_responsive: bool
    __guilds_ready: Set[int]
    __update_codes_task: asyncio.Task

    def __init__(self, guild_configs: List[GuildConfig], history: PostHistory, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__guild_configs = guild_configs
        self.__history = history

        self.__api_responsive = True
        self.__guilds_ready = set()

    async def on_guild_available(self, guild):
        self.__guilds_ready.add(guild.id)
        log(f'Guild ID {guild.id} ready.')

        guild_config_ids = set(config.guild_id for config in self.__guild_configs)
        if guild_config_ids <= self.__guilds_ready:
            self.__update_codes_task = self.loop.create_task(self.__update_codes_loop())

    async def on_message(self, message: discord.Message):
        guild_config = next((config for config in self.__guild_configs
                             if message.channel.id == config.command_channel_id), None)
        if not guild_config:
            return

        command = [''.join(match) for match in re.findall(r'"(.+?)"|(\S+)', message.content)]

        try:
            if len(command) >= 6 and command[0] == '$post':
                await self.__post_code(guild_config, parse_manual_code(command[1:]))
            elif len(command) >= 7 and command[0] == '$edit':
                await self.__edit_code(guild_config, int(command[1]), parse_manual_code(command[2:]))
            else:
                return
        except ValueError:
            await message.channel.send('Arguments in unrecognised format.')
            return

        save_history(self.__history)

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
            if code.time_added < self.__history.start_time or code.code in self.__history.codes:
                continue

            guild_config = next((config for config in self.__guild_configs
                                 if re.search(config.game_pattern, code.game)), None)
            if not guild_config:
                continue

            await self.__post_code(guild_config, code)

        save_history(self.__history)

    async def __post_code(self, guild_config: GuildConfig, code: ShiftCode):
        news_channel = self.get_channel(guild_config.news_channel_id)

        message = await news_channel.send(embed=build_embed(guild_config.embed_emoji, code))
        await message.publish()
        await news_channel.send(f'<@&{guild_config.news_role_id}>')

        self.__history.codes.add(code.code)

    async def __edit_code(self, guild_config: GuildConfig, message_id: int, code: ShiftCode):
        news_channel = self.get_channel(guild_config.news_channel_id)
        command_channel = self.get_channel(guild_config.command_channel_id)

        post = await news_channel.fetch_message(message_id)
        if post is None:
            command_channel.send('Post ID does not exist.')
            return

        await post.edit(embed=build_embed(guild_config.embed_emoji, code))

        self.__history.codes.add(code.code)


def main():
    api_key = os.environ.get('SHIFT_BOT_API_KEY')
    if not api_key:
        log('API key must be specified as SHIFT_BOT_API_KEY environment variable.')
        return

    guild_configs = load_guild_configs()
    if not guild_configs:
        log('At least one guild must be specified in guild_configs.json.')
        return

    history = load_history()

    client = ShiftBot(guild_configs, history)
    client.run(api_key)


if __name__ == '__main__':
    main()
