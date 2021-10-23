import io

import matplotlib.colors
import matplotlib.cm
import pandas as pd
import matplotlib.pyplot as plt
import aiohttp
from disnake import ApplicationCommandInteraction, File
from matplotlib.dates import DateFormatter
from matplotlib.font_manager import FontProperties

from dors import slash_command

pretty_colors = [
    (0.5568627450980392, 0.1411764705882353, 0.6666666666666666),
    (0.8470588235294118, 0.10588235294117647, 0.3764705882352941),
    (0.5568627450980392, 0.1411764705882353, 0.6666666666666666),
    (0.3686274509803922, 0.20784313725490197, 0.6941176470588235),
    (0.11764705882352941, 0.5333333333333333, 0.8980392156862745),
    (0.011764705882352941, 0.6078431372549019, 0.8980392156862745),
    (0.0, 0.6745098039215687, 0.7568627450980392),
    (0.0, 0.5372549019607843, 0.4823529411764706),
    (0.2627450980392157, 0.6274509803921569, 0.2784313725490196),
    (0.48627450980392156, 0.7019607843137254, 0.25882352941176473),
    (0.7529411764705882, 0.792156862745098, 0.2),
    (0.9921568627450981, 0.8470588235294118, 0.20784313725490197),
    (1.0, 0.7019607843137254, 0.0),
    (0.984313725490196, 0.5490196078431373, 0.0),
    (0.9568627450980393, 0.3176470588235294, 0.11764705882352941),
    (0.42745098039215684, 0.2980392156862745, 0.2549019607843137),
    (0.4588235294117647, 0.4588235294117647, 0.4588235294117647),
    (0.32941176470588235, 0.43137254901960786, 0.47843137254901963),
    (0.7176470588235294, 0.10980392156862745, 0.10980392156862745),
    (0.5333333333333333, 0.054901960784313725, 0.30980392156862746),
    (0.2901960784313726, 0.0784313725490196, 0.5490196078431373)
]

color_map = matplotlib.colors.ListedColormap(pretty_colors)


def do_plotting(data, feedata, btc_price):
    # Dear lord

    columns = ["0", "0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-8", "8-10", "10-12", "12-15", "15-20",
               "20-30", "30-40", "40-50", "50-60", "60-70", "80-90", "90-100", "100-125", "125-150"]

    # pdata = [[x['vsizes'][datapoint] for datapoint in range(len(columns))] for x in data]
    pdata = {columns[x]: [y['vsizes'][x] for y in data] for x in range(len(columns))}
    pdata['time'] = [x['added'] for x in data]

    plt.style.use('dark_background')

    df = pd.DataFrame(pdata)
    df['time'] = pd.to_datetime(df['time'].replace(".000Z", ""), format='%Y-%m-%dT%H:%M:%S')

    f, (a0, a1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [5, 2]})
    f.set_size_inches(10, 5)

    # Plot mempool graph
    plt.axes(a0)
    ax = df.plot.area(x='time', linewidth=0, colormap=color_map, ax=a0)
    ax.autoscale(tight=True)
    ax.set_ylabel("vBytes")
    date_form = DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_form)
    ax.yaxis.set_major_formatter(lambda x, y: f"{round(x / 1000000, 2)} MvB")
    ax.set_facecolor((0.11372549019607843, 0.12156862745098039, 0.19215686274509805))

    plt.xticks(rotation=90)

    data_stream = io.BytesIO()
    plt.title("Bitcoin mempool status")
    plt.legend(loc='center right', bbox_to_anchor=(-0.18, 0.5), title="sat/vB")

    # Plot fee in $ table
    # raw sat/vb table
    mempool_blocks = {f"$\\bf{{{(x + 1) * 10}m}}$": int(round(feedata[x]['medianFee'], 0)) for x in range(len(feedata))}

    # fig.patch.set_visible(False)
    plt.axes(a1)
    a1.axis('off')
    a1.axis('tight')
    a1.set_facecolor((0.11372549019607843, 0.12156862745098039, 0.19215686274509805))

    sat_price = btc_price / 10 ** 8

    dcsummary = pd.DataFrame(
        {x: [y, '',
             f"${round((y * 226) * sat_price, 2)}",
             f"${round((y * 166) * sat_price, 2)}",
             f"${round((y * 141) * sat_price, 2)}"] for x, y in mempool_blocks.items()},
        index=['sat/vB', '', 'legacy', 'segwit', 'bech32'])

    tbl = plt.table(cellText=dcsummary.values,
                    rowLabels=dcsummary.index, colWidths=[0.25 for x in dcsummary.columns],
                    colColours=[(0.11372549019607843, 0.12156862745098039, 0.19215686274509805)] *
                               (len(mempool_blocks) + 1),
                    rowColours=[(0.11372549019607843, 0.12156862745098039, 0.19215686274509805)] * 10,
                    cellColours=[[(0.11372549019607843, 0.12156862745098039, 0.19215686274509805)]
                                 * len(mempool_blocks)] * 5,
                    colLabels=dcsummary.columns,
                    cellLoc="left", rowLoc="right", colLoc="left",
                    loc='top', bbox=[-0.08, 0.5, 0.25 * (len(mempool_blocks) + 1), 0.4])
    for row, c in tbl.get_celld().items():
        c.visible_edges = 'open'

    tbl.auto_set_column_width(col=list(range(len(dcsummary.columns))))
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    tbl.scale(1, 1.5)

    # box = a1.get_position()
    # a1.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    plt.title("Average fees")

    plt.rcParams['axes.facecolor'] = (0.11372549019607843, 0.12156862745098039, 0.19215686274509805)
    plt.rcParams['savefig.facecolor'] = (0.11372549019607843, 0.12156862745098039, 0.19215686274509805)

    plt.subplots_adjust(left=0.22, right=1, wspace=0.2, hspace=0.2)
    # plt.show()

    plt.savefig(data_stream, format='png', dpi=80)
    data_stream.seek(0)
    return data_stream


@slash_command(name="fees", description="Shows BTC/ETH transaction fees")
async def foo(interaction: ApplicationCommandInteraction):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        btc_price = await session.get("https://blockchain.info/ticker")
        btc_price = await btc_price.json()

        btc_mempool_history = await session.get("https://mempool.space/api/v1/statistics/2h")
        btc_mempool_history = await btc_mempool_history.json()
        btc_fee_data = await session.get("https://mempool.space/api/v1/fees/mempool-blocks")
        btc_fee_data = await btc_fee_data.json()

        nifty_plot = do_plotting(btc_mempool_history, btc_fee_data, btc_price['USD']['last'])

    file = File(nifty_plot, filename="btc_mempool_history.png")
    await interaction.followup.send(file=file)
