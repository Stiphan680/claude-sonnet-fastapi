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
from providers_config import get_best_code_provider, FAST_PROVIDERS

app = FastAPI(
    title="Expert Code AI API - Ultra Fast & Large Context",
    description="Optimized for Code | Low Latency | Up to 1M Tokens Support | Advanced Prompts",
    version="3.1.0"
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
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="List of messages")
    model: Optional[str] = Field(default="gpt-4", description="Model name")
    max_tokens: Optional[int] = Field(
        default=8192, 
        ge=1,
        le=1000000,
        description="Max tokens to generate (1 to 1,000,000). Note: Actual limit depends on provider."
    )
    temperature: Optional[float] = Field(default=0.3, ge=0.0, le=2.0, description="Lower = more focused")
    stream: Optional[bool] = Field(default=True, description="Enable streaming")
    provider: Optional[str] = Field(default="auto", description="AI provider")
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
    token_limit_info: Optional[Dict[str, Any]] = None

def get_token_limit_info(requested_tokens: int, provider: str) -> Dict[str, Any]:
    """Provide information about token limits"""
    provider_limits = {
        "deepinfra": {"typical": 32000, "max": 100000},
        "phind": {"typical": 16000, "max": 32000},
        "blackbox": {"typical": 8000, "max": 16000},
        "you": {"typical": 8000, "max": 16000},
        "bing": {"typical": 4000, "max": 8000},
        "auto": {"typical": 32000, "max": 100000}
    }
    
    limit = provider_limits.get(provider, provider_limits["auto"])
    
    return {
        "requested": requested_tokens,
        "provider_typical": limit["typical"],
        "provider_max": limit["max"],
        "will_use": min(requested_tokens, limit["max"]),
        "note": f"Provider may use up to {limit['max']} tokens. For larger contexts, response may be truncated."
    }

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

def get_provider_for_code(provider_name: str, code_mode: bool):
    """Get optimized provider for code generation"""
    if code_mode and provider_name == "auto":
        return get_best_code_provider()
    
    if provider_name in FAST_PROVIDERS:
        return FAST_PROVIDERS[provider_name]
    
    return None  # Auto-select

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Expert Code AI API - Ultra Fast & Large Context",
        "version": "3.1.0",
        "status": "active",
        "optimizations": [
            "⚡ Low latency (0.5-2s first token)",
            "🚀 Fast streaming",
            "💻 Expert code generation",
            "📚 Large context (up to 1M tokens requested)",
            "🎯 Advanced system prompts",
            "🔄 Smart provider selection",
            "100% Free"
        ],
        "features": {
            "code_mode": "Specialized for code generation",
            "streaming": "Ultra-fast token streaming",
            "max_tokens_api_limit": "1,000,000 (1M)",
            "typical_provider_limit": "8K-100K tokens",
            "latency": "<2 seconds first token",
            "languages": "Python, JavaScript, Java, C++, Go, Rust, and more"
        },
        "token_info": {
            "api_accepts": "1 to 1,000,000 tokens",
            "provider_limits": "Vary by provider (8K-100K typical)",
            "recommendation": "Use 8K-32K for best compatibility",
            "large_context": "100K+ may be truncated by providers"
        },
        "endpoints": {
            "/chat": "POST - Standard chat",
            "/chat/stream": "POST - Fast streaming",
            "/code": "POST - Expert code generation",
            "/code/stream": "POST - Expert code streaming",
            "/v1/chat/completions": "POST - OpenAI compatible",
            "/health": "GET - Health check",
            "/providers": "GET - Available providers",
            "/token-limits": "GET - Token limit information"
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
        "latency": "optimized",
        "code_generation": "expert",
        "max_tokens_supported": "1M (provider-dependent)"
    }

@app.get("/providers")
async def list_providers():
    """List all available AI providers"""
    return {
        "fast_providers": list(FAST_PROVIDERS.keys()),
        "code_optimized": ["deepinfra", "phind", "blackbox"],
        "default": "auto",
        "recommendation": "Use 'auto' for best performance"
    }

