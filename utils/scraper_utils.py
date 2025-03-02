import json
from typing import List, Set, Tuple
from config import COOKIES, API_KEY

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy
)

from models.project import Project_base, Project_adv
from utils.data_utils import is_complete_project, is_duplicate_project


def get_browser_config() -> BrowserConfig:
    # Setting the config of the browser
    return BrowserConfig(
        browser_type="chromium",  # Type of browser to simulate
        headless=False,           # Whether to run in headless mode (no GUI)
        verbose=True,             # Enable verbose logging
        # proxy="http://127.0.0.1:7890"  # Using proxy server
        cookies=COOKIES
    )


def get_llm_base() -> LLMExtractionStrategy:
    # Setting the config of the LLM
    return LLMExtractionStrategy(
        provider="ollama/deepseek-r1:latest",   # Name of the LLM provider
        # api_token=API_KEY,                      # API token for the LLM provider (if required)
        schema=Project_base.model_json_schema(),# JSON schema of the data model
        extraction_type="schema",               # Type of extraction to perform
        instruction=(
            "接下来我将提供从一个关于 '睡眠检测' 项目的招标网页上提炼的 markdown 数据, 您需要从中提炼以下信息: "
            "包括项目的名称 (Title, 该项必须包含, 是最终数据的主键之一, 位于 markdown 第一行信息); "
            "招标编号/项目编号 (No, 一个正确的编号应该同时包含字母和数字, 您所提取的编号必须是同时包含符号和数字的); "
            "招标公司 (Company, 该项必须包含, UTF-8 中文编码); 项目总价/招标估价 (price); "
            "项目所在地 (Location, 如果没有直接给出的话, 您可以根据公司名称推断, 精确到省份即可); "
        ),                                      # Instructions for the LLM
        input_format="markdown",                # Format of the input content
        extra_args={"temperature": 0.0},        # Additional arguments
        verbose=True,                           # Enable verbose logging
        # proxy="http://127.0.0.1:7890"
    )

def get_llm_adv() -> LLMExtractionStrategy:
    # Setting the config of the LLM
    return LLMExtractionStrategy(
        provider="ollama/deepseek-r1:latest",   # Name of the LLM provider
        # api_token=API_KEY,                    # API token for the LLM provider (if required)
        schema=Project_adv.model_json_schema(), # JSON schema of the data model
        extraction_type="schema",               # Type of extraction to perform
        instruction=(
            "接下来我将提供从一个关于 '睡眠检测' 项目的招标网页上提炼的 markdown 数据, 您需要从中提炼以下信息: "
            "所用仪器的品牌 (Brand, 如果有的话); "
            "所需要的仪器名称 (Model, 如果有的话); "
            "以及如果该项目已经中标, 请帮我提炼出中标的时间 (Winning_time)."
            "请注意, 您所提炼的文本最终要是UTF-8并且是中文格式的."
        ),                                      # Instructions for the LLM
        input_format="markdown",                # Format of the input content
        extra_args={"temperature": 0.0},        # Additional arguments
        verbose=True,                           # Enable verbose logging
        # proxy="http://127.0.0.1:7890"
    )

async def fetch_and_process_page(
    url: str,
    crawler: AsyncWebCrawler,
    css_selector: List[str],
    llm_strategy: List[LLMExtractionStrategy],
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str]
) -> dict:

    print(f"Loading page {url}...")

    # Fetch page content with the extraction strategy
    result1 = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,                    # Do not use cached data
            # extraction_strategy=JsonCssExtractionStrategy(SCHEMA, verbose=True),
            extraction_strategy=llm_strategy[0],            # Strategy for data extraction
            css_selector=css_selector[0],                   # Target specific content on the page
            session_id=session_id,                          # Unique session ID for the crawl
        ),
    )

    result2 = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,                    # Do not use cached data
            # extraction_strategy=JsonCssExtractionStrategy(SCHEMA, verbose=True),
            extraction_strategy=llm_strategy[1],            # Strategy for data extraction
            css_selector=css_selector[1],                   # Target specific content on the page
            session_id=session_id,                          # Unique session ID for the crawl
        ),
    )

    if not (result1.success and result1.extracted_content and json.loads(result1.extracted_content)):
        print(f"Error fetching page {url}: {result1.error_message}")
        return {}
    
    extracted_data = json.loads(result1.extracted_content)[0]

    # Parse extracted content
    if not (result2.success and json.loads(result2.extracted_content)):
        extracted_data.update({'Brand': '', 'Model': '', 'Winning_time': ''})
    else:
        extracted_data.update(json.loads(result2.extracted_content)[0])

    if not extracted_data:
        print(f"No project found on page {url}.")
        return {}

    # After parsing extracted content
    print("Extracted data:", extracted_data)

    # Process venues

    # Ignore the 'error' key if it's False
    if extracted_data.get("error") is False:
        extracted_data.pop("error", None)  # Remove the 'error' key if it's False

    if not is_complete_project(extracted_data, required_keys):
        return {}         # Skip incomplete venues

    if is_duplicate_project(extracted_data["Title"], seen_names):
        print(f"Duplicate venue '{extracted_data['Title']}' found. Skipping.")
        return {}         # Skip duplicate venues

    # Add venue to the list
    seen_names.add(extracted_data["Title"])

    return extracted_data         # Continue crawling
