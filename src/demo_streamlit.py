from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from load_cases import load_cases
from regex_ner_articles import extract_articles
from regex_ner_persons import extract_persons
from build_local_graph import build_local_case_graph


def main() -> None:
    st.set_page_config(page_title="LegalGraph-RU", layout="wide")

    st.title("LegalGraph-RU: демо графа уголовных дел")
    st.caption(
        "Локальный режим: документы и граф строятся из JSON-файлов "
        "и не требуют подключения к Neo4j."
    )

    cases = load_cases()
    if not cases:
        st.error("Не найдены JSON-файлы в data/sample_cases.")
        return

    case_id_to_case = {case["case_id"]: case for case in cases}
    case_ids = [case["case_id"] for case in cases]

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
    graph = build_local_case_graph(case, articles, persons)

    # inline делает HTML самодостаточным:
    # vis.js и CSS включаются в файл, а не ищутся в папке lib/.
    network = Network(
        height="520px",
        width="100%",
        directed=True,
        notebook=False,
        cdn_resources="in_line",
    )
    network.from_nx(graph)

    html_path = Path("output") / "local_graph.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    network.write_html(str(html_path), open_browser=False, notebook=False)

    # Встраиваем содержимое HTML, а не строковый путь к файлу.
    html = html_path.read_text(encoding="utf-8")
    components.html(html, height=540, scrolling=False)

    st.info(
        "Neo4j является дополнительным режимом для глобального поиска "
        "и метрик. Этот локальный граф работает без Neo4j."
    )


if __name__ == "__main__":
    main()
