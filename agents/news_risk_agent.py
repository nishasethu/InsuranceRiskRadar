import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = BASE_DIR / ".." / "risk_analysis.json"


def _load_json_data(filename: str) -> List[Dict[str, object]]:
    file_path = BASE_DIR / "sampleData" / filename
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_name(title: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", title).strip()
    if not cleaned:
        return "General Risk"

    lowered = cleaned.lower()
    if "cyclone" in lowered:
        return "Cyclone"
    if "flood" in lowered:
        return "Floods"
    if "cyber" in lowered or "ransomware" in lowered:
        return "Cyber Warfare Risk"
    if "health" in lowered or "hospital" in lowered:
        return "Healthcare System Stress"
    if "supply" in lowered or "chain" in lowered:
        return "Supply Chain Fragility"
    if "climate" in lowered or "emission" in lowered:
        return "Climate Litigation"
    if "trade" in lowered or "geopolitical" in lowered:
        return "Geopolitical Trade Disruption"
    if "fire" in lowered:
        return "Building Fire Accident"

    words = [word for word in cleaned.split() if word.lower() not in {"the", "and", "of", "for", "in", "on", "to", "a", "an"}]
    if not words:
        return "General Risk"
    return " ".join(words[:4]).title()


def _infer_risk_level(trend_score: int) -> str:
    if trend_score >= 85:
        return "High"
    if trend_score >= 70:
        return "Medium"
    return "Low"


def _infer_location(title: str) -> str:
    cleaned = title.strip()
    if not cleaned:
        return "Global"

    location_candidates = [
        "North America", "Europe", "Asia", "APAC", "LATAM", "Global",
        "United States", "USA", "UK", "India", "China", "Japan", "Singapore",
        "Australia", "Brazil", "Middle East", "Africa", "Europe", "Canada"
    ]
    lowered = cleaned.lower()
    for location in location_candidates:
        if location.lower() in lowered:
            return location

    return "Global"


def normalize_headlines_to_signals(headlines: List[Dict[str, str]], existing_signals: Optional[List[Dict[str, object]]] = None) -> List[Dict[str, object]]:
    existing_signals = existing_signals or _load_json_data("risk_signals.json.txt")
    signal_map: Dict[str, Dict[str, object]] = {}

    for signal in existing_signals:
        name = str(signal.get("risk_name", "")).strip()
        if name:
            signal_map[name] = dict(signal)

    headline_risk_names: List[str] = []
    for headline in headlines:
        title = str(headline.get("title", "")).strip()
        summary = str(headline.get("summary", "")).strip()
        risk_name = _normalize_name(title)
        if risk_name in {"General Risk"}:
            continue

        headline_risk_names.append(risk_name)
        if risk_name not in signal_map:
            signal_map[risk_name] = {
                "risk_id": f"R{len(signal_map) + 1:03d}",
                "risk_name": risk_name,
                "sector": "Insurance",
                "trend_score": 70,
                "risk_level": "Medium",
                "description": summary or title,
                "time_horizon": "1-3 years",
                "location": _infer_location(title),
            }
            continue

        current_score = int(signal_map[risk_name].get("trend_score", 60))
        repetition_bonus = 8
        signal_map[risk_name]["trend_score"] = min(100, current_score + repetition_bonus)
        signal_map[risk_name]["risk_level"] = _infer_risk_level(int(signal_map[risk_name]["trend_score"]))
        signal_map[risk_name]["description"] = summary or str(signal_map[risk_name].get("description", title))
        signal_map[risk_name]["location"] = signal_map[risk_name].get("location", _infer_location(title))

    ordered: List[Dict[str, object]] = []
    seen: set[str] = set()
    for risk_name in headline_risk_names:
        if risk_name in signal_map and risk_name not in seen:
            ordered.append(signal_map[risk_name])
            seen.add(risk_name)

    for signal in signal_map.values():
        risk_name = str(signal.get("risk_name", ""))
        if risk_name not in seen:
            ordered.append(signal)
            seen.add(risk_name)

    return ordered


def fetch_latest_risk_news(query: str = "commercial insurance emerging risk news") -> List[Dict[str, str]]:
    encoded_query = quote(query)
    url = f"https://r.jina.ai/http://www.google.com/search?q={encoded_query}"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        content = response.read().decode("utf-8", errors="ignore")

    items: List[Dict[str, str]] = []
    for line in content.splitlines():
        if "https://" in line and "http" in line:
            continue
        if line.strip().startswith("http"):
            continue
        if len(line.strip()) < 15:
            continue
        if line.lower().startswith(("google", "search results", "result")):
            continue
        if re.search(r"\b(cyber|cyclone|flood|climate|supply|healthcare|geopolitical|fire|liability|insurance|risk)\b", line, re.IGNORECASE):
            items.append({"title": line.strip(), "summary": line.strip()})
            if len(items) >= 10:
                break
    return items or [{"title": "No fresh risk news found", "summary": "No fresh risk news found"}]


def update_risk_analysis_file(output_path: Optional[Path] = None, headlines: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, object]]:
    output_path = output_path or DEFAULT_OUTPUT_PATH
    headlines = headlines if headlines is not None else fetch_latest_risk_news()
    existing_signals = _load_json_data("risk_signals.json.txt")
    signals = normalize_headlines_to_signals(headlines, existing_signals=existing_signals)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(signals, handle, indent=2)

    return signals


if __name__ == "__main__":
    update_risk_analysis_file()
