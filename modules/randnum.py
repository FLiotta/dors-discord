import random

from disnake import ApplicationCommandInteraction

from dors import slash_command


@slash_command(name="random", description="Sends a number between 1 and 10")
async def foo(interaction: ApplicationCommandInteraction):
    await interaction.response.send_message(random.randint(1, 10))
