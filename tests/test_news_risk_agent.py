import json
import tempfile
import unittest
from pathlib import Path

from agents.news_risk_agent import normalize_headlines_to_signals, update_risk_analysis_file


class NewsRiskAgentTests(unittest.TestCase):
    def test_normalize_headlines_updates_trend_scores_for_repeated_events(self) -> None:
        headlines = [
            {"title": "Cyclone hits major port terminals", "summary": "Storm damage disrupts logistics"},
            {"title": "Cyclone disruption worsens supply chains", "summary": "Another cyclone impacts shipping"},
            {"title": "Cyber attack cripples hospital systems", "summary": "Ransomware incident reported"},
        ]

        signals = normalize_headlines_to_signals(headlines, existing_signals=[{"risk_name": "Cyclone", "trend_score": 80}])

        self.assertGreaterEqual(len(signals), 2)
        cyclone_signal = next(item for item in signals if item["risk_name"] == "Cyclone")
        self.assertGreater(cyclone_signal["trend_score"], 80)
        self.assertEqual(cyclone_signal["risk_level"], "High")

    def test_update_risk_analysis_file_writes_expected_format(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "risk_analysis.json"
            headlines = [{"title": "Floods cause widespread property losses", "summary": "River flooding causes insured losses"}]

            result = update_risk_analysis_file(output_path, headlines=headlines)

            self.assertTrue(output_path.exists())
            self.assertIn("risk_name", result[0])
            self.assertIn("trend_score", result[0])
            self.assertIn("risk_level", result[0])
            self.assertIn("location", result[0])

            content = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(content[0]["risk_name"], "Floods")
