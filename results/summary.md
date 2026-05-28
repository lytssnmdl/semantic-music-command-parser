# Evaluation Summary

This document summarizes the current evaluation results and design choices of the Semantic Music Command Parser.

---

## Overview

This project implements a semantic parsing pipeline that converts Japanese natural language music-control expressions into structured commands for an interactive music generation system.

The main goal is to evaluate how reliably user expressions such as:

```text
もっと明るくして
ドラムを消して
夜っぽくて落ち着いた感じにして
サビっぽく盛り上げて
```

can be converted into executable command slots such as:

```text
emotion
energy
drum
bass
lead
back
reverb
inst
ambiguous
```

---

## Parsers

This project currently implements three parser types.

| Parser            | Description                                                                             |
| ----------------- | --------------------------------------------------------------------------------------- |
| Rule-based parser | A deterministic keyword-based baseline parser                                           |
| LLM-based parser  | A schema-constrained parser using an LLM                                                |
| Hybrid parser     | A robust parser that combines rule-based parsing, LLM parsing, validation, and fallback |

---

## Current Evaluation Setting

The evaluation is based on 50 Japanese music-control expressions in:

```text
data/test_data.csv
```

The dataset includes several types of user expressions:

| Type                     | Example             |
| ------------------------ | ------------------- |
| Explicit command         | `ドラムを消して`           |
| Compound command         | `明るくしてドラムも入れて`      |
| Negative command         | `ドラムはいらないけどベースはほしい` |
| Ambiguous expression     | `夜っぽくして`            |
| Style-related expression | `サビっぽくして`           |

The dataset is intentionally small, but it is designed to test whether the parser can handle both direct and ambiguous music-control expressions.

---

## Evaluation Metrics

The following metrics are used.

| Metric                       | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| Slot Accuracy                | Accuracy over all command slots                   |
| Exact Match Accuracy         | Percentage of samples where all slots are correct |
| JSON Validity Rate           | Whether the output follows the predefined schema  |
| Ambiguous Detection Accuracy | Accuracy of detecting ambiguous expressions       |

These metrics are used to evaluate not only whether the parser produces a valid output, but also whether it correctly interprets each controllable music parameter.

---

## Output Files

Evaluation results are exported to:

```text
results/evaluation_result_rule.csv
results/evaluation_result_hybrid.csv
results/evaluation_result_llm.csv
```

Error cases are exported to:

```text
results/error_cases_rule.csv
results/error_cases_hybrid.csv
results/error_cases_llm.csv
```

Each error case contains:

* input text
* expected output
* predicted output
* exact match result
* schema validity
* confidence
* parsing reason

These files are useful for inspecting failure cases and improving the parser.

---

## Note on the Hybrid Parser

The hybrid parser is designed to combine the stability of rule-based parsing with the flexibility of LLM-based parsing.

The basic decision flow is:

```text
1. Run the rule-based parser first
2. If the rule parser is confident, use the rule result
3. If the input is ambiguous, try the LLM parser
4. Validate the LLM output
5. If the LLM is unavailable or invalid, fallback to the rule result
```

When `OPENAI_API_KEY` is not set, the LLM parser is skipped safely.

In this case, the hybrid parser automatically falls back to the rule-based parser. Therefore, the rule-based parser and hybrid parser may produce the same evaluation results.

This behavior is intentional. It ensures that the system fails safely instead of crashing when API access is unavailable.

---

## Current Interpretation

The current implementation should be understood as a compact AI engineering prototype rather than a large-scale model training project.

Its main contributions are:

* defining a semantic parsing task for music-control language
* preparing a small test dataset
* implementing a deterministic baseline
* adding an LLM parser interface
* designing a hybrid parser with validation and fallback
* evaluating parser outputs quantitatively
* exporting error cases for future improvement

This structure makes the project more than a simple prompt demo. It includes task definition, baseline design, evaluation, and error analysis.

---

## Known Limitations

The current version has several limitations.

| Limitation                 | Explanation                                                     |
| -------------------------- | --------------------------------------------------------------- |
| Small dataset              | The dataset contains only 50 manually prepared examples         |
| Rule dependency            | The baseline parser depends on manually designed keyword rules  |
| Limited language coverage  | The current dataset mainly focuses on Japanese expressions      |
| Limited ambiguity modeling | Ambiguity is detected using heuristic rules                     |
| No model fine-tuning       | The project currently does not train or fine-tune a model       |
| No real user logs          | The dataset is not yet based on collected user interaction data |

These limitations also suggest clear directions for future improvement.

---

## Future Improvements

Possible next steps include:

* expanding the test dataset
* collecting real user utterance logs
* adding few-shot LLM prompting
* comparing different LLM models
* improving confidence estimation
* adding detailed error categories
* fine-tuning a lightweight intent classifier
* adding semantic similarity or embedding-based retrieval
* connecting parser output to an actual music-generation backend
* adding a small web demo interface

---

## Summary

This project demonstrates a small but complete AI engineering workflow:

```text
Task Definition
→ Dataset Construction
→ Baseline Parser
→ LLM Parser Interface
→ Hybrid Parser
→ Schema Validation
→ Quantitative Evaluation
→ Error Analysis
```

The project is designed to show how natural language understanding can be connected to an interactive music-generation system in a structured and evaluable way.
