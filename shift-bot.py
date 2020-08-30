import discord

from datetime import datetime, timezone

from shift.helper import log, get_shift_api_data, build_embed
from shift.types import ShiftDataUnavailableError, ShiftDataInvalidError


BORDERLANDS_GUILD_ID = 132671445376565248
NEWS_CHANNEL_ID = 749485616621813841
NEWS_ROLE_ID = 624528614330859520


class ShiftBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.__last_update = datetime.now(timezone.utc)
        self.__last_update = datetime.fromtimestamp(0, timezone.utc)

    async def on_guild_available(self, guild):
        if guild.id != BORDERLANDS_GUILD_ID:
            return

        try:
            data = get_shift_api_data()
        except ShiftDataUnavailableError:
            log("Could not contact API. Ignoring this run.")
            return
        except ShiftDataInvalidError:
            log("Received invalid data from API. Check for updates. Exiting.")
            await self.close()
            raise

        if data.metadata.updated <= self.__last_update:
            return

        channel = self.get_channel(NEWS_CHANNEL_ID)
        await channel.send(embed=build_embed(data.codes[0]))


def main():
    with open('api_key', 'r') as f:
        api_key = f.read().replace('\n', '')

    client = ShiftBot()
    client.run(api_key)


if __name__ == '__main__':
    main()
