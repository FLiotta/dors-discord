from io import BytesIO

import aiohttp
from disnake import ApplicationCommandInteraction, File
from disnake.ext import commands

import config
from dors import slash_command


allowed_symbols = ['BTCUSD', 'ETHUSD', 'DOGEUSDT', 'BNBUSDT', 'DOTUSDT', 'USDTARS']


@slash_command()
async def tradingview(
    interaction: ApplicationCommandInteraction,
    symbol: str = commands.Param(name="symbol", choices=allowed_symbols)
):
    """ La pantallita de tradingview para tu shitcoin favorita """
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.chart-img.com/v1/tradingview/advanced-chart", params={
            "height": 400,
            "interval": "1h",
            "symbol": symbol,
            "key": config.chartimg_api_key
        }) as resp:
            buffer = BytesIO(await resp.read())

    file = File(buffer, filename="graph.png")
    await interaction.followup.send(file=file)
