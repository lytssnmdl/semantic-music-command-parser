from dataclasses import dataclass, asdict
from typing import Dict, Any


VALID_EMOTIONS = {"happy", "sad", "keep"}
VALID_ENERGIES = {"H", "L", "keep"}
VALID_TRACK_VALUES = {"on", "off", "keep"}
VALID_INST = {"inst1", "inst2", "keep"}
VALID_REVERB = {"keep", "0.2", "0.5", "0.7", "0.8"}


TRACK_NAMES = ["drum", "bass", "lead", "back"]


@dataclass
class ParseResult:
    emotion: str
    energy: str
    tracks: Dict[str, str]
    reverb: str
    inst: str
    confidence: float
    ambiguous: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def default_result() -> ParseResult:
    return ParseResult(
        emotion="keep",
        energy="keep",
        tracks={
            "drum": "keep",
            "bass": "keep",
            "lead": "keep",
            "back": "keep",
        },
        reverb="keep",
        inst="keep",
        confidence=0.5,
        ambiguous=False,
        reason="No specific command was detected.",
    )


def validate_result(result: ParseResult) -> bool:
    if result.emotion not in VALID_EMOTIONS:
        return False

    if result.energy not in VALID_ENERGIES:
        return False

    if result.inst not in VALID_INST:
        return False

    if result.reverb not in VALID_REVERB:
        return False

    for track in TRACK_NAMES:
        if track not in result.tracks:
            return False
        if result.tracks[track] not in VALID_TRACK_VALUES:
            return False

    if not isinstance(result.confidence, float):
        return False

    if result.confidence < 0.0 or result.confidence > 1.0:
        return False

    if not isinstance(result.ambiguous, bool):
        return False

    return True