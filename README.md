# 🚀 Claude Sonnet 3.5 FastAPI

**High-performance FastAPI with Claude Sonnet 3.5 streaming support** - Deploy kar sakte ho Render par **bilkul free**!

## ✨ Features

- ⚡ **FastAPI** - Lightning fast async API
- 🤖 **Claude Sonnet 3.5** - Latest AI model integration
- 📡 **Streaming Support** - Real-time response streaming
- 🔄 **OpenAI Compatible** - Drop-in replacement for OpenAI API
- 🔒 **Custom API Key** - Optional authentication
- 🌐 **CORS Enabled** - Works with any frontend
- 📊 **Auto Documentation** - Built-in Swagger UI
- 🆓 **Free Deployment** - Render free tier compatible

## 🛠️ Quick Setup

### 1️⃣ Local Development

```bash
# Clone repository
git clone https://github.com/Stiphan680/claude-sonnet-fastapi.git
cd claude-sonnet-fastapi

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export CUSTOM_API_KEY="your-custom-key" # Optional

# Run server
uvicorn main:app --reload --port 8000
```

### 2️⃣ Render Deployment (Free)

1. **Fork ya clone karo** ye repository
2. **Render par jao**: [https://render.com](https://render.com)
3. **New Web Service** create karo
4. **GitHub repository** connect karo
5. **Environment Variables** add karo:
   - `ANTHROPIC_API_KEY`: Tumhara Anthropic API key
   - `CUSTOM_API_KEY`: Optional custom authentication key

6. **Deploy** karo! 🎉

## 🔑 Anthropic API Key Kaise Le?

1. Jao: [https://console.anthropic.com/](https://console.anthropic.com/)
2. Account banao (free tier available)
3. API Keys section me jao
4. Naya key generate karo
5. **Important**: Free tier me $5 credit milta hai initially!

## 📡 API Endpoints

### Root Endpoint
```bash
GET /
```

### Health Check
```bash
GET /health
```

### Chat (Non-Streaming)
```bash
POST /chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "max_tokens": 1024,
  "temperature": 1.0
}
```

### Chat (Streaming)
```bash
POST /chat/stream
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Tell me a story"}
  ],
  "stream": true
}
```

### OpenAI Compatible Endpoint
```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hi there!"}
  ],
  "model": "claude-3-5-sonnet-20241022",
  "stream": false
}
```

## 🧪 Testing Examples

### Python Example
```python
import requests
import json

url = "https://your-app.onrender.com/chat"
headers = {"Content-Type": "application/json"}
data = {
    "messages": [
        {"role": "user", "content": "What is FastAPI?"}
    ],
    "max_tokens": 1024
}

response = requests.post(url, headers=headers, json=data)
print(response.json()["content"])
```

### Streaming Example
```python
import requests
import json

url = "https://your-app.onrender.com/chat/stream"
headers = {"Content-Type": "application/json"}
data = {
    "messages": [
        {"role": "user", "content": "Write a poem"}
    ],
    "stream": true
}

with requests.post(url, headers=headers, json=data, stream=True) as response:
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                if 'content' in data:
                    print(data['content'], end='', flush=True)
```

### cURL Example
```bash
curl -X POST "https://your-app.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 1024
  }'
```

## 📚 Documentation

Jab server run ho raha ho, to automatic documentation available hai:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude access |
| `CUSTOM_API_KEY` | No | Optional custom key for API authentication |
| `PORT` | No | Server port (default: 8000) |

### Model Options

- `claude-3-5-sonnet-20241022` (Default - Best performance)
- `claude-3-5-haiku-20241022` (Faster, cheaper)
- `claude-3-opus-20240229` (Most capable)

## 🎯 Performance

- **Latency**: <100ms (streaming start)
- **Throughput**: Depends on Anthropic API limits
- **Concurrent Requests**: FastAPI async support
- **Free Tier Limits**: Render free tier - 750 hours/month

## 🔐 Security

- Environment variables for sensitive data
- Optional custom API key authentication
- CORS properly configured
- No API keys in code

## 🐛 Troubleshooting

### API Key Error
```
ANTHROPIC_API_KEY not configured
```
**Solution**: Environment variable properly set karo

### Rate Limit Error
```
Rate limit exceeded
```
**Solution**: Anthropic free tier limits check karo

### Render Deployment Issue
**Solution**: 
1. `render.yaml` file repository me hai
2. Environment variables Render dashboard me set kiye
3. Build logs check karo for errors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Stiphan680/claude-sonnet-fastapi/issues)
- **Documentation**: [FastAPI Docs](https://fastapi.tiangolo.com)
- **Anthropic Docs**: [Anthropic API](https://docs.anthropic.com)

## 📄 License

MIT License - Free to use and modify!

## 🌟 Star This Repo!

Agar helpful laga to ⭐ star karo GitHub par!

---

**Made with ❤️ for free AI API deployment**