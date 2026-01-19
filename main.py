from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import anthropic
import os
import json
import asyncio
from datetime import datetime

app = FastAPI(
    title="Claude Sonnet 3.5 API",
    description="FastAPI with Claude Sonnet 3.5 Streaming Support",
    version="1.0.0"
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
    model: Optional[str] = Field(default="claude-3-5-sonnet-20241022", description="Model name")
    max_tokens: Optional[int] = Field(default=8096, description="Max tokens to generate")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    stream: Optional[bool] = Field(default=False, description="Enable streaming")

class ChatResponse(BaseModel):
    id: str
    model: str
    role: str
    content: str
    stop_reason: Optional[str]
    usage: Dict[str, int]

# Initialize Anthropic client
def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    return anthropic.Anthropic(api_key=api_key)

# Custom API key validation
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    custom_key = os.getenv("CUSTOM_API_KEY")
    if custom_key and x_api_key != custom_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Claude Sonnet 3.5 FastAPI",
        "version": "1.0.0",
        "model": "claude-3-5-sonnet-20241022",
        "status": "active",
        "endpoints": {
            "/chat": "POST - Chat with Claude (non-streaming)",
            "/chat/stream": "POST - Chat with Claude (streaming)",
            "/v1/chat/completions": "POST - OpenAI-compatible endpoint",
            "/health": "GET - Health check"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "claude-sonnet-api"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint"""
    try:
        client = get_anthropic_client()
        
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Create message
        response = client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            messages=anthropic_messages
        )
        
        return ChatResponse(
            id=response.id,
            model=response.model,
            role=response.role,
            content=response.content[0].text,
            stop_reason=response.stop_reason,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        )
    
    except anthropic.APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    try:
        client = get_anthropic_client()
        
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        async def generate():
            try:
                with client.messages.stream(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    messages=anthropic_messages
                ) as stream:
                    for text in stream.text_stream:
                        # SSE format
                        yield f"data: {json.dumps({'content': text})}\n\n"
                        await asyncio.sleep(0)  # Allow other tasks to run
                    
                    # Send final message
                    final_message = stream.get_final_message()
                    yield f"data: {json.dumps({'done': True, 'usage': {'input_tokens': final_message.usage.input_tokens, 'output_tokens': final_message.usage.output_tokens}})}\n\n"
            
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
        client = get_anthropic_client()
        
        # Convert messages
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        if request.stream:
            # Streaming response
            async def generate():
                try:
                    with client.messages.stream(
                        model=request.model,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature,
                        messages=anthropic_messages
                    ) as stream:
                        chunk_id = 0
                        for text in stream.text_stream:
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
                        final_chunk = {
                            "id": f"chatcmpl-{chunk_id}",
                            "object": "chat.completion.chunk",
                            "created": int(datetime.utcnow().timestamp()),
                            "model": request.model,
                            "choices": [{
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop"
                            }]
                        }
                        yield f"data: {json.dumps(final_chunk)}\n\n"
                        yield "data: [DONE]\n\n"
                
                except Exception as e:
                    error_chunk = {"error": str(e)}
                    yield f"data: {json.dumps(error_chunk)}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        
        else:
            # Non-streaming response
            response = client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=anthropic_messages
            )
            
            return {
                "id": response.id,
                "object": "chat.completion",
                "created": int(datetime.utcnow().timestamp()),
                "model": response.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": response.role,
                        "content": response.content[0].text
                    },
                    "finish_reason": response.stop_reason
                }],
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
    
    except anthropic.APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))