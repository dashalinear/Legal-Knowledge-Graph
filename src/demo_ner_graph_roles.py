#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsNERTagger,
    Doc,
    NamesExtractor,
)

# Built-in fallback extractor for Criminal Code of the Russian Federation articles.
RE_UK_ARTICLE = re.compile(
    r"(?:\u0447\.\s*\d+\s*)?(?:\u0441\u0442\.|\u0441\u0442\u0430\u0442\u044c\u044f)\s*\d+(?:\.\d+)?(?:\s*\u0423\u041a\s*\u0420\u0424)?",
    flags=re.IGNORECASE,
)


def extract_articles_v2(text: str):
    matches = RE_UK_ARTICLE.findall(text or "")
    return list(dict.fromkeys(" ".join(item.split()) for item in matches))


# ═════════════════════════════════════════════════════════════════════
# NATASHA
# ═════════════════════════════════════════════════════════════════════

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)
names_extractor = NamesExtractor(morph_vocab)


# ═════════════════════════════════════════════════════════════════════
# REGEX
# ═════════════════════════════════════════════════════════════════════

RE_COURT = re.compile(
    r"([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁа-яё]+){0,5}\s+суд)",
    re.UNICODE
)

RE_PROSECUTOR = re.compile(
    r"(?:прокурор|прокурора|государственного обвинителя|гособвинителя|помощника прокурора)"
    r"[^,;:\n]{0,80}\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})",
    re.UNICODE | re.IGNORECASE,
)

RE_DEFENDER = re.compile(
    r"(?:адвокат|защитник|защитника\s*[–-]?\s*адвоката)"
    r"[^,;:\n]{0,80}\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})",
    re.UNICODE | re.IGNORECASE,
)

RE_SECRETARY = re.compile(
    r"(?:при\s+секретаре\s+судебного\s+заседания|секретаре\s+судебного\s+заседания|секретарь\s+судебного\s+заседания)"
    r"[^,;:\n]{0,80}\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})",
    re.UNICODE | re.IGNORECASE,
)

RE_ACCUSED = re.compile(
    r"(?:в\s+отношении|обвиняем\w*|подсудим\w*|осужд[её]н\w*)\s+"
    r"([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})",
    re.UNICODE | re.IGNORECASE,
)

RE_VICTIM = re.compile(
    r"(?:потерпевш[а-яё]*|пострадавш[а-яё]*)\s+"
    r"([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})",
    re.UNICODE | re.IGNORECASE,
)

COURT_NAME_WORDS = {
    "аларского", "иркутского", "московского", "ленинского", "октябрьского",
    "кировского", "советского", "центрального", "заводского", "железнодорожного",
    "свердловского", "промышленного", "нижегородского", "новосибирского",
    "районного", "городского", "областного", "краевого", "республиканского",
    "мирового", "арбитражного", "федерального", "военного", "апелляционного",
    "кассационного", "верховного", "конституционного", "надзорного",
    "суда", "суде", "судом", "судьи",
}

RE_JUDGE_ANCHOR = re.compile(
    r"(?:(?:[Фф]едеральный\s+)?[Сс]удь[яёеи]\w*|[Пп]редседательствующ\w+|[Пп]од\s+председательством\s+судьи)"
    r"(?:\s+единолично)?(.{0,120})",
    re.UNICODE,
)

RE_NAME_IN_TAIL = re.compile(
    r"[А-ЯЁ][а-яё-]+(?:\s+(?:[А-ЯЁ]\.){1,2})?",
    re.UNICODE,
)


# ═════════════════════════════════════════════════════════════════════
# EXAMPLES
# ═════════════════════════════════════════════════════════════════════

EXAMPLE_TEXTS = [
    {
        "id": "case_1",
        "title": "Пример 1 — кража",
        "text": (
            "Аларский районный суд рассмотрел уголовное дело в отношении "
            "Федорова Алексея Алексеевича. "
            "Председательствующий судья Иванов И.И. "
            "С участием государственного обвинителя Петрова П.П., "
            "адвоката Сидорова С.С., "
            "при секретаре судебного заседания Кузнецовой А.А. "
            "Потерпевший Смирнов С.В. "
            "Действия подсудимого квалифицированы по ст. 158 УК РФ."
        ),
    },
    {
        "id": "case_2",
        "title": "Пример 2 — причинение вреда здоровью",
        "text": (
            "Московский городской суд в составе судьи Орлова О.О. "
            "рассмотрел материалы дела по обвинению Васильева Ивана Петровича. "
            "Прокурор Николаев Н.Н., защитник адвокат Егоров Е.Е. "
            "Потерпевшая Федорова М.А. "
            "Суд квалифицировал деяние по ст. 111 УК РФ."
        ),
    },
]


