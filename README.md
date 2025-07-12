# 🤖 Agno Bot - Advanced AI Chatbot

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19.1.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue.svg)](https://www.postgresql.org/)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-blue.svg)](https://railway.app/)

## 🚀 Live Demo

**🌐 Live Application**: [https://agno-bot.railway.app](https://agno-bot.railway.app)

**📹 Demo Video**: [Watch Demo](https://www.loom.com/share/your-video-id)

**🏗️ Architecture Diagram**: [View Architecture](https://www.figma.com/file/your-file-id)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Agno Bot is an advanced AI chatbot application that combines the power of Google's Gemini AI with hybrid memory systems (Zep AI and Mem0) to create intelligent, context-aware conversations. Built with FastAPI and React, it provides real-time chat capabilities with persistent memory and learning capabilities.

### Key Highlights

- 🤖 **Advanced AI Integration**: Powered by Google Gemini 1.5 Pro
- 🧠 **Hybrid Memory System**: Combines vector (Zep) and fact-based (Mem0) memory
- ⚡ **Real-time Communication**: WebSocket-based instant messaging
- 🔐 **Secure Authentication**: JWT-based user management
- 📱 **Modern UI/UX**: Responsive React frontend
- 🚀 **Production Ready**: Deployed on Railway with PostgreSQL

## ✨ Features

### 🧠 Intelligent Memory System
- **Vector Memory (Zep AI)**: Semantic search and context retrieval
- **Fact-based Memory (Mem0)**: Relationship tracking and knowledge graphs
- **Context-Aware Responses**: Maintains conversation context across sessions
- **Memory Analytics**: Insights into conversation patterns and knowledge

### 💬 Real-time Chat
- **Instant Messaging**: WebSocket-based real-time communication
- **Typing Indicators**: Visual feedback during AI processing
- **Message History**: Persistent conversation storage
- **Multi-session Support**: Manage multiple chat sessions

### 🔐 User Management
- **Secure Registration/Login**: JWT-based authentication
- **Session Management**: Persistent user sessions
- **Password Security**: Strong password requirements
- **User Profiles**: Personalized experience

### 🎨 Modern Interface
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live message delivery
- **Intuitive UI**: Clean, modern interface
- **Accessibility**: WCAG compliant design

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL (Railway)
- **Memory Systems**: 
  - Zep AI (Vector Memory)
  - Mem0 (Fact-based Memory)
- **AI Integration**: Google Gemini 1.5 Pro
- **Authentication**: JWT with bcrypt
- **Real-time**: WebSocket (websockets)
- **Deployment**: Railway

### Frontend
- **Framework**: React 19.1.0
- **Routing**: React Router DOM 6.23.0
- **Styling**: CSS3 with modern design
- **Real-time**: WebSocket client
- **State Management**: React Hooks
- **Build Tool**: Create React App

### DevOps
- **Platform**: Railway
- **Database**: PostgreSQL (Railway)
- **Environment**: Production-ready
- **Monitoring**: Built-in health checks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  PostgreSQL DB  │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (Railway)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   WebSocket     │
                       │   Connection    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Memory Systems │    │  Gemini AI API  │
                       │  (Zep + Mem0)   │    │   (Google)      │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL database
- API keys for:
  - Google Gemini AI
  - Zep AI
  - Mem0

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agno-bot.git
   cd agno-bot
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Backend (.env)
   DATABASE_URL=postgresql://user:password@localhost:5432/agno_bot
   GEMINI_API_KEY=your_gemini_api_key
   ZEP_API_KEY=your_zep_api_key
   MEM0_API_KEY=your_mem0_api_key
   SECRET_KEY=your_secret_key
   CORS_ORIGINS=["http://localhost:3000"]
   ```

5. **Run the Application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python run.py

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📚 API Documentation

### Authentication Endpoints

```http
POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
```

### Chat Endpoints

```http
POST /api/v1/chat/sessions
POST /api/v1/chat/send
GET /api/v1/chat/sessions/{id}
GET /api/v1/chat/sessions/{id}/history
```

### Memory Endpoints

```http
GET /api/v1/memory/context/{session_id}
POST /api/v1/memory/search
GET /api/v1/memory/facts
GET /api/v1/memory/relationships
```

### WebSocket

```http
WS /api/v1/ws/{session_id}
```

For detailed API documentation, visit: http://localhost:8000/docs

## 🚀 Deployment

### Railway Deployment

1. **Connect Repository**
   - Fork this repository
   - Connect to Railway from GitHub

2. **Environment Variables**
   ```env
   DATABASE_URL=postgresql://...
   GEMINI_API_KEY=your_gemini_api_key
   ZEP_API_KEY=your_zep_api_key
   MEM0_API_KEY=your_mem0_api_key
   SECRET_KEY=your_secret_key
   CORS_ORIGINS=["https://your-app.railway.app"]
   ```

3. **Deploy**
   - Railway will automatically detect and deploy the application
   - Backend and frontend will be deployed as separate services

### Manual Deployment

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Tests
```bash
cd backend
python test_comprehensive_api.py
```

## 📊 Performance

- **Response Time**: < 500ms for chat responses
- **Memory Usage**: Optimized for production workloads
- **Scalability**: Horizontal scaling ready
- **Uptime**: 99.9% availability target

## 🔒 Security

- **Authentication**: JWT with secure session management
- **Data Protection**: Input validation and sanitization
- **API Security**: Rate limiting and request validation
- **CORS**: Properly configured for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for providing the AI capabilities
- **Zep AI** for vector memory system
- **Mem0** for fact-based memory system
- **Railway** for hosting and deployment
- **FastAPI** and **React** communities

## 📞 Contact

- **Developer**: [Your Name]
- **Email**: [your.email@example.com]
- **GitHub**: [https://github.com/yourusername](https://github.com/yourusername)
- **LinkedIn**: [https://linkedin.com/in/yourusername](https://linkedin.com/in/yourusername)

## 📈 Project Status

- ✅ **Core Features**: Complete
- ✅ **Authentication**: Complete
- ✅ **Real-time Chat**: Complete
- ✅ **Memory Systems**: Complete
- ✅ **Deployment**: Complete
- 🔄 **Mobile App**: In Progress
- 🔄 **Voice Integration**: Planned

---

**⭐ Star this repository if you find it helpful!**

**🐛 Report bugs** by opening an issue.

**💡 Suggest features** by opening a discussion. 