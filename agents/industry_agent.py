from typing import Dict


def run_industry_agent(profile: Dict[str, object], signals: list[Dict[str, object]]) -> Dict[str, object]:
    sector = profile.get("industry", "Other")
    region = str(profile.get("region", "Global") or "Global")
    mapped = []
    for signal in signals:
        if signal.get("sector") == sector and (region == "Global" or str(signal.get("location", "Global")) == region):
            mapped.append(signal)

    return {
        "agent": "Industry Mapping Agent",
        "output": {
            "sector": sector,
            "mapped_signals": mapped,
        },
        "summary": f"Mapped emerging risks to the {sector} industry footprint for portfolio relevance.",
    }