# ═════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════

def unique_nonempty(items):
    seen = set()
    result = []
    for item in items:
        val = str(item or "").strip()
        if not val:
            continue
        if val not in seen:
            seen.add(val)
            result.append(val)
    return result


def extract_matches(pattern, text):
    results = []
    for m in pattern.finditer(text):
        try:
            val = m.group(1).strip()
            if len(val) > 2:
                results.append(val)
        except Exception:
            pass
    return unique_nonempty(results)


def clean_person_value(val: str) -> str:
    val = str(val or "").strip(" ,.;:()[]\"'«»")
    val = re.sub(r"\s+", " ", val)
    return val


# ═════════════════════════════════════════════════════════════════════
# CORE EXTRACTORS
# ═════════════════════════════════════════════════════════════════════

def extract_articles(text):
    try:
        return extract_articles_v2(text)
    except Exception:
        return []


def extract_court_name(text: str) -> str:
    m = RE_COURT.search(text)
    if m:
        return m.group(1).strip()
    return ""


def extract_persons_natasha(text: str):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)

    persons = []
    seen = set()

    for span in doc.spans:
        if span.type != "PER":
            continue

        try:
            span.normalize(morph_vocab)
        except Exception:
            pass

        try:
            span.extract_fact(names_extractor)
        except Exception:
            pass

        val = (getattr(span, "normal", None) or span.text or "").strip()
        val = clean_person_value(val)

        if not val:
            continue

        if val not in seen:
            seen.add(val)
            persons.append(val)

    return persons


def extract_judge_names(text: str):
    seen = set()
    results = []

    for m in RE_JUDGE_ANCHOR.finditer(text):
        tail = m.group(1)

        for nm in RE_NAME_IN_TAIL.finditer(tail):
            val = nm.group(0).strip()
            surname_lower = val.split()[0].lower()

            if surname_lower in COURT_NAME_WORDS:
                continue

            val = re.sub(r"\s+[А-ЯЁ][а-яё]{2,}$", "", val).strip()
            val = clean_person_value(val)

            if val and val not in seen:
                seen.add(val)
                results.append(val)
                break

    return results


def extract_person_roles(text: str):
    results = []

    for judge_name in extract_judge_names(text):
        results.append({"role": "JUDGE", "text": judge_name})

    for m in RE_PROSECUTOR.finditer(text):
        results.append({"role": "PROSECUTOR", "text": clean_person_value(m.group(1))})

    for m in RE_DEFENDER.finditer(text):
        results.append({"role": "DEFENDER", "text": clean_person_value(m.group(1))})

    for m in RE_SECRETARY.finditer(text):
        results.append({"role": "SECRETARY", "text": clean_person_value(m.group(1))})

    for m in RE_ACCUSED.finditer(text):
        results.append({"role": "ACCUSED", "text": clean_person_value(m.group(1))})

    for m in RE_VICTIM.finditer(text):
        results.append({"role": "VICTIM", "text": clean_person_value(m.group(1))})

    cleaned = []
    seen = set()
    for item in results:
        key = (item["role"], item["text"])
        if item["text"] and key not in seen:
            seen.add(key)
            cleaned.append(item)

    return cleaned


def attach_roles_to_persons(persons, role_spans):
    role_map = {}
    for rs in role_spans:
        role_map.setdefault(rs["text"], []).append(rs["role"])

    result = []
    used = set()

    for p in persons:
        assigned = False

        for role_text, roles in role_map.items():
            if p == role_text or p in role_text or role_text in p:
                for role in roles:
                    key = (p, role)
                    if key not in used:
                        used.add(key)
                        result.append({"text": p, "role": role})
                assigned = True

        if not assigned:
            key = (p, "UNKNOWN")
            if key not in used:
                used.add(key)
                result.append({"text": p, "role": "UNKNOWN"})

    for rs in role_spans:
        key = (rs["text"], rs["role"])
        if key not in used:
            used.add(key)
            result.append({"text": rs["text"], "role": rs["role"]})

    dedup = []
    seen = set()
    for item in result:
        key = (item["text"], item["role"])
        if key not in seen:
            seen.add(key)
            dedup.append(item)

    return dedup


