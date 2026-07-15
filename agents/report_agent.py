from typing import Dict


def run_report_agent(profile: Dict[str, object], agents: list[Dict[str, object]]) -> Dict[str, object]:
    top_risks = []
    for agent in agents:
        if agent["agent"] == "Trend Discovery Agent":
            top_risks = agent["output"]["top_risks"]
            break

    department = profile.get("industry", "the selected department")
    region = profile.get("region", "the selected region")
    summary = (
        f"For {profile.get('company_name', 'the portfolio')}, the review highlights {', '.join(top_risks[:3])} as the primary emerging risks for the {department} portfolio in {region}. "
        f"The portfolio should prepare for tighter underwriting terms and higher scrutiny around concentration risk."
    )

    return {
        "agent": "Executive Report Agent",
        "output": {
            "report_title": "Emerging Risk Radar Report",
            "report_summary": summary,
        },
        "summary": "Prepared an executive-ready report summarizing the most material emerging risks and actions.",
    }
