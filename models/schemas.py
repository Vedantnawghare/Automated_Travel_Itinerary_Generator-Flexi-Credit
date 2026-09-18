from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PreferenceProfile(BaseModel):
    interests: List[str] = Field(default_factory=list)
    travel_style: str = "balanced"
    avoid: List[str] = Field(default_factory=list)
    morning_preference: str = "moderate_start"
    accommodation_preference: str = "mid-range hotel"
    transportation_preference: str = "flight / train / cab"
    notes: Optional[str] = None


class ResearchItem(BaseModel):
    title: str
    url: str = ""
    content: str


class BudgetBreakdown(BaseModel):
    transportation: float = 0.0
    accommodation: float = 0.0
    food: float = 0.0
    activities: float = 0.0
    local_transport: float = 0.0
    miscellaneous: float = 0.0
    total: float = 0.0
    budget: float = 0.0
    remaining: float = 0.0
    within_budget: bool = True
    currency: str = "INR"
    currency_symbol: str = "₹"
    breakdown_notes: List[str] = Field(default_factory=list)


class DayActivity(BaseModel):
    name: str
    time_slot: str  # Morning, Afternoon, Evening
    description: str
    estimated_cost: float = 0.0
    location_or_tips: str = ""


class ItineraryDay(BaseModel):
    day: int
    date: Optional[str] = None  # e.g., "2026-10-15" or None if duration-only
    theme: str = ""
    morning: List[str] = Field(default_factory=list)
    afternoon: List[str] = Field(default_factory=list)
    evening: List[str] = Field(default_factory=list)
    activities: List[DayActivity] = Field(default_factory=list)
    estimated_cost: float = 0.0
    notes: Optional[str] = None
    travel_tips: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool = True
    budget_ok: bool = True
    duration_ok: bool = True
    preference_ok: bool = True
    density_ok: bool = True
    issues: List[str] = Field(default_factory=list)
    suggested_corrections: List[str] = Field(default_factory=list)


class TravelWebhookPayload(BaseModel):
    destination: str
    origin: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: int
    travellers: int
    budget: float
    total_estimated_cost: float
    currency: str = "INR"
    preferences: Dict[str, Any] = Field(default_factory=dict)
    itinerary: List[Dict[str, Any]] = Field(default_factory=list)
    email: Optional[str] = None
    create_calendar_events: bool = True
    send_email: bool = True
