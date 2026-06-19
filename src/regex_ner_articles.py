import re
from typing import List, Dict


# Regex rules focus on common Russian Criminal Code citation patterns.
ARTICLE_PATTERNS = [
    # ст. 228 ч. 2
    r"(ст\.?\s*(\d{1,3})\s*ч\.?\s*(\d{1,2})(?:\s*п\.?\s*[а-я])?)",
    # часть 2 статьи 228
    r"(част[ьяи]\s*(\d{1,2})\s*стать[ьи]\s*(\d{1,3}))",
    # статьи 111 и 119
    r"(статьи?\s*(\d{1,3})(?:\s*и\s*(\d{1,3}))?)",
]


def extract_articles(text: str) -> List[Dict]:
    """Extract Criminal Code articles from a given text using regex patterns."""
    matches: List[Dict] = []
    for pattern in ARTICLE_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            span = match.span()
            matches.append(
                {
                    "text": match.group(0),
                    "start": span[0],
                    "end": span[1],
                    "article_numbers": [
                        g for g in match.groups()[1:] if g is not None
                    ],
                }
            )
    return matches