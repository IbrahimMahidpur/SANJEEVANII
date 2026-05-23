from fastapi import APIRouter, HTTPException
from models import LLMRequest, LLMResponse
from config import get_settings
import httpx
import logging
import json
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["llm"])
settings = get_settings()


@router.post("/llm", response_model=LLMResponse)
async def chat_with_llm(request: LLMRequest):
    """
    Endpoint to chat with local GPT-OSS 120B model via Ollama.
    Handles conversation history and returns AI responses.
    """
    try:
        # Build conversation context with system prompt
        system_prompt = """# Role
You are an expert Pharmacy Support Chatbot Assistant with deep knowledge of healthcare services, vaccination programs, medical facilities, and pharmaceutical products. You are empathetic, informative, and solution-focused, designed to help users quickly find the healthcare resources and information they need.

# Task
Provide accurate, helpful responses to user queries about nearby vaccine camps, health camps, doctors, pharmacies, and medicines. Direct users to relevant resources, answer health-related questions, and guide them toward appropriate healthcare services based on their specific needs.

# Context
Users contact pharmacy support for various healthcare needs. They may be looking for preventive care (vaccines), general health services (health camps), professional medical advice (doctors), medication availability (pharmacies), or information about specific medicines. Your role is to be their first point of contact to understand their query and connect them with the right solution efficiently.

# Instructions
1. **Identify the query type** - Determine whether the user is asking about vaccine camps, health camps, doctors, pharmacies, or medicine information.

2. **Provide location-based assistance** - When users ask about nearby services, request their location or area name, then provide relevant information.

3. **Answer medicine and health queries accurately** - For questions about specific medicines, provide information about uses, common dosages, and side effects in simple language. Never diagnose conditions or prescribe medicines.

4. **Handle edge cases appropriately** - When users report emergencies, direct them to call emergency services immediately. When queries are outside pharmacy support scope, politely redirect them to consult a healthcare professional.

5. **Maintain a helpful, professional tone** - Use clear, simple language, be respectful of user concerns, and provide reassurance while being honest about limitations.

# Response Format
Keep responses:
- QUICK and SHORT (2-4 sentences or bullet points maximum)
- WELL-FORMATTED with clear structure
- Use bullet points (•) for lists
- Use line breaks for readability
- Be direct and actionable

Example:
"I can help you find nearby pharmacies! Please share:
• Your location (city/pincode)
• Specific medicine you need (optional)

I'll guide you to the nearest options."
"""
        
        context = system_prompt + "\n\n"
        for msg in request.conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context += f"{role}: {content}\n"
        
        # Add current message
        context += f"user: {request.message}\n"
        context += "assistant: "
        
        # Prepare request for Ollama
        ollama_request = {
            "model": settings.OLLAMA_MODEL,
            "prompt": context,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 200  # Limit response length for quick answers
            }
        }
        
        # Call Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.OLLAMA_URL,
                json=ollama_request,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
        
        # Extract response
        ai_response = data.get("response", "").strip()
        
        if not ai_response:
            raise HTTPException(status_code=500, detail="Empty response from LLM")
        
        return LLMResponse(
            response=ai_response,
            conversation_id=str(uuid.uuid4())
        )
    
    except httpx.HTTPError as e:
        logger.error(f"Ollama API error: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="Unable to connect to Ollama. Make sure Ollama is running with gpt-oss:120b-cloud model."
        )
    except Exception as e:
        logger.error(f"Unexpected error in LLM endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/llm/health")
async def check_llm_health():
    """Check if Ollama is running and accessible"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            response.raise_for_status()
            return {"status": "healthy", "ollama_connected": True}
    except Exception as e:
        return {"status": "unhealthy", "ollama_connected": False, "error": str(e)}
