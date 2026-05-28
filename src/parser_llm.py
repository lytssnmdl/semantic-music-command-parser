import json
import os
from typing import Any, Dict

from dotenv import load_dotenv

from src.schema import ParseResult, default_result, validate_result


SYSTEM_PROMPT = """
You are a semantic parser for an interactive music generation system.

Your task is to convert a Japanese natural language music-control expression
into a structured JSON command.

You must output JSON only. Do not include markdown, comments, or explanations.

Allowed values:
- emotion: "happy", "sad", "keep"
- energy: "H", "L", "keep"
- tracks.drum: "on", "off", "keep"
- tracks.bass: "on", "off", "keep"
- tracks.lead: "on", "off", "keep"
- tracks.back: "on", "off", "keep"
- reverb: "keep", "0.2", "0.5", "0.7", "0.8"
- inst: "inst1", "inst2", "keep"
- confidence: float between 0.0 and 1.0
- ambiguous: true or false
- reason: short English explanation

Interpretation guidelines:
- "明るい", "楽しい" usually imply emotion="happy".
- "悲しい", "寂しい", "暗い", "夜っぽい" usually imply emotion="sad".
- "盛り上げる", "激しい", "派手", "サビ", "クライマックス" imply energy="H".
- "落ち着く", "静か", "軽い", "主歌" imply energy="L".
- "ドラム", "リズム" correspond to tracks.drum.
- "ベース" corresponds to tracks.bass.
- "メロディ", "リード", "前に出る" correspond to tracks.lead.
- "伴奏", "バッキング" correspond to tracks.back.
- "響き", "空間", "広がり" correspond to reverb.
- "激しい楽器", "派手な楽器" imply inst="inst2".
- "普通の楽器", "元の楽器" imply inst="inst1".
- Ambiguous expressions should still be parsed conservatively, with ambiguous=true.
- If a dimension is not mentioned, use "keep".

Required JSON format:
{
  "emotion": "keep",
  "energy": "keep",
  "tracks": {
    "drum": "keep",
    "bass": "keep",
    "lead": "keep",
    "back": "keep"
  },
  "reverb": "keep",
  "inst": "keep",
  "confidence": 0.8,
  "ambiguous": false,
  "reason": "..."
}
""".strip()


def _safe_float(value: Any, default: float = 0.5) -> float:
    try:
        value = float(value)
        return max(0.0, min(1.0, value))
    except Exception:
        return default


def _to_parse_result(data: Dict[str, Any]) -> ParseResult:
    tracks = data.get("tracks", {})

    result = ParseResult(
        emotion=str(data.get("emotion", "keep")),
        energy=str(data.get("energy", "keep")),
        tracks={
            "drum": str(tracks.get("drum", "keep")),
            "bass": str(tracks.get("bass", "keep")),
            "lead": str(tracks.get("lead", "keep")),
            "back": str(tracks.get("back", "keep")),
        },
        reverb=str(data.get("reverb", "keep")),
        inst=str(data.get("inst", "keep")),
        confidence=_safe_float(data.get("confidence", 0.5)),
        ambiguous=bool(data.get("ambiguous", False)),
        reason=str(data.get("reason", "Parsed by LLM.")),
    )

    if validate_result(result):
        return result

    fallback = default_result()
    fallback.confidence = 0.0
    fallback.ambiguous = True
    fallback.reason = "LLM output did not match the schema. Returned fallback result."
    return fallback


def parse_llm(text: str) -> ParseResult:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        fallback = default_result()
        fallback.confidence = 0.0
        fallback.ambiguous = True
        fallback.reason = "OPENAI_API_KEY is not set. LLM parser was skipped."
        return fallback

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.0,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return _to_parse_result(data)

    except Exception as e:
        fallback = default_result()
        fallback.confidence = 0.0
        fallback.ambiguous = True
        fallback.reason = f"LLM parser failed: {e}"
        return fallback