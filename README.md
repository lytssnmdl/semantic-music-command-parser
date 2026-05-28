# Semantic Music Command Parser

A small AI engineering project that converts Japanese natural language music-control expressions into structured commands for an interactive music generation system.

This project focuses on semantic parsing, baseline comparison, schema validation, robust command generation, and automatic evaluation.

---

## Overview

In interactive music generation, users often express musical intentions in vague or subjective language, such as:

```text
もっと明るくして
サビっぽく盛り上げて
夜っぽくて落ち着いた感じにして
```

However, an interactive music system needs stable and executable control commands.

For example, the expression:

```text
もっと明るくして、ドラムも入れて
```

can be converted into the following structured command:

```json
{
  "emotion": "happy",
  "energy": "keep",
  "tracks": {
    "drum": "on",
    "bass": "keep",
    "lead": "keep",
    "back": "keep"
  },
  "reverb": "keep",
  "inst": "keep",
  "confidence": 0.85,
  "ambiguous": false,
  "reason": "Detected a bright mood and a command to add drums."
}
```

This project implements a semantic parsing pipeline that maps natural language input into this structured command space.

---

## Motivation

This project is inspired by my research on interactive music generation and human-computer interaction.

In real interaction scenarios, users do not always give explicit commands such as "turn on the drum track." Instead, they often use subjective or metaphorical expressions such as:

```text
もっと楽しくして
夜っぽくして
少し軽くして
サビっぽくして
```

These expressions are easy for humans to understand, but difficult for a system to execute directly.

Therefore, this project treats natural language music control as a small-scale semantic parsing problem:

```text
Natural Language
→ Intent / Slot Interpretation
→ Structured Command
→ Executable Music Control
```

The goal is not only to call an LLM, but also to define a clear task, prepare a small test dataset, build a rule-based baseline, evaluate parser outputs, and design a more robust hybrid pipeline.

---

## Command Schema

The parser outputs a structured command with the following fields:

| Field        | Values                             | Meaning                                 |
| ------------ | ---------------------------------- | --------------------------------------- |
| `emotion`    | `happy`, `sad`, `keep`             | Musical mood / valence                  |
| `energy`     | `H`, `L`, `keep`                   | High or low musical energy              |
| `drum`       | `on`, `off`, `keep`                | Drum track control                      |
| `bass`       | `on`, `off`, `keep`                | Bass track control                      |
| `lead`       | `on`, `off`, `keep`                | Lead / melody track control             |
| `back`       | `on`, `off`, `keep`                | Backing track control                   |
| `reverb`     | `0.2`, `0.5`, `0.7`, `0.8`, `keep` | Spatial impression                      |
| `inst`       | `inst1`, `inst2`, `keep`           | Instrument style                        |
| `confidence` | `0.0` - `1.0`                      | Parser confidence                       |
| `ambiguous`  | `true`, `false`                    | Whether the input is ambiguous          |
| `reason`     | string                             | Short explanation of the parsing result |

The main controllable dimensions are:

```text
emotion: happy / sad / keep
energy: H / L / keep
tracks: drum / bass / lead / back
reverb: 0.2 / 0.5 / 0.7 / 0.8 / keep
inst: inst1 / inst2 / keep
```

---

## Methods

This project compares three parsing approaches.

### 1. Rule-based Parser

The rule-based parser is a keyword-based baseline.

It is stable and explainable, but limited in handling diverse, indirect, or ambiguous expressions.

Example:

```text
ドラムを消して
→ drum = off
```

```text
もっと明るくして
→ emotion = happy
```

```text
少し落ち着かせて
→ energy = L
```

The rule-based parser is useful as a baseline because its behavior is deterministic and easy to inspect.

---

### 2. LLM-based Parser

The LLM-based parser converts natural language into a structured JSON command.

It is designed with:

* strict JSON output
* predefined command schema
* low-temperature generation
* schema validation
* safe fallback behavior

If `OPENAI_API_KEY` is not set, the LLM parser safely returns a fallback result instead of crashing.

This makes the project runnable even without API access.

---

### 3. Hybrid Parser

The hybrid parser combines the stability of rule-based parsing with the flexibility of LLM-based parsing.

The basic logic is:

```text
1. Run the rule-based parser first
2. If the rule parser is confident, use the rule result
3. If the input is ambiguous, try the LLM parser
4. Validate the LLM output
5. If the LLM is unavailable or invalid, fallback to the rule result
```

This design reflects a practical AI engineering approach:

```text
Rule-based stability
+ LLM-based flexibility
+ Schema validation
+ Safe fallback
= More robust semantic parsing pipeline
```

