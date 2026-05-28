import argparse
import os

from src.evaluator import (
    load_test_data,
    evaluate,
    save_evaluation_result,
    save_error_cases,
)
from src.parser_rule import parse_rule


def get_parser(parser_name: str):
    if parser_name == "rule":
        return parse_rule

    raise ValueError(f"Unknown parser: {parser_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parser",
        type=str,
        default="rule",
        choices=["rule"],
        help="Parser type to evaluate.",
    )
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    rows = load_test_data("data/test_data.csv")
    parser_func = get_parser(args.parser)

    result = evaluate(rows, parser_func)

    save_evaluation_result(
        result["metrics"],
        "results/evaluation_result.csv",
        args.parser,
    )
    save_error_cases(
        result["details"],
        "results/error_cases.csv",
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
    print("- results/evaluation_result.csv")
    print("- results/error_cases.csv")


if __name__ == "__main__":
    main()