# TruthTracker Documentation
## AI-Powered Twitter Fact-Checking System

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Components](#3-components)
4. [API Reference](#4-api-reference)
5. [Setup and Installation](#5-setup-and-installation)
6. [Configuration](#6-configuration)
7. [Development Guide](#7-development-guide)
8. [Deployment](#8-deployment)
9. [Troubleshooting](#9-troubleshooting)
10. [Best Practices](#10-best-practices)

## 1. System Overview

### 1.1 Introduction
TruthTracker is an advanced fact-checking system designed to analyze and verify Twitter content using AI and multiple data sources. It provides real-time analysis of tweets and text claims, evaluating their veracity through comprehensive source verification and AI-powered analysis.

### 1.2 Key Features
- Real-time tweet and text analysis
- Multi-source verification
- AI-powered claim evaluation
- Source credibility assessment
- Engagement metrics analysis
- Async processing
- Detailed reporting

### 1.3 System Requirements
- Python 3.9+
- FastAPI
- Groq AI API access
- Twitter API access

### 1.4 Core Technologies
- **FastAPI**: Web framework
- **Groq AI**: Analysis engine
- **Twitter API**: Data source
- **BeautifulSoup**: Web scraping
- **DuckDuckGo API**: Search functionality
- **Wikipedia API**: Reference data

## 2. Architecture

### 2.1 High-Level Architecture
```
[Client] → [FastAPI Server] → [Fact Check Workflow]
                              ↓
                    [Multiple Components]
                    - Twitter Fetcher
                    - Multi Search Tool
                    - Groq Analysis
                    ↓
                    [Results Processing]
                    ↓
[Client] ← [Response Formatting] ← [State Management]
```

### 2.2 Component Interactions
1. **Request Flow**:
   - Client sends request
   - API validates input
   - Workflow initiated
   - Components process data
   - Results aggregated
   - Response formatted
   - Client receives results

2. **Data Flow**:
   ```
   Input → Validation → Processing → Analysis → Formatting → Output
   ```

3. **State Management**:
   - Immutable state objects
   - Step-by-step progression
   - Error handling at each stage

### 2.3 System Design Principles
1. **Modularity**:
   - Independent components
   - Clear interfaces
   - Pluggable architecture

2. **Scalability**:
   - Async processing
   - Stateless design
   - Caching support

3. **Reliability**:
   - Error handling
   - Fallback mechanisms
   - Logging and monitoring

## 3. Components

### 3.1 Twitter Fetcher
```python
class TwitterFetcher:
    """
    Handles Twitter API interactions and data retrieval.
    
    Features:
    - Rate limiting
    - Error handling
    - Data normalization
    """

    def get_tweets(self, tweet_ids: Union[str, List[str]]) -> Dict:
        """
        Fetch tweet data from Twitter API.
        
        Args:
            tweet_ids: Single ID or list of IDs
            
        Returns:
            Dict containing tweet data
        """
```

### 3.2 Multi Search Tool
```python
class MultiSearchTool:
    """
    Aggregates search results from multiple sources.
    
    Sources:
    - Google
    - DuckDuckGo
    - Wikipedia
    """

    def search(self, query: str, tweet_data: Optional[Dict] = None) -> List[Dict]:
        """
        Perform multi-source search.
        
        Args:
            query: Search query
            tweet_data: Optional tweet context
            
        Returns:
            List of search results
        """
```

### 3.3 Groq Analysis Tool
```python
class GroqTool:
    """
    AI-powered analysis using Groq.
    
    Features:
    - Source evaluation
    - Claim analysis
    - Evidence assessment
    """

    def evaluate_sources(self, query: str, sources: List[Dict]) -> List[Dict]:
        """Evaluate source credibility and relevance"""

    def analyze_claim(self, claim: str, evaluated_sources: List[Dict]) -> Dict:
        """Analyze claim veracity"""
```

### 3.4 Fact Check Workflow
```python
class FactCheckWorkflow:
    """
    Orchestrates the fact-checking process.
    
    Stages:
    1. Input processing
    2. Data gathering
    3. Analysis
    4. Result formatting
    """

    def process(self, state: Dict) -> Dict:
        """
        Execute fact-checking workflow.
        
        Args:
            state: Input state
            
        Returns:
            Final state with results
        """
```

## 4. API Reference

### 4.1 REST API Endpoints

#### Check Tweet
```http
POST /api/v1/check/tweet
Content-Type: application/json

{
    "tweet_id": "string",
    "background_check": boolean
}
```

Response:
```json
{
    "check_id": "string",
    "status": "string",
    "started_at": "datetime",
    "completed_at": "datetime",
    "results": {
        "responses": ["string"],
        "analysis": {
            "verdict": "string",
            "confidence": "string",
            "explanation": "string",
            "evidence_quality": {},
            "source_consensus": {},
            "temporal_analysis": {},
            "social_context": {}
        }
    }
}
```

#### Check Text
```http
POST /api/v1/check/text
Content-Type: application/json

{
    "text": "string",
    "background_check": boolean
}
```

### 4.2 Status Codes
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Server Error

### 4.3 Error Handling
```json
{
    "detail": "Error message"
}
```

## 5. Setup and Installation

### 5.1 Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/truthtracker.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload
```

### 5.2 Production Deployment
```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Configure environment
export ENVIRONMENT=production
export LOG_LEVEL=INFO

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 6. Configuration

### 6.1 Environment Variables
```env
GROQ_API_KEY=your_groq_api_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
ENVIRONMENT=development
LOG_LEVEL=INFO
CACHE_TTL=86400
MAX_WORKERS=3
```

### 6.2 Configuration Classes
```python
class Settings(BaseSettings):
    APP_NAME: str = "Fact Checker API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    GROQ_API_KEY: str
    TWITTER_BEARER_TOKEN: str
    CACHE_TTL: int = 86400
    MAX_WORKERS: int = 3
```

## 7. Development Guide

### 7.1 Code Style
- Follow PEP 8
- Use type hints
- Document all functions
- Write unit tests

### 7.2 Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### 7.3 Logging
```python
logger = get_logger(__name__)
logger.info("Information message")
logger.error("Error message")
```

## 8. Deployment

### 8.1 Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: truthtracker
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: truthtracker
        image: truthtracker:latest
        ports:
        - containerPort: 8000
```

## 9. Troubleshooting

### 9.1 Common Issues
1. API Authentication Errors
   ```
   Solution: Check API keys in .env
   ```

2. Rate Limiting
   ```
   Solution: Implement exponential backoff
   ```

### 9.2 Debugging
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

## 10. Best Practices

### 10.1 Code Organization
1. Modular Structure
2. Clear Separation of Concerns
3. Consistent Naming Conventions

### 10.2 Error Handling
1. Use Try-Except Blocks
2. Proper Error Propagation
3. Informative Error Messages

### 10.3 Performance Optimization
1. Caching Strategies
2. Async Processing
3. Resource Management

### 10.4 Security
1. Input Validation
2. API Key Protection
3. Rate Limiting

## Contact & Support
- GitHub Issues
- Documentation Updates
- Community Contributions

