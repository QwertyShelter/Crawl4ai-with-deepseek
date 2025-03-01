import json
from typing import List, Set, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy
)

from models.project import Project
from utils.data_utils import is_complete_project, is_duplicate_project


def get_browser_config() -> BrowserConfig:
    # Setting the config of the browser
    return BrowserConfig(
        browser_type="chromium",  # Type of browser to simulate
        headless=False,           # Whether to run in headless mode (no GUI)
        verbose=True,             # Enable verbose logging
        # proxy="http://127.0.0.1:7890"  # Using proxy server
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    # Setting the config of the LLM
    return LLMExtractionStrategy(
        provider="ollama/deepseek-r1:latest",   # Name of the LLM provider
        api_token="none",                       # API token for the LLM provider (if required)
        schema=Project.model_json_schema(),     # JSON schema of the data model
        extraction_type="schema",               # Type of extraction to perform
        instruction=(
            "接下来我将提供从一个关于 '睡眠检测' 项目的招标网页, 您需要从中提炼以下信息: "
            "包括项目的名称 (name, 该项必须包含, 是最终数据的主键之一); 项目价格 (price, 如果有的话); "
            "报名时间 (bidding_time, 如果有的话); 中标时间 (winning_time, 如果项目已经中标的话); "
            "废标时间 (scrapping_time, 如果项目已经废标的话); 以及项目详细的具体要求 "
            "(description, 除项目名称, 时间, 价格方面以外的其他具体要求, 让我知道应该如何为这个项目准备, 同样是最终数据的主键之一)."
            "请注意, 您所提炼的文本最终要是UTF-8并且是中文格式的."
        ),                                      # Instructions for the LLM
        input_format="markdown",                # Format of the input content
        extra_args={"temperature": 0.0},        # Additional arguments
        verbose=True,                           # Enable verbose logging
    )

async def fetch_and_process_page(
    url: str,
    tag: str,
    crawler: AsyncWebCrawler,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str]
) -> Tuple[List[dict], bool]:

    print(f"Loading page {url}...")

    # Fetch page content with the extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,                    # Do not use cached data
            # extraction_strategy=JsonCssExtractionStrategy(SCHEMA, verbose=True),
            extraction_strategy=llm_strategy,               # Strategy for data extraction
            css_selector=css_selector,                      # Target specific content on the page
            session_id=session_id,                          # Unique session ID for the crawl
        ),
    )

    if not (result.success and result.extracted_content):
        print(f"Error fetching page {url}: {result.error_message}")
        return [], False

    # Parse extracted content
    extracted_data = json.loads(result.extracted_content)
    if not extracted_data:
        print(f"No project found on page {url}.")
        return [], False

    # After parsing extracted content
    print("Extracted data:", extracted_data)

    # Process venues
    complete_projects = []
    for project in extracted_data:
        # Debugging: Print each venue to understand its structure
        print("Processing venue:", project)

        # Ignore the 'error' key if it's False
        if project.get("error") is False:
            project.pop("error", None)  # Remove the 'error' key if it's False

        if not is_complete_project(project, required_keys):
            continue  # Skip incomplete venues

        if is_duplicate_project(project["name"] + tag, seen_names):
            print(f"Duplicate venue '{project['name']}' found. Skipping.")
            continue  # Skip duplicate venues

        # Add venue to the list
        seen_names.add(project["name"] + tag)
        complete_projects.append(project)

    if not complete_projects:
        print(f"No complete venues found on page {url}.")
        return [], False

    print(f"Extracted {len(complete_projects)} venues from page {url}.")
    return complete_projects, False  # Continue crawling
