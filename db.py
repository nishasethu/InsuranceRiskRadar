from typing import Dict, List


class LocalDataStore:
    def save_agent_memory(self, workflow_id: str, agent_name: str, input_text: str, output: Dict[str, object]) -> Dict[str, object]:
        return {
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "input": input_text,
            "output": output,
        }

    def save_final_report(self, workflow_id: str, report_title: str, report_summary: str) -> Dict[str, object]:
        return {
            "workflow_id": workflow_id,
            "report_title": report_title,
            "report_summary": report_summary,
        }


def get_emerging_risks() -> List[Dict[str, object]]:
    return [
        {"name": "AI Liability", "trend_score": 91, "sector": "Technology"},
        {"name": "EV Battery Fire Risk", "trend_score": 85, "sector": "Automotive"},
        {"name": "Data Center Concentration Risk", "trend_score": 80, "sector": "Technology"},
    ]


def get_portfolio_by_sector(sector: str) -> List[Dict[str, object]]:
    return [{"sector": sector, "exposure_value": 250_000_000 if sector == "Technology" else 120_000_000}]


def get_treaties_by_ids(ids: List[str]) -> List[Dict[str, object]]:
    return [{"treaty_id": treaty_id} for treaty_id in ids]


def get_historical_loss_ratio(risk_name: str) -> Dict[str, object]:
    return {"risk_name": risk_name, "loss_ratio": 74}
