import json
from pathlib import Path
from typing import Dict


def _load_json_data(filename: str) -> list[Dict[str, object]]:
    file_path = Path(__file__).resolve().parent / "sampleData" / filename
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_exposure_agent(profile: Dict[str, object], mapped_signals: list[Dict[str, object]]) -> Dict[str, object]:
    sector = profile.get("industry", "Other")
    region = str(profile.get("region", "Global") or "Global")
    exposure_records = _load_json_data("portfolio_exposure.json.txt")
    sector_exposure = [record for record in exposure_records if record["sector"] == sector and (region == "Global" or record.get("region") == region)]
    exposure_value = sum(record["insured_value_usd"] for record in sector_exposure)

    return {
        "agent": "Portfolio Exposure Agent",
        "output": {
            "sector": sector,
            "exposure_value": exposure_value,
            "mapped_signals": mapped_signals,
            "portfolio_records": sector_exposure,
        },
        "summary": f"Quantified portfolio concentration for {sector} using the sample exposure data.",
    }
