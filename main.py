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
    title="Expert Code AI API",
    description="Free Forever - No Upgrade Messages",
    version="3.0.4"
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
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

@app.get("/")
async def root():
    return {
        "status": "active",
        "version": "3.0.4",
        "message": "No Blackbox - Free Forever"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Convert messages
        msgs = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Let g4f auto-select provider (it will try multiple)
        # We'll filter blackbox messages in response
        response_text = await asyncio.wait_for(
            asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=msgs,
                # NO provider specified - let g4f choose
            ),
            timeout=30.0
        )
        
        # Convert to string
        content = str(response_text)
        
        # 🔥 FILTER OUT BLACKBOX UPGRADE MESSAGES
        blackbox_phrases = [
            "You have not upgraded your account",
            "Please upgrade to a premium plan",
            "upgrade to premium",
            "blackbox.ai/pricing",
            "upgrade-required"
        ]
        
        # Check if response contains blackbox upgrade message
        is_blackbox_msg = any(phrase.lower() in content.lower() for phrase in blackbox_phrases)
        
        if is_blackbox_msg:
            # Blackbox detected! Try again with different approach
            # Return a clean error-free response
            content = "I'm here to help! Could you please rephrase your question?"
        
        return {
            "id": f"chat-{uuid.uuid4().hex[:8]}",
            "content": content,
            "model": request.model,
            "filtered": is_blackbox_msg
        }
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        # Don't crash, return helpful message
        return {
            "id": f"chat-error-{uuid.uuid4().hex[:8]}",
            "content": f"Service temporarily unavailable. Please try again. ({str(e)[:50]})",
            "error": True
        }

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        msgs = [{"role": m.role, "content": m.content} for m in request.messages]
        
        async def generate():
            try:
                full_response = ""
                response_gen = g4f.ChatCompletion.create(
                    model=request.model,
                    messages=msgs,
                    stream=True
                )
                
                for chunk in response_gen:
                    if chunk:
                        chunk_str = str(chunk)
                        full_response += chunk_str
                        
                        # Don't stream if it's a blackbox message
                        if "upgrade" not in chunk_str.lower():
                            yield f"data: {json.dumps({'content': chunk_str})}\n\n"
                            await asyncio.sleep(0)
                
                # Check final response
                blackbox_phrases = ["upgrade your account", "premium plan", "blackbox.ai"]
                if any(p in full_response.lower() for p in blackbox_phrases):
                    yield f"data: {json.dumps({'content': 'Response filtered. Please try again.', 'filtered': True})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)[:100]})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:100])

@app.post("/code")
async def code(request: ChatRequest):
    request.temperature = 0.2
    return await chat(request)

@app.post("/v1/chat/completions")
async def openai_compat(request: ChatRequest):
    result = await chat(request)
    return {
        "id": result.get("id"),
        "object": "chat.completion",
        "created": int(datetime.utcnow().timestamp()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": result.get("content")},
            "finish_reason": "stop"
        }]
    }

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))