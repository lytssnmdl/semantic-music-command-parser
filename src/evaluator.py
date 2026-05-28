import csv
import json
from typing import Dict, List, Any

from src.schema import validate_result, TRACK_NAMES


TARGET_FIELDS = [
    "emotion",
    "energy",
    "drum",
    "bass",
    "lead",
    "back",
    "reverb",
    "inst",
]


def load_test_data(path: str) -> List[Dict[str, str]]:
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def flatten_prediction(pred: Any) -> Dict[str, str]:
    return {
        "emotion": pred.emotion,
        "energy": pred.energy,
        "drum": pred.tracks["drum"],
        "bass": pred.tracks["bass"],
        "lead": pred.tracks["lead"],
        "back": pred.tracks["back"],
        "reverb": pred.reverb,
        "inst": pred.inst,
        "ambiguous": str(pred.ambiguous).lower(),
        "confidence": str(pred.confidence),
        "reason": pred.reason,
    }


def evaluate(rows: List[Dict[str, str]], parser_func) -> Dict[str, Any]:
    total_slots = 0
    correct_slots = 0
    exact_matches = 0
    valid_json_count = 0
    ambiguous_correct = 0

    detailed_results = []

    for row in rows:
        text = row["text"]
        pred = parser_func(text)

        is_valid = validate_result(pred)
        if is_valid:
            valid_json_count += 1

        flat_pred = flatten_prediction(pred)

        row_correct_slots = 0
        for field in TARGET_FIELDS:
            total_slots += 1
            if str(row[field]) == str(flat_pred[field]):
                correct_slots += 1
                row_correct_slots += 1

        expected_ambiguous = row["ambiguous"].lower()
        predicted_ambiguous = flat_pred["ambiguous"].lower()

        if expected_ambiguous == predicted_ambiguous:
            ambiguous_correct += 1

        is_exact = row_correct_slots == len(TARGET_FIELDS)
        if is_exact:
            exact_matches += 1

        detailed_results.append({
            "id": row["id"],
            "text": text,
            "expected": json.dumps({k: row[k] for k in TARGET_FIELDS}, ensure_ascii=False),
            "predicted": json.dumps({k: flat_pred[k] for k in TARGET_FIELDS}, ensure_ascii=False),
            "expected_ambiguous": expected_ambiguous,
            "predicted_ambiguous": predicted_ambiguous,
            "exact_match": str(is_exact).lower(),
            "valid_schema": str(is_valid).lower(),
            "confidence": flat_pred["confidence"],
            "reason": flat_pred["reason"],
        })

    n = len(rows)

    metrics = {
        "num_samples": n,
        "slot_accuracy": round(correct_slots / total_slots, 4),
        "exact_match_accuracy": round(exact_matches / n, 4),
        "json_validity_rate": round(valid_json_count / n, 4),
        "ambiguous_detection_accuracy": round(ambiguous_correct / n, 4),
    }

    return {
        "metrics": metrics,
        "details": detailed_results,
    }


def save_evaluation_result(metrics: Dict[str, Any], path: str, parser_name: str) -> None:
    fieldnames = ["parser", "num_samples", "slot_accuracy", "exact_match_accuracy", "json_validity_rate", "ambiguous_detection_accuracy"]

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        row = {"parser": parser_name}
        row.update(metrics)
        writer.writerow(row)


def save_error_cases(details: List[Dict[str, str]], path: str) -> None:
    fieldnames = [
        "id",
        "text",
        "expected",
        "predicted",
        "expected_ambiguous",
        "predicted_ambiguous",
        "exact_match",
        "valid_schema",
        "confidence",
        "reason",
    ]

    errors = [item for item in details if item["exact_match"] != "true"]

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in errors:
            writer.writerow(item)