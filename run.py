#!/usr/bin/env python3

from dors import DorsDiscord
import config

bot = DorsDiscord(command_prefix=config.prefix)
bot.run(config.token)
