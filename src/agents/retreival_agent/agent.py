from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain.tools import tool

from config.logger import get_logger
from rag.laws_rag.retreival import retrieval_pipeline as laws_retrieval_pipeline
from rag.policies_rag.retreival import (
    retrieval_pipeline as policies_retrieval_pipeline,
)
from agents.retreival_agent.prompt import build_user_prompt


logger = get_logger(__name__)


MAX_CONTENT_CHARS = 800
QUERY_SPLIT_THRESHOLD = 320
QUERY_PART_MAX = 280


def _truncate(text: str, limit: int = MAX_CONTENT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _format_documents(
    documents: List[object],
    source: str,
    query_part: str,
) -> List[Dict[str, Any]]:
    results = []
    for doc in documents:
        metadata = getattr(doc, "metadata", {})
        page_content = getattr(doc, "page_content", "")
        results.append(
            {
                "content": _truncate(page_content),
                "metadata": metadata,
                "source": source,
                "query_part": query_part,
            }
        )
    return results


@tool("laws_rag_search")
def laws_rag_search(query: str, k: int = 4) -> List[Dict[str, Any]]:
    """Search the laws RAG index for relevant passages."""
    logger.info("Searching laws RAG for query: %s", query)
    documents = laws_retrieval_pipeline(query, k=k)
    return _format_documents(documents, source="laws", query_part=query)


@tool("policies_rag_search")
def policies_rag_search(query: str, k: int = 4) -> List[Dict[str, Any]]:
    """Search the policies RAG index for relevant passages."""
    logger.info("Searching policies RAG for query: %s", query)
    documents = policies_retrieval_pipeline(query, k=k)
    return _format_documents(documents, source="policies", query_part=query)


def _split_query(user_query: str) -> List[str]:
    query = user_query.strip()
    if len(query) <= QUERY_SPLIT_THRESHOLD:
        return [query]

    parts = []
    buffer = ""
    for chunk in query.replace("?", ".").replace("!", ".").split("."):
        chunk = chunk.strip()
        if not chunk:
            continue
        if len(chunk) > QUERY_PART_MAX:
            for start in range(0, len(chunk), QUERY_PART_MAX):
                parts.append(chunk[start : start + QUERY_PART_MAX])
            buffer = ""
            continue
        candidate = f"{buffer} {chunk}".strip() if buffer else chunk
        if len(candidate) <= QUERY_PART_MAX:
            buffer = candidate
            continue
        if buffer:
            parts.append(buffer)
        buffer = chunk
    if buffer:
        parts.append(buffer)

    if not parts:
        return [query[:QUERY_PART_MAX]]
    return parts


def _normalize_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for item in results:
        normalized.append(
            {
                "content": _truncate(str(item.get("content", ""))),
                "metadata": item.get("metadata", {}),
                "source": item.get("source", ""),
                "query_part": item.get("query_part", ""),
            }
        )
    return normalized


def _dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique = []
    for item in results:
        key = (
            item.get("content", ""),
            json.dumps(item.get("metadata", {}), sort_keys=True),
            item.get("source", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


class RetrievalAgent:
    """Retrieve relevant policy and law passages for a query."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)


    def retrieve(self, user_query: str, k: int = 4) -> str:
        """Return structured retrieval results from laws and policies."""
        prompt = build_user_prompt(user_query)
        self.logger.info("Retrieval request: %s", prompt)

        query_parts = _split_query(user_query)
        results: List[Dict[str, Any]] = []

        for part in query_parts:
            results.extend(laws_rag_search.invoke({"query": part, "k": k}))
            results.extend(policies_rag_search.invoke({"query": part, "k": k}))

        results = _normalize_results(results)
        results = _dedupe_results(results)
        payload = {
            "query": user_query,
            "parts": query_parts,
            "results": results,
            "count": len(results),
        }
        return json.dumps(payload, indent=2, ensure_ascii=True)
