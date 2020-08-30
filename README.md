# SHiFT Code Mirror Bot

A Discord bot that looks for updates to Orcicorn's [SHiFT Code Archive](https://shift.orcicorn.com/) API, then posts and publishes announcements for them in a (news) channel of your choice. Also pings any news roles you have set.

Currently just a proof of concept, and a work in progress intended for use in the official [Borderlands Discord](discord.gg/borderlands).

Thanks to Orangespire for the idea and continued support.

## Usage

Currently requires the discord.py, requests and jsonschema libraries to be installed (I'll likely package this into a Pipenv later).

Your API key must be placed in a file called api_key. For the time being you'll need to edit the IDs and embed formats in the source code to suit you.