import json
from pathlib import Path
from typing import Dict


def _load_json_data(filename: str) -> list[Dict[str, object]]:
    file_path = Path(__file__).resolve().parent / "sampleData" / filename
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_strategy_agent(
    profile: Dict[str, object],
    risk_score: int,
    scenarios: list[Dict[str, object]]
) -> Dict[str, object]:

    treaties = _load_json_data("treaties.json.txt")

    department = str(profile.get("industry", "Other") or "Other")
    region = str(profile.get("region", "Global") or "Global")

    actions = []

    filtered_treaties = [
        treaty for treaty in treaties
        if region == "Global" or str(treaty.get("region", "Global")) == region
    ]

    # High-risk actions
    if risk_score >= 80:
        actions.extend([
            f"Increase pricing load for {department.lower()} treaties by 8–12%",
            f"Add exclusion wording for {department.lower()} liability claims",
            f"Reassess renewal pricing assumptions for {department} portfolio and consider a 5-15% rate strengthening.",
            "Review treaty attachment points and limits to reduce accumulation exposure.",
            "Increase catastrophe and emerging-risk loadings within underwriting models.",
            "Evaluate additional retrocession protection for peak exposure zones."
        ])

    elif risk_score >= 60:
        actions.extend([
            "Perform targeted portfolio review on affected cedants and industry segments.",
            "Enhance monitoring of loss development and claim frequency trends.",
            "Apply tighter underwriting guidelines for new business in exposed sectors."
        ])

    # Scenario-specific recommendations
    scenario_names = {s.get("scenario", "") for s in scenarios}

    if "Data center outage accumulation" in scenario_names:
        actions.extend([
            "Conduct aggregation analysis across cloud providers and data-center operators.",
            "Review cyber treaty wording for systemic outage and contingent business interruption exposure.",
            "Stress test probable maximum loss (PML) under multi-region outage scenarios."
        ])

    if "Cyber attack" in scenario_names:
        actions.extend([
            "Review affirmative and silent cyber exposure across treaty portfolio.",
            "Assess accumulation risk from shared technology vendors and service providers."
        ])

    if "Supply chain disruption" in scenario_names:
        actions.extend([
            "Analyze concentration risk in critical manufacturing and logistics hubs.",
            "Review business interruption and contingent business interruption exposures."
        ])

    # Treaty-specific recommendations
    if filtered_treaties:
        treaty_ids = ", ".join(
            treaty["treaty_id"] for treaty in filtered_treaties[:5]
        )

        actions.extend([
            f"Perform treaty performance review for {treaty_ids}.",
            f"Validate adequacy of limits, sublimits, and reinstatement provisions for {region} portfolio.",
            f"Assess cedant exposure growth impacting treaty capacity in {region}."
        ])
    else:
        actions.append(
            f"Review treaty structure, retention levels, and capacity deployment for {region}."
        )

    # Capital and portfolio management
    actions.extend([
        "Update emerging-risk heat map and present findings to underwriting and portfolio management committees.",
        f"Schedule quarterly emerging-risk review covering {department} exposures in {region}.",
        "Incorporate scenario outcomes into capital modeling and ORSA risk assessments.",
        "Monitor accumulation metrics and establish trigger thresholds for management action."
    ])

    return {
        "agent": "Strategy Recommendation Agent",
        "output": {
            "actions": actions,
        },
        "summary": (
            "Converted emerging-risk signals into reinsurance portfolio, "
            "treaty management, underwriting, retrocession, and capital "
            "allocation recommendations."
        ),
    }