from playwright.sync_api import Playwright, sync_playwright, expect
from config import COOKIES
import os

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    if COOKIES:
       context.add_cookies(COOKIES)

    page.goto("https://www.qianlima.com")

    os.system("pause")
    #判断登录成功后获取cookies
    cookies = context.cookies()

    print("cookies: ", cookies)
    # Close page
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)