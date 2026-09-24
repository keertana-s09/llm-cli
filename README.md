# 🤖 Multi-Model Comparison Lab

> *"For each task category, which model wins, and by how much?"*

A Python CLI that runs a curated benchmark across five NVIDIA-hosted models and produces a shareable Markdown comparison report.

---

## Quick Start

```bash
# 1. Clone / set up
cd nvidia-llm-lab
pip install -r requirements.txt

# 2. Set your NVIDIA API key
cp .env.example .env
# Edit .env and paste your key from https://build.nvidia.com

# 3. Run the full pipeline
export $(cat .env | xargs)

# Step A — collect responses
python -m compare.runner \
  --benchmark compare/benchmark.yaml \
  --output compare/results/

# Step B — score responses
python -m compare.judge \
  --results compare/results/<run_id>_run.json

# Step C — generate report
python -m compare.report \
  --results compare/results/<run_id>_run_scored.json \
  --output compare/reports/
```

The final `compare/reports/<run_id>_report.md` is ready to publish as a blog post.

---

## Project Structure

```
nvidia-llm-lab/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── compare/
    ├── benchmark.yaml      # 20 prompts across 4 categories
    ├── models.yaml         # 5 NVIDIA-hosted models + judge config
    ├── runner.py           # Collects responses with backoff logic
    ├── judge.py            # Rubric-based + LLM-as-judge scoring
    ├── report.py           # Generates Markdown report
    ├── results/            # Raw and scored JSON run files
    └── reports/            # Generated Markdown reports
```

---

## Components

### `benchmark.yaml`
20 prompts across four categories:

| Category | Prompts | Scoring |
|---|---|---|
| `reasoning` | Logic puzzles, lateral thinking | Rubric (key-term coverage) |
| `code_generation` | Python functions, decorators, async | LLM-as-judge |
| `creative_writing` | Flash fiction, poetry, product copy | LLM-as-judge |
| `factual_recall` | CS theory, algorithms, systems | Rubric (key-term coverage) |

Each prompt has an `id`, `category`, and `prompt`. Factual prompts also carry an `expected` field (ground-truth rubric).

### `models.yaml`
Registry of five NVIDIA-hosted models:

- **DeepSeek-V3** (`deepseek-ai/deepseek-v3`)
- **Kimi k2.6** (`moonshotai/kimi-k2`)
- **Qwen3-235B-A22B** (`qwen/qwen3-235b-a22b`)
- **Mistral Large** (`mistralai/mistral-large-2-instruct`)
- **Llama Nemotron 70B** (`nvidia/llama-3.1-nemotron-70b-instruct`) — also used as judge

### `runner.py`
- Iterates over every `(model × prompt)` pair
- Captures response text, latency, completion tokens
- **Exponential backoff** on transient API errors (4 attempts, 2× backoff factor)
- Saves a timestamped `_run.json` to `results/`

### `judge.py`
Two scoring modes:

| Mode | Trigger | Method |
|---|---|---|
| **Rubric-based** | Prompt has `expected` field | Key-term coverage ratio + exact-match bonus |
| **LLM-as-judge** | Open-ended prompts | Prompts judge model for 0–10 score, normalised to [0, 1] |

**Conflict-of-interest disclosure**: when the judge model evaluates its own responses, results are flagged with `conflict_of_interest: true` and highlighted in the report.

### `report.py`
Generates a Markdown report with:
- Overall leaderboard (ranked by average score, with ASCII bars)
- Per-category breakdown with winner callouts
- Latency comparison table (median, mean, P95)
- Completion token usage
- Conflict-of-interest warnings
- Full per-prompt outputs in an appendix
- Methodology section

---

## CLI Reference

```bash
# Runner — collect responses
python -m compare.runner \
  --benchmark compare/benchmark.yaml \
  --output compare/results/ \
  [--models compare/models.yaml] \
  [--model-ids deepseek-v3 kimi-k2]   # restrict to subset

# Judge — score responses
python -m compare.judge \
  --results compare/results/<run_id>_run.json \
  [--models compare/models.yaml]

# Report — generate Markdown
python -m compare.report \
  --results compare/results/<run_id>_run_scored.json \
  [--output compare/reports/]
```

---

## Reproducibility

- Random `seed` is pinned per model in `models.yaml`
- Model API strings are recorded verbatim in every run JSON
- The `benchmark.yaml` used is embedded in run metadata
- `results/` and `reports/` are gitignored by default — commit the specific files you want to preserve

---

## Stretch Features (Optional)

- [ ] **Plotly charts** — latency boxplots, win-rate heatmaps added to report
- [ ] **Streamlit UI** — submit custom prompts and see live comparisons
- [ ] **Ollama integration** — compare NVIDIA-hosted vs locally-hosted models
- [ ] **Code-execution scoring** — actually run generated code and check test results

---

## Environment Variables

| Variable | Description |
|---|---|
| `NVIDIA_API_KEY` | Your NVIDIA Build API key (required) |

Get a key at [build.nvidia.com](https://build.nvidia.com).
