# 🚀 Free AI API - No Keys Required!

**100% Free FastAPI** with multiple AI providers - **Koi API key ki zaroorat nahi!** Direct Render par deploy karo!

## ✨ Key Features

- 🆓 **Completely FREE** - No API keys, No billing, No limits!
- 🤖 **Multiple AI Providers** - Auto-switches between providers
- ⚡ **GPT-4 Quality** - High-quality AI responses
- 📡 **Streaming Support** - Real-time response streaming
- 🔄 **OpenAI Compatible** - Drop-in replacement
- 🌐 **CORS Enabled** - Use from any frontend
- 📚 **Auto Documentation** - Built-in Swagger UI
- ☁️ **Render Ready** - One-click deployment

## 🎯 Supported AI Providers

| Provider | Speed | Quality | Status |
|----------|-------|---------|--------|
| Auto | ⚡⚡⚡ | ⭐⭐⭐⭐ | ✅ Active |
| Bing | ⚡⚡ | ⭐⭐⭐⭐ | ✅ Active |
| You | ⚡⚡⚡ | ⭐⭐⭐ | ✅ Active |
| Phind | ⚡⚡ | ⭐⭐⭐⭐ | ✅ Active |
| DeepInfra | ⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ Active |
| Blackbox | ⚡⚡⚡ | ⭐⭐⭐ | ✅ Active |

## 🚀 Render Par Deploy Kaise Kare

### Step 1: Repository Fork/Clone Karo
```bash
git clone https://github.com/Stiphan680/claude-sonnet-fastapi.git
```

### Step 2: Render Par Jao
1. [Render.com](https://render.com) par jao
2. **Sign up** karo (GitHub se - Free!)
3. **New Web Service** click karo
4. **Connect GitHub repository**: `claude-sonnet-fastapi`
5. Settings auto-detect ho jayengi
6. **Create Web Service** click karo

### Step 3: Deploy Complete! 🎉
- **Koi environment variable nahi chahiye!**
- **Koi API key nahi chahiye!**
- **2-3 minutes me deploy ho jayega**

## 📡 API Endpoints

### 1. Root Information
```bash
GET https://your-app.onrender.com/
```

### 2. Health Check
```bash
GET https://your-app.onrender.com/health
```

### 3. List Providers
```bash
GET https://your-app.onrender.com/providers
```

### 4. Chat (Non-Streaming)
```bash
POST https://your-app.onrender.com/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello AI!"}
  ],
  "model": "gpt-4",
  "provider": "auto"
}
```

### 5. Chat (Streaming)
```bash
POST https://your-app.onrender.com/chat/stream
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Tell me a story"}
  ],
  "stream": true
}
```

### 6. OpenAI Compatible
```bash
POST https://your-app.onrender.com/v1/chat/completions
Content-Type: application/json

{
  "messages": [{"role": "user", "content": "Hi!"}],
  "model": "gpt-4",
  "stream": false
}
```

## 🧪 Testing Examples

### Python Non-Streaming
```python
import requests

url = "https://your-app.onrender.com/chat"
response = requests.post(url, json={
    "messages": [
        {"role": "user", "content": "What is Python?"}
    ]
})

print(response.json()["content"])
```

### Python Streaming
```python
import requests
import json

url = "https://your-app.onrender.com/chat/stream"
data = {
    "messages": [{"role": "user", "content": "Write a poem"}],
    "stream": True
}

with requests.post(url, json=data, stream=True) as r:
    for line in r.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                chunk = json.loads(line[6:])
                if 'content' in chunk:
                    print(chunk['content'], end='', flush=True)
```

### JavaScript/Node.js
```javascript
const response = await fetch('https://your-app.onrender.com/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    messages: [{role: 'user', content: 'Hello!'}]
  })
});

const data = await response.json();
console.log(data.content);
```

### cURL
```bash
curl -X POST "https://your-app.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hi AI!"}]
  }'
```

## ⚙️ Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| messages | array | required | Chat messages |
| model | string | "gpt-4" | AI model name |
| max_tokens | int | 4096 | Max response length |
| temperature | float | 0.7 | Creativity (0.0-2.0) |
| stream | bool | false | Enable streaming |
| provider | string | "auto" | AI provider selection |

## 🎯 Provider Selection

```python
# Auto-select (recommended)
{"provider": "auto"}

# Specific provider
{"provider": "bing"}  # Fast & reliable
{"provider": "you"}   # Good quality
{"provider": "phind"} # Technical queries
```

## 📊 Response Format

### Standard Response
```json
{
  "id": "chat-abc123",
  "model": "gpt-4",
  "role": "assistant",
  "content": "Your AI response here",
  "provider": "auto",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 50,
    "total_tokens": 60
  }
}
```

### Streaming Response (SSE)
```
data: {"content": "Hello"}
data: {"content": " World"}
data: {"done": true, "usage": {"output_tokens": 2}}
```

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/Stiphan680/claude-sonnet-fastapi.git
cd claude-sonnet-fastapi

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 8000

# Open documentation
http://localhost:8000/docs
```

## 📚 Interactive Documentation

Jab deploy ho jaye:
- **Swagger UI**: `https://your-app.onrender.com/docs`
- **ReDoc**: `https://your-app.onrender.com/redoc`

## 💡 Use Cases

1. **Chatbots** - Build intelligent chatbots
2. **Content Generation** - Articles, blogs, stories
3. **Code Assistant** - Programming help
4. **Q&A Systems** - Knowledge bases
5. **Translation** - Multi-language support
6. **Summarization** - Text summarization
7. **Creative Writing** - Story generation

## ⚡ Performance

- **Latency**: ~1-3 seconds (first response)
- **Streaming**: Instant start
- **Concurrent Requests**: Unlimited (async)
- **Uptime**: 99%+ (multiple providers)

## 🆓 Pricing

| Component | Cost |
|-----------|------|
| API Usage | ₹0 (Free) |
| Render Hosting | ₹0 (750 hrs/month) |
| API Keys | ₹0 (Not required) |
| **Total** | **₹0** |

## 🛡️ Limitations

- **Free tier**: 15 min auto-sleep (cold start ~30s)
- **Rate limits**: Provider-dependent
- **Response time**: Varies by provider
- **Availability**: 99%+ (auto-failover)

## 🐛 Troubleshooting

### "Service Unavailable"
- App sleeping (free tier) - Wait 30 seconds
- Try again after cold start

### "Provider Error"
- Try different provider: `{"provider": "bing"}`
- Use auto-select: `{"provider": "auto"}`

### Slow Response
- Normal for first request after sleep
- Subsequent requests faster
- Consider paid Render plan ($7/month) for instant wake

## 🔄 Updates

```bash
# Pull latest code
git pull origin main

# Render auto-deploys on push
git push
```

## 📖 Documentation Links

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [g4f Library](https://github.com/xtekky/gpt4free)
- [Render Docs](https://render.com/docs)

## 🤝 Contributing

Pull requests welcome! Issues bhi raise kar sakte ho.

## ⭐ Star This Repo

Agar helpful laga to GitHub par star karo!

## 📄 License

MIT License - Free to use!

---

**🎉 Enjoy your FREE AI API with ZERO cost!**

**No API Keys • No Billing • No Limits • 100% Free**