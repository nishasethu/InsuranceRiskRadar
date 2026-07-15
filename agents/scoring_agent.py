import json
from pathlib import Path
from typing import Dict


def _load_json_data(filename: str) -> list[Dict[str, object]]:
    file_path = Path(__file__).resolve().parent / "sampleData" / filename
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_scoring_agent(profile: Dict[str, object], exposure: Dict[str, object], signals: list[Dict[str, object]]) -> Dict[str, object]:
    losses = _load_json_data("historical_losses.json.txt")
    claims = _load_json_data("claims.json.txt")
    treaties = _load_json_data("treaties.json.txt")
    risk_score = 60
    exposure_payload = exposure.get("output", exposure) if isinstance(exposure, dict) else {}
    selected_department = str(profile.get("industry", "Other") or "Other")
    selected_region = str(profile.get("region", "Global") or "Global")

    department_signals = [signal for signal in signals if isinstance(signal, dict)]
    region_filtered_signals = [
        signal for signal in department_signals
        if selected_region == "Global" or str(signal.get("location", "Global")) == selected_region
    ]
    department_risk_names = {str(signal.get("name") or "") for signal in region_filtered_signals if signal.get("name")}

    department_claims = [
        item for item in claims
        if str(item.get("risk_name", "")) in department_risk_names
        and item.get("amount") is not None
        and (selected_region == "Global" or str(item.get("region", "Global")) == selected_region)
    ]
    department_losses = [
        item for item in losses
        if str(item.get("risk_name", "")) in department_risk_names
        and item.get("average_loss_ratio") is not None
        and (selected_region == "Global" or str(item.get("region", "Global")) == selected_region)
    ]

    derived_claim_amount = sum(float(item.get("amount", 0)) for item in department_claims)
    derived_claim_count = len(department_claims)
    derived_loss_ratio = 0.0

    if department_losses:
        average_loss_ratio = sum(float(item["average_loss_ratio"]) for item in department_losses if item.get("average_loss_ratio")) / len(department_losses)
        derived_loss_ratio = average_loss_ratio * 100
        risk_score += int(average_loss_ratio * 100 / 2)
        risk_score += min(8, len(department_losses) * 2)

    for signal in region_filtered_signals:
        matching = next((item for item in losses if item["risk_name"] == signal["name"]), None)
        if matching:
            risk_score += int(float(matching["average_loss_ratio"]) * 100 / 2)
        claim_matching = next((item for item in department_claims if item["risk_name"] == signal["name"]), None)
        if claim_matching:
            risk_score += min(10, int(float(claim_matching.get("amount", 0)) / 250_000))
            if claim_matching.get("severity") == "High":
                risk_score += 3
        if signal["name"] in {"AI Liability", "Data Center Concentration Risk"}:
            risk_score += 8

    if not region_filtered_signals and claims:
        total_claim_amount = sum(float(item.get("amount", 0)) for item in claims if item.get("amount"))
        risk_score += min(10, int(total_claim_amount / 500_000))

    if exposure_payload.get("exposure_value", 0) > 400_000_000:
        risk_score += 6

    if selected_department == "Technology" and selected_region in {"APAC", "North America", "Europe"}:
        risk_score += 10

    treaty_limits = [
        int(treaty["limit_usd"])
        for treaty in treaties
        if treaty.get("limit_usd") and (selected_region == "Global" or str(treaty.get("region", "Global")) == selected_region)
    ]
    if treaty_limits:
        max_treaty_limit = max(treaty_limits)
        if max_treaty_limit >= 75_000_000:
            risk_score += 5

    return {
        "agent": "Risk Scoring Agent",
        "output": {
            "risk_score": min(100, risk_score),
            "risk_band": "High" if risk_score >= 80 else "Moderate" if risk_score >= 60 else "Low",
            "derived_claim_count": derived_claim_count,
            "derived_claim_amount": round(derived_claim_amount, 2),
            "derived_loss_ratio": round(derived_loss_ratio, 2),
            "department": selected_department,
            "region": selected_region,
        },
        "summary": "Calculated a portfolio risk score using the sample historical loss ratios and sector concentration.",
    }
