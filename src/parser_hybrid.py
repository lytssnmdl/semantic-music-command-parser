from src.parser_rule import parse_rule
from src.parser_llm import parse_llm
from src.schema import ParseResult, validate_result


def _merge_reason(rule_result: ParseResult, final_result: ParseResult, source: str) -> str:
    return (
        f"Hybrid parser selected {source}. "
        f"Rule reason: {rule_result.reason} "
        f"Selected reason: {final_result.reason}"
    )


def parse_hybrid(text: str) -> ParseResult:
    rule_result = parse_rule(text)

    # If rule-based parser is confident enough, use it directly.
    # This makes the system stable for explicit commands.
    if rule_result.confidence >= 0.78 and not rule_result.ambiguous:
        rule_result.reason = _merge_reason(rule_result, rule_result, "rule parser")
        return rule_result

    llm_result = parse_llm(text)

    # If LLM is unavailable, parse_llm returns confidence=0.0.
    # In that case, safely fallback to rule result.
    if not validate_result(llm_result) or llm_result.confidence <= 0.0:
        rule_result.reason = _merge_reason(rule_result, rule_result, "rule parser fallback")
        return rule_result

    # Prefer LLM when the expression is ambiguous and LLM is confident.
    if rule_result.ambiguous and llm_result.confidence >= 0.65:
        llm_result.reason = _merge_reason(rule_result, llm_result, "LLM parser")
        return llm_result

    # Prefer the result with higher confidence.
    if llm_result.confidence > rule_result.confidence:
        llm_result.reason = _merge_reason(rule_result, llm_result, "LLM parser")
        return llm_result

    rule_result.reason = _merge_reason(rule_result, rule_result, "rule parser")
    return rule_result