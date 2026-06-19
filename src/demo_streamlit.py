import json
from pathlib import Path

import networkx as nx
import streamlit as st
from pyvis.network import Network

from load_cases import load_cases
from regex_ner_articles import extract_articles
from regex_ner_persons import extract_persons
from build_local_graph import build_local_case_graph


def main() -> None:
    st.title("LegalGraph-RU: демо графа уголовных дел")

    cases = load_cases()
    if not cases:
        st.error("Не найдены JSON-файлы в data/sample_cases.")
        return

    case_id_to_case = {c["case_id"]: c for c in cases}

    case_ids = [c["case_id"] for c in cases]
    selected_case_id = st.selectbox("Выберите дело", case_ids)

    case = case_id_to_case[selected_case_id]

    st.subheader("Метаданные дела")
    st.json(
        {
            "case_id": case["case_id"],
            "case_number": case.get("case_number"),
            "court": case.get("court"),
        }
    )

    st.subheader("Фрагмент текста")
    st.text(case.get("text", "")[:2000])

    articles = extract_articles(case.get("text", ""))
    persons = extract_persons(case.get("text", ""))

    st.subheader("Извлечённые статьи УК")
    st.write(articles)

    st.subheader("Извлечённые лица")
    st.write(persons)

    st.subheader("Локальный граф дела")
    G = build_local_case_graph(case, articles, persons)

    # PyVis-граф; notebook=False, чтобы не было ошибки template.render
    net = Network(height="500px", width="100%", directed=True, notebook=False)
    net.from_nx(G)

    html_path = Path("output") / "local_graph.html"
    html_path.parent.mkdir(exist_ok=True)

    net.write_html(str(html_path), open_browser=False, notebook=False)

    # Встраиваем HTML-граф через iframe (новый рекомендованный способ)
    st.iframe(str(html_path), height=500)


if __name__ == "__main__":
    main()