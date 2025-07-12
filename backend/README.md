# Agno Bot Backend

A FastAPI-based backend for the Agno Bot with hybrid memory systems (Zep + Mem0) and Google Gemini AI integration.

## 🚀 Features

- **Agno Framework Integration**: Robust chatbot architecture
- **Google Gemini AI**: Natural language processing with latest Gemini model
- **Hybrid Memory Systems**: 
  - **Zep**: Temporal knowledge graph-based memory
  - **Mem0**: Scalable long-term memory with fact extraction
- **RESTful API**: Complete API with automatic documentation
- **WebSocket Support**: Real-time communication
- **Memory Analytics**: Comprehensive memory usage tracking
- **Session Management**: Multi-session support with persistence
- **Structured Logging**: Advanced logging with structlog
- **Health Monitoring**: Built-in health checks and monitoring

## 🛠️ Tech Stack

- **FastAPI** - Modern web framework
- **Agno Framework** - Chatbot framework
- **Google Gemini** - AI language model
- **Zep** - Temporal knowledge graph memory
- **Mem0** - Scalable long-term memory
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Pydantic** - Data validation
- **Structlog** - Structured logging
- **Uvicorn** - ASGI server

## 📦 Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Application Settings
APP_NAME=Agno Bot
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# API Keys (Required)
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
ZEP_API_KEY=your_zep_api_key_here
MEM0_API_KEY=your_mem0_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/agno_bot

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Memory System Configuration
ZEP_BASE_URL=https://api.zep.ai
MEM0_BASE_URL=https://api.mem0.ai
ZEP_SESSION_TTL=3600
MEM0_FACT_TTL=86400
MAX_MEMORY_CONTEXT=1000

# Gemini AI Configuration
GEMINI_MODEL=gemini-pro
GEMINI_MAX_TOKENS=2048
GEMINI_TEMPERATURE=0.7

# Security
SECRET_KEY=your_secret_key_here_make_it_long_and_random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## 📁 Project Structure

```
backend/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration management
│   ├── api/               # API routes
│   │   ├── __init__.py
│   │   ├── chat.py        # Chat endpoints
│   │   ├── memory.py      # Memory endpoints
│   │   └── websocket.py   # WebSocket endpoints
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── chat.py        # Chat models
│   │   ├── memory.py      # Memory models
│   │   └── user.py        # User models
│   ├── services/          # Business logic services
│   │   ├── __init__.py
│   │   ├── agno_service.py    # Agno framework integration
│   │   ├── gemini_service.py  # Gemini AI integration
│   │   ├── memory_service.py  # Hybrid memory management
│   │   ├── zep_service.py     # Zep memory integration
│   │   └── mem0_service.py    # Mem0 memory integration
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── logger.py      # Logging configuration
│       └── helpers.py     # Helper functions
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_chatbot.py
│   ├── test_memory.py
│   ├── test_zep_memory.py
│   ├── test_mem0_memory.py
│   └── test_hybrid_memory.py
├── requirements.txt       # Python dependencies
├── run.py                # Application startup script
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Development environment
├── railway.json          # Railway deployment config
├── env.example           # Environment variables template
└── README.md            # This file
```

## 🔌 API Endpoints

### Health & Status

- `GET /` - Application information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

### Chat API

- `POST /api/v1/chat/send` - Send a message
- `GET /api/v1/chat/history/{session_id}` - Get chat history
- `GET /api/v1/chat/sessions` - List chat sessions

### Memory API

- `GET /api/v1/memory/health` - Memory service health
- `GET /api/v1/memory/stats` - Memory statistics
- `POST /api/v1/memory/search` - Search memory
- `GET /api/v1/memory/context/{session_id}` - Get memory context
- `GET /api/v1/memory/analytics` - Memory analytics
- `GET /api/v1/memory/debug/{session_id}` - Memory debug info
- `GET /api/v1/memory/facts` - List memory facts
- `GET /api/v1/memory/relationships` - List memory relationships
- `POST /api/v1/memory/relationships` - Create relationship
- `DELETE /api/v1/memory/facts/{fact_id}` - Delete fact
- `DELETE /api/v1/memory/relationships/{relationship_id}` - Delete relationship

### WebSocket API

- `GET /api/v1/ws/health` - WebSocket health
- `GET /api/v1/ws/connections` - Connection statistics
- `WS /api/v1/ws/chat/{session_id}` - Real-time chat

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=app
```

### Run Specific Test Categories
```bash
pytest tests/test_memory.py
pytest tests/test_chatbot.py
pytest tests/test_zep_memory.py
pytest tests/test_mem0_memory.py
```

### Memory System Tests
```bash
# Test temporal knowledge graph
pytest tests/test_zep_memory.py -v

# Test fact extraction
pytest tests/test_mem0_extraction.py -v

# Test memory routing
pytest tests/test_hybrid_memory.py -v
```

## 🚀 Deployment

### Development Mode
```bash
python run.py
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
docker build -t agno-bot-backend .
docker run -p 8000:8000 --env-file .env agno-bot-backend
```

### Docker Compose
```bash
docker-compose up --build
```

### Railway Deployment
```bash
railway login
railway link
railway up
```

## 🔧 Development

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Run linting
flake8 app/ tests/

# Type checking
mypy app/
```

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement feature with tests**
   ```bash
   # Add tests first
   pytest tests/test_new_feature.py
   
   # Implement feature
   # Run tests again
   pytest tests/test_new_feature.py
   ```

3. **Submit pull request**

## 📊 Monitoring & Analytics

### Memory Analytics Dashboard

Access memory analytics at `/api/v1/memory/analytics` to view:
- Memory usage statistics
- Fact extraction metrics
- Relationship tracking data
- Performance benchmarks

### Logging

The application uses structured logging with levels:
- **DEBUG**: Detailed debugging information
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors that may cause application failure

### Health Monitoring

- **Health Check**: `/health` endpoint
- **Memory Health**: `/api/v1/memory/health`
- **WebSocket Health**: `/api/v1/ws/health`

## 🔒 Security

- **Input Validation**: Pydantic models for all inputs
- **CORS Configuration**: Configurable CORS settings
- **Rate Limiting**: Built-in rate limiting
- **Error Handling**: Comprehensive error handling
- **Logging**: Security event logging

## 📈 Performance

- **Async/Await**: Full async support throughout
- **Connection Pooling**: Database connection pooling
- **Caching**: Redis-based caching
- **Memory Optimization**: Efficient memory usage
- **Response Time**: Optimized response times

## 🔗 Integration

### Agno Framework

The application integrates with the Agno framework for:
- Conversation management
- Session handling
- Message processing
- Context management

### Memory Systems

#### Zep Integration
- Temporal knowledge graph
- Relationship tracking
- Session-based memory
- Complex query support

#### Mem0 Integration
- Fact extraction and storage
- Memory consolidation
- Efficient retrieval
- Cross-session continuity

### Gemini AI

- Natural language processing
- Context-aware responses
- Memory-enhanced conversations
- Real-time generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [API documentation](http://localhost:8000/docs)
- Review the [technical report](../TECHNICAL_REPORT.md) 