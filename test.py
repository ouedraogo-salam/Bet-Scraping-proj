
from loguru import logger
import sys
from bs4 import BeautifulSoup
import re

logger.remove()
logger.add("Betting.log", level="INFO")
logger.add(sys.stderr, level="INFO")

base_amount = "246"
win_amount = ""
guest_number = "1"

# result_win = page.locator("div.fortune-apple-character__result--win")
html = """
    <div data-v-731c028a="" class="fortune-apple__logo fortune-apple-logo"><picture data-v-731c028a="" class="fortune-apple-logo__picture"><div data-v-731c028a="" class="fortune-apple-character__result fortune-apple-character__result--win"><p data-v-731c028a="" class="fortune-apple-character__msg">
                You have won 302.58 XOF
            </p></div><source data-v-731c028a="" srcset="https://cdngam.com/mfs/game-fortune-apple/mobile-logo56aff95d2b91.webp" type="image/webp"> <img data-v-731c028a="" src="https://cdngam.com/mfs/game-fortune-apple/mobile-logoe1795b885cd7.png" width="335" height="124" alt="fortune-apple" class="fortune-apple-logo__img"></picture></div>
"""
soup = BeautifulSoup(html, "html.parser")
content = soup.text.strip()
patters = r"\d+\.\d+|\d+"
print(re.findall(patters, content))

logger.info(
    f"Congratulation You Win - BET AMOUNT : {base_amount}, WIN AMOUNT: {win_amount}, Gess Number: {guest_number}")
