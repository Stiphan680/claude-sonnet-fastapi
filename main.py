from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import g4f
from datetime import datetime
import uuid

app = FastAPI(
    title="Free AI API - Claude Sonnet Alternative",
    description="FastAPI with Multiple Free AI Providers - No API Key Required!",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Message(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="List of messages")
    model: Optional[str] = Field(default="gpt-4", description="Model name")
    max_tokens: Optional[int] = Field(default=4096, description="Max tokens")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    stream: Optional[bool] = Field(default=False, description="Enable streaming")
    provider: Optional[str] = Field(default="auto", description="AI provider")

class ChatResponse(BaseModel):
    id: str
    model: str
    role: str
    content: str
    provider: str
    usage: Dict[str, int]

# Available providers configuration
AVAILABLE_PROVIDERS = {
    "auto": None,  # Auto-select best available
    "bing": g4f.Provider.Bing,
    "you": g4f.Provider.You,
    "phind": g4f.Provider.Phind,
    "deepinfra": g4f.Provider.DeepInfra,
    "blackbox": g4f.Provider.Blackbox,
}

def get_provider(provider_name: str):
    """Get provider object or auto-select"""
    if provider_name == "auto" or provider_name not in AVAILABLE_PROVIDERS:
        return None  # Let g4f auto-select
    return AVAILABLE_PROVIDERS[provider_name]

def convert_messages(messages: List[Message]) -> List[Dict[str, str]]:
    """Convert Pydantic messages to g4f format"""
    return [{"role": msg.role, "content": msg.content} for msg in messages]

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Free AI API - No Keys Required",
        "version": "2.0.0",
        "description": "Multiple free AI providers aggregated",
        "status": "active",
        "features": [
            "No API keys required",
            "Multiple AI providers",
            "Streaming support",
            "GPT-4 quality responses",
            "100% Free"
        ],
        "endpoints": {
            "/chat": "POST - Chat (non-streaming)",
            "/chat/stream": "POST - Chat (streaming)",
            "/v1/chat/completions": "POST - OpenAI compatible",
            "/health": "GET - Health check",
            "/providers": "GET - List available providers"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "free-ai-api",
        "api_key_required": False
    }

@app.get("/providers")
async def list_providers():
    """List all available AI providers"""
    return {
        "providers": list(AVAILABLE_PROVIDERS.keys()),
        "default": "auto",
        "description": "Use 'auto' for automatic provider selection"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint"""
    try:
        # Convert messages
        messages = convert_messages(request.messages)
        provider = get_provider(request.provider)
        
        # Generate response
        response_text = await asyncio.to_thread(
            g4f.ChatCompletion.create,
            model=request.model,
            messages=messages,
            provider=provider,
            temperature=request.temperature
        )
        
        # Calculate approximate token usage
        input_tokens = sum(len(msg.content.split()) for msg in request.messages)
        output_tokens = len(response_text.split())
        
        return ChatResponse(
            id=f"chat-{uuid.uuid4().hex[:8]}",
            model=request.model,
            role="assistant",
            content=response_text,
            provider=request.provider,
            usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    try:
        messages = convert_messages(request.messages)
        provider = get_provider(request.provider)
        
        async def generate():
            try:
                # Create streaming response
                response_generator = g4f.ChatCompletion.create(
                    model=request.model,
                    messages=messages,
                    provider=provider,
                    temperature=request.temperature,
                    stream=True
                )
                
                total_content = ""
                for chunk in response_generator:
                    if chunk:
                        total_content += chunk
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                        await asyncio.sleep(0)
                
                # Send completion message
                output_tokens = len(total_content.split())
                yield f"data: {json.dumps({'done': True, 'usage': {'output_tokens': output_tokens}})}\n\n"
            
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")
async def openai_compatible(request: ChatRequest):
    """OpenAI-compatible endpoint"""
    try:
        messages = convert_messages(request.messages)
        provider = get_provider(request.provider)
        
        if request.stream:
            # Streaming response
            async def generate():
                try:
                    response_generator = g4f.ChatCompletion.create(
                        model=request.model,
                        messages=messages,
                        provider=provider,
                        temperature=request.temperature,
                        stream=True
                    )
                    
                    chunk_id = 0
                    for text in response_generator:
                        if text:
                            chunk = {
                                "id": f"chatcmpl-{chunk_id}",
                                "object": "chat.completion.chunk",
                                "created": int(datetime.utcnow().timestamp()),
                                "model": request.model,
                                "choices": [{
                                    "index": 0,
                                    "delta": {"content": text},
                                    "finish_reason": None
                                }]
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"
                            chunk_id += 1
                            await asyncio.sleep(0)
                    
                    # Final chunk
                    final = {
                        "id": f"chatcmpl-{chunk_id}",
                        "object": "chat.completion.chunk",
                        "created": int(datetime.utcnow().timestamp()),
                        "model": request.model,
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                    }
                    yield f"data: {json.dumps(final)}\n\n"
                    yield "data: [DONE]\n\n"
                
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        else:
            # Non-streaming response
            response_text = await asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=messages,
                provider=provider,
                temperature=request.temperature
            )
            
            input_tokens = sum(len(msg.content.split()) for msg in request.messages)
            output_tokens = len(response_text.split())
            
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(datetime.utcnow().timestamp()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))