import numpy.random
from playwright.async_api import async_playwright
import asyncio
import time
from urllib.parse import urljoin
import numpy as np
import re
from loguru import logger
import sys
from pprint import pprint
from bs4 import BeautifulSoup

logger.remove()
logger.add("Betting.log", level="INFO")
logger.add(sys.stderr, level="INFO")

SBR_WS_CDP = "wss://brd-customer-hl_dab59981-zone-scraping_browser3-country-ng:j9ipqs4tmk4s@brd.superproxy.io:9222"
BASE_URL = "https://1xbet.ng/en"
URL = urljoin(BASE_URL, "https://1xbet.ng/en/allgamesentrance/fortuneapple")
TIME_WAIT = 5
MIN_BET_AMOUNT = "1000"
TAUX = 1.23


async def connection(page):
    USERNAME = "729122089"
    PASSWORD = "Naboz@2025"
    page.locator("#app iframe").content_frame.get_by_text("You have won: 202 XOF").click()

    try:
        await page.get_by_role("button", name="Log in").click()
        time.sleep(TIME_WAIT)
        await page.get_by_role("textbox", name="E-mail or ID").click()
        time.sleep(TIME_WAIT)
        await page.get_by_role("textbox", name="E-mail or ID").fill(USERNAME)
        time.sleep(TIME_WAIT)
        await page.get_by_role("textbox", name="Password").click()
        time.sleep(TIME_WAIT)
        await page.get_by_role("textbox", name="Password").fill(PASSWORD)
        time.sleep(TIME_WAIT)
        await page.locator("form").get_by_role("button", name="Log in").click()
        time.sleep(TIME_WAIT / 2)
        select_account = await page.get_by_label("Select account").is_visible()
        time.sleep(TIME_WAIT / 2)
        my_account = await page.get_by_label("My account").is_visible()
        time.sleep(TIME_WAIT * 2)
        return my_account and select_account
    except:
        return False


async def bet_results(page, guest_number, base_amount):
    take_winnings = page.locator("#app iframe").content_frame.get_by_role("button", name="Take winnings")
    win_amount = ''

    take_winnings_visible = await take_winnings.is_visible()
    time.sleep(TIME_WAIT / 2)
    # take_winnings_enable = await take_winnings.is_enabled()

    if take_winnings_visible:
        winnings_bet = page.locator("#app iframe").content_frame.locator("div.fortune-apple-bet__actions")
        await winnings_bet.click()
        time.sleep(TIME_WAIT)
        win_amount = float(base_amount) * TAUX
        logger.info(
            f"Congratulation You Win - BET AMOUNT : {base_amount}, WIN AMOUNT: {win_amount}, Gess Number: {guest_number}")
    else:
        win_amount = MIN_BET_AMOUNT
        logger.info(f"Damage You Loose - BET AMOUNT : {base_amount}, Gess Number: {guest_number}")
    return str(win_amount)


async def place_bet(page, amount, guest_number):
    try:
        time.sleep(TIME_WAIT)
        bet_input = page.locator("#app iframe").content_frame.get_by_placeholder("0")
        await bet_input.click()
        time.sleep(TIME_WAIT / 2)
        await bet_input.fill(amount)
        time.sleep(TIME_WAIT)
        await page.locator("#app iframe").content_frame.locator("div.fortune-apple-bet__actions").click()

        time.sleep(TIME_WAIT + 2)
        await (page.locator("#app iframe").content_frame
               .locator(f"div:nth-child(10) > button:nth-child({guest_number})").click())
        time.sleep(TIME_WAIT + 2)
        return True
    except Exception as e:
        print(f"Exception from place_bet")
        # raise Exception
        return False


async def run(pwg):
    logger.info("Begginning of The Programme")

    win_amount = base_amount = MIN_BET_AMOUNT
    round = 0
    k = 1
    MAX_ROUND = 24

    # browser = await pwg.chromium.connect_over_cdp(SBR_WS_CDP)
    # Launch a firefox Browser
    browser = await pwg.chromium.launch(headless=False)
    #
    # Open a new page
    page = await browser.new_page()

    await page.goto(URL)

    # Trying to connect to site web
    time.sleep(TIME_WAIT * 2)
    connection_resp = await connection(page)

    if connection_resp:
        round_list = np.random.randint(1, 10, 24)
        n = np.random.randint(1, 24)
        round = int(round_list[n])

        COUNT = 1
        while COUNT <= MAX_ROUND:
            logger.info(f"{COUNT}")
            # The
            GUESS_NUMBER = numpy.random.randint(low=1, high=5)

            game = await page.get_by_text("Game not finished You have an").is_visible()
            if game:
                await page.get_by_role("button", name="OK").click()
                win_amount = await bet_results(page, guest_number=GUESS_NUMBER,
                                               base_amount=base_amount)
                time.sleep(TIME_WAIT)
            else:

                bet_result = await place_bet(page, win_amount, guest_number=GUESS_NUMBER, )
                if bet_result:
                    win_amount = await bet_results(page, guest_number=GUESS_NUMBER,
                                                   base_amount=base_amount)
                else:
                    win_amount = MIN_BET_AMOUNT
                    print("No Bet")
                    pass
            base_amount = win_amount

            time_frame = np.random.randint(10, 60)
            wait_time = 60 * time_frame
            logger.info(f"#{COUNT}Waiting Time : {time_frame} Min!")
            COUNT += 1
            time.sleep(wait_time)

    else:
        print("connection faile")

    await page.pause()
    await page.close()
    await browser.close()
    logger.info("Endding of The Programme")


# Press the green button in the gutter to run the script.
async def main():
    async with async_playwright() as pwg:
        await run(pwg)


if __name__ == '__main__':
    asyncio.run(main())

