import os
import time
from io import BytesIO

import multipart
from disnake import ApplicationCommandInteraction, File
from selenium.common.exceptions import NoSuchElementException

from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from dors import slash_command


@slash_command(name="btc", description="Precio del bitcoin")
async def btcprice(interaction: ApplicationCommandInteraction):
    await interaction.response.defer()
    options = webdriver.ChromeOptions()
    try:
        os.mkdir(f"{os.getcwd()}/chrome")
    except FileExistsError:
        pass

    def interceptor(request):  # A response interceptor takes two args
        if request.url == 'https://in.tradingview.com/snapshot/':
            data = request.body

            request.create_response(
                status_code=200,
                headers={'Content-Type': 'image/png'},  # Optional headers dictionary
                body=data  # Optional body
            )

    options.add_argument(f"user-data-dir={os.getcwd()}/chrome")
    driver = webdriver.Chrome(options=options)
    driver.request_interceptor = interceptor
    driver.get("https://in.tradingview.com/chart/?symbol=BTCUSD")

    driver.maximize_window()
    driver.execute_script('window.localStorage.setItem("tradingview.current_theme.name", "dark")')

    # Close Sales and shit
    try:
        driver.find_element(By.CLASS_NAME, "js-dialog__close").click()
    except NoSuchElementException:
        pass

    ActionChains(driver).key_down(Keys.ALT).send_keys('s').perform()

    request = driver.wait_for_request("https://in.tradingview.com/snapshot/", timeout=120)

    s = request.body.split(b"\r")[0][2:]
    p = multipart.MultipartParser(BytesIO(request.body), s)
    imag = None
    for part in p.parts():
        if part.name == "preparedImage":
            imag = part.raw

    streamerino = BytesIO(imag)
    driver.close()

    file = File(streamerino, filename="graph.png")
    await interaction.followup.send(file=file)