When `OPENAI_API_KEY` is not set, the hybrid parser automatically falls back to the rule-based parser. In that case, the rule-based parser and hybrid parser may produce the same evaluation results.

---

## Dataset

The test dataset is located at:

```text
data/test_data.csv
```

It contains 50 Japanese music-control expressions.

The dataset includes:

* explicit commands
* compound commands
* negative commands
* ambiguous expressions
* style-related expressions

Example rows:

| Text             | Expected interpretation                             |
| ---------------- | --------------------------------------------------- |
| `もっと明るくして`       | `emotion = happy`                                   |
| `悲しい雰囲気にして`      | `emotion = sad`                                     |
| `ドラムを消して`        | `drum = off`                                        |
| `夜っぽくして`         | `emotion = sad`, `reverb = 0.7`, `ambiguous = true` |
| `サビっぽくして`        | `energy = H`, `inst = inst2`, `ambiguous = true`    |
| `ドラムを消してベースは残して` | `drum = off`, `bass = on`                           |

The dataset is small, but it is designed to evaluate whether the parser can handle different types of user expressions.

---

## Evaluation Metrics

The parsers are evaluated using the following metrics:

| Metric                       | Description                                               |
| ---------------------------- | --------------------------------------------------------- |
| Slot Accuracy                | Accuracy over all command slots                           |
| Exact Match Accuracy         | Percentage of samples where all command slots are correct |
| JSON Validity Rate           | Whether the parser output matches the predefined schema   |
| Ambiguous Detection Accuracy | Accuracy of detecting ambiguous inputs                    |

This makes the project more than a simple demo. Each method can be evaluated and compared quantitatively.

---

## Project Structure

```text
semantic-music-command-parser/
├── README.md
├── requirements.txt
├── main.py
├── data/
│   └── test_data.csv
├── src/
│   ├── schema.py
│   ├── parser_rule.py
│   ├── parser_llm.py
│   ├── parser_hybrid.py
│   ├── evaluator.py
│   └── error_analysis.py
└── results/
    ├── evaluation_result_rule.csv
    ├── evaluation_result_hybrid.csv
    └── error_cases_rule.csv
```

---

## How to Run

### 1. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.venv\Scripts\activate
```

If activation is blocked, you can directly use the Python executable inside the virtual environment:

```powershell
.venv\Scripts\python.exe main.py --parser rule
```

---

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

If the virtual environment is not activated:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

### 3. Run evaluation

Rule-based parser:

```powershell
python main.py --parser rule
```

Hybrid parser:

```powershell
python main.py --parser hybrid
```

LLM parser:

```powershell
python main.py --parser llm
```

If the virtual environment is not activated:

```powershell
.venv\Scripts\python.exe main.py --parser rule
.venv\Scripts\python.exe main.py --parser hybrid
.venv\Scripts\python.exe main.py --parser llm
```

---

## Optional: Using OpenAI API

To enable the LLM parser, create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Then run:

```powershell
python main.py --parser llm
python main.py --parser hybrid
```

The `.env` file is excluded from Git by `.gitignore`.

Do not upload your API key to GitHub.

---

## Output Files

Evaluation results are saved in:

```text
results/evaluation_result_rule.csv
results/evaluation_result_hybrid.csv
results/evaluation_result_llm.csv
```

Error cases are saved in:

```text
results/error_cases_rule.csv
results/error_cases_hybrid.csv
results/error_cases_llm.csv
```

Each error case includes:

* input text
* expected output
* predicted output
* exact match result
* schema validity
* confidence
* parsing reason

---

## Example Result

After running:

```powershell
python main.py --parser rule
```

the terminal shows metrics such as:

```text
Evaluation finished.
Parser: rule
Samples: 50
Slot Accuracy: ...
Exact Match Accuracy: ...
JSON Validity Rate: 1.0
Ambiguous Detection Accuracy: ...
```

The exact values may change as rules and test data are updated.

---

## Current Status

Implemented:

* rule-based baseline parser
* LLM parser interface
* hybrid parser with fallback
* schema validation
* test dataset
* automatic evaluation
* error case export
* GitHub-ready documentation

The current version is a compact AI engineering prototype designed for semantic parsing and robust command generation.

---

## Future Work

Possible improvements include:

* collecting real user utterance logs
* expanding the test dataset
* adding few-shot LLM prompting
* comparing different LLM models
* fine-tuning a lightweight intent classifier
* improving confidence calibration
* adding detailed error categories
* connecting parser output to an actual music-generation backend
* adding a small web demo interface

---

## Keywords

Semantic Parsing / Natural Language Understanding / Human-Computer Interaction / Interactive Music Generation / LLM / Rule-based Baseline / Hybrid AI System
