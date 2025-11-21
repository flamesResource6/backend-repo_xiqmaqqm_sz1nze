import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from database import create_document
from schemas import Subscriber

app = FastAPI(title="SportLive SaaS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubscribeRequest(BaseModel):
    email: EmailStr
    favorite_team: Optional[str] = None
    source: Optional[str] = "website"

class Match(BaseModel):
    id: str
    competition: str
    stage: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    status: str  # LIVE, FT, HT, NS
    minute: Optional[int] = None
    start_time: str

@app.get("/")
def read_root():
    return {"message": "SportLive SaaS Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from SportLive backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

@app.post("/api/subscribe")
def subscribe(req: SubscribeRequest):
    try:
        sub = Subscriber(email=req.email, favorite_team=req.favorite_team, source=req.source)
        _id = create_document("subscriber", sub)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/matches", response_model=List[Match])
def get_matches():
    """Return sample live and upcoming matches. In production you would aggregate real feeds."""
    sample: List[Match] = [
        Match(
            id="ucl-001",
            competition="UEFA Champions League",
            stage="Group A",
            home_team="Paris SG",
            away_team="Manchester City",
            home_score=1,
            away_score=1,
            status="LIVE",
            minute=57,
            start_time="19:00 UTC",
        ),
        Match(
            id="epl-101",
            competition="Premier League",
            stage="Matchweek 14",
            home_team="Arsenal",
            away_team="Chelsea",
            home_score=3,
            away_score=2,
            status="FT",
            minute=None,
            start_time="16:30 UTC",
        ),
        Match(
            id="nba-550",
            competition="NBA",
            stage="Regular Season",
            home_team="Lakers",
            away_team="Warriors",
            home_score=98,
            away_score=101,
            status="LIVE",
            minute=4,
            start_time="Halftime",
        ),
        Match(
            id="mls-220",
            competition="MLS",
            stage="Playoffs",
            home_team="LAFC",
            away_team="Inter Miami",
            home_score=0,
            away_score=0,
            status="NS",
            minute=None,
            start_time="22:00 UTC",
        ),
    ]
    return sample

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
