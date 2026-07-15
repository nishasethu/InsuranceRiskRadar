from typing import Dict


def run_scenario_agent(profile: Dict[str, object], risk_score: int) -> Dict[str, object]:
    scenario_results = []
    if risk_score >= 80:
        scenario_results.append({"scenario": "AI liability cascade", "impact": "Severe", "loss_estimate": 40_000_000})
    if profile.get("industry") == "Technology":
        scenario_results.append({"scenario": "Data center outage accumulation", "impact": "High", "loss_estimate": 25_000_000})

    return {
        "agent": "Scenario Simulation Agent",
        "output": {
            "scenarios": scenario_results or [{"scenario": "Baseline steady-state", "impact": "Low", "loss_estimate": 5_000_000}],
        },
        "summary": "Simulated adverse scenarios to estimate loss impact and accumulation pressure.",
    }
