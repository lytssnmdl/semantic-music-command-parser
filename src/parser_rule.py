from src.schema import default_result, ParseResult


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(word in text for word in keywords)


def parse_rule(text: str) -> ParseResult:
    result = default_result()
    reasons = []
    confidence = 0.5
    ambiguous = False

    # emotion
    if _contains_any(text, ["明る", "楽しい", "楽しく", "ポジティブ", "happy"]):
        result.emotion = "happy"
        reasons.append("Detected words related to a bright or happy mood.")
        confidence += 0.12

    if _contains_any(text, ["悲しい", "悲しく", "寂しい", "暗い", "sad", "夜っぽ", "夜の感じ"]):
        result.emotion = "sad"
        reasons.append("Detected words related to a sad, dark, or night-like mood.")
        confidence += 0.12

    # energy
    if _contains_any(text, ["盛り上げ", "盛り上が", "激しい", "派手", "クライマックス", "サビ"]):
        result.energy = "H"
        reasons.append("Detected words related to high musical energy.")
        confidence += 0.12

    if _contains_any(text, ["落ち着", "静か", "軽く", "主歌"]):
        result.energy = "L"
        reasons.append("Detected words related to low musical energy.")
        confidence += 0.12

    # tracks: drum
    if _contains_any(text, ["ドラム", "リズム"]):
        if _contains_any(text, ["消", "抜", "いらない", "なし", "オフ"]):
            result.tracks["drum"] = "off"
            reasons.append("Detected a command to remove drums or rhythm.")
        else:
            result.tracks["drum"] = "on"
            reasons.append("Detected a command to add or keep drums/rhythm.")
        confidence += 0.12

    # tracks: bass
    if _contains_any(text, ["ベース"]):
        if _contains_any(text, ["消", "抜", "いらない", "なし", "オフ"]):
            result.tracks["bass"] = "off"
            reasons.append("Detected a command to remove bass.")
        else:
            result.tracks["bass"] = "on"
            reasons.append("Detected a command to add or keep bass.")
        confidence += 0.12

    # tracks: lead
    if _contains_any(text, ["メロディ", "リード", "前に出る"]):
        if _contains_any(text, ["消", "抜", "いらない", "なし", "オフ"]):
            result.tracks["lead"] = "off"
            reasons.append("Detected a command to remove lead or melody.")
        else:
            result.tracks["lead"] = "on"
            reasons.append("Detected a command to add lead or melody.")
        confidence += 0.12

    # tracks: backing
    if _contains_any(text, ["伴奏", "バッキング", "back"]):
        if _contains_any(text, ["消", "抜", "いらない", "なし", "オフ"]):
            result.tracks["back"] = "off"
            reasons.append("Detected a command to remove backing.")
        else:
            result.tracks["back"] = "on"
            reasons.append("Detected a command to add backing.")
        confidence += 0.12

    # broad expression: 全部もっと派手
    if _contains_any(text, ["全部もっと派手", "全部派手"]):
        result.energy = "H"
        result.inst = "inst2"
        for track in result.tracks:
            result.tracks[track] = "on"
        reasons.append("Detected a broad command to make the whole arrangement more intense.")
        confidence += 0.1
        ambiguous = True

    # reverb
    if _contains_any(text, ["響かせ", "広がり", "空間を広げ", "広げて"]):
        result.reverb = "0.8"
        reasons.append("Detected a command to increase spatial impression or reverb.")
        confidence += 0.1

    if _contains_any(text, ["夜っぽ", "夜の感じ"]):
        result.reverb = "0.7"
        reasons.append("Night-like expression was mapped to moderate-high reverb.")
        confidence += 0.05
        ambiguous = True

    if _contains_any(text, ["響きを少なく", "響きも抑え", "近い感じ"]):
        result.reverb = "0.2"
        reasons.append("Detected a command to reduce reverb or spatial impression.")
        confidence += 0.1

    # instrument style
    if _contains_any(text, ["激しい楽器", "派手に", "サビっぽ", "クライマックスっぽ"]):
        result.inst = "inst2"
        reasons.append("Detected a command to use a more intense instrument style.")
        confidence += 0.1

    if _contains_any(text, ["普通の楽器", "元の楽器", "戻して"]):
        result.inst = "inst1"
        reasons.append("Detected a command to return to the normal instrument style.")
        confidence += 0.1

    # ambiguous expressions
    ambiguous_keywords = [
        "夜っぽ",
        "前に出る",
        "空間",
        "軽く",
        "サビっぽ",
        "クライマックスっぽ",
        "少しだけ",
        "リズムを強く",
        "派手",
    ]
    if _contains_any(text, ambiguous_keywords):
        ambiguous = True

    result.confidence = min(round(confidence, 2), 0.95)
    result.ambiguous = ambiguous
    result.reason = " ".join(reasons) if reasons else "No rule matched."

    return result