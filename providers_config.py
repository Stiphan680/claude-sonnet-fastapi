"""Provider configuration for optimized performance"""
import g4f

# Fast providers optimized for code generation
FAST_PROVIDERS = {
    "auto": None,
    "deepinfra": g4f.Provider.DeepInfra,  # Best for code, fast
    "phind": g4f.Provider.Phind,  # Specialized for code
    "blackbox": g4f.Provider.Blackbox,  # Fast for code
    "you": g4f.Provider.You,  # Good balance
    "bing": g4f.Provider.Bing,  # Reliable
}

# Provider priority for code generation
CODE_PROVIDER_PRIORITY = [
    g4f.Provider.DeepInfra,  # Best for code
    g4f.Provider.Phind,  # Code-specialized
    g4f.Provider.Blackbox,  # Fast code generation
    g4f.Provider.You,  # Fallback
]

def get_best_code_provider():
    """Get best available provider for code generation"""
    # Return first available from priority list
    for provider in CODE_PROVIDER_PRIORITY:
        try:
            return provider
        except:
            continue
    return None  # Let g4f auto-select

# Performance settings
PERFORMANCE_CONFIG = {
    "timeout": 30,  # seconds
    "max_retries": 2,
    "streaming_chunk_size": 64,  # bytes
    "connection_pool_size": 10,
}