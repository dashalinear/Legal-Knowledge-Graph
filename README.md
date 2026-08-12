# LegalGraph-RU: Russian Criminal Court Knowledge Graph

**Live demo:** https://legal-knowledge-graph.streamlit.app/

LegalGraph-RU is a research prototype for transforming Russian criminal court decisions into a structured knowledge graph. It combines deterministic extraction of Criminal Code article references, role-aware person extraction, Neo4j graph modelling, and an interactive Streamlit interface.

The public repository is intentionally reproducible and does not include the full research corpus, credentials, or computer-specific paths. It contains synthetic sample cases, source code, generated figures, and the LaTeX source of the accompanying paper.

## Features

- Extract references to articles of the Criminal Code of the Russian Federation from legal text.
- Extract person mentions and procedural roles in the local role-aware NER mode.
- Build local case graphs with articles, persons, courts, and typed relationships.
- Search an optional Neo4j AuraDB graph by case number or Criminal Code article.
- Inspect a case card, an AuraDB subgraph, and graph-level metrics.
- Analyse supplied text locally and export extracted entities and roles as JSON.
- Reproduce the public sample-data workflow without access to the full research corpus.

## Repository layout

```text
Legal-Knowledge-Graph/
├── data/
│   └── sample_cases/                 # Synthetic public examples
├── lib/                              # Auxiliary local assets
├── output/                           # Generated demo figures
├── paper/
│   ├── main.tex                      # Paper source
│   └── references.bib
├── src/
│   ├── demo_streamlit_unified.py     # Main Streamlit application
│   ├── demo_ner_graph_roles.py       # Local role-aware NER and graph module
│   ├── import_aura_subset.py          # Optional AuraDB import helper
│   ├── demo_streamlit.py              # Legacy sample-data demo
│   ├── build_local_graph.py
│   ├── build_neo4j_graph.py
│   ├── regex_ner_articles.py
│   ├── regex_ner_persons.py
│   └── evaluation.py
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.11 is recommended.
- Git.
- Neo4j AuraDB is optional: it is required only for real-case search, AuraDB subgraphs, and graph metrics.

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

Start the main application:

```bash
streamlit run src/demo_streamlit_unified.py
```

Streamlit prints a local address, normally `http://localhost:8501`. This address is available only on the computer where Streamlit is running.

The public deployment is available at:

```text
https://legal-knowledge-graph.streamlit.app/
```

## Local role-aware NER mode

The **Text analysis** page works without AuraDB credentials and without a `.env` file. The role-aware NER module is bundled in `src/demo_ner_graph_roles.py` and is discovered automatically.

Choose a bundled example or paste Russian legal text to obtain:

- Criminal Code article references.
- Court name.
- Person mentions grouped by procedural role.
- A local case graph.
- A JSON export containing extracted entities and role spans.

Generated files are written to `output/unified_ner/` and are intentionally ignored by Git.

## Optional AuraDB mode

AuraDB enables real-case search, article search, AuraDB subgraphs, and graph metrics.

For local use, copy the safe configuration template:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Fill in the private `.env` file with valid database credentials:

```env
NEO4J_URI=neo4j+s://...
NEO4J_USER=...
NEO4J_PASSWORD=...
NEO4J_DATABASE=...
```

For Streamlit Community Cloud, store these values in **Manage app → Settings → Secrets**, not in the repository.

Never commit `.env`, passwords, Streamlit Secrets, private AuraDB credentials, a full research corpus, or paths specific to one computer.

If AuraDB is unavailable, the local text-analysis mode remains available.

## Optional AuraDB import

`src/import_aura_subset.py` is a developer utility for importing a deliberately limited subset of a private corpus into AuraDB. It requires an external private source pipeline and data directory configured locally through `.env`:

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

The sample cases are stored in `data/sample_cases/`. The legacy demo is independent of AuraDB and is useful as a minimal local sanity check.

## Evaluation and paper

The accompanying paper source is located in `paper/main.tex`. The reported evaluation distinguishes graph-oriented article-number matching from strict mention-span matching.

On the manually annotated 20-case set:

| Task | Precision | Recall | F1 |
|---|---:|---:|---:|
| Article-number extraction | 1.000 | 0.955 | 0.977 |
| Person extraction | 0.9259 | 1.000 | 0.9615 |

To compile the paper with a TeX distribution or Overleaf:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Reproducibility scope and limitations

- Public sample data is synthetic and intended for safe reproducibility.
- The complete research corpus and local research paths are not included.
- Extraction rules are tailored to Russian criminal court decisions and do not automatically generalize to other jurisdictions.
- Role-aware extraction is provided for interactive analysis and qualitative inspection; the primary reported quantitative evaluation concerns article numbers and person mentions.
- Any real-world use of legal-text graphs must consider privacy, data protection, and the consequences of aggregating legal information.
- This repository is a research prototype and is not legal advice.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
