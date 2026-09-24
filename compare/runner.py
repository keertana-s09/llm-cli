"""
runner.py — Benchmark runner for the Multi-Model Comparison Lab.

Usage:
    python -m compare.runner --benchmark benchmark.yaml --output results/
    python -m compare.runner --benchmark benchmark.yaml --output results/ --models models.yaml
    python -m compare.runner --benchmark benchmark.yaml --output results/ --model-ids deepseek-v3 kimi-k2
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("runner")


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class PromptResult:
    prompt_id: str
    category: str
    prompt: str
    expected: str | None
    model_id: str
    model_name: str
    response: str
    latency_s: float
    completion_tokens: int
    prompt_tokens: int
    error: str | None = None


@dataclass
class RunResult:
    run_id: str
    benchmark_version: str
    started_at: str
    finished_at: str
    models: list[dict]
    prompt_results: list[dict] = field(default_factory=list)


# ── Back-off logic (mirrors EX 09 approach) ──────────────────────────────────

def call_with_backoff(
    client: OpenAI,
    model: str,
    messages: list[dict],
    max_tokens: int,
    temperature: float,
    seed: int,
    max_attempts: int = 6,
    base_delay: float = 15.0,
    backoff_factor: float = 2.0,
) -> tuple[str, int, int, float]:
    """
    Call the NVIDIA API with exponential backoff on transient errors.
    Uses a longer base_delay to respect the free-tier rate limit (~40 req/min).

    Returns:
        (response_text, completion_tokens, prompt_tokens, latency_seconds)
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            t0 = time.perf_counter()
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                seed=seed,
            )
            latency = time.perf_counter() - t0
            text = completion.choices[0].message.content or ""
            c_tokens = completion.usage.completion_tokens if completion.usage else 0
            p_tokens = completion.usage.prompt_tokens if completion.usage else 0
            return text, c_tokens, p_tokens, latency

        except Exception as exc:
            last_exc = exc
            # Use a longer delay for 429 rate-limit errors
            is_rate_limit = "429" in str(exc)
            delay = (30.0 if is_rate_limit else base_delay) * (backoff_factor ** (attempt - 1))
            delay = min(delay, 120.0)  # cap at 2 minutes
            if attempt < max_attempts:
                log.warning(
                    "Attempt %d/%d failed for model %s: %s — retrying in %.1fs",
                    attempt, max_attempts, model, exc, delay,
                )
                time.sleep(delay)
            else:
                log.error(
                    "All %d attempts failed for model %s: %s",
                    max_attempts, model, exc,
                )

    raise last_exc  # type: ignore[misc]


# ── Core runner ───────────────────────────────────────────────────────────────

def load_benchmark(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_models(path: Path, filter_ids: list[str] | None = None) -> list[dict]:
    with open(path) as f:
        data = yaml.safe_load(f)
    models = data["models"]
    if filter_ids:
        models = [m for m in models if m["id"] in filter_ids]
    return models


def run_benchmark(
    benchmark_path: Path,
    models_path: Path,
    output_dir: Path,
    model_ids: list[str] | None = None,
) -> Path:
    api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Set NVIDIA_API_KEY (or OPENAI_API_KEY) before running the benchmark."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://integrate.api.nvidia.com/v1",
    )

    benchmark = load_benchmark(benchmark_path)
    models = load_models(models_path, filter_ids=model_ids)
    prompts = benchmark["prompts"]

    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    started_at = datetime.now(timezone.utc).isoformat()

    log.info(
        "Starting run %s | %d models × %d prompts = %d calls",
        run_id, len(models), len(prompts), len(models) * len(prompts),
    )

    all_results: list[dict] = []

    for model in models:
        model_name = model["name"]
        api_model = model["api_model"]
        log.info("── Model: %s (%s) ──", model_name, api_model)

        for prompt_cfg in prompts:
            pid = prompt_cfg["id"]
            category = prompt_cfg["category"]
            user_text = prompt_cfg["prompt"].strip()
            expected = prompt_cfg.get("expected")

            log.info("  [%s] %s …", category, pid)
            time.sleep(2.0)  # courtesy pause — keeps us under ~30 req/min free-tier limit

            messages = [{"role": "user", "content": user_text}]
            error_msg: str | None = None
            response_text = ""
            c_tokens = 0
            p_tokens = 0
            latency = 0.0

            try:
                response_text, c_tokens, p_tokens, latency = call_with_backoff(
                    client=client,
                    model=api_model,
                    messages=messages,
                    max_tokens=model.get("max_tokens", 1024),
                    temperature=model.get("temperature", 0.7),
                    seed=model.get("seed", 42),
                )
                log.info(
                    "    ✓ %.2fs | %d tokens",
                    latency, c_tokens,
                )
            except Exception as exc:
                error_msg = str(exc)
                log.error("    ✗ %s", error_msg)

            result = PromptResult(
                prompt_id=pid,
                category=category,
                prompt=user_text,
                expected=expected,
                model_id=model["id"],
                model_name=model_name,
                response=response_text,
                latency_s=round(latency, 3),
                completion_tokens=c_tokens,
                prompt_tokens=p_tokens,
                error=error_msg,
            )
            all_results.append(asdict(result))

    finished_at = datetime.now(timezone.utc).isoformat()

    run_result = {
        "run_id": run_id,
        "benchmark_version": benchmark.get("metadata", {}).get("version", "unknown"),
        "benchmark_description": benchmark.get("metadata", {}).get("description", ""),
        "started_at": started_at,
        "finished_at": finished_at,
        "models": models,
        "prompt_results": all_results,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{run_id}_run.json"
    with open(out_file, "w") as f:
        json.dump(run_result, f, indent=2)

    log.info("Results saved → %s", out_file)
    return out_file


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Multi-Model Comparison benchmark."
    )
    parser.add_argument(
        "--benchmark", required=True,
        type=Path, help="Path to benchmark.yaml",
    )
    parser.add_argument(
        "--output", required=True,
        type=Path, help="Directory to write results JSON",
    )
    parser.add_argument(
        "--models",
        type=Path,
        default=Path(__file__).parent / "models.yaml",
        help="Path to models.yaml (default: compare/models.yaml)",
    )
    parser.add_argument(
        "--model-ids", nargs="+",
        help="Restrict run to specific model IDs (space-separated)",
    )
    args = parser.parse_args()

    result_file = run_benchmark(
        benchmark_path=args.benchmark,
        models_path=args.models,
        output_dir=args.output,
        model_ids=args.model_ids,
    )
    print(f"\nDone! Results file: {result_file}")


if __name__ == "__main__":
    main()
