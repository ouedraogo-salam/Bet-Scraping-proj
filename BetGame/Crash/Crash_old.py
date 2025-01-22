import numpy.random
from playwright.async_api import async_playwright, Playwright, TimeoutError
import asyncio
import time
from urllib.parse import urljoin
import numpy as np
import re
from loguru import logger
import sys

logger.remove()
logger.add("Betting.log", level="INFO")
logger.add(sys.stderr, level="INFO")

SBR_WS_CDP = "wss://brd-customer-hl_dab59981-zone-scraping_browser3-country-ng:j9ipqs4tmk4s@brd.superproxy.io:9222"
BASE_URL = "https://1xbet.ng/en"
URL = urljoin(BASE_URL, "https://1xbet.ng/en/allgamesentrance/crash")
TIME_WAIT = 5
MIN_BET_AMOUNT = 1000.0 #500.0
TAUX = 1.01


async def connection(page):
    USERNAME = "729122089"
    PASSWORD = "Naboz@2025"
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
    except TimeoutError:
        return False


async def account(page):
    select_account = page.get_by_label("Select account")
    account_content = await select_account.text_content()
    patters = r"\d+\.\d+|\d+"

    return re.findall(patters, account_content)[0]


async def run(pw: Playwright):
    logger.info("Begginning of The Programme - GOOD LUCK !")

    browser = await pw.chromium.launch(headless=False)
    # Open a new page
    page = await browser.new_page()
    BET_AMOUNT = MIN_BET_AMOUNT
    MAX_AMOUNT = str(int(BET_AMOUNT) * 10)
    MAIN_ACCOUNT = ""
    ODS = "1.05"
    MAX_ROUND = 24

    await page.goto(URL)

    time.sleep(10)
    print('shake and bake')
    await page.reload()
    print("finishing reload")

    time.sleep(TIME_WAIT * 2)
    connection_resp = await connection(page)
    if connection_resp:
        time.sleep(TIME_WAIT)
        count = 1

        try:
            auto_bet = page.locator("#app iframe").content_frame.get_by_role("button", name="Autobet")
            if await auto_bet.is_visible():
                time.sleep(TIME_WAIT / 2)
                await auto_bet.click()
                while count <= MAX_ROUND:
                    MAIN_ACCOUNT = await account(page)
                    time.sleep(TIME_WAIT)
                    base_bet = page.locator("#app iframe").content_frame.get_by_label("Base bet")
                    time.sleep(TIME_WAIT / 2)
                    if await base_bet.is_visible():
                        time.sleep(TIME_WAIT / 2)
                        await base_bet.click()
                        time.sleep(TIME_WAIT / 2)
                        await base_bet.fill(str(round(BET_AMOUNT, 3)))
                        pass

                    time.sleep(TIME_WAIT / 2)
                    await page.locator("#app iframe").content_frame.get_by_label("Maximum stake amount").fill(
                        MAX_AMOUNT)

                    time.sleep(TIME_WAIT / 2)
                    enter_ods = page.locator("#app iframe").content_frame.get_by_placeholder("Enter odds")
                    await enter_ods.click()
                    time.sleep(TIME_WAIT / 2)
                    await enter_ods.fill(ODS)

                    time.sleep(TIME_WAIT)
                    place_autobet = page.locator("#app iframe").content_frame.get_by_role("button", name="Place autobet")
                    while True:
                        if await place_autobet.is_visible():
                            break
                    await place_autobet.click()
                    time.sleep(TIME_WAIT)
                    cancel_autobet = page.locator("#app iframe").content_frame.get_by_role("button", name="Cancel autobet")
                    if await cancel_autobet.is_visible():
                        time.sleep(TIME_WAIT / 3)
                        await cancel_autobet.click()

                    time.sleep(TIME_WAIT)
                    NEW_ACCOUNT = await account(page)

                    account_diff = float(NEW_ACCOUNT) - float(MAIN_ACCOUNT)

                    if account_diff > 0:
                        MAIN_ACCOUNT = NEW_ACCOUNT
                        win_amount = round(BET_AMOUNT, 3)*float(ODS)


                        logger.info(f"{count}. Congratulation You Win - BET AMOUNT: {BET_AMOUNT}"
                                    f" - WIN AMOUNT: {win_amount} - MAIN_ACCOUNT: {MAIN_ACCOUNT}")
                        BET_AMOUNT *= float(ODS)

                    else:
                        loose_amount = round(BET_AMOUNT + account_diff, 3)
                        MAIN_ACCOUNT += account_diff
                        logger.info(f"{count}. Damage You Loose - BET AMOUNT: {BET_AMOUNT} "
                                    f"- LOSE AMOUNT: {loose_amount} MAIN_ACCOUNT : {MAIN_ACCOUNT}")
                        BET_AMOUNT =MIN_BET_AMOUNT
                        pass

                    time_frame = np.random.randint(10, 60)
                    logger.info(f"Waiting Time {60 * time_frame}")
                    time.sleep(60 * time_frame)  # Wait for One Hours
                    count += 1
        except TimeoutError:
            print("Timeout ERROR")

    await page.pause()
    await page.close()
    await browser.close()
    logger.info("Endding of The Programme")


# Press the green button in the gutter to run the script.
async def main():
    """ Main entry function that initializes the Playwright instance and runs the betting logic. """
    async with async_playwright() as pw:
        await run(pw)


if __name__ == '__main__':
    asyncio.run(main())

    # page.goto("https://1xbet.ng/en/allgamesentrance/crash")