@app.get("/token-limits")
async def token_limits_info():
    """Information about token limits by provider"""
    return {
        "api_accepts": {
            "minimum": 1,
            "maximum": 1000000,
            "default": 8192
        },
        "provider_capabilities": {
            "deepinfra": {"typical": "32K", "max": "100K", "recommended": True},
            "phind": {"typical": "16K", "max": "32K", "recommended": True},
            "blackbox": {"typical": "8K", "max": "16K", "recommended": False},
            "you": {"typical": "8K", "max": "16K", "recommended": False},
            "bing": {"typical": "4K", "max": "8K", "recommended": False},
            "auto": {"typical": "32K", "max": "100K", "recommended": True}
        },
        "recommendations": [
            "For best compatibility: Use 8K-32K tokens",
            "For large contexts: Use 'deepinfra' provider with up to 100K",
            "For 1M tokens: Request accepted but provider will use their max",
            "Responses may be truncated if exceeding provider limits"
        ],
        "note": "API accepts up to 1M tokens, but actual limit depends on selected provider."
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Optimized chat endpoint"""
    start_time = datetime.utcnow()
    
    try:
        messages = convert_messages(request.messages, request.code_mode, request.language)
        provider = get_provider_for_code(request.provider, request.code_mode)
        token_info = get_token_limit_info(request.max_tokens, request.provider)
        
        # Generate response with timeout
        response_text = await asyncio.wait_for(
            asyncio.to_thread(
                g4f.ChatCompletion.create,
                model=request.model,
                messages=messages,
                provider=provider,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ),
            timeout=60.0  # Increased to 60s for large contexts
        )
        
        latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        input_tokens = sum(len(msg.content.split()) * 1.3 for msg in request.messages)
        output_tokens = len(response_text.split()) * 1.3
        
        return ChatResponse(
            id=f"chat-{uuid.uuid4().hex[:8]}",
            model=request.model,
            role="assistant",
            content=response_text,
            provider=request.provider,
            latency_ms=latency,
            usage={
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens)
            },
            token_limit_info=token_info
        )
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout - try streaming mode or reduce max_tokens")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Ultra-fast streaming endpoint"""
    try:
        messages = convert_messages(request.messages, request.code_mode, request.language)
        provider = get_provider_for_code(request.provider, request.code_mode)
        token_info = get_token_limit_info(request.max_tokens, request.provider)
        
        async def generate():
            first_token_sent = False
            start_time = datetime.utcnow()
            total_content = ""
            
            # Send token limit info first
            yield f"data: {json.dumps({'token_limit_info': token_info})}\n\n"
            
            try:
                response_generator = g4f.ChatCompletion.create(
                    model=request.model,
                    messages=messages,
                    provider=provider,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=True
                )
                
                for chunk in response_generator:
                    if chunk:
                        # Calculate first token latency
                        if not first_token_sent:
                            first_token_latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                            yield f"data: {json.dumps({'latency_ms': first_token_latency, 'first_token': True})}\n\n"
                            first_token_sent = True
                        
                        total_content += chunk
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                        await asyncio.sleep(0)  # Non-blocking
                
                # Final stats
                total_latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                output_tokens = int(len(total_content.split()) * 1.3)
                
                yield f"data: {json.dumps({'done': True, 'total_latency_ms': total_latency, 'usage': {'output_tokens': output_tokens}})}\n\n"
            
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
    """Expert code generation endpoint (non-streaming)"""
    # Force code mode
    request.code_mode = True
    request.temperature = 0.2  # Lower temperature for code
    
    return await chat(request)

@app.post("/code/stream")
async def code_generation_stream(request: ChatRequest):
    """Expert code generation endpoint (streaming)"""
    # Force code mode
    request.code_mode = True
    request.temperature = 0.2  # Lower temperature for code
    
    return await chat_stream(request)

@app.post("/v1/chat/completions")
async def openai_compatible(request: ChatRequest):
    """OpenAI-compatible endpoint with optimizations"""
    try:
        messages = convert_messages(request.messages, request.code_mode, request.language)
        provider = get_provider_for_code(request.provider, request.code_mode)
        
        if request.stream:
            async def generate():
                chunk_id = 0
                first_token_time = None
                start_time = datetime.utcnow()
                
                try:
                    response_generator = g4f.ChatCompletion.create(
                        model=request.model,
                        messages=messages,
                        provider=provider,
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
                    
                    # Final chunk with latency info
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
                    provider=provider,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ),
                timeout=60.0
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
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))