import os
from typing import Any, List, Sequence, Dict

import disnake
from disnake import Option
from disnake.ext import commands
from disnake.ext.commands import slash_core, InvokableSlashCommand

import config


class DorsDiscord(commands.Bot):
    def __init__(self, **options: Any):
        super().__init__(**options)

        self.plugins = {}

        modules = []
        whitelistonly = False
        for module in os.listdir(os.path.dirname("modules/")):
            if module == '__init__.py' or module[-3:] != '.py':
                continue
            module = module[:-3]
            modules.append(module)
            if module in config.whitelistonly_modules:
                whitelistonly = True

        self.slash_command()

        if whitelistonly:
            for module in config.whitelistonly_modules:
                self.load_module(module)
        else:
            for module in modules:
                if module in config.disabled_modules:
                    continue
                self.load_module(module)

    def load_module(self, module: str):
        print("Loading", module)
        themodule = __import__("modules." + module, locals(), globals())
        themodule = getattr(themodule, module)

        self.plugins[module] = themodule

        funcs = [f for _, f in themodule.__dict__.items() if callable(f)]
        for func in funcs:
            # if not (handler := getattr(func, '__handler', False)) or not (data := getattr(func, '__data', False)):
            #     continue
            if isinstance(func, InvokableSlashCommand):
                # slash_cmd = self.slash_command(**data)(func)
                self.add_slash_command(func)


slash_command = slash_core.slash_command
