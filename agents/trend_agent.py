import json
from pathlib import Path
from typing import Dict


def _load_json_data(filename: str) -> list[Dict[str, object]]:
    file_path = Path(__file__).resolve().parent / "sampleData" / filename
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_trend_agent(profile: Dict[str, object]) -> Dict[str, object]:
    selected_department = str(profile.get("industry", "Other") or "Other")
    selected_region = str(profile.get("region", "Global") or "Global")
    signals = _load_json_data("risk_signals.json.txt")

    department_signals = [
        signal for signal in signals
        if signal.get("sector") == selected_department
    ]
    region_filtered = [
        signal for signal in department_signals
        if selected_region == "Global" or str(signal.get("location", "Global")) == selected_region
    ]

    ranked = sorted(region_filtered or department_signals, key=lambda item: item.get("trend_score", 0), reverse=True)
    top_three = [
        {
            "name": risk["risk_name"],
            "trend_score": risk["trend_score"],
            "sector": risk["sector"],
            "description": risk["description"],
        }
        for risk in ranked[:3]
    ]

    return {
        "agent": "Trend Discovery Agent",
        "output": {
            "top_risks": [risk["name"] for risk in top_three],
            "signals": top_three,
            "department": selected_department,
            "region": selected_region,
        },
        "summary": f"Discovered emerging risks relevant to the {selected_department} department in {selected_region}.",
    }
