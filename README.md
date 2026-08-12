# LegalGraph-RU: Russian Criminal Court Knowledge Graph

LegalGraph-RU is a research prototype for transforming Russian criminal court decisions into a structured knowledge graph. It combines deterministic extraction of Criminal Code article numbers, person extraction, a Neo4j graph, and an interactive Streamlit interface.

The public repository is intentionally reproducible and does not include the full research corpus or any credentials. It contains synthetic sample cases, code, figures, and the LaTeX source of the accompanying paper.

## Features

- Extract Criminal Code article references from Russian legal text.
- Extract person mentions and procedural roles in the local role-aware NER mode.
- Build local case graphs with articles, persons, courts, and typed relationships.
- Search an optional Neo4j AuraDB graph by case number or Criminal Code article.
- Inspect a case card, a local AuraDB subgraph, and graph-level metrics.
- Analyse a supplied text locally and export extracted entities and roles as JSON.
- Reproduce the public sample-data workflow without access to the full corpus.

## Repository layout

```text
Legal-Knowledge-Graph/
├── data/
│   └── sample_cases/                 # Synthetic public examples
├── paper/
│   ├── main.tex                       # Paper source
│   ├── references.bib
│   └── figures/
├── src/
│   ├── demo_streamlit_unified.py      # Main application
│   ├── demo_ner_graph_roles.py        # Local role-aware NER and graph module
│   ├── import_aura_subset.py          # Optional AuraDB import helper
│   ├── demo_streamlit.py              # Legacy sample-data demo
│   ├── build_local_graph.py
│   ├── build_neo4j_graph.py
│   ├── regex_ner_articles.py
│   ├── regex_ner_persons.py
│   └── evaluation.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/dashalinear/Legal-Knowledge-Graph.git
cd Legal-Knowledge-Graph
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the unified demo

Create a local configuration file from the safe template:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

For the local role-aware NER mode, retain this value in `.env`:

```env
ROLE_DEMO_DIR=src
```

Start the application:

```bash
streamlit run src/demo_streamlit_unified.py
```

Streamlit prints a local address, normally `http://localhost:8501`. This address is available only on the computer where Streamlit is running; it is not a public deployment URL.

### Local role-aware NER mode

The **Анализ своего текста** page works without AuraDB. Choose a bundled example or paste text, then run the analysis to obtain:

- Criminal Code article references;
- court name;
- person mentions grouped by procedural role;
- a PNG local graph;
- a JSON download containing extracted entities and role spans.

Generated files are written to `output/unified_ner/` and are intentionally ignored by Git.

### Optional AuraDB mode

To enable case search, article search, AuraDB subgraphs, and metrics, fill in these values in your private `.env` file:

```env
NEO4J_URI=neo4j+s://...
NEO4J_USER=...
NEO4J_PASSWORD=...
NEO4J_DATABASE=...
```

Never commit `.env`, credentials, a private AuraDB URI, or paths specific to one computer.

If AuraDB is unavailable, the local text-analysis mode remains available.

## Optional AuraDB import

`src/import_aura_subset.py` is a developer utility for importing a deliberately limited subset of a private corpus into AuraDB. It requires an external private source pipeline and data directory configured through `.env`:

```env
SOURCE_PIPELINE_DIR=
FULL_DATA_DIR=
AURA_MAX_CASES_PER_FILE=10
AURA_BATCH_SIZE=10
```

The full research corpus is not distributed in this repository. This script is not required to run the public local demo.

## Sample-data workflow

The repository retains a compact synthetic-data workflow for fully local reproduction:

```bash
streamlit run src/demo_streamlit.py
```

The sample cases are stored in `data/sample_cases/`. The legacy demo is independent of AuraDB and is useful for a minimal local sanity check.

## Evaluation and paper

The accompanying paper source is in `paper/main.tex`. The reported evaluation distinguishes graph-oriented article-number matching from strict mention-span matching. On the manually annotated 20-case set, article-number extraction achieved precision 1.000, recall 0.955, and F1 0.977; person extraction achieved precision 0.9259, recall 1.000, and F1 0.9615.

To compile the paper with a TeX distribution or Overleaf:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Reproducibility scope and limitations

- The public sample data is synthetic and is intended for safe reproducibility.
- The complete research corpus and local research paths are not included.
- The extraction rules are tailored to Russian criminal court decisions and do not automatically generalize to other jurisdictions.
- Role-aware extraction is provided for interactive analysis and qualitative inspection; the primary reported quantitative evaluation concerns article numbers and person mentions.
- Any real-world use of legal-text graphs must consider privacy, data protection, and the consequences of aggregating legal information.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
