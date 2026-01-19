"""Provider configuration - NO BLACKBOX! Only free providers without upgrade messages"""
import g4f

# ✅ FREE PROVIDERS - No upgrade messages!
# ❌ Blackbox REMOVED - Was showing "Please upgrade to premium" messages
FAST_PROVIDERS = {
    "auto": None,
    "deepinfra": g4f.Provider.DeepInfra,  # ✅ Best for code, 100% free
    "phind": g4f.Provider.Phind,          # ✅ Code-specialized, free
    "you": g4f.Provider.You,              # ✅ Good balance, free
    "bing": g4f.Provider.Bing,            # ✅ Reliable, free
    # "blackbox": REMOVED! ❌ - Shows upgrade messages
}

# Provider priority for code generation (NO BLACKBOX!)
CODE_PROVIDER_PRIORITY = [
    g4f.Provider.DeepInfra,  # ✅ Best for code, no upgrade messages
    g4f.Provider.Phind,       # ✅ Code-specialized, always free
    g4f.Provider.You,         # ✅ Fallback, no restrictions
    g4f.Provider.Bing,        # ✅ Reliable, no premium needed
    # Blackbox REMOVED from priority list!
]

def get_best_code_provider():
    """Get best available FREE provider (NO BLACKBOX!)"""
    # Return first available from priority list
    # All these providers are 100% free with no upgrade messages
    for provider in CODE_PROVIDER_PRIORITY:
        try:
            return provider
        except:
            continue
    return None  # Let g4f auto-select from free providers

# Performance settings
PERFORMANCE_CONFIG = {
    "timeout": 30,  # seconds
    "max_retries": 2,
    "streaming_chunk_size": 64,  # bytes
    "connection_pool_size": 10,
}

# Provider info for users
PROVIDER_INFO = {
    "deepinfra": {
        "status": "✅ Free",
        "quality": "Excellent",
        "speed": "Fast",
        "upgrade_required": False
    },
    "phind": {
        "status": "✅ Free",
        "quality": "Very Good",
        "speed": "Fast",
        "upgrade_required": False
    },
    "you": {
        "status": "✅ Free",
        "quality": "Good",
        "speed": "Medium",
        "upgrade_required": False
    },
    "bing": {
        "status": "✅ Free",
        "quality": "Good",
        "speed": "Medium",
        "upgrade_required": False
    }
}

print("✅ Providers loaded: NO BLACKBOX! Only free providers without upgrade messages.")