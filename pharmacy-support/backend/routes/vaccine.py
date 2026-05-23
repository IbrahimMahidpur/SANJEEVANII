from fastapi import APIRouter, HTTPException
from models import VaccineCenterRequest, VaccineCenterResponse, VaccineCenter, VaccineSession
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["vaccine"])


@router.post("/vaccine-centers", response_model=VaccineCenterResponse)
async def get_vaccine_centers(request: VaccineCenterRequest):
    """
    Fetch real vaccination centers from CoWIN API.
    No fallback data - shows actual government data or error.
    """
    try:
        # CoWIN API endpoint
        url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin"
        
        params = {
            "pincode": request.pincode,
            "date": request.date
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }
        
        logger.info(f"Fetching CoWIN data for pincode: {request.pincode}, date: {request.date}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Transform CoWIN response to our format
            centers = []
            for center_data in data.get("centers", []):
                sessions = []
                for session_data in center_data.get("sessions", []):
                    sessions.append(VaccineSession(
                        date=session_data.get("date", ""),
                        available_capacity=session_data.get("available_capacity", 0),
                        vaccine=session_data.get("vaccine", ""),
                        min_age_limit=session_data.get("min_age_limit", 18),
                        slots=session_data.get("slots", [])
                    ))
                
                centers.append(VaccineCenter(
                    center_id=center_data.get("center_id", 0),
                    name=center_data.get("name", ""),
                    address=center_data.get("address", ""),
                    pincode=center_data.get("pincode", ""),
                    sessions=sessions
                ))
            
            logger.info(f"Successfully fetched {len(centers)} vaccination centers from CoWIN")
            return VaccineCenterResponse(centers=centers)
    
    except httpx.HTTPStatusError as e:
        logger.error(f"CoWIN API HTTP error: {e.response.status_code} - {str(e)}")
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="No vaccination centers found for this PIN code. Please try a different PIN code.")
        elif e.response.status_code == 403:
            raise HTTPException(status_code=403, detail="Access denied by CoWIN API. Please wait a moment and try again.")
        else:
            raise HTTPException(status_code=503, detail="CoWIN API is temporarily unavailable. Please try again later.")
    
    except httpx.TimeoutException:
        logger.error("CoWIN API timeout")
        raise HTTPException(status_code=504, detail="CoWIN API request timed out. Please try again.")
    
    except httpx.RequestError as e:
        logger.error(f"CoWIN API connection error: {str(e)}")
        raise HTTPException(status_code=503, detail="Unable to connect to CoWIN API. Please check your internet connection and try again.")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

