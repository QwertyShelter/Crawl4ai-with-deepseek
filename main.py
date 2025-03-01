import asyncio
from collections import defaultdict
from crawl4ai import AsyncWebCrawler
from playwright.sync_api import sync_playwright

from config import CSS_SELECTOR, REQUIRED_KEYS, BASE_URL
from utils.data_utils import (
    save_projects_to_csv,
)
from utils.scraper_utils import (
    fetch_and_process_page,
    get_browser_config,
    get_llm_strategy,
)
from utils.playwright_utils import get_all_urls

async def crawl_projects(url_tags: dict):
    # Initialize configurations
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "project_crawl_session"

    # Initialize state variables
    all_projects = defaultdict(list)
    seen_names = set()

    # Start the web crawler context
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url_tag in url_tags:
            # Fetch and process data from the current page
            projects, no_results_found = await fetch_and_process_page(
                url_tag['href'],
                url_tag['tag'],
                crawler,
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS,
                seen_names,
            )

            if no_results_found:
                print("No more projects found. Ending crawl.")

            if not projects:
                print(f"No projects extracted from page {url_tag['href']}.")

            # Add the projects from this page to the total list
            all_projects[url_tag['tag']].extend(projects)

            # Pause between requests to be polite and avoid rate limits
            await asyncio.sleep(2)  # Adjust sleep time as needed

    # Save the collected projects to a CSV file
    if all_projects:
        for tag, projects in all_projects.items():
            save_projects_to_csv(projects, tag + ".csv")
    else:
        print("No projects were found during the crawl.")

    # Display usage statistics for the LLM strategy
    llm_strategy.show_usage()


if __name__ == "__main__":
    # Get all urls
    url_tags = {}
    with sync_playwright() as playwright:
        url_tags = get_all_urls(BASE_URL, playwright, 3)
    
    asyncio.run(crawl_projects(url_tags))