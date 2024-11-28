# TruthTracker: AI-Powered Twitter Fact-Checking System

TruthTracker is an advanced fact-checking system that uses AI to analyze and verify Twitter content in real-time. It combines multiple search engines, AI analysis, and source credibility assessment to provide comprehensive fact-checking results.

## 🌟 Features

- **Real-time Tweet Analysis**: Fetch and analyze tweets instantly
- **Multi-Source Verification**: Aggregate data from Google, DuckDuckGo, and Wikipedia
- **AI-Powered Analysis**: Advanced claim verification using Groq AI
- **Source Credibility**: Evaluate source reliability and relevance
- **Comprehensive Reports**: Detailed fact-checking results with evidence
- **Engagement Analysis**: Consider social context and virality
- **Async Processing**: Handle multiple requests efficiently

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Twitter API Bearer Token
- Groq API Key
- FastAPI
- uvicorn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/truthtracker.git
cd truthtracker
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
ENVIRONMENT=development
LOG_LEVEL=INFO
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## 📖 API Documentation

### Endpoints

#### Check Tweet
```http
POST /api/v1/check/tweet
```
```json
{
    "tweet_id": "1234567890",
    "background_check": false
}
```

#### Check Text
```http
POST /api/v1/check/text
```
```json
{
    "text": "Your text to fact check",
    "background_check": false
}
```

#### Get Check Status
```http
GET /api/v1/check/{check_id}
```

### Example Response
```json
{
    "check_id": "uuid",
    "status": "completed",
    "started_at": "2024-11-24T12:00:00Z",
    "completed_at": "2024-11-24T12:00:30Z",
    "results": {
        "responses": [
            "Fact Check Results",
            "Evidence Analysis",
            "Source Analysis"
        ],
        "analysis": {
            "verdict": "True/False/Partially True",
            "confidence": "high/medium/low",
            // ... more analysis details
        }
    }
}
```

## 🏗️ Project Structure

```
fact_checker/
├── app/
│   ├── api/
│   │   ├── routes.py      # API endpoints
│   │   ├── models.py      # Pydantic models
│   │   └── dependencies.py
│   ├── core/
│   │   ├── twitter.py     # Twitter integration
│   │   ├── search.py      # Search tools
│   │   ├── analysis.py    # Groq analysis
│   │   └── workflow.py    # Fact-check workflow
│   ├── services/
│   │   └── fact_checker.py
│   └── utils/
│       └── logging.py
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| GROQ_API_KEY | Your Groq API key | Yes |
| TWITTER_BEARER_TOKEN | Twitter API bearer token | Yes |
| ENVIRONMENT | development/production | No |
| LOG_LEVEL | INFO/DEBUG/WARNING/ERROR | No |
| CACHE_TTL | Cache time-to-live in seconds | No |
| MAX_WORKERS | Maximum worker threads | No |


## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Groq](https://groq.com/) for AI analysis
- [Twitter API](https://developer.twitter.com/en) for data access
- All the contributors and supporters

## 📞 Support

For support and questions, please [open an issue](https://github.com/yourusername/truthtracker/issues) on GitHub.

---
Built with ❤️ and Python
