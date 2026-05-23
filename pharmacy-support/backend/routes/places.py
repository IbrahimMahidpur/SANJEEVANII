from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["places"])

# Google Places API Key (from environment or config)
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyDw9gsbzxtG8EYwbK-ntmLJa9gsbzxtG8EYwbK")


class PlacesSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 5000  # meters
    place_type: str = "pharmacy"  # pharmacy, hospital, doctor


class Place(BaseModel):
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    opening_hours: Optional[str] = None
    is_open_now: Optional[bool] = None
    distance: Optional[float] = None


class PlacesSearchResponse(BaseModel):
    places: List[Place]
    count: int
    status: str


def map_place_type(place_type: str) -> str:
    """Map our types to Google Places types"""
    type_mapping = {
        "pharmacy": "pharmacy",
        "hospital": "hospital",
        "doctor": "doctor"
    }
    return type_mapping.get(place_type, "pharmacy")


@router.post("/places/search", response_model=PlacesSearchResponse)
async def search_places(request: PlacesSearchRequest):
    """
    Search for places using Google Places API (Nearby Search).
    Returns real, live data for pharmacies, hospitals, and doctors.
    """
    try:
        google_type = map_place_type(request.place_type)
        
        # Google Places API Nearby Search endpoint
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        params = {
            "location": f"{request.latitude},{request.longitude}",
            "radius": request.radius,
            "type": google_type,
            "key": GOOGLE_API_KEY
        }
        
        logger.info(f"Searching Google Places for {google_type} near ({request.latitude}, {request.longitude}) within {request.radius}m")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                if data.get("status") == "ZERO_RESULTS":
                    logger.info(f"No {google_type}s found in the area")
                    return PlacesSearchResponse(places=[], count=0, status="ZERO_RESULTS")
                else:
                    logger.error(f"Google Places API error: {data.get('status')}")
                    raise HTTPException(status_code=500, detail=f"Google Places API error: {data.get('status')}")
            
            # Transform Google Places response
            places = []
            for result in data.get("results", []):
                geometry = result.get("geometry", {})
                location = geometry.get("location", {})
                
                # Get opening hours
                opening_hours = result.get("opening_hours", {})
                is_open = opening_hours.get("open_now")
                
                place = Place(
                    place_id=result.get("place_id", ""),
                    name=result.get("name", ""),
                    address=result.get("vicinity", ""),
                    latitude=location.get("lat", 0),
                    longitude=location.get("lng", 0),
                    rating=result.get("rating"),
                    user_ratings_total=result.get("user_ratings_total"),
                    is_open_now=is_open
                )
                places.append(place)
            
            logger.info(f"Found {len(places)} {google_type}(s) from Google Places API")
            
            return PlacesSearchResponse(
                places=places,
                count=len(places),
                status="OK"
            )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Places API HTTP error: {e}")
        raise HTTPException(status_code=503, detail="Google Places API is unavailable")
    
    except httpx.TimeoutException:
        logger.error("Google Places API timeout")
        raise HTTPException(status_code=504, detail="Google Places API request timed out")
    
    except Exception as e:
        logger.error(f"Error searching places: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/places/{place_id}/details")
async def get_place_details(place_id: str):
    """
    Get detailed information about a specific place including phone number.
    """
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,opening_hours,rating,user_ratings_total,geometry",
            "key": GOOGLE_API_KEY
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                raise HTTPException(status_code=404, detail="Place not found")
            
            result = data.get("result", {})
            return {
                "name": result.get("name"),
                "address": result.get("formatted_address"),
                "phone": result.get("formatted_phone_number"),
                "rating": result.get("rating"),
                "opening_hours": result.get("opening_hours", {}).get("weekday_text", [])
            }
    
    except Exception as e:
        logger.error(f"Error getting place details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/places/health")
async def places_health():
    """Health check for Google Places API integration"""
    return {
        "status": "healthy",
        "service": "google_places",
        "api_key_configured": bool(GOOGLE_API_KEY)
    }
