# src/regex_ner_persons.py
import re
from typing import List, Dict


# Простой шаблон ФИО: "Иванов Иван Иванович" или "Иванов И. И."
PERSON_PATTERN = re.compile(
    r"\b([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+\.?|[А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+\.?)?",
    re.UNICODE,
)


def _normalize_surname(surname: str) -> str:
    """
    Грубая нормализация фамилии:
    - приводит к И.п. мужского рода: Федоров, Иванов, Петров и т.п.
    - работает по типичным русским окончаниям.
    Это не морфология, но уже склеит:
      Федорова, Федорову, Федоровым, Федорове → Федоров
    """
    s = surname.strip()

    # если совсем коротко — не трогаем
    if len(s) <= 4:
        return s

    low = s.lower()

    # частые падежные окончания жен./муж. фамилий
    for suf in ("ова", "овой", "ову", "овой", "ову", "овой", "ову", "ову", "овой"):
        if low.endswith(suf):
            # "Федорова" -> "Федоров"
            return s[:-1]

    # общие падежные окончания -а, -у, -ой, -ым, -ом, -е
    for suf in ("ыми", "ыми", "ами", "ями", "его", "ему", "ими", "ами", "ями"):
        if low.endswith(suf):
            # ничего умного не делаем — возвращаем как есть
            return s

    for suf in ("ой", "ый", "им", "ым", "ом", "ем", "ам", "ям", "ах", "ях", "ей", "ою", "ею"):
        if low.endswith(suf) and len(s) > 5:
            # пробуем откусить падежное окончание до основы
            return s[:-2]

    for suf in ("а", "у", "е", "ы", "и", "о"):
        if low.endswith(suf) and len(s) > 5:
            return s[:-1]

    return s


def normalize_person(text: str) -> str:
    """
    Нормализация ФИО для ключа в графе:
    - нормализуем только фамилию, остальное оставляем как есть.
    """
    parts = text.split()
    if not parts:
        return text.strip()

    surname = parts[0]
    norm_surname = _normalize_surname(surname)

    rest = " ".join(parts[1:])
    if rest:
        return f"{norm_surname} {rest}"
    return norm_surname


def extract_persons(text: str) -> List[Dict]:
    """
    Извлечь персон и одновременно вернуть нормализованное имя
    для использования как ключа в графе.
    """
    persons: List[Dict] = []
    for match in PERSON_PATTERN.finditer(text):
        span = match.span()
        raw = match.group(0).strip()
        normalized = normalize_person(raw)

        persons.append(
            {
                "text": raw,          # как в тексте
                "normalized": normalized,  # ключ для графа
                "start": span[0],
                "end": span[1],
            }
        )
    return persons
