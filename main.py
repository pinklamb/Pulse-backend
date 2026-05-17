
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from draft_email import draft_email_for_deal
from deal_scoring import score_deal




app = FastAPI(title="Deal Risk Radar API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load deals once on startup
DEALS_PATH = Path(__file__).parent / "deals.json"
with open(DEALS_PATH) as f:
    _DEALS_RAW = json.load(f)


_DEALS_SCORED = []
for d in _DEALS_RAW:
    scored = score_deal(d)
    _DEALS_SCORED.append({**d, **scored})  # merges score, bucket, breakdown
_DEALS_SCORED.sort(key=lambda x: x["score"], reverse=True)


_DEALS_BY_ID = {d["id"]: d for d in _DEALS_SCORED}


@app.get("/")
def root():
    return {"status": "ok", "deals_loaded": len(_DEALS_SCORED)}


@app.get("/api/deals")
def list_deals():
    
    return _DEALS_SCORED


@app.get("/api/deals/{deal_id}")
def get_deal(deal_id: str):
    
    deal = _DEALS_BY_ID.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
    return deal


@app.get("/api/summary")
def summary():

    red = [d for d in _DEALS_SCORED if d["bucket"] == "red"]
    yellow = [d for d in _DEALS_SCORED if d["bucket"] == "yellow"]
    green = [d for d in _DEALS_SCORED if d["bucket"] == "green"]

    pipeline_at_risk = sum(d["amount"] for d in red + yellow)
    total_pipeline = sum(d["amount"] for d in _DEALS_SCORED)

    # Avg days since customer contact across all OPEN deals (rough KPI).
    # Pull from the customer_silence rule's points (≈ days, capped at 30).
    silence_points = []
    for d in _DEALS_SCORED:
        for item in d["breakdown"]:
            if item["rule"] == "customer_silence":
                silence_points.append(item["points"])
                break
    avg_silence_days = (
        round(sum(silence_points) / len(silence_points), 1)
        if silence_points else 0
    )

    # Rep leaderboard — $ at risk per owner, descending.
    rep_risk = {}
    for d in red + yellow:
        owner = d["owner"]
        rep_risk.setdefault(owner, {"owner": owner, "at_risk_amount": 0, "at_risk_count": 0})
        rep_risk[owner]["at_risk_amount"] += d["amount"]
        rep_risk[owner]["at_risk_count"] += 1
    leaderboard = sorted(rep_risk.values(), key=lambda r: r["at_risk_amount"], reverse=True)

    return {
        "total_deals": len(_DEALS_SCORED),
        "total_pipeline": total_pipeline,
        "pipeline_at_risk": pipeline_at_risk,
        "red_count": len(red),
        "yellow_count": len(yellow),
        "green_count": len(green),
        "avg_silence_days": avg_silence_days,
        "rep_leaderboard": leaderboard,
    }


@app.post("/api/deals/{deal_id}/draft-email")
def draft_email_endpoint(deal_id: str):
    
    
    deal = _DEALS_BY_ID.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
    
    try:
        return draft_email_for_deal(deal)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email generation failed: {str(e)}")