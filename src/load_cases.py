import json
from pathlib import Path
from typing import List, Dict

from config import DATA_DIR


def load_cases() -> List[Dict]:
    """Load sample criminal cases from JSON files."""
    cases: List[Dict] = []
    for path in Path(DATA_DIR).glob("*.json"):
        with path.open("r", encoding="utf-8") as f:
            cases.append(json.load(f))
    return cases