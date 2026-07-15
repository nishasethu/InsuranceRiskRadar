# InsuranceRiskRadar

RiskRadar AI is a Streamlit-based multi-agent prototype for reinsurance emerging risk intelligence.

## What it does
- Runs a seven-step agent workflow: trend discovery, industry mapping, portfolio exposure, risk scoring, scenario simulation, strategy recommendation, and executive reporting.
- Presents a dashboard-style UI for portfolio intake and agent output.
- Uses a simple orchestrator so the agents can share context within one workflow.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Demo prompt

What emerging risks should our portfolio prepare for?
