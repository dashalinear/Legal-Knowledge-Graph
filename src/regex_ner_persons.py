import re
from typing import List, Dict

# Very simple FIO pattern: "Иванов Иван Иванович" or "Иванов И. И."
PERSON_PATTERN = re.compile(
    r"\b([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+\.?|[А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+\.?)?",
    re.UNICODE,
)


def extract_persons(text: str) -> List[Dict]:
    """Extract person names from text using a simple regex fallback pattern."""
    persons: List[Dict] = []
    for match in PERSON_PATTERN.finditer(text):
        span = match.span()
        persons.append(
            {
                "text": match.group(0),
                "start": span[0],
                "end": span[1],
            }
        )
    return persons