# ═════════════════════════════════════════════════════════════════════
# GRAPH
# ═════════════════════════════════════════════════════════════════════

ROLE_COLORS = {
    "CASE": "#dfe7fd",
    "COURT": "#fde2e4",
    "ARTICLE": "#e2f0cb",
    "JUDGE": "#cde7ff",
    "PROSECUTOR": "#fff1c1",
    "DEFENDER": "#e8d5ff",
    "SECRETARY": "#ffd6e0",
    "ACCUSED": "#ffc9c9",
    "VICTIM": "#d3f8d3",
    "UNKNOWN": "#eeeeee",
}


def build_case_graph(case_id, articles, persons_with_roles, court):
    G = nx.Graph()

    case_node = f"CASE::{case_id}"
    G.add_node(case_node, label=case_id, role="CASE", color=ROLE_COLORS["CASE"])

    if court:
        court_node = f"COURT::{court}"
        G.add_node(court_node, label=court, role="COURT", color=ROLE_COLORS["COURT"])
        G.add_edge(case_node, court_node, rel="HEARD_BY")

    for a in articles or []:
        if isinstance(a, dict):
            art_text = a.get("text") or a.get("article_num")
        else:
            art_text = str(a)

        art_text = str(art_text or "").strip()
        if not art_text:
            continue

        art_node = f"ARTICLE::{art_text}"
        G.add_node(art_node, label=f"ст. {art_text}", role="ARTICLE", color=ROLE_COLORS["ARTICLE"])
        G.add_edge(case_node, art_node, rel="INVOLVES_ARTICLE")

    for p in persons_with_roles or []:
        name = str(p.get("text", "")).strip()
        role = str(p.get("role", "UNKNOWN")).upper().strip() or "UNKNOWN"

        if not name:
            continue

        node_id = f"PERSON::{role}::{name}"
        color = ROLE_COLORS.get(role, ROLE_COLORS["UNKNOWN"])
        G.add_node(node_id, label=name, role=role, color=color)
        G.add_edge(case_node, node_id, rel=role)

    return G


def visualize_graph(G, case_id, graph_path):
    try:
        if G is None or len(G.nodes) == 0:
            return False

        graph_path = Path(graph_path)
        graph_path.parent.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, seed=42, k=1.2)

        node_colors = [G.nodes[n].get("color", "#cccccc") for n in G.nodes]
        labels = {n: G.nodes[n].get("label", n) for n in G.nodes}

        nx.draw(
            G,
            pos,
            labels=labels,
            with_labels=True,
            node_color=node_colors,
            node_size=2200,
            font_size=9,
            font_weight="bold",
            edge_color="#888888",
            width=1.5,
        )

        plt.title(f"Role-aware local graph: {case_id}", fontsize=14)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(graph_path, dpi=220, bbox_inches="tight")
        plt.close()
        return True
    except Exception:
        plt.close("all")
        return False


# ═════════════════════════════════════════════════════════════════════
# LOCAL DEBUG
# ═════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sample = EXAMPLE_TEXTS[0]["text"]

    print("COURT:", extract_court_name(sample))
    print("ARTICLES:", extract_articles(sample))
    print("PERSONS:", extract_persons_natasha(sample))
    print("ROLES:", extract_person_roles(sample))

    persons = extract_persons_natasha(sample)
    roles = extract_person_roles(sample)
    persons_with_roles = attach_roles_to_persons(persons, roles)

    print("PERSONS WITH ROLES:", persons_with_roles)

    outdir = Path("output") / "streamlit_demo"
    outdir.mkdir(parents=True, exist_ok=True)
    graph_path = outdir / "demo_case_roles.png"

    G = build_case_graph("demo_case", extract_articles(sample), persons_with_roles, extract_court_name(sample))
    ok = visualize_graph(G, "demo_case", graph_path)
    print("GRAPH OK:", ok, graph_path)