# AI Provider Configuration
# Automatically handled by g4f library

DEFAULT_MODEL = "gpt-4"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# Provider priority (g4f auto-selects)
PROVIDER_PRIORITY = [
    "Bing",
    "You",
    "Phind",
    "DeepInfra",
    "Blackbox"
]

# Response settings
STREAMING_ENABLED = True
CORS_ALLOW_ALL = True

# Health check
HEALTH_CHECK_INTERVAL = 300  # seconds