"""
report.py — Generate a Markdown comparison report from scored results.

Usage:
    python -m compare.report --results results/2026-05-20_run_scored.json
    python -m compare.report --results results/2026-05-20_run_scored.json --output reports/
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_score(score: float) -> str:
    return f"{score:.1%}"


def _bar(score: float, width: int = 20) -> str:
    """ASCII progress bar."""
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)


def _medal(rank: int) -> str:
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")


# ── Report builder ────────────────────────────────────────────────────────────

def build_report(results_file: Path, output_dir: Path | None = None) -> Path:
    with open(results_file) as f:
        data: dict = json.load(f)

    run_id = data["run_id"]
    started = data.get("started_at", "")
    finished = data.get("finished_at", "")
    judge_model = data.get("judge_model", "unknown")
    models_cfg: list[dict] = data.get("models", [])
    results: list[dict] = data["prompt_results"]

    model_ids = [m["id"] for m in models_cfg]
    model_names = {m["id"]: m["name"] for m in models_cfg}
    categories = sorted({r["category"] for r in results})

    # ── Aggregate statistics ──────────────────────────────────────────────────

    # model → category → [scores]
    cat_scores: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    # model → [latencies]
    latencies: dict[str, list[float]] = defaultdict(list)
    # model → [tokens]
    tokens: dict[str, list[int]] = defaultdict(list)
    # model → [scores] (all categories)
    all_scores: dict[str, list[float]] = defaultdict(list)
    # category → prompt_id → model → result
    prompt_map: dict[str, dict[str, dict[str, dict]]] = defaultdict(lambda: defaultdict(dict))

    for r in results:
        mid = r["model_id"]
        cat = r["category"]
        score = r.get("scoring", {}).get("score", 0.0)
        cat_scores[mid][cat].append(score)
        all_scores[mid].append(score)
        if not r.get("error"):
            latencies[mid].append(r.get("latency_s", 0.0))
            tokens[mid].append(r.get("completion_tokens", 0))
        prompt_map[cat][r["prompt_id"]][mid] = r

    # Overall average score per model
    overall_avg: dict[str, float] = {
        mid: statistics.mean(scores) if scores else 0.0
        for mid, scores in all_scores.items()
    }
    ranked_models = sorted(overall_avg.items(), key=lambda x: -x[1])

    # Category win counts
    cat_wins: dict[str, dict[str, int]] = {mid: defaultdict(int) for mid in model_ids}
    for cat in categories:
        cat_avg = {
            mid: statistics.mean(cat_scores[mid][cat]) if cat_scores[mid][cat] else 0.0
            for mid in model_ids
        }
        winner = max(cat_avg, key=cat_avg.__getitem__)
        cat_wins[winner][cat] += 1

    # ── Build Markdown ────────────────────────────────────────────────────────

    lines: list[str] = []

    def h(level: int, text: str) -> None:
        lines.append(f"{'#' * level} {text}\n")

    def p(text: str = "") -> None:
        lines.append(text + "\n")

    def hr() -> None:
        lines.append("---\n")

    # Title
    h(1, "🤖 Multi-Model LLM Comparison Report")
    p(f"**Run ID:** `{run_id}`  ")
    p(f"**Started:** {started}  ")
    p(f"**Finished:** {finished}  ")
    p(f"**Models compared:** {len(model_ids)}  ")
    p(f"**Prompts:** {len({r['prompt_id'] for r in results})} across {len(categories)} categories  ")
    p(f"**Judge model:** `{judge_model}`  ")
    hr()

    # ── Overall Leaderboard ───────────────────────────────────────────────────
    h(2, "🏆 Overall Leaderboard")
    p()
    p("| Rank | Model | Overall Score | Win Rate |")
    p("|------|-------|---------------|----------|")
    for rank, (mid, avg) in enumerate(ranked_models, 1):
        wins = sum(cat_wins[mid].values())
        win_rate = wins / len(categories) if categories else 0.0
        p(f"| {_medal(rank)} | **{model_names.get(mid, mid)}** | {_fmt_score(avg)} {_bar(avg, 15)} | {wins}/{len(categories)} categories |")
    p()

    # ── Category Breakdown ────────────────────────────────────────────────────
    h(2, "📊 Per-Category Breakdown")

    for cat in categories:
        cat_display = cat.replace("_", " ").title()
        h(3, f"{cat_display}")

        cat_avg_per_model = {
            mid: statistics.mean(cat_scores[mid][cat]) if cat_scores[mid][cat] else 0.0
            for mid in model_ids
        }
        ranked_cat = sorted(cat_avg_per_model.items(), key=lambda x: -x[1])

        p("| Rank | Model | Avg Score |")
        p("|------|-------|-----------|")
        for rank, (mid, avg) in enumerate(ranked_cat, 1):
            p(f"| {_medal(rank)} | {model_names.get(mid, mid)} | {_fmt_score(avg)} {_bar(avg, 12)} |")

        # Category winner callout
        winner_mid, winner_score = ranked_cat[0]
        runner_mid, runner_score = ranked_cat[1] if len(ranked_cat) > 1 else (winner_mid, winner_score)
        margin = winner_score - runner_score
        p()
        p(f"> **Winner:** {model_names.get(winner_mid, winner_mid)} "
          f"(+{_fmt_score(margin)} over runner-up {model_names.get(runner_mid, runner_mid)})")
        p()

    # ── Latency Comparison ────────────────────────────────────────────────────
    h(2, "⏱️ Latency Comparison")
    p()
    p("| Model | Median Latency | Mean Latency | P95 Latency |")
    p("|-------|---------------|--------------|-------------|")
    for mid, lats in sorted(latencies.items(), key=lambda x: statistics.median(x[1]) if x[1] else 999):
        if not lats:
            continue
        median_l = statistics.median(lats)
        mean_l = statistics.mean(lats)
        sorted_lats = sorted(lats)
        p95 = sorted_lats[int(len(sorted_lats) * 0.95)]
        p(f"| {model_names.get(mid, mid)} | {median_l:.2f}s | {mean_l:.2f}s | {p95:.2f}s |")
    p()

    # ── Token Usage ───────────────────────────────────────────────────────────
    h(2, "🪙 Completion Tokens")
    p()
    p("| Model | Total Tokens | Avg per Prompt |")
    p("|-------|-------------|----------------|")
    for mid in model_ids:
        toks = tokens[mid]
        if not toks:
            continue
        p(f"| {model_names.get(mid, mid)} | {sum(toks):,} | {statistics.mean(toks):.0f} |")
    p()

    # ── Conflict of Interest Disclosure ──────────────────────────────────────
    coi_entries = [
        r for r in results
        if r.get("scoring", {}).get("conflict_of_interest")
    ]
    if coi_entries:
        h(2, "⚠️ Conflict of Interest Disclosure")
        p(
            f"The judge model (`{judge_model}`) was used to evaluate "
            f"its own responses on {len(coi_entries)} prompt(s). "
            "These scores may be inflated and should be interpreted with caution."
        )
        p()
        p("| Prompt ID | Category |")
        p("|-----------|----------|")
        for r in coi_entries:
            p(f"| `{r['prompt_id']}` | {r['category']} |")
        p()

    hr()

    # ── Appendix: Full Per-Prompt Outputs ─────────────────────────────────────
    h(2, "📎 Appendix: Full Per-Prompt Outputs")

    for cat in categories:
        cat_display = cat.replace("_", " ").title()
        h(3, f"Category: {cat_display}")

        for pid, model_responses in sorted(prompt_map[cat].items()):
            # Grab prompt text from first available result
            first_result = next(iter(model_responses.values()))
            prompt_text = first_result.get("prompt", "")
            expected = first_result.get("expected")

            h(4, f"Prompt `{pid}`")
            p("**Prompt:**")
            p(f"```\n{prompt_text}\n```")
            if expected:
                p("**Expected / Reference Answer:**")
                p(f"```\n{expected.strip()}\n```")
            p()

            for mid in model_ids:
                if mid not in model_responses:
                    continue
                r = model_responses[mid]
                scoring = r.get("scoring", {})
                score = scoring.get("score", 0.0)
                method = scoring.get("method", "?")
                rationale = scoring.get("rationale", "")
                coi_flag = " ⚠️ COI" if scoring.get("conflict_of_interest") else ""

                p(f"**{model_names.get(mid, mid)}** — Score: `{_fmt_score(score)}` ({method}){coi_flag}")
                p(f"*{rationale}*")
                if r.get("error"):
                    p(f"❌ Error: {r['error']}")
                else:
                    p(f"> {r.get('response', '').strip()[:800]}"
                      + ("…" if len(r.get("response", "")) > 800 else ""))
                p(f"*Latency: {r.get('latency_s', 0):.2f}s | Tokens: {r.get('completion_tokens', 0)}*")
                p()

    # ── Methodology Notes ──────────────────────────────────────────────────────
    hr()
    h(2, "🔬 Methodology")
    p(
        "**Rubric-based scoring** is used for prompts with a ground-truth `expected` field. "
        "Key terms from the expected answer are extracted and matched against the response; "
        "coverage ratio forms the base score, with a bonus for exact short-answer matches."
    )
    p()
    p(
        "**LLM-as-judge scoring** is used for open-ended prompts (reasoning, creative writing). "
        f"The judge model `{judge_model}` is prompted with a 0–10 scale rubric and "
        "its score is normalised to [0, 1]. Prompts where the judge model evaluates its own "
        "output are flagged with a conflict-of-interest warning."
    )
    p()
    p("**Reproducibility:** Random seeds are pinned per model. Model IDs are recorded verbatim.")
    p()

    # ── Write output ──────────────────────────────────────────────────────────
    report_text = "\n".join(lines)

    if output_dir is None:
        output_dir = results_file.parent.parent / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    out_file = output_dir / f"{run_id}_report.md"
    out_file.write_text(report_text, encoding="utf-8")
    print(f"\n✅ Report written → {out_file}")
    return out_file


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Markdown report from scored results.")
    parser.add_argument("--results", required=True, type=Path,
                        help="Path to _scored.json file from judge.py")
    parser.add_argument("--output", type=Path, default=None,
                        help="Directory to write the report (default: ../reports/ relative to results)")
    args = parser.parse_args()
    build_report(args.results, args.output)


if __name__ == "__main__":
    main()
