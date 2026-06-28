"""Search Tool — Web search via DuckDuckGo for competitor/market intelligence."""

from __future__ import annotations

from app.core.logging import logger


class SearchTool:
    """Web search using DuckDuckGo for market intelligence."""

    async def web_search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search the web using DuckDuckGo."""
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "href": r.get("href", ""),
                    })

            logger.info(f"Web search: '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            return [{"title": "Search unavailable", "body": str(e), "href": ""}]
