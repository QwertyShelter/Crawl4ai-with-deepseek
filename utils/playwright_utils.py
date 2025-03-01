from time import sleep
from config import COOKIES
from playwright.sync_api import Playwright, Page, BrowserContext

def download_page(url: str, context: BrowserContext) -> str:
    page = context.new_page()

    page.goto(url)

    sleep(5)
    # 提取所有 <li> 元素
    last_index = url.rfind('/')

    filename = "download/" + url[last_index+1: ]
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page.content())

    page.close()

    return filename

def get_all_links(page: Page, links: list, context: BrowserContext):
    page.wait_for_load_state("load")
    # 提取所有 <li> 元素
    li_elements = page.query_selector_all("li")
    num_links = 0
        
    for li in li_elements:
        # 提取 <a> 标签中的链接
        link = li.query_selector("a.con-title")
        # 提取特定的 <a> 标签 (class="a.con-address.con-type")
        if link:
            href = link.get_attribute("href")
            links.append("file://" + download_page("https:" + href, context))
            num_links += 1        

    print(f"{num_links} links found.")

def get_all_urls(url: str, playwright: Playwright, num_pages: int):

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    context.add_cookies(COOKIES)

    page.goto(url)

    page.wait_for_load_state("load")
    sleep(3)

    page.evaluate('document.querySelector("li.listItem.fl.listItem2").click()')  # 点击 "近7天"

    links = []  # 用来存储提取的链接

    for i in range(num_pages):
        get_all_links(page, links, context)
        page.evaluate('document.querySelector("div.next.fr").click()')               # 点击 "下一页"
        print(f"Page {i + 1} processed.")

    print(f"Find {len(links)} records in total.")

    # Close page
    page.close()
    # ---------------------
    context.close()
    browser.close()

    return links
