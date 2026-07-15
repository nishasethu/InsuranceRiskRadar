import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import build_profile
from agents.scoring_agent import run_scoring_agent
from agents.trend_agent import run_trend_agent
from orchestrator import build_recent_incident_summary, run_workflow


class WorkflowTests(unittest.TestCase):
    def test_workflow_produces_high_risk_recommendations(self) -> None:
        profile = {
            "company_name": "Test Co",
            "industry": "Technology",
            "claims_3_years": 4,
            "loss_ratio": 90,
            "safety_score": 40,
            "data_quality": 50,
            "region": "APAC",
            "incident_summary": "Severe event",
        }

        result = run_workflow(profile)

        self.assertEqual(result["summary"]["risk_outlook"], "High")
        self.assertIn("Increase pricing load for technology treaties by 8–12%", result["summary"]["recommended_actions"])
        self.assertIn("AI Liability", result["summary"]["top_risks"])
        self.assertIn("Cyber Warfare Risk", result["summary"]["top_risks"])

    def test_scoring_uses_treaty_limits_when_revenue_is_absent(self) -> None:
        profile = {
            "industry": "Technology",
            "region": "APAC",
        }
        exposure = {"output": {"exposure_value": 450_000_000}}
        signals = [{"name": "AI Liability"}]

        result = run_scoring_agent(profile, exposure, signals)

        self.assertGreaterEqual(result["output"]["risk_score"], 80)

    def test_scoring_uses_sample_claims_data_when_claim_count_is_absent(self) -> None:
        profile = {
            "industry": "Technology",
            "region": "APAC",
        }
        exposure = {"output": {"exposure_value": 100_000_000}}
        signals = []

        result = run_scoring_agent(profile, exposure, signals)

        self.assertGreaterEqual(result["output"]["risk_score"], 70)

    def test_trend_agent_filters_signals_for_selected_department(self) -> None:
        profile = {"industry": "Healthcare"}

        result = run_trend_agent(profile)

        self.assertTrue(result["output"]["signals"])
        self.assertTrue(all(signal["sector"] == "Healthcare" for signal in result["output"]["signals"]))

    def test_build_profile_drops_manual_quality_controls(self) -> None:
        profile = build_profile({"industry": "Healthcare", "region": "APAC", "incident_summary": "Test incident"})

        self.assertEqual(profile["industry"], "Healthcare")
        self.assertEqual(profile["region"], "APAC")
        self.assertNotIn("safety_score", profile)
        self.assertNotIn("data_quality", profile)

    def test_recent_incident_summary_uses_department_and_region(self) -> None:
        summary = build_recent_incident_summary({"industry": "Healthcare", "region": "APAC"})

        self.assertIn("Healthcare", summary)
        self.assertIn("APAC", summary)


if __name__ == "__main__":
    unittest.main()
