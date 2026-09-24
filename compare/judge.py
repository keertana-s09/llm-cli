"""
judge.py — Scoring layer for the Multi-Model Comparison Lab.

Supports two scoring modes:
  • rubric-based  — for prompts with an `expected` field; uses keyword/semantic matching
  • llm-as-judge  — for open-ended prompts; uses a separate model as a judge

Usage:
    python -m compare.judge --results results/2026-05-20_run.json
    python -m compare.judge --results results/2026-05-20_run.json --models models.yaml
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

import yaml
from openai import OpenAI

log = logging.getLogger("judge")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

# ── Rubric scoring ────────────────────────────────────────────────────────────

def _extract_key_terms(text: str) -> list[str]:
    """Extract meaningful tokens (≥4 chars, lowercased) from text."""
    return [w.lower() for w in re.findall(r"\b[A-Za-z0-9_]{4,}\b", text)]


def rubric_score(response: str, expected: str) -> dict:
    """
    Score a response against an expected answer using keyword overlap.

    Returns a dict with:
        score       float in [0.0, 1.0]
        method      "rubric"
        rationale   explanation string
    """
    resp_terms = set(_extract_key_terms(response))
    exp_terms = set(_extract_key_terms(expected))

    if not exp_terms:
        return {"score": 0.5, "method": "rubric", "rationale": "No expected terms to compare."}

    overlap = resp_terms & exp_terms
    coverage = len(overlap) / len(exp_terms)

    # Bonus: exact numeric / short-answer match
    exact_bonus = 0.0
    exp_stripped = expected.strip().lower()
    if len(exp_stripped.split()) <= 5 and exp_stripped in response.lower():
        exact_bonus = 0.2

    score = min(1.0, coverage + exact_bonus)

    rationale = (
        f"Covered {len(overlap)}/{len(exp_terms)} expected key terms "
        f"({coverage:.0%} coverage)"
    )
    if exact_bonus:
        rationale += " + exact match bonus."

    return {"score": round(score, 3), "method": "rubric", "rationale": rationale}


# ── LLM-as-judge scoring ──────────────────────────────────────────────────────

JUDGE_SYSTEM = """You are an impartial AI evaluator. Your task is to score a language model's response to a prompt.

Score on a scale of 0–10 where:
  0  = completely wrong, irrelevant, or harmful
  5  = partially correct or acceptable but with notable gaps
  10 = excellent, accurate, complete, well-structured

Respond ONLY with a valid JSON object in this exact format (no markdown, no preamble):
{"score": <integer 0-10>, "rationale": "<one sentence explanation>"}"""

JUDGE_USER_TEMPLATE = """PROMPT:
{prompt}

RESPONSE TO EVALUATE:
{response}"""


def llm_judge_score(
    client: OpenAI,
    judge_model: str,
    prompt: str,
    response: str,
    max_attempts: int = 3,
) -> dict:
    """
    Use an LLM to score an open-ended response.

    Returns a dict with:
        score       float in [0.0, 1.0] (normalised from 0–10)
        method      "llm-as-judge"
        rationale   string from the judge
        judge_model model used as judge

    ⚠ Conflict-of-interest disclosure: if the model being judged is also the
    judge model, the score is flagged with conflict_of_interest=True. Scores
    from self-judging should be interpreted with extra caution.
    """
    messages = [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": JUDGE_USER_TEMPLATE.format(
            prompt=prompt, response=response
        )},
    ]

    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            completion = client.chat.completions.create(
                model=judge_model,
                messages=messages,
                max_tokens=200,
                temperature=0.0,  # deterministic judging
                seed=0,
            )
            raw = completion.choices[0].message.content or "{}"
            # Strip any accidental markdown fences
            raw = re.sub(r"```(?:json)?|```", "", raw).strip()
            data = json.loads(raw)
            raw_score = float(data.get("score", 5))
            normalised = round(max(0.0, min(10.0, raw_score)) / 10.0, 3)
            return {
                "score": normalised,
                "method": "llm-as-judge",
                "rationale": data.get("rationale", "No rationale provided."),
                "judge_model": judge_model,
            }
        except Exception as exc:
            last_exc = exc
            if attempt < max_attempts:
                time.sleep(2 ** attempt)

    log.error("Judge failed after %d attempts: %s", max_attempts, last_exc)
    return {
        "score": 0.5,
        "method": "llm-as-judge",
        "rationale": f"Judging failed: {last_exc}",
        "judge_model": judge_model,
        "error": True,
    }


# ── Main scoring pipeline ─────────────────────────────────────────────────────

def score_results(results_file: Path, models_path: Path) -> Path:
    api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set NVIDIA_API_KEY before running the judge.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://integrate.api.nvidia.com/v1",
    )

    with open(results_file) as f:
        run_data: dict = json.load(f)

    with open(models_path) as f:
        models_cfg = yaml.safe_load(f)
    judge_model: str = models_cfg.get("judge_model", "nvidia/llama-3.1-nemotron-70b-instruct")

    log.info("Judge model: %s", judge_model)

    scored_results = []
    prompt_results: list[dict] = run_data["prompt_results"]
    total = len(prompt_results)

    for i, result in enumerate(prompt_results, 1):
        if result.get("error"):
            score_info = {
                "score": 0.0,
                "method": "error",
                "rationale": "Model returned an error; no response to score.",
            }
        elif result.get("expected"):
            score_info = rubric_score(result["response"], result["expected"])
        else:
            # Detect conflict of interest
            coi = judge_model in (result.get("model_id", "") + result.get("api_model", ""))
            score_info = llm_judge_score(
                client=client,
                judge_model=judge_model,
                prompt=result["prompt"],
                response=result["response"],
            )
            if coi:
                score_info["conflict_of_interest"] = True
                log.warning(
                    "  ⚠ Conflict of interest: %s is judging its own response for [%s]",
                    judge_model, result["prompt_id"],
                )

        log.info(
            "[%d/%d] %s / %s → score=%.3f (%s)",
            i, total,
            result["prompt_id"], result["model_id"],
            score_info["score"], score_info["method"],
        )

        scored_results.append({**result, "scoring": score_info})

    run_data["prompt_results"] = scored_results
    run_data["judge_model"] = judge_model

    out_file = results_file.with_name(results_file.stem + "_scored.json")
    with open(out_file, "w") as f:
        json.dump(run_data, f, indent=2)

    log.info("Scored results saved → %s", out_file)
    return out_file


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Score a benchmark run.")
    parser.add_argument("--results", required=True, type=Path,
                        help="Path to _run.json file from runner.py")
    parser.add_argument(
        "--models",
        type=Path,
        default=Path(__file__).parent / "models.yaml",
        help="Path to models.yaml (for judge model config)",
    )
    args = parser.parse_args()
    score_results(args.results, args.models)


if __name__ == "__main__":
    main()
