from playwright.async_api import async_playwright, TimeoutError, Playwright, Page
import asyncio
import time
from urllib.parse import urljoin
import numpy as np
import re
from loguru import logger
import sys

# Setting up the logger
logger.remove()  # Removes default logger configurations
logger.add("Betting.log", level="INFO")  # Log to a file
logger.add(sys.stderr, level="INFO")  # Log to stderr for real-time monitoring

# Base URL and endpoint for the game
BASE_URL = "https://1xbet.ng/en/allgamesentrance/"
URL = urljoin(BASE_URL, "crash")  # Simplified, avoids redundant BASE_URL

# Constants
TIME_WAIT = 5  # Time to wait between actions in seconds
base_amount_dict: dict = {
    "initial": 200.0,
    "current": 200.0
}  # Minimum bet amount dict

bet_amount_dict = {
    "200": 1000.0,
    "500": 1500.0,
    "1000": 3_000.0,
    "10000": 30_000
}

# Login credentials
USERNAME = "729122089"
PASSWORD = "Naboz@2025"


# Function for handling login to the 1xBet page
async def connection(page):
    """
    Handles the login process on the 1xBet website.

    Args:
        page: Playwright page object

    Returns:
        bool: True if login is successful, False if there is a timeout or failure.
    """
    try:
        # Click the login button
        await page.get_by_role("button", name="Log in").click()
        time.sleep(TIME_WAIT * 2)  # Wait after each action for page load stability

        # Enter username
        await page.get_by_role("textbox", name="E-mail or ID").click()
        await page.get_by_role("textbox", name="E-mail or ID").fill(USERNAME)
        time.sleep(TIME_WAIT)  # Wait after each action for page load stability

        # Enter password
        await page.get_by_role("textbox", name="Password").click()
        await page.get_by_role("textbox", name="Password").fill(PASSWORD)
        time.sleep(TIME_WAIT)  # Wait after each action for page load stability

        # Submit the login form
        await page.locator("form").get_by_role("button", name="Log in").click()
        time.sleep(TIME_WAIT / 2)

        # Check if account selection screen is visible
        select_account_visible = await page.get_by_label("Select account").is_visible()
        my_account_visible = await page.get_by_label("My account").is_visible()
        time.sleep(TIME_WAIT * 2)  # Allow for final loading

        # Return True if both 'Select account' and 'My account' are visible
        return my_account_visible and select_account_visible

    except TimeoutError:  # Catch any timeouts during page interaction
        logger.error("Timeout occurred during login")
        return False


async def execute_bet_cycle(page, bet_amount, max_amount, ods):
    """
        Main loop to execute the betting cycle.
        Cycles through a defined number of rounds, places bets, and updates the account balance.

        Args:
            :param ods: the betting ods
            :param max_amount: the maximum amount to bet
            :param page: Playwright page object
            :param bet_amount: the bet amount

        Returns:
            None

        """

    time.sleep(TIME_WAIT)

    try:
        # Locate and click the 'Autobet' button

        count = 1

        await page.locator("#app iframe").content_frame.get_by_label("Maximum stake amount").fill(str(max_amount))

        time.sleep(TIME_WAIT / 2)
        enter_ods = page.locator("#app iframe").content_frame.get_by_placeholder("Enter odds")
        await enter_ods.click()
        await enter_ods.fill(str(ods))
        time.sleep(TIME_WAIT)

        # Loop through each round
        while True:
            main_account = await get_main_account(page)
            time.sleep(TIME_WAIT / 2)

            # Place the bet for this round
            await place_bet(page, bet_amount)

            # Handle the result of the bet
            bet_amount, main_account = await handle_bet_result(page, bet_amount, main_account, ods, count)

            # Wait before the next round
            time_frame = np.random.randint(10, 60)
            wait_time = 60 * time_frame
            logger.info(f"Waiting Time : {time_frame} Min!")
            count += 1
            time.sleep(wait_time)

    except TimeoutError as e:
        logger.error(f"Timeout ERROR Occurred {e}")
        page.reload()
        await execute_bet_cycle(page, bet_amount, max_amount, ods)


# Function to scrape the account balance
async def get_balance(page):
    """
    Scrapes the user's account balance from the page.

    Args:
        page: Playwright page object

    Returns:
        float: Extracted account balance from the page.
    """
    try:
        select_account = page.get_by_label("Select account")
        account_content = await select_account.text_content()

        # Use regex to find account balance (decimal or integer)
        pattern = r"\d+\.\d+|\d+"
        balance = re.findall(pattern, account_content)

        if balance:
            return float(balance[0])  # Convert string to float for numeric operations
        else:
            logger.warning("No balance found on account page")
            return 0.0

    except Exception as e:
        logger.error(f"Error occurred while retrieving account balance: {e}")
        return 0.0


