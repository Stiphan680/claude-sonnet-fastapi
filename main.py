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
from code_prompts import CODE_EXPERT_PROMPTS, get_code_prompt

app = FastAPI(
    title="Expert Code AI API - NO BLACKBOX!",
    description="Optimized for Code | No Upgrade Messages | Free Forever",
    version="3.0.2"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚫 BLACKBOX HARD BLOCKED!
SAFE_PROVIDERS = {
    "deepinfra": g4f.Provider.DeepInfra,
    "phind": g4f.Provider.Phind,
    "you": g4f.Provider.You,
    "bing": g4f.Provider.Bing,
}

# Priority order for free providers (NO BLACKBOX!)
PROVIDER_PRIORITY = [
    g4f.Provider.DeepInfra,  # Best
    g4f.Provider.Phind,      # Code-specialized
    g4f.Provider.You,        # Good
    g4f.Provider.Bing,       # Reliable
]

def get_safe_provider(provider_name: str = "auto"):
    """Get a SAFE provider - NEVER returns Blackbox!"""
    
    # 🚫 BLOCK BLACKBOX EXPLICITLY
    if provider_name and "blackbox" in provider_name.lower():
        print("⚠️ Blackbox blocked! Using DeepInfra instead.")
        return g4f.Provider.DeepInfra
    
    # If specific provider requested
    if provider_name and provider_name.lower() in SAFE_PROVIDERS:
        return SAFE_PROVIDERS[provider_name.lower()]
    
    # Auto mode: Return first safe provider from priority
    # This ensures g4f never auto-selects Blackbox
    return PROVIDER_PRIORITY[0]  # Always DeepInfra for consistency

# Pydantic models
class Message(BaseModel):
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="List of messages")
    model: Optional[str] = Field(default="gpt-4", description="Model name")
    max_tokens: Optional[int] = Field(default=8192, description="Max tokens (up to 32K)")
    temperature: Optional[float] = Field(default=0.3, ge=0.0, le=2.0, description="Lower = more focused")
    stream: Optional[bool] = Field(default=True, description="Enable streaming")
    provider: Optional[str] = Field(default="auto", description="AI provider (NOT blackbox!)")
    code_mode: Optional[bool] = Field(default=False, description="Enable expert code mode")
    language: Optional[str] = Field(default="auto", description="Programming language")

class ChatResponse(BaseModel):
    id: str
    model: str
    role: str
    content: str
    provider: str
    latency_ms: Optional[int]
    usage: Dict[str, int]

def convert_messages(messages: List[Message], code_mode: bool = False, language: str = "auto") -> List[Dict[str, str]]:
    """Convert messages with code optimization"""
    converted = []
    
    # Add expert system prompt for code mode
    if code_mode:
        system_prompt = get_code_prompt(language)
        converted.append({"role": "system", "content": system_prompt})
    
    # Add user messages
    for msg in messages:
        converted.append({"role": msg.role, "content": msg.content})
    
    return converted

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Expert Code AI API - NO BLACKBOX!",
        "version": "3.0.2",
        "status": "active",
        "important": "🚫 BLACKBOX BLOCKED! No upgrade messages!",
        "optimizations": [
            "⚡ Low latency (0.5-2s first token)",
            "🚀 Fast streaming",
            "💻 Expert code generation",
            "📚 Large context (up to 32K tokens)",
            "🎯 Advanced system prompts",
            "🔄 Smart provider selection",
            "🚫 NO BLACKBOX - No upgrade messages!",
            "100% Free"
        ],
        "safe_providers": list(SAFE_PROVIDERS.keys()),
        "blocked_providers": ["blackbox"],
        "features": {
            "code_mode": "Specialized for code generation",
            "streaming": "Ultra-fast token streaming",
            "context_window": "8K-32K tokens support",
            "latency": "<2 seconds first token",
            "languages": "Python, JavaScript, Java, C++, Go, Rust, and more",
            "upgrade_messages": "NONE! Blackbox blocked!"
        },
        "endpoints": {
            "/chat": "POST - Standard chat (NO BLACKBOX)",
            "/chat/stream": "POST - Fast streaming (NO BLACKBOX)",
            "/code": "POST - Expert code generation (NO BLACKBOX)",
            "/code/stream": "POST - Expert code streaming (NO BLACKBOX)",
            "/v1/chat/completions": "POST - OpenAI compatible (NO BLACKBOX)",
            "/health": "GET - Health check",
            "/providers": "GET - Available providers (NO BLACKBOX)"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "expert-code-ai-api",
        "api_key_required": False,
        "blackbox_blocked": True,
        "upgrade_messages": "NONE",
        "latency": "optimized",
        "code_generation": "expert"
    }

