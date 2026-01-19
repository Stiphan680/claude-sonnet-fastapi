from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import asyncio
import json
import g4f
from datetime import datetime
import uuid

app = FastAPI(
    title="Expert Code AI API - NO BLACKBOX!",
    description="Free Forever | No Upgrade Messages!",
    version="3.0.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ SAFE PROVIDERS ONLY - NO BLACKBOX!
def get_safe_provider(provider_name: str = "auto"):
    """🚫 NEVER returns Blackbox! Always returns safe provider."""
    
    # Block blackbox explicitly
    if provider_name and "blackbox" in provider_name.lower():
        return g4f.Provider.DeepInfra
    
    providers_map = {
        "deepinfra": g4f.Provider.DeepInfra,
        "phind": g4f.Provider.Phind,
        "you": g4f.Provider.You,
        "bing": g4f.Provider.Bing,
    }
    
    # Return requested provider or default to DeepInfra
    return providers_map.get(provider_name.lower(), g4f.Provider.DeepInfra)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-4"
    max_tokens: Optional[int] = 8192
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    provider: Optional[str] = "auto"

class ChatResponse(BaseModel):
    id: str
    model: str
    role: str
    content: str
    provider: str
    usage: Dict[str, int]

@app.get("/")
async def root():
    return {
        "name": "Expert Code AI API",
        "version": "3.0.3",
        "status": "active",
        "message": "🚫 NO BLACKBOX! No upgrade messages!",
        "providers": ["deepinfra", "phind", "you", "bing"],
        "blocked": ["blackbox"],
        "free": True
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "blackbox_blocked": True
    }

@app.get("/providers")
async def providers():
    return {
        "available": ["deepinfra", "phind", "you", "bing"],
        "blocked": ["blackbox"],
        "default": "deepinfra"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Convert messages
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Get SAFE provider (never blackbox!)
        provider = get_safe_provider(request.provider)
        
        # Generate response
        response_text = await asyncio.wait_for(
            asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=messages,
                provider=provider,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ),
            timeout=30.0
        )
        
        # Calculate tokens (approximate)
        input_tokens = sum(len(m.content.split()) for m in request.messages)
        output_tokens = len(str(response_text).split())
        
        return ChatResponse(
            id=f"chat-{uuid.uuid4().hex[:8]}",
            model=request.model,
            role="assistant",
            content=str(response_text),
            provider="safe_provider",
            usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
        )
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        provider = get_safe_provider(request.provider)
        
        async def generate():
            try:
                response_gen = g4f.ChatCompletion.create(
                    model=request.model,
                    messages=messages,
                    provider=provider,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=True
                )
                
                for chunk in response_gen:
                    if chunk:
                        yield f"data: {json.dumps({'content': str(chunk)})}\n\n"
                        await asyncio.sleep(0)
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/code")
async def code(request: ChatRequest):
    request.temperature = 0.2
    return await chat(request)

@app.post("/code/stream")
async def code_stream(request: ChatRequest):
    request.temperature = 0.2
    return await chat_stream(request)

@app.post("/v1/chat/completions")
async def openai_compat(request: ChatRequest):
    try:
        chat_response = await chat(request)
        
        return {
            "id": chat_response.id,
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": chat_response.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": chat_response.content
                },
                "finish_reason": "stop"
            }],
            "usage": chat_response.usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    print("✅ API Starting - NO BLACKBOX!")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))