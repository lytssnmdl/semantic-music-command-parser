import argparse
import os

from src.evaluator import (
    load_test_data,
    evaluate,
    save_evaluation_result,
    save_error_cases,
)
from src.parser_rule import parse_rule
from src.parser_llm import parse_llm
from src.parser_hybrid import parse_hybrid


def get_parser(parser_name: str):
    if parser_name == "rule":
        return parse_rule

    if parser_name == "llm":
        return parse_llm

    if parser_name == "hybrid":
        return parse_hybrid

    raise ValueError(f"Unknown parser: {parser_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parser",
        type=str,
        default="rule",
        choices=["rule", "llm", "hybrid"],
        help="Parser type to evaluate.",
    )
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    rows = load_test_data("data/test_data.csv")
    parser_func = get_parser(args.parser)

    result = evaluate(rows, parser_func)

    evaluation_path = f"results/evaluation_result_{args.parser}.csv"
    error_path = f"results/error_cases_{args.parser}.csv"

    save_evaluation_result(
        result["metrics"],
        evaluation_path,
        args.parser,
    )
    save_error_cases(
        result["details"],
        error_path,
    )

    print("Evaluation finished.")
    print(f"Parser: {args.parser}")
    print(f"Samples: {result['metrics']['num_samples']}")
    print(f"Slot Accuracy: {result['metrics']['slot_accuracy']}")
    print(f"Exact Match Accuracy: {result['metrics']['exact_match_accuracy']}")
    print(f"JSON Validity Rate: {result['metrics']['json_validity_rate']}")
    print(f"Ambiguous Detection Accuracy: {result['metrics']['ambiguous_detection_accuracy']}")
    print("")
    print("Saved:")
    print(f"- {evaluation_path}")
    print(f"- {error_path}")


if __name__ == "__main__":
    main()