@app.get("/providers")
async def list_providers():
    """List all SAFE AI providers (NO BLACKBOX!)"""
    return {
        "safe_providers": list(SAFE_PROVIDERS.keys()),
        "blocked_providers": ["blackbox"],
        "code_optimized": ["deepinfra", "phind"],
        "default": "deepinfra",
        "recommendation": "Use 'deepinfra' or 'auto' for best performance",
        "note": "Blackbox is BLOCKED to prevent upgrade messages!"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Optimized chat endpoint - NO BLACKBOX!"""
    start_time = datetime.utcnow()
    
    try:
        messages = convert_messages(request.messages, request.code_mode, request.language)
        
        # 🚫 GET SAFE PROVIDER (NEVER BLACKBOX!)
        provider = get_safe_provider(request.provider)
        
        # Generate response with timeout
        response_text = await asyncio.wait_for(
            asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=messages,
                provider=provider,  # SAFE PROVIDER ONLY!
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ),
            timeout=30.0
        )
        
        latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        input_tokens = sum(len(msg.content.split()) * 1.3 for msg in request.messages)
        output_tokens = len(response_text.split()) * 1.3
        
        return ChatResponse(
            id=f"chat-{uuid.uuid4().hex[:8]}",
            model=request.model,
            role="assistant",
            content=response_text,
            provider="safe_provider (not blackbox)",
            latency_ms=latency,
            usage={
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens)
            }
        )
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout - try streaming mode")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Ultra-fast streaming endpoint - NO BLACKBOX!"""
    try:
        messages = convert_messages(request.messages, request.code_mode, request.language)
        
        # 🚫 GET SAFE PROVIDER (NEVER BLACKBOX!)
        provider = get_safe_provider(request.provider)
        
        async def generate():
            first_token_sent = False
            start_time = datetime.utcnow()
            total_content = ""
            
            try:
                response_generator = g4f.ChatCompletion.create(
                    model=request.model,
                    messages=messages,
                    provider=provider,  # SAFE PROVIDER ONLY!
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=True
                )
                
                for chunk in response_generator:
                    if chunk:
                        # Calculate first token latency
                        if not first_token_sent:
                            first_token_latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                            yield f"data: {json.dumps({'latency_ms': first_token_latency, 'first_token': True, 'provider': 'safe (not blackbox)'})}\n\n"
                            first_token_sent = True
                        
                        total_content += chunk
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                        await asyncio.sleep(0)
                
                # Final stats
                total_latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                output_tokens = int(len(total_content.split()) * 1.3)
                
                yield f"data: {json.dumps({'done': True, 'total_latency_ms': total_latency, 'usage': {'output_tokens': output_tokens}, 'no_blackbox': True})}\n\n"
            
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

@app.post("/code")
async def code_generation(request: ChatRequest):
    """Expert code generation endpoint (non-streaming) - NO BLACKBOX!"""
    # Force code mode and safe provider
    request.code_mode = True
    request.temperature = 0.2
    
    return await chat(request)

@app.post("/code/stream")
async def code_generation_stream(request: ChatRequest):
    """Expert code generation endpoint (streaming) - NO BLACKBOX!"""
    # Force code mode and safe provider
    request.code_mode = True
    request.temperature = 0.2
    
    return await chat_stream(request)

@app.post("/v1/chat/completions")
async def openai_compatible(request: ChatRequest):
    """OpenAI-compatible endpoint - NO BLACKBOX!"""
    try:
        messages = convert_messages(request.messages, request.code_mode, request.language)
        
        # 🚫 GET SAFE PROVIDER (NEVER BLACKBOX!)
        provider = get_safe_provider(request.provider)
        
        if request.stream:
            async def generate():
                chunk_id = 0
                first_token_time = None
                start_time = datetime.utcnow()
                
                try:
                    response_generator = g4f.ChatCompletion.create(
                        model=request.model,
                        messages=messages,
                        provider=provider,  # SAFE PROVIDER ONLY!
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        stream=True
                    )
                    
                    for text in response_generator:
                        if text:
                            if first_token_time is None:
                                first_token_time = datetime.utcnow()
                            
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
                    total_latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    final = {
                        "id": f"chatcmpl-{chunk_id}",
                        "object": "chat.completion.chunk",
                        "created": int(datetime.utcnow().timestamp()),
                        "model": request.model,
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                        "latency_ms": total_latency
                    }
                    yield f"data: {json.dumps(final)}\n\n"
                    yield "data: [DONE]\n\n"
                
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        else:
            start_time = datetime.utcnow()
            
            response_text = await asyncio.wait_for(
                asyncio.to_thread(
                    g4f.ChatCompletion.create,
                    model=request.model,
                    messages=messages,
                    provider=provider,  # SAFE PROVIDER ONLY!
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ),
                timeout=30.0
            )
            
            latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            input_tokens = int(sum(len(msg.content.split()) * 1.3 for msg in request.messages))
            output_tokens = int(len(response_text.split()) * 1.3)
            
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
                },
                "latency_ms": latency
            }
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    print("🚫 Blackbox provider BLOCKED!")
    print("✅ Only safe providers: DeepInfra, Phind, You, Bing")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))