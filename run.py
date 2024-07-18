#!/usr/bin/env python3
from disnake import Intents

from dors import DorsDiscord
import config

bot = DorsDiscord(command_prefix=config.prefix, intents=Intents.all())
bot.run(config.token)
