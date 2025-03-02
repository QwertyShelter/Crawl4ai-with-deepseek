import asyncio
import os
from crawl4ai import AsyncWebCrawler
from playwright.sync_api import sync_playwright

from config import CSS_SELECTOR, REQUIRED_KEYS, BASE_URL
from utils.data_utils import (
    save_projects_to_csv,
)
from utils.scraper_utils import (
    fetch_and_process_page,
    get_browser_config,
    get_llm_base,
    get_llm_adv
)
from utils.playwright_utils import get_all_urls

async def crawl_projects(urls: list):
    # Initialize configurations
    # browser_config = get_browser_config()
    llm_strategy = [get_llm_base(), get_llm_adv()]
    session_id = "project_crawl_session"

    # Initialize state variables
    all_projects = []
    seen_names = set()

    # Start the web crawler context
    async with AsyncWebCrawler(#config=browser_config
        ) as crawler:
        for url in urls:
            # Fetch and process data from the current page
            project = await fetch_and_process_page(
                url,
                crawler,
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS,
                seen_names,
            )

            if not project:
                print(f"No projects extracted from page {url}.")
            else:
                all_projects.append(project)

            # Add the projects from this page to the total list

            # Pause between requests to be polite and avoid rate limits
            await asyncio.sleep(2)  # Adjust sleep time as needed

    # Save the collected projects to a CSV file
    if all_projects:
        save_projects_to_csv(all_projects, "Output.csv")
    else:
        print("No projects were found during the crawl.")

    # Display usage statistics for the LLM strategy
    llm_strategy[0].show_usage()
    llm_strategy[1].show_usage()

def get_all_files(directory):
    file_list = []
    for _, _, files in os.walk(directory):
        for file in files:
            file_list.append("file://download/" + file)  # 获取文件的完整路径
    return file_list

if __name__ == "__main__":
    # Get all urls
    all_urls = get_all_files("download")

    # with sync_playwright() as playwright:
    #    all_urls = get_all_urls(BASE_URL, playwright, 3)
    
    asyncio.run(crawl_projects(all_urls))