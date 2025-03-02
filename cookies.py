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

    page.goto("https://www.qianlima.com/bid-487957422.html")
    # page.goto("file:///C:/Users/20368/Desktop/Browser%20&%20Crawler%20Config%20-%20Crawl4AI%20Documentation%20(v0.4.3bx).html")

    os.system("pause")
    #判断登录成功后获取cookies

    with open("output.html", "w", encoding="utf-8") as f:
        f.write(page.content())

    cookies = context.cookies()

    print("cookies: ", cookies)

    # Close page
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)