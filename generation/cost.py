"""Simple deterministic cost tracking."""

import json

MODEL_NAME = "deterministic-fallback"


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def build_cost_tracking(intake: dict, output: dict) -> dict:
    return {
        "model_name": MODEL_NAME,
        "input_tokens_estimate": estimate_tokens(json.dumps(intake, ensure_ascii=False)),
        "output_tokens_estimate": estimate_tokens(json.dumps(output, ensure_ascii=False)),
        "estimated_cost_eur": 0.0,
    }
