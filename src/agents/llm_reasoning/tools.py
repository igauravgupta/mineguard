import re
from typing import Dict, List
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from langchain.tools import tool

from config.logger import get_logger


logger = get_logger(__name__)


def _extract_ddg_results(html: str, limit: int) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    title_pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>'
    )
    snippet_pattern = re.compile(
        r'<a[^>]*class="result__snippet"[^>]*>(?P<snippet>.*?)</a>'
    )

    titles = title_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    for index, item in enumerate(titles[:limit]):
        href, title = item
        snippet = snippets[index] if index < len(snippets) else ""
        clean_title = re.sub(r"<.*?>", "", title).strip()
        clean_snippet = re.sub(r"<.*?>", "", snippet).strip()
        results.append(
            {
                "title": clean_title,
                "url": href,
                "snippet": clean_snippet,
            }
        )
    return results


@tool("duckduckgo_search")
def duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search DuckDuckGo and return a list of results with title, url, snippet."""
    if not query.strip():
        return []

    encoded = quote_plus(query)
    url = f"https://duckduckgo.com/html/?q={encoded}"
    logger.info("Searching DuckDuckGo for query: %s", query)

    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")

    return _extract_ddg_results(html, max_results)