async def get_main_account(page):
    """
    Fetch the main account balance.

    Args:
        page: Playwright page object

    Returns:
        float: balance from the page.
    """

    return await get_balance(page)


async def place_bet(page: Page, bet_amount: float):
    """
    Function to interact with the page and place a bet.
    Fills in the required fields for betting, including bet amount and odds.

    Args:

        :param page: Playwright page object
        :param bet_amount: float

    Returns:
        None
    """

    base_bet = page.locator("#app iframe").content_frame.get_by_label("Base bet")
    time.sleep(TIME_WAIT / 2)

    # await base_bet.click()
    time.sleep(TIME_WAIT / 2)
    await base_bet.fill(str(round(bet_amount, 3)))

    await confirm_autobet(page)


async def confirm_autobet(page):
    """
    Confirm the autobet action.
    Waits for the 'Place autobet' button to be visible, clicks it, and cancels if needed.

    Args:
        :param page: Playwright page object

    Returns:
        None
    """

    place_autobet = page.locator("#app iframe").content_frame.get_by_role("button", name="Place autobet")

    # Wait for 'Place autobet' button to be visible
    while not await place_autobet.is_visible():
        time.sleep(TIME_WAIT*1.5)

    await place_autobet.click()
    time.sleep(TIME_WAIT)

    # Check if the 'Cancel autobet' button appears, and click if visible
    cancel_autobet = page.locator("#app iframe").content_frame.get_by_role("button", name="Cancel autobet")
    if await cancel_autobet.is_visible():
        time.sleep(TIME_WAIT / 3)
        await cancel_autobet.click()


async def handle_bet_result(page, bet_amount, main_account, ods, count):
    """
    Determine if the bet was won or lost and adjust the bet amount and account balance accordingly.
    Logs the result and updates the next bet amount.

    Args:
        :param count:
        :param ods:
        :param main_account:
        :param bet_amount:
        :param page: Playwright page object

    Returns:
        float: bet_amount, new_account  balance from the page.
    """
    time.sleep(TIME_WAIT * 1.5)
    new_account = await get_main_account(page)
    account_diff = float(new_account) - float(main_account)

    if account_diff > 0:
        # Win scenario
        win_amount = round(bet_amount, 3) * float(ods)
        logger.info(
            f"{count}. Congratulations! You Win - BET AMOUNT: {bet_amount} "
            f"- WIN AMOUNT: {win_amount} - MAIN_ACCOUNT: {new_account}")
        bet_amount *= float(ods)  # Increase bet amount for the next round

        if float(bet_amount) >= bet_amount_dict[str(int(base_amount_dict['initial']))]:
            bet_amount = base_amount_dict['initial']
    else:
        # Loss scenario
        loose_amount = round(bet_amount + account_diff, 3)
        logger.info(
            f"{count}. Damage! You Lose - BET AMOUNT: {bet_amount} "
            f"- LOSE AMOUNT: {loose_amount} - MAIN_ACCOUNT: {new_account}")
        bet_amount = "200" # base_amount_dict.get("current")  # Reset bet amount to the minimum

    return bet_amount, new_account


async def run(pw: Playwright):
    """
    Main function to launch the browser and execute the betting cycle.

    Args:
        :param pw: Playwright object

    Returns:
        None
    """

    # Initialize values
    bet_amount = base_amount_dict.get("current")
    max_amount = str(int(bet_amount) * 10)
    ods = "1.01"

    browser = await pw.firefox.launch(headless=False)
    page = await browser.new_page()
    await page.goto(URL)
    time.sleep(TIME_WAIT * 2)

    # Check connection to the site
    connection_resp = await connection(page)
    time.sleep(TIME_WAIT)
    if connection_resp:
        auto_bet = page.locator("#app iframe").content_frame.get_by_role("button", name="Autobet")
        if await auto_bet.is_visible():
            time.sleep(TIME_WAIT / 3)
            await auto_bet.click()
            await execute_bet_cycle(page, bet_amount, max_amount, ods)
    else:
        logger.error("Failed to log in")

    # Close browser and finish
    await page.pause()
    await page.close()
    await browser.close()
    logger.info("End of the Program")


async def main():
    """ Main entry function that initializes the Playwright instance and runs the betting logic. """
    async with async_playwright() as pw:
        logger.info("Beginning of the Program - GOOD LUCK!")
        await run(pw)


if __name__ == '__main__':
    asyncio.run(main())
