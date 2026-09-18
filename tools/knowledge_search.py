
from pathlib import Path
import json
import re

from langchain.tools import tool


KNOWLEDGE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "knowledge_base.json"
)

STOP_WORDS = {
    "how", "do", "i", "my", "the", "a", "an",
    "is", "what", "can", "to", "for", "of", "and",
    "please", "me", "our", "we", "on", "in",
    "does", "it", "this", "that", "with"
}


def _tokenize(text: str) -> set[str]:
    """Convert text into lowercase searchable words."""
    text = text.lower().replace("-", " ")
    return set(re.findall(r"\b[a-z0-9]+\b", text))


@tool
def search_knowledge(query: str) -> list[dict]:
    """
    Search the local IT knowledge base.

    Use this tool for IT procedures, troubleshooting, and
    information available in the local knowledge base.
    """

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        knowledge_base = json.load(file)

    query_words = _tokenize(query) - STOP_WORDS

    if not query_words:
        return []

    scored_results = []

    for article in knowledge_base:
        searchable_text = " ".join(
            [
                article["title"],
                article["category"],
                article["content"],
            ]
        )

        article_words = _tokenize(searchable_text)

        matched_words = query_words.intersection(article_words)
        score = len(matched_words)

        if score >= 2:
            scored_results.append((score, article))

    scored_results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    # Return the strongest match first.
    if not scored_results:
      return [
        {
            "id": "NO_RESULT",
            "title": "No matching information found",
            "category": "System",
            "content": (
                "No relevant information was found in the "
                "available IT knowledge base."
            )
        }
      ]

    return [
        article
        for _, article in scored_results[:3]
    ]
