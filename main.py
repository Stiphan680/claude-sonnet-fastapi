from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime
import uuid

# Try importing g4f, handle if not available
try:
    import g4f
    from g4f.Provider import Bing, You
    G4F_AVAILABLE = True
except:
    G4F_AVAILABLE = False

app = FastAPI(
    title="Free AI API",
    description="100% Free - No Limits",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

@app.get("/")
async def root():
    return {
        "status": "active",
        "version": "4.0.0",
        "g4f_available": G4F_AVAILABLE,
        "message": "Free AI API - Working!"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "g4f_status": "available" if G4F_AVAILABLE else "unavailable"
    }

async def generate_with_g4f(messages, model, temperature):
    """Generate response using g4f with multiple provider fallbacks"""
    
    if not G4F_AVAILABLE:
        return "G4F library not available. Please check deployment."
    
    # Providers to try in order (stable ones only)
    providers_to_try = [
        You,    # Most stable
        Bing,   # Backup
        None,   # Let g4f auto-select
    ]
    
    last_error = None
    
    for provider in providers_to_try:
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    g4f.ChatCompletion.create,
                    model=model,
                    messages=messages,
                    provider=provider
                ),
                timeout=25.0
            )
            
            # Convert to string and return if valid
            result = str(response)
            if result and len(result) > 10:
                return result
                
        except asyncio.TimeoutError:
            last_error = "Request timeout"
            continue
        except Exception as e:
            last_error = str(e)
            continue
    
    # All providers failed
    return f"All providers busy. Please try again in a moment. (Last: {last_error})"

@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint with bulletproof error handling"""
    
    try:
        # Convert messages to dict format
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Generate response
        content = await generate_with_g4f(
            messages=messages,
            model=request.model,
            temperature=request.temperature
        )
        
        return {
            "id": f"chat-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": request.model,
            "content": content,
            "role": "assistant",
            "usage": {
                "total_tokens": len(content.split())
            }
        }
        
    except Exception as e:
        # Never return 500 - always return valid response
        return {
            "id": f"chat-error-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": request.model,
            "content": f"Service temporarily busy. Please try again. (Error: {str(e)[:30]})",
            "role": "assistant",
            "error": True
        }

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming endpoint"""
    
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    async def generate():
        try:
            if not G4F_AVAILABLE:
                yield f"data: {json.dumps({'content': 'Service unavailable'})}\n\n"
                return
            
            response = g4f.ChatCompletion.create(
                model=request.model,
                messages=messages,
                provider=You,  # Use stable provider
                stream=True
            )
            
            for chunk in response:
                if chunk:
                    yield f"data: {json.dumps({'content': str(chunk)})}\n\n"
                    await asyncio.sleep(0)
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)[:50]})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.post("/code")
async def code_gen(request: ChatRequest):
    """Code generation endpoint"""
    request.temperature = 0.2
    return await chat(request)

@app.post("/v1/chat/completions")
async def openai_compatible(request: ChatRequest):
    """OpenAI compatible endpoint"""
    result = await chat(request)
    
    return {
        "id": result.get("id"),
        "object": "chat.completion",
        "created": result.get("created"),
        "model": result.get("model"),
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": result.get("content")
            },
            "finish_reason": "stop"
        }],
        "usage": result.get("usage", {})
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting API on port {port}")
    print(f"✅ G4F Status: {'Available' if G4F_AVAILABLE else 'Unavailable'}")
    uvicorn.run(app, host="0.0.0.0", port=port)