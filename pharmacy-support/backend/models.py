from pydantic import BaseModel
from typing import List, Optional


class VaccineCenterRequest(BaseModel):
    pincode: str
    date: str  # Format: DD-MM-YYYY


class VaccineSession(BaseModel):
    date: str
    available_capacity: int
    vaccine: str
    min_age_limit: int
    slots: List[str] = []


class VaccineCenter(BaseModel):
    center_id: int
    name: str
    address: str
    pincode: str
    sessions: List[VaccineSession]


# Health Camps Models
class HealthCamp(BaseModel):
    name: str
    organizer: str
    type: str  # General, Dental, Eye, Specialized
    location: str
    date: str
    time: str
    services: List[str]
    contact: str = ""
    pincode: str


class HealthCampsRequest(BaseModel):
    pincode: str


class HealthCampsResponse(BaseModel):
    camps: List[HealthCamp]



class VaccineCenterResponse(BaseModel):
    centers: List[VaccineCenter]


class LLMRequest(BaseModel):
    message: str
    conversation_history: List[dict] = []


class LLMResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    timestamp: str
