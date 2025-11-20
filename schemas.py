"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class Caroffer(BaseModel):
    """
    Long-term car rental offers
    Collection name: "caroffer"
    """
    brand: str = Field(..., description="Car brand")
    model: str = Field(..., description="Car model")
    monthly_price: float = Field(..., ge=0, description="Monthly rental price")
    upfront: float = Field(0, ge=0, description="Upfront payment (anticipo)")
    term_months: int = Field(..., ge=12, le=60, description="Contract duration in months")
    annual_km: int = Field(..., ge=10000, description="Included kilometers per year")
    fuel_type: Literal['benzina','diesel','ibrida','elettrica','gpl','metano'] = Field(..., description="Fuel type")
    transmission: Literal['manuale','automatico'] = Field(..., description="Transmission")
    body_type: Literal['berlina','suv','citycar','station','cabrio','coupé','monovolume','altro'] = Field('altro', description="Body type")
    image_url: Optional[str] = Field(None, description="Image URL")
    availability: bool = Field(True, description="Offer available")

class Lead(BaseModel):
    """
    Leads / Quote requests captured from website
    Collection name: "lead"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    type: Literal['privato','azienda'] = Field('privato', description="Customer type")
    brand: Optional[str] = Field(None, description="Desired brand")
    model: Optional[str] = Field(None, description="Desired model")
    offer_id: Optional[str] = Field(None, description="Selected offer ID if any")
    preferred_term: Optional[int] = Field(None, ge=12, le=60, description="Preferred months")
    preferred_km: Optional[int] = Field(None, ge=10000, description="Preferred annual km")
    budget: Optional[float] = Field(None, ge=0, description="Monthly budget")
    message: Optional[str] = Field(None, description="Notes / message")
    company: Optional[str] = Field(None, description="Company name (for business)")
    vat_number: Optional[str] = Field(None, description="VAT number (for business)")
