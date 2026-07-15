import json
from pathlib import Path
from typing import Dict, List

from agents.trend_agent import run_trend_agent
from agents.industry_agent import run_industry_agent
from agents.exposure_agent import run_exposure_agent
from agents.scoring_agent import run_scoring_agent
from agents.scenario_agent import run_scenario_agent
from agents.strategy_agent import run_strategy_agent
from agents.report_agent import run_report_agent
from agents.news_risk_agent import update_risk_analysis_file


def _load_json_data(filename: str) -> list[Dict[str, object]]:
    file_path = Path(__file__).resolve().parent / "agents" / "sampleData" / filename
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_recent_incident_summary(profile: Dict[str, object]) -> str:
    department = str(profile.get("industry", "Other") or "Other")
    region = str(profile.get("region", "Global") or "Global")
    incidents = _load_json_data("risk_signals.json.txt")
    matching = [item for item in incidents if item.get("sector") == department]
    if region != "Global":
        matching = [item for item in matching if str(item.get("location", "Global")) == region]
    if not matching:
        matching = [item for item in incidents if item.get("sector") == department] or incidents[:3]

    latest = matching[:3]
    if not latest:
        return f"No recent incidents available for {department} in {region}."

    bullets = [f"- {item.get('risk_name', 'Unnamed risk')} ({item.get('location', region)})" for item in latest]
    return f"Recent incidents for {department} in {region}:\n" + "\n".join(bullets)


def run_workflow(profile: Dict[str, object]) -> Dict[str, object]:
    update_risk_analysis_file()
    trend = run_trend_agent(profile)
    industry = run_industry_agent(profile, trend["output"]["signals"])
    exposure = run_exposure_agent(profile, industry["output"]["mapped_signals"])
    scoring = run_scoring_agent(profile, exposure["output"], trend["output"]["signals"])
    scenario = run_scenario_agent(profile, scoring["output"]["risk_score"])
    strategy = run_strategy_agent(profile, scoring["output"]["risk_score"], scenario["output"]["scenarios"])
    report = run_report_agent(profile, [trend, industry, exposure, scoring, scenario, strategy])

    scoring_output = scoring.get("output", {}) if isinstance(scoring, dict) else {}
    derived_claim_count = scoring_output.get("derived_claim_count", 0)
    derived_claim_amount = scoring_output.get("derived_claim_amount", 0.0)
    derived_loss_ratio = scoring_output.get("derived_loss_ratio", 0.0)
    recent_incident_summary = build_recent_incident_summary(profile)

    return {
        "profile": profile,
        "workflow": [trend, industry, exposure, scoring, scenario, strategy, report],
        "summary": {
            "top_risks": trend["output"]["top_risks"],
            "highest_exposure": exposure["output"]["sector"],
            "exposure_value": exposure["output"]["exposure_value"],
            "risk_outlook": scoring_output.get("risk_band", "Low"),
            "derived_claim_count": derived_claim_count,
            "derived_claim_amount": derived_claim_amount,
            "derived_loss_ratio": derived_loss_ratio,
            "exposed_companies": exposure["output"].get("portfolio_records", []),
            "recommended_actions": strategy["output"]["actions"],
            "report_summary": report["output"]["report_summary"],
            "recent_incident_summary": recent_incident_summary,
            "selected_department": profile.get("industry", "Other"),
            "selected_region": profile.get("region", "Global"),
        },
    }
