from io import BytesIO

import aiohttp
from disnake import ApplicationCommandInteraction, File

from dors import slash_command


async def do_ticker(interaction: ApplicationCommandInteraction, symbol):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.chart-img.com/v1/tradingview/advanced-chart", params={
            "height": 400,
            "interval": "1h",
            "symbol": symbol
        }) as resp:
            buffer = BytesIO(await resp.read())

    file = File(buffer, filename="graph.png")
    await interaction.followup.send(file=file)


@slash_command()
async def tradingview(interaction: ApplicationCommandInteraction):
    """ La pantallita de tradingview para tu shitcoin favorita """
    await interaction.response.defer()


@tradingview.sub_command()
async def btc(interaction: ApplicationCommandInteraction):
    """ Bitcoin """
    await do_ticker(interaction, "BTCUSD")


@tradingview.sub_command()
async def eth(interaction: ApplicationCommandInteraction):
    """ Ethereum """
    await do_ticker(interaction, "ETHUSD")


@tradingview.sub_command()
async def bnb(interaction: ApplicationCommandInteraction):
    """ BNB """
    await do_ticker(interaction, "BNBUSD")


@tradingview.sub_command()
async def doge(interaction: ApplicationCommandInteraction):
    """ Perrocoin """
    await do_ticker(interaction, "DOGEUSD")
