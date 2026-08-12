from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pyvis.network import Network


load_dotenv()

AURA_URI = os.getenv("NEO4J_URI")
AURA_USER = os.getenv("NEO4J_USER")
AURA_PASSWORD = os.getenv("NEO4J_PASSWORD")
AURA_DATABASE = os.getenv("NEO4J_DATABASE")
ROLE_DEMO_DIR = os.getenv("ROLE_DEMO_DIR")


@st.cache_resource
def get_aura_driver():
    if not all([AURA_URI, AURA_USER, AURA_PASSWORD]):
        raise RuntimeError(
            "В .env отсутствуют NEO4J_URI, NEO4J_USER или NEO4J_PASSWORD."
        )

    driver = GraphDatabase.driver(
        AURA_URI,
        auth=(AURA_USER, AURA_PASSWORD),
    )
    driver.verify_connectivity()
    return driver


@st.cache_resource
def get_role_module():
    if not ROLE_DEMO_DIR:
        raise RuntimeError("В .env отсутствует ROLE_DEMO_DIR.")

    source_dir = Path(ROLE_DEMO_DIR)
    source_file = source_dir / "demo_ner_graph_roles.py"

    if not source_file.exists():
        raise FileNotFoundError(f"Не найден role-aware NER файл: {source_file}")

    sys.path.insert(0, str(source_dir))

    spec = importlib.util.spec_from_file_location(
        "role_ner_source",
        source_file,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("Не удалось загрузить demo_ner_graph_roles.py.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_query(cypher: str, **parameters: Any) -> list[dict[str, Any]]:
    driver = get_aura_driver()

    with driver.session(database=AURA_DATABASE or None) as session:
        result = session.run(cypher, parameters)
        return [record.data() for record in result]


@st.cache_data(ttl=60)
def get_node_metrics() -> list[dict[str, Any]]:
    return run_query(
        """
        MATCH (n)
        UNWIND labels(n) AS label
        RETURN label AS node_type, count(*) AS total
        ORDER BY total DESC
        """
    )


@st.cache_data(ttl=60)
def get_relationship_metrics() -> list[dict[str, Any]]:
    return run_query(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS relationship, count(*) AS total
        ORDER BY total DESC
        """
    )


@st.cache_data(ttl=60)
def get_articles() -> list[dict[str, Any]]:
    return run_query(
        """
        MATCH (c:Case)-[:INVOLVES_ARTICLE]->(a:Article)
        WITH toString(coalesce(a.code, a.number, a.id, a.name)) AS article,
             count(DISTINCT c) AS cases_count
        WHERE article IS NOT NULL AND article <> "null"
        RETURN article, cases_count
        ORDER BY cases_count DESC, article
        """
    )


@st.cache_data(ttl=60)
def get_cases_by_article(article: str) -> list[dict[str, Any]]:
    return run_query(
        """
        MATCH (c:Case)-[:INVOLVES_ARTICLE]->(a:Article)
        WHERE toString(coalesce(a.code, a.number, a.id, a.name)) = $article
        OPTIONAL MATCH (court:Court)-[:HEARS]->(c)

        RETURN
            c.id AS case_id,
            c.case_number AS case_number,
            c.source_file AS source_file,
            collect(DISTINCT court.name) AS courts

        ORDER BY case_id
        LIMIT 100
        """,
        article=article,
    )


@st.cache_data(ttl=60)
def get_cases_by_number(case_number: str) -> list[dict[str, Any]]:
    return run_query(
        """
        MATCH (c:Case)
        WHERE toLower(coalesce(c.case_number, ""))
              CONTAINS toLower($case_number)

        OPTIONAL MATCH (court:Court)-[:HEARS]->(c)

        RETURN
            c.id AS case_id,
            c.case_number AS case_number,
            c.source_file AS source_file,
            collect(DISTINCT court.name) AS courts

        ORDER BY case_id
        LIMIT 50
        """,
        case_number=case_number,
    )


@st.cache_data(ttl=60)
def get_case_details(case_id: str) -> dict[str, Any]:
    case_rows = run_query(
        """
        MATCH (c:Case {id: $case_id})
        RETURN properties(c) AS case_properties
        """,
        case_id=case_id,
    )

    if not case_rows:
        return {}

    people = run_query(
        """
        MATCH (p:Person)-[r:ACCUSED_IN|VICTIM_IN]->(c:Case {id: $case_id})
        RETURN p.name AS name, type(r) AS relation
        ORDER BY relation, name
        """,
        case_id=case_id,
    )

    articles = run_query(
        """
        MATCH (c:Case {id: $case_id})-[:INVOLVES_ARTICLE]->(a:Article)
        RETURN toString(coalesce(a.code, a.number, a.id, a.name)) AS article
        ORDER BY article
        """,
        case_id=case_id,
    )

    judges = run_query(
        """
        MATCH (j:Judge)-[:PRESIDES_OVER]->(c:Case {id: $case_id})
        RETURN j.name AS name
        ORDER BY name
        """,
        case_id=case_id,
    )

    courts = run_query(
        """
        MATCH (court:Court)-[:HEARS]->(c:Case {id: $case_id})
        RETURN court.name AS name
        ORDER BY name
        """,
        case_id=case_id,
    )

    verdicts = run_query(
        """
        MATCH (c:Case {id: $case_id})-[:HAS_VERDICT]->(v:Verdict)
        RETURN v.punishment_type AS punishment_type, v.raw_number AS raw_text
        """,
        case_id=case_id,
    )

    locations = run_query(
        """
        MATCH (location:Location)-[:SCENE_OF]->(c:Case {id: $case_id})
        RETURN location.name AS name
        ORDER BY name
        """,
        case_id=case_id,
    )

    regions = run_query(
        """
        MATCH (court:Court)-[:LOCATED_IN]->(region:Region)
        MATCH (court)-[:HEARS]->(c:Case {id: $case_id})
        RETURN DISTINCT region.name AS name
        ORDER BY name
        """,
        case_id=case_id,
    )

    return {
        "case_properties": case_rows[0]["case_properties"],
        "people": people,
        "articles": articles,
        "judges": judges,
        "courts": courts,
        "verdicts": verdicts,
        "locations": locations,
        "regions": regions,
    }


@st.cache_data(ttl=60)
def get_case_subgraph(case_id: str) -> list[dict[str, Any]]:
    return run_query(
        """
        MATCH (c:Case {id: $case_id})-[r]-(n)
        RETURN
            elementId(c) AS case_key,
            labels(c) AS case_labels,
            properties(c) AS case_properties,
            elementId(n) AS node_key,
            labels(n) AS node_labels,
            properties(n) AS node_properties,
            type(r) AS relationship
        LIMIT 100
        """,
        case_id=case_id,
    )


def node_color(label: str) -> str:
    colors = {
        "Case": "#2563eb",
        "Article": "#7c3aed",
        "Person": "#dc2626",
        "Judge": "#ea580c",
        "Court": "#0891b2",
        "Region": "#0f766e",
        "Location": "#16a34a",
        "CaseType": "#ca8a04",
        "Verdict": "#be123c",
    }
    return colors.get(label, "#64748b")


def node_title(labels: list[str], properties: dict[str, Any]) -> str:
    label = labels[0] if labels else "Node"

    value = (
        properties.get("name")
        or properties.get("code")
        or properties.get("case_number")
        or properties.get("id")
        or properties.get("punishment_type")
        or "без названия"
    )

    value = str(value)

    if len(value) > 45:
        value = value[:42] + "..."

    return f"{label}: {value}"


def render_aura_subgraph(case_id: str) -> None:
    rows = get_case_subgraph(case_id)

    if not rows:
        st.info("Для выбранного дела связанных узлов не найдено.")
        return

    network = Network(
        height="600px",
        width="100%",
        directed=False,
        notebook=False,
        cdn_resources="in_line",
    )

    added_nodes: set[str] = set()

    for row in rows:
        case_key = row["case_key"]
        case_labels = row["case_labels"]
        case_properties = row["case_properties"]

        if case_key not in added_nodes:
            network.add_node(
                case_key,
                label=node_title(case_labels, case_properties),
                title=str(case_properties),
                color=node_color("Case"),
                shape="box",
            )
            added_nodes.add(case_key)

        node_key = row["node_key"]
        node_labels = row["node_labels"]
        node_properties = row["node_properties"]
        node_label = node_labels[0] if node_labels else "Node"

        if node_key not in added_nodes:
            network.add_node(
                node_key,
                label=node_title(node_labels, node_properties),
                title=str(node_properties),
                color=node_color(node_label),
            )
            added_nodes.add(node_key)

        network.add_edge(
            case_key,
            node_key,
            label=row["relationship"],
            title=row["relationship"],
        )

    html = network.generate_html(notebook=False)
    st.iframe(html, height=620)


def clean_location_names(
    locations: list[str],
    people: list[dict[str, Any]],
) -> list[str]:
    bad_fragments = [
        "обращает внимание",
        "приговор",
        "в пользовании",
        "право собственности",
        "документов",
        "заключения договора",
        "неустановленного лица",
        "предварительный сговор",
        "проведена проверка",
        "выехав по заявке",
        "нахождение барж",
        "с апреля по август",
        "для того",
        "с просьбой",
        "в отношении",
        "оправдательный",
    ]

    country_values = {
        "рф",
        "россия",
        "российская федерация",
    }

    person_surnames = {
        str(row.get("name", "")).strip().lower().split()[0]
        for row in people
        if str(row.get("name", "")).strip()
    }

    result = []
    seen = set()

    for value in locations:
        location = str(value or "").strip(" ,.;:-")
        lower = location.lower()

        if not location or lower in seen:
            continue

        if lower in country_values:
            continue

        if len(location) < 3 or len(location) > 55:
            continue

        if len(location.split()) > 6:
            continue

        if any(fragment in lower for fragment in bad_fragments):
            continue

        if lower in person_surnames:
            continue

        seen.add(lower)
        result.append(location)

    return result


def deduplicate_people_by_role(
    persons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}

    noise_people = {
        "по ст",
        "по статье",
        "квалифицированы по ст",
        "квалифицированы по статье",
    }

    for person in persons:
        name = " ".join(str(person.get("text", "")).split())
        role = str(person.get("role", "PERSON"))

        if not name or name.lower() in noise_people:
            continue

        surname = name.split()[0].lower().replace(".", "")
        key = (role, surname)

        current = selected.get(key)

        if current is None:
            selected[key] = person
            continue

        current_name = " ".join(str(current.get("text", "")).split())

        if len(name.split()) > len(current_name.split()):
            selected[key] = person
        elif len(name.split()) == len(current_name.split()) and len(name) > len(current_name):
            selected[key] = person

    return list(selected.values())


def render_case_card(case_id: str) -> None:
    details = get_case_details(case_id)

    if not details:
        st.warning("Дело не найдено в AuraDB.")
        return

    case_properties = details["case_properties"]
    people = details["people"]

    accused = [
        row["name"]
        for row in people
        if row["relation"] == "ACCUSED_IN"
    ]

    victims = [
        row["name"]
        for row in people
        if row["relation"] == "VICTIM_IN"
    ]

    articles = [row["article"] for row in details["articles"]]
    judges = [row["name"] for row in details["judges"]]
    courts = [row["name"] for row in details["courts"]]
    locations_raw = [row["name"] for row in details["locations"]]
    locations = clean_location_names(locations_raw, people)
    regions = [row["name"] for row in details["regions"]]

    left_col, right_col = st.columns([1, 1.35])

    with left_col:
        st.subheader("Карточка дела")
        st.write(f"**Номер дела:** {case_properties.get('case_number') or '—'}")
        st.write(f"**Внутренний ID:** {case_id}")
        st.write(
            f"**Исходный файл:** "
            f"{case_properties.get('source_file') or '—'}"
        )
        st.write(f"**Дата:** {case_properties.get('date') or '—'}")
        st.write(
            f"**Объём документа:** "
            f"{case_properties.get('text_len') or '—'} символов"
        )
        st.write(f"**Суд:** {', '.join(courts) if courts else '—'}")
        st.write(f"**Судья:** {', '.join(judges) if judges else '—'}")
        st.write(f"**Статьи УК:** {', '.join(articles) if articles else '—'}")
        st.write(
            f"**Обвиняемые:** "
            f"{', '.join(accused) if accused else 'не извлечены'}"
        )
        st.write(
            f"**Потерпевшие:** "
            f"{', '.join(victims) if victims else 'не извлечены'}"
        )
        st.write(f"**Локации:** {', '.join(locations) if locations else '—'}")
        st.write(f"**Регионы:** {', '.join(regions) if regions else '—'}")

        verdicts = details["verdicts"]

        if verdicts:
            verdict_text = []

            for verdict in verdicts:
                value = verdict["punishment_type"] or "тип не извлечён"
                raw = verdict["raw_text"] or ""
                verdict_text.append(f"{value}: {raw}".strip(": "))

            st.write(f"**Приговор:** {'; '.join(verdict_text)}")
        else:
            st.write("**Приговор:** не извлечён")

    with right_col:
        st.subheader("Локальный граф дела")
        render_aura_subgraph(case_id)

        st.info(
            "Полный текст документа в Neo4j не хранится. "
            "В графе сохранены структурированные сущности и связи."
        )


def render_case_search() -> None:
    st.header("Карточка дела и локальный граф")
    st.caption("Поиск реального дела в Neo4j AuraDB по номеру дела.")

    query = st.text_input(
        "Введите номер дела или его фрагмент",
        placeholder="Например: 1-111/2010",
    )

    if not query.strip():
        st.info("Введите номер дела, чтобы начать поиск.")
        return

    cases = get_cases_by_number(query.strip())

    if not cases:
        st.warning("Дела с таким номером не найдены.")
        return

    options = {
        row["case_id"]: (
            f"{row['case_number'] or row['case_id']} | "
            f"{', '.join(row['courts']) if row['courts'] else 'суд не указан'}"
        )
        for row in cases
    }

    selected_case_id = st.selectbox(
        "Выберите дело",
        list(options),
        format_func=lambda value: options[value],
    )

    render_case_card(selected_case_id)


def render_article_search() -> None:
    st.header("Поиск по статье УК")

    articles = get_articles()

    if not articles:
        st.warning("Статьи УК в AuraDB не найдены.")
        return

    article_options = [row["article"] for row in articles]
    article_counts = {
        row["article"]: row["cases_count"]
        for row in articles
    }

    selected_article = st.selectbox(
        "Выберите статью",
        article_options,
        format_func=lambda value: (
            f"Статья {value} — {article_counts[value]} дел"
        ),
    )

    cases = get_cases_by_article(selected_article)

    st.caption(f"Найдено дел: {len(cases)}")

    if not cases:
        st.info("Для выбранной статьи дел не найдено.")
        return

    options = {
        row["case_id"]: (
            f"{row['case_number'] or row['case_id']} | "
            f"{', '.join(row['courts']) if row['courts'] else 'суд не указан'}"
        )
        for row in cases
    }

    selected_case_id = st.selectbox(
        "Выберите дело по статье",
        list(options),
        format_func=lambda value: options[value],
    )

    render_case_card(selected_case_id)


def render_text_analysis() -> None:
    st.header("Анализ собственного текста")
    st.caption(
        "Role-aware NER: статьи УК, участники процесса, роли, суд и локальный граф."
    )

    try:
        role_module = get_role_module()
    except Exception as exc:
        st.error("Не удалось загрузить role-aware NER модуль.")
        st.code(str(exc))
        return

    mode = st.radio(
        "Источник текста",
        ["Пример дела", "Свой текст"],
        horizontal=True,
    )

    examples = role_module.EXAMPLE_TEXTS

    if mode == "Пример дела":
        index = st.selectbox(
            "Выберите пример",
            range(len(examples)),
            format_func=lambda i: examples[i]["title"],
        )
        case = examples[index]
        case_id = case["id"]
        text = st.text_area(
            "Входной текст",
            value=case["text"],
            height=260,
        )
    else:
        case_id = st.text_input("ID нового дела", value="custom_case")
        text = st.text_area(
            "Вставьте текст судебного решения",
            height=260,
        )

    if not st.button("Запустить анализ", type="primary"):
        return

    if not text.strip():
        st.warning("Вставьте текст дела или выберите готовый пример.")
        return

    with st.spinner("Выполняется извлечение сущностей и ролей..."):
        articles = role_module.extract_articles(text)
        persons = role_module.extract_persons_natasha(text)
        role_spans = role_module.extract_person_roles(text)

        persons_with_roles = role_module.attach_roles_to_persons(
            persons,
            role_spans,
        )

        court = role_module.extract_court_name(text)

        graph = role_module.build_case_graph(
            case_id,
            articles,
            persons_with_roles,
            court,
        )

        output_dir = Path("output") / "unified_ner"
        output_dir.mkdir(parents=True, exist_ok=True)

        graph_path = output_dir / f"{case_id}_roles.png"

        graph_created = False

        if graph is not None:
            graph_created = role_module.visualize_graph(
                graph,
                case_id,
                graph_path,
            )

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Карточка дела")
        st.write(f"**ID:** {case_id}")
        st.write(f"**Суд:** {court}")

        st.write(
            f"**Статьи УК:** "
            f"{', '.join(item['text'] for item in articles) if articles else 'не извлечены'}"
        )

        st.subheader("Персоны по ролям")

        persons_with_roles = deduplicate_people_by_role(persons_with_roles)

        role_groups: dict[str, list[str]] = {}

        for person in persons_with_roles:
            role = person.get("role", "PERSON")
            role_groups.setdefault(role, []).append(person["text"])

        role_labels = {
            "ACCUSED": "Обвиняемый",
            "DEFENDANT": "Подсудимый",
            "VICTIM": "Потерпевший",
            "WITNESS": "Свидетель",
            "JUDGE": "Судья",
            "PROSECUTOR": "Прокурор",
            "SECRETARY": "Секретарь судебного заседания",
            "LAWYER": "Адвокат",
            "DEFENSE_LAWYER": "Защитник",
            "PERSON": "Персона",
        }

        if role_groups:
            for role, names in role_groups.items():
                st.markdown(f"**{role_labels.get(role, role)}**")

                for name in names:
                    st.write(f"- {name}")
        else:
            st.info("Роли не найдены.")

        st.subheader("Экспорт JSON")

        result = {
            "case_id": case_id,
            "court": court,
            "articles_found": articles,
            "persons_found": persons_with_roles,
            "role_spans_found": role_spans,
        }

        st.download_button(
            "Скачать результат JSON",
            data=__import__("json").dumps(
                result,
                ensure_ascii=False,
                indent=2,
            ),
            file_name=f"{case_id}_result.json",
            mime="application/json",
        )

    with right_col:
        st.subheader("Локальный граф")

        if graph_created and graph_path.exists():
            st.image(
                str(graph_path),
                caption=f"Role-aware graph for {case_id}",
                width="stretch",
            )
        else:
            st.warning("Граф не удалось построить.")

    with st.expander("Raw role spans"):
        if role_spans:
            st.dataframe(role_spans, width="stretch")
        else:
            st.info("Role spans не найдены.")


def render_metrics() -> None:
    st.header("Метрики графа")

    node_metrics = get_node_metrics()
    relationship_metrics = get_relationship_metrics()

    total_nodes = sum(row["total"] for row in node_metrics)
    total_relationships = sum(row["total"] for row in relationship_metrics)

    total_cases = next(
        (
            row["total"]
            for row in node_metrics
            if row["node_type"] == "Case"
        ),
        0,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Дела", total_cases)
    col2.metric("Узлы", total_nodes)
    col3.metric("Связи", total_relationships)

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Типы узлов")
        st.dataframe(
            node_metrics,
            width="stretch",
            hide_index=True,
        )

    with right_col:
        st.subheader("Типы связей")
        st.dataframe(
            relationship_metrics,
            width="stretch",
            hide_index=True,
        )

    st.subheader("Проверка реального корпуса")

    st.code(
        """
MATCH (c:Case {source_file: "5_9342e8f2_docs.json"})
RETURN count(c) AS imported_cases;
        """.strip(),
        language="cypher",
    )


def main() -> None:
    st.set_page_config(
        page_title="LegalGraph-RU",
        page_icon="⚖️",
        layout="wide",
    )

    st.title("⚖️ LegalGraph-RU")

    st.caption(
        "Role-aware NER и knowledge graph уголовных дел на базе Neo4j AuraDB."
    )

    with st.sidebar:
        st.header("Навигация")

        page = st.radio(
            "Сценарий demo",
            [
                "Карточка дела",
                "Поиск по статье УК",
                "Анализ своего текста",
                "Метрики графа",
            ],
        )

        if st.button("Обновить данные Aura"):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        try:
            get_aura_driver()
            st.success("AuraDB подключена")
        except Exception:
            st.warning(
                "AuraDB недоступна. "
                "Режим анализа собственного текста всё равно работает."
            )

        st.caption(
            "Данные Aura: реальный корпус судебных решений; "
            "локальный режим: role-aware NER."
        )

    if page == "Карточка дела":
        try:
            render_case_search()
        except Exception as exc:
            st.error("Ошибка при обращении к AuraDB.")
            st.code(str(exc))

    elif page == "Поиск по статье УК":
        try:
            render_article_search()
        except Exception as exc:
            st.error("Ошибка при обращении к AuraDB.")
            st.code(str(exc))

    elif page == "Анализ своего текста":
        render_text_analysis()

    elif page == "Метрики графа":
        try:
            render_metrics()
        except Exception as exc:
            st.error("Ошибка при получении метрик AuraDB.")
            st.code(str(exc))


if __name__ == "__main__":
    main()