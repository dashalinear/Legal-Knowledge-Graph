# LegalGraph-RU: Knowledge Graph for Russian Criminal Cases

LegalGraph-RU is a minimal, reproducible implementation of a pipeline
for building a knowledge graph from Russian criminal court decisions.
It was extracted from a larger research prototype used to study
rule-based NER and legal knowledge graphs on Russian court texts.[web:1][web:4]

The repository is intentionally small: it focuses on a clear, end-to-end
example that can be cloned, run locally and easily extended for further
research or teaching.

---

## Features

- Parse synthetic examples of Russian criminal court decisions in JSON format.
- Extract Criminal Code article references with deterministic regex-based NER.
- Extract person mentions via a simple regex-based fallback pattern.
- Build local case graphs using NetworkX.
- Populate a small Neo4j knowledge graph with cases, articles and persons.
- Explore cases and their local graphs through an interactive Streamlit demo.[web:5]

---

## Live demos

- Full pipeline demo (extended version):  
  [https://knowledge-graph-full.streamlit.app/](https://knowledge-graph-full.streamlit.app/)

- Minimal legal graph demo for this repo:  
  [https://legal-graph-demo.streamlit.app/](https://legal-graph-demo.streamlit.app/)
  
---

## Project structure

```text
legal-graph-ru/
  README.md          ← you are here
  LICENSE            ← MIT license
  requirements.txt   ← Python dependencies
  src/
    __init__.py
    config.py        ← configuration (paths, Neo4j connection)
    load_cases.py    ← loading sample JSON cases
    regex_ner_articles.py ← regex-based NER for Criminal Code articles
    regex_ner_persons.py  ← simple regex-based person NER
    build_local_graph.py  ← local case graph construction (NetworkX)
    build_neo4j_graph.py  ← global Neo4j graph builder (Neo4j)
    evaluation.py    ← simple evaluation utilities (precision/recall/F1)
    demo_streamlit.py← Streamlit demo app
  data/
    sample_cases/    ← small JSON examples for a quick start
      case_0001.json
      case_0002.json
  notebooks/
    01_exploration.ipynb   ← optional exploratory notebook
    02_tsne_embeddings.ipynb ← optional t-SNE visualization
```

You can treat this repository as a starting point for your own legal NLP
experiments or as an executable appendix to a research paper.

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/<your-username>/legal-graph-ru.git
cd legal-graph-ru
```

2. **Create and activate a virtual environment (recommended)**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Neo4j connection (optional)**

If you want to build the global graph in Neo4j, create a `.env` file in
the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
DATA_DIR=data/sample_cases
```

Make sure your Neo4j instance is running and accessible.

If you only want to use the local NetworkX graph and Streamlit demo,
you can skip this step.

---

## Quick start: local case graph demo

The fastest way to see the project in action is via the Streamlit demo.

```bash
streamlit run src/demo_streamlit.py
```

This will:

- load sample JSON cases from `data/sample_cases`,
- extract Criminal Code article references using regex-based NER,
- extract person mentions using a simple regex pattern,
- build a local directed graph for the selected case,
- visualize it with PyVis inside the Streamlit app.

Open the URL printed by Streamlit (typically `http://localhost:8501`) in
your browser and select one of the sample cases from the dropdown.

---

## Building the Neo4j knowledge graph

If Neo4j is configured (see the `.env` section above), you can populate
a small knowledge graph as follows:

```bash
python -m src.build_neo4j_graph
```

This will:

- create `Case` nodes for each sample case,
- create `Article` nodes for distinct Criminal Code articles,
- create `Person` nodes for person mentions,
- connect them via `INVOLVES_ARTICLE` and `ACCUSED_IN` relationships.

You can then open the Neo4j Browser and inspect the graph, for example:

```cypher
MATCH (c:Case)-[r:INVOLVES_ARTICLE]->(a:Article)
RETURN c, r, a
LIMIT 50;
```

---

## Evaluation utilities

The repository includes a minimal evaluation utility for article
extraction:

```python
from src.evaluation import compute_f1
from src.regex_ner_articles import extract_articles

text = "Подсудимый признан виновным по ст. 228 ч. 2 УК РФ."
gold = [
    {
        "text": "ст. 228 ч. 2",
        "start": 30,
        "end": 43,
        "article_numbers": ["228", "2"],
    }
]
pred = extract_articles(text)

precision, recall, f1 = compute_f1(gold, pred)
print(precision, recall, f1)
```

This toy example illustrates the evaluation protocol used in the
underlying research: we match spans and article numbers and report
precision, recall and F1 for article extraction on a small annotated set.

---

## Data

- `data/sample_cases/` contains small, synthetic JSON examples that mimic
  the structure of real criminal cases (`case_id`, `case_number`,
  `court`, `text`, etc.).
- These files are **not** real court decisions and are provided solely
  for demonstration and reproducibility.
- If you want to run the pipeline on real data, you need to collect and
  preprocess court decisions from official open sources in your
  jurisdiction, respecting all legal and ethical constraints.

---

## Limitations and ethical considerations

- The current implementation is tailored to **Russian** criminal court
  decisions and, in particular, to citation patterns of the Russian
  Criminal Code.
- The regex-based NER patterns are designed for standardized legal
  references and will not automatically generalize to other jurisdictions
  or domains.
- Sample data is synthetic; any real-world deployment must consider
  privacy, data protection and potential harms of aggregating legal
  information into a graph.

---

## Research context and citation

This repository was created as an open artifact for a research project
on Natural Legal Language Processing (NLLP) and legal knowledge graphs.
If you use this code or ideas in your research, please cite the
corresponding paper (preprint link will be added here once available).

For questions, feel free to open an issue or discussion on GitHub.[web:2][web:7][web:10]

---

## License

This project is released under the MIT License (see `LICENSE` for
details).