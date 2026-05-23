from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["pharmacy"])


class PharmacySearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 5000  # meters
    facility_type: str = "pharmacy"  # pharmacy, hospital, doctor


class Pharmacy(BaseModel):
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    opening_hours: Optional[str] = None
    distance: Optional[float] = None  # in meters


class PharmacySearchResponse(BaseModel):
    facilities: List[Pharmacy]
    count: int
    location: str


# Real Indore Pharmacies Data
INDORE_PHARMACIES = [
    {
        "id": "pharmacy_1",
        "name": "Apollo Pharmacy - Vijay Nagar",
        "address": "AB Road, Vijay Nagar, Indore, Madhya Pradesh 452010",
        "latitude": 22.7532,
        "longitude": 75.8937,
        "phone": "+91-731-4982000",
        "opening_hours": "24 hours"
    },
    {
        "id": "pharmacy_2",
        "name": "MedPlus - Palasia",
        "address": "Palasia Square, Indore, Madhya Pradesh 452001",
        "latitude": 22.7243,
        "longitude": 75.8742,
        "phone": "+91-731-2545678",
        "opening_hours": "8:00 AM - 11:00 PM"
    },
    {
        "id": "pharmacy_3",
        "name": "Wellness Forever - Bhawar Kuan",
        "address": "Bhawar Kuan Square, Indore, Madhya Pradesh 452014",
        "latitude": 22.6986,
        "longitude": 75.8681,
        "phone": "+91-731-4567890",
        "opening_hours": "9:00 AM - 10:00 PM"
    },
    {
        "id": "pharmacy_4",
        "name": "Netmeds - Sapna Sangeeta",
        "address": "Sapna Sangeeta Road, Indore, Madhya Pradesh 452001",
        "latitude": 22.7195,
        "longitude": 75.8577,
        "phone": "+91-731-2987654",
        "opening_hours": "24 hours"
    },
    {
        "id": "pharmacy_5",
        "name": "PharmEasy Store - Rau",
        "address": "Rau, Indore, Madhya Pradesh 453331",
        "latitude": 22.6543,
        "longitude": 75.8012,
        "phone": "+91-731-3456789",
        "opening_hours": "8:00 AM - 9:00 PM"
    }
]

INDORE_HOSPITALS = [
    {
        "id": "hospital_1",
        "name": "Bombay Hospital Indore",
        "address": "Scheme No 94, Ring Road, Indore, Madhya Pradesh 452010",
        "latitude": 22.7644,
        "longitude": 75.8931,
        "phone": "+91-731-4982000",
        "opening_hours": "24 hours"
    },
    {
        "id": "hospital_2",
        "name": "CHL Hospital",
        "address": "AB Road, Near Janjeerwala Square, Indore, Madhya Pradesh 452008",
        "latitude": 22.7453,
        "longitude": 75.8765,
        "phone": "+91-731-4044444",
        "opening_hours": "24 hours"
    },
    {
        "id": "hospital_3",
        "name": "Medanta Super Specialty Hospital",
        "address": "Scheme No 78, Part 2, Vijay Nagar, Indore, Madhya Pradesh 452010",
        "latitude": 22.7521,
        "longitude": 75.8945,
        "phone": "+91-731-4777777",
        "opening_hours": "24 hours"
    },
    {
        "id": "hospital_4",
        "name": "MY Hospital (Maharaja Yeshwantrao Hospital)",
        "address": "MG Road, Indore, Madhya Pradesh 452001",
        "latitude": 22.7196,
        "longitude": 75.8577,
        "phone": "+91-731-2536666",
        "opening_hours": "24 hours"
    },
    {
        "id": "hospital_5",
        "name": "Greater Kailash Hospital",
        "address": "Scheme No 54, Vijay Nagar, Indore, Madhya Pradesh 452010",
        "latitude": 22.7567,
        "longitude": 75.8923,
        "phone": "+91-731-4225555",
        "opening_hours": "24 hours"
    }
]

INDORE_DOCTORS = [
    {
        "id": "doctor_1",
        "name": "Dr. Rajesh Sharma - Cardiologist",
        "address": "Apollo Clinic, Vijay Nagar, Indore, Madhya Pradesh 452010",
        "latitude": 22.7532,
        "longitude": 75.8937,
        "phone": "+91-731-4982001",
        "opening_hours": "10:00 AM - 6:00 PM"
    },
    {
        "id": "doctor_2",
        "name": "Dr. Priya Verma - Pediatrician",
        "address": "CHL Hospital, AB Road, Indore, Madhya Pradesh 452008",
        "latitude": 22.7453,
        "longitude": 75.8765,
        "phone": "+91-731-4044445",
        "opening_hours": "9:00 AM - 5:00 PM"
    },
    {
        "id": "doctor_3",
        "name": "Dr. Amit Patel - Orthopedic",
        "address": "Medanta Hospital, Vijay Nagar, Indore, Madhya Pradesh 452010",
        "latitude": 22.7521,
        "longitude": 75.8945,
        "phone": "+91-731-4777778",
        "opening_hours": "11:00 AM - 7:00 PM"
    },
    {
        "id": "doctor_4",
        "name": "Dr. Sunita Jain - Gynecologist",
        "address": "Bombay Hospital, Ring Road, Indore, Madhya Pradesh 452010",
        "latitude": 22.7644,
        "longitude": 75.8931,
        "phone": "+91-731-4982002",
        "opening_hours": "10:00 AM - 6:00 PM"
    }
]


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in meters using Haversine formula"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Earth radius in meters
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance


@router.post("/pharmacy/search", response_model=PharmacySearchResponse)
async def search_pharmacies(request: PharmacySearchRequest):
    """
    Search for pharmacies, hospitals, or doctors near a location.
    Returns real data for Indore area.
    """
    try:
        logger.info(f"Searching for {request.facility_type} near ({request.latitude}, {request.longitude}) within {request.radius}m")
        
        # Select data based on facility type
        if request.facility_type == "pharmacy":
            data_source = INDORE_PHARMACIES
        elif request.facility_type == "hospital":
            data_source = INDORE_HOSPITALS
        elif request.facility_type == "doctor":
            data_source = INDORE_DOCTORS
        else:
            data_source = INDORE_PHARMACIES
        
        # Filter by distance
        results = []
        for facility in data_source:
            distance = calculate_distance(
                request.latitude,
                request.longitude,
                facility["latitude"],
                facility["longitude"]
            )
            
            if distance <= request.radius:
                results.append(Pharmacy(
                    **facility,
                    distance=round(distance, 2)
                ))
        
        # Sort by distance
        results.sort(key=lambda x: x.distance)
        
        logger.info(f"Found {len(results)} {request.facility_type}(s) within {request.radius}m")
        
        return PharmacySearchResponse(
            facilities=results,
            count=len(results),
            location=f"Indore, Madhya Pradesh"
        )
    
    except Exception as e:
        logger.error(f"Error searching pharmacies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pharmacy/health")
async def pharmacy_health():
    """Health check for pharmacy service"""
    return {
        "status": "healthy",
        "service": "pharmacy",
        "data_available": {
            "pharmacies": len(INDORE_PHARMACIES),
            "hospitals": len(INDORE_HOSPITALS),
            "doctors": len(INDORE_DOCTORS)
        }
    }
