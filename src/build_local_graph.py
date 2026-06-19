# src/build_local_graph.py
import networkx as nx
from typing import Dict, Any, List


def build_local_case_graph(
    case: Dict[str, Any],
    articles: List[Dict],
    persons: List[Dict],
) -> nx.DiGraph:
    """
    Локальный ориентированный граф для одного дела.

    Узлы: Case, Article, Person
    Рёбра:
      - Case -> Article (INVOLVES_ARTICLE)
      - Case -> Person (ACCUSED_IN)
    """
    G = nx.DiGraph()

    case_id = case.get("case_id", "UNKNOWN_CASE")
    G.add_node(case_id, label="Case", type="Case")

    # Статьи
    for art in articles:
        for num in art.get("article_numbers", []):
            article_node = f"UK_{num}"
            if not G.has_node(article_node):
                G.add_node(article_node, label=f"Article {num}", type="Article")
            G.add_edge(case_id, article_node, type="INVOLVES_ARTICLE")

    # Персоны: коорсируем по normalized
    for person in persons:
        raw_name = person["text"]
        norm_name = person.get("normalized") or raw_name

        person_node = f"Person::{norm_name}"
        if not G.has_node(person_node):
            G.add_node(
                person_node,
                label=raw_name,
                normalized_name=norm_name,
                type="Person",
            )

        if not G.has_edge(case_id, person_node):
            G.add_edge(case_id, person_node, type="ACCUSED_IN")

    return G
