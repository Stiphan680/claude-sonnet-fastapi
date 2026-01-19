# Token Configuration

# API accepts up to 1M tokens
MAX_TOKENS_API_LIMIT = 1000000
DEFAULT_MAX_TOKENS = 8192
MIN_MAX_TOKENS = 1

# Provider-specific token limits (approximate)
PROVIDER_TOKEN_LIMITS = {
    "deepinfra": {
        "typical": 32000,
        "maximum": 100000,
        "recommended_for_large_context": True
    },
    "phind": {
        "typical": 16000,
        "maximum": 32000,
        "recommended_for_large_context": False
    },
    "blackbox": {
        "typical": 8000,
        "maximum": 16000,
        "recommended_for_large_context": False
    },
    "you": {
        "typical": 8000,
        "maximum": 16000,
        "recommended_for_large_context": False
    },
    "bing": {
        "typical": 4000,
        "maximum": 8000,
        "recommended_for_large_context": False
    },
    "auto": {
        "typical": 32000,
        "maximum": 100000,
        "recommended_for_large_context": True
    }
}

# Recommendations
RECOMMENDED_TOKEN_RANGES = {
    "small_tasks": (1000, 4000),
    "medium_tasks": (4000, 16000),
    "large_tasks": (16000, 32000),
    "very_large_tasks": (32000, 100000),
    "ultra_large_tasks": (100000, 1000000)  # May be truncated
}

# Performance settings
TIMEOUT_CONFIG = {
    "small_context": 30,   # < 10K tokens
    "medium_context": 60,  # 10K-50K tokens
    "large_context": 120   # > 50K tokens
}