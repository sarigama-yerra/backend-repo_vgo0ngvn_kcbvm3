import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Caroffer, Lead

app = FastAPI(title="Broker Noleggio Lungo Termine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend del broker di noleggio è attivo"}

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

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Utilities to convert ObjectId
class CarofferOut(BaseModel):
    id: str
    brand: str
    model: str
    monthly_price: float
    upfront: float
    term_months: int
    annual_km: int
    fuel_type: str
    transmission: str
    body_type: str
    image_url: Optional[str]
    availability: bool

class LeadIn(Lead):
    pass

class LeadOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    type: str
    brand: Optional[str]
    model: Optional[str]
    offer_id: Optional[str]
    preferred_term: Optional[int]
    preferred_km: Optional[int]
    budget: Optional[float]
    message: Optional[str]
    company: Optional[str]
    vat_number: Optional[str]

@app.get("/api/offers", response_model=List[CarofferOut])
def list_offers(brand: Optional[str] = None, budget_max: Optional[float] = None, fuel: Optional[str] = None):
    filter_dict = {"availability": True}
    if brand:
        filter_dict["brand"] = {"$regex": brand, "$options": "i"}
    if fuel:
        filter_dict["fuel_type"] = fuel
    if budget_max is not None:
        filter_dict["monthly_price"] = {"$lte": budget_max}

    docs = get_documents("caroffer", filter_dict)
    results: List[CarofferOut] = []
    for d in docs:
        results.append(CarofferOut(
            id=str(d.get("_id")),
            brand=d.get("brand"),
            model=d.get("model"),
            monthly_price=d.get("monthly_price"),
            upfront=d.get("upfront", 0),
            term_months=d.get("term_months"),
            annual_km=d.get("annual_km"),
            fuel_type=d.get("fuel_type"),
            transmission=d.get("transmission"),
            body_type=d.get("body_type", "altro"),
            image_url=d.get("image_url"),
            availability=d.get("availability", True),
        ))
    return results

@app.post("/api/leads", response_model=LeadOut)
def create_lead(lead: LeadIn):
    lead_id = create_document("lead", lead)
    created = db["lead"].find_one({"_id": ObjectId(lead_id)})
    return LeadOut(
        id=lead_id,
        name=created.get("name"),
        email=created.get("email"),
        phone=created.get("phone"),
        type=created.get("type"),
        brand=created.get("brand"),
        model=created.get("model"),
        offer_id=created.get("offer_id"),
        preferred_term=created.get("preferred_term"),
        preferred_km=created.get("preferred_km"),
        budget=created.get("budget"),
        message=created.get("message"),
        company=created.get("company"),
        vat_number=created.get("vat_number"),
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
