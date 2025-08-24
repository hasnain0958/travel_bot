from pydantic import BaseModel, Field
from typing import List, Optional

class TripSlots(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget_inr: Optional[int] = None
    interests: List[str] = Field(default_factory=list)

class Turn(BaseModel):
    user: str
    bot: str

class ConversationState(BaseModel):
    session_id: str
    history: List[Turn] = Field(default_factory=list)
    slots: TripSlots = TripSlots()
    phase: str = "collect_info"  # or "suggest_itinerary" / "done"