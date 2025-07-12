# 🏗️ Agno Bot - Text-Based Architecture Diagram

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AGNO BOT ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   USER INTERFACE│    │  FASTAPI BACKEND│    │  POSTGRESQL DB  │
│   (React App)   │◄──►│   (Python 3.13) │◄──►│   (Railway)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  WEBSOCKET      │    │  AUTHENTICATION │    │  USER DATA      │
│  CONNECTION     │    │  (JWT + bcrypt) │    │  SESSIONS       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  REAL-TIME      │    │  MEMORY SERVICE │    │  CHAT HISTORY   │
│  CHAT           │    │  (Hybrid)       │    │  MESSAGES       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    EXTERNAL SERVICES    │
                    └─────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  GOOGLE GEMINI  │ │   ZEP AI        │ │   MEM0          │
    │  (AI Model)     │ │  (Vector Memory)│ │ (Fact Memory)   │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🧠 Memory Architecture Detail

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HYBRID MEMORY ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │                 QUERY ANALYSIS                          │
                    │           (Determine Memory Strategy)                   │
                    └─────────────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │   ZEP AI        │ │  HYBRID ROUTER  │ │   MEM0          │
        │   MEMORY        │ │                 │ │   MEMORY        │
        └─────────────────┘ └─────────────────┘ └─────────────────┘
                    │                   │                   │
                    ▼                   ▼                   ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │ • ChatHistory   │ │ • Query Type    │ │ • Extraction    │
        │ • Knowledge     │ │   Analysis      │ │   Pipeline      │
        │   Graph         │ │ • Memory        │ │ • Update        │
        │ • Temporal      │ │   Selection     │ │   Pipeline      │
        │   Memory        │ │ • Response      │ │ • Fact          │
        │ • Entity        │ │   Aggregation   │ │   Consolidation │
        │   Tracking      │ │ • Redundancy    │ │ • Cross-session │
        └─────────────────┘ │   Prevention    │ │   Memory        │
                    │       └─────────────────┘ └─────────────────┘
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │                 CONTEXT AGGREGATION                     │
                    │           (Combine Memory Results)                      │
                    └─────────────────────────────────────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │                 AI RESPONSE                             │
                    │           (Gemini with Context)                         │
                    └─────────────────────────────────────────────────────────┘
```

## 🛠️ Technical Stack Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TECHNICAL STACK LAYERS                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ • React 19.1.0                    • React Router DOM 6.23.0                │
│ • WebSocket Client                 • CSS3 Styling                          │
│ • Chat Interface                   • Memory Visualization                   │
│ • Authentication UI                • Responsive Design                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                AI LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Google Gemini 1.5 Pro            • Natural Language Processing           │
│ • Context-Aware Responses          • Multi-turn Conversations              │
│ • Memory-Enhanced AI               • Error Handling                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MEMORY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Zep AI SDK                       • Mem0 API                              │
│ • Hybrid Memory Service            • Memory Consolidation                  │
│ • Query Routing                    • Cross-session Memory                  │
│ • Temporal Knowledge Graph         • Fact Extraction                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ • FastAPI Framework                • Python 3.13                           │
│ • WebSocket Support                • JWT Authentication                    │
│ • REST API Endpoints               • bcrypt Password Hashing               │
│ • Session Management               • Error Logging                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INFRASTRUCTURE LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Railway Platform                 • PostgreSQL Database                   │
│ • Docker Containerization          • Environment Variables                 │
│ • SSL/TLS Encryption               • CORS Configuration                    │
│ • Health Checks                    • Rate Limiting                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW SEQUENCE                             │
└─────────────────────────────────────────────────────────────────────────────┘

    1. USER INPUT
         │
         ▼
    2. FRONTEND VALIDATION
         │
         ▼
    3. BACKEND API (REST)
         │
         ▼
    4. AUTHENTICATION CHECK
         │
         ▼
    5. MEMORY CONTEXT RETRIEVAL
         │
         ▼
    6. MEMORY SYSTEMS QUERY
         │
         ▼
    7. CONTEXT AGGREGATION
         │
         ▼
    8. GEMINI AI (with context)
         │
         ▼
    9. RESPONSE GENERATION
         │
         ▼
    10. MEMORY UPDATE
         │
         ▼
    11. WEBSOCKET → FRONTEND
         │
         ▼
    12. USER DISPLAY

┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA TYPES                                     │
└─────────────────────────────────────────────────────────────────────────────┘

• User Messages (Blue arrows)
• Memory Queries (Orange arrows)
• AI Responses (Purple arrows)
• Real-time Updates (Yellow arrows)
• Authentication (Green arrows)
```

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAILWAY DEPLOYMENT                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              RAILWAY PLATFORM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  FRONTEND       │    │  BACKEND        │    │  DATABASE       │         │
│  │  SERVICE        │    │  SERVICE        │    │  SERVICE        │         │
│  │                 │    │                 │    │                 │         │
│  │ • React Build   │    │ • FastAPI App   │    │ • PostgreSQL    │         │
│  │ • CDN Dist      │    │ • Docker        │    │ • Auto Backups  │         │
│  │ • Env Vars      │    │ • Health Checks │    │ • Connection    │         │
│  │ • Static Files  │    │ • Logging       │    │   Pooling       │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│           │                       │                       │                 │
│           └───────────────────────┼───────────────────────┘                 │
│                                   │                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        EXTERNAL INTEGRATIONS                            │ │
│  │                                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │ │
│  │  │  GOOGLE GEMINI  │  │   ZEP AI        │  │   MEM0          │         │ │
│  │  │  API            │  │  CLOUD          │  │  API            │         │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           SECURITY LAYER                                │ │
│  │                                                                         │ │
│  │  • SSL/TLS Encryption    • CORS Configuration    • API Key Management  │ │
│  │  • Rate Limiting         • Input Validation      • Error Handling      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme Reference

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              COLOR PALETTE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

• Primary Blue (React/Frontend):     #2563EB
• Secondary Green (FastAPI/Backend): #10B981
• Accent Purple (AI/Gemini):         #8B5CF6
• Memory Orange (Zep AI):            #F59E0B
• Memory Blue (Mem0):                #3B82F6
• Database Gray (PostgreSQL):        #6B7280
• Deployment Yellow (Railway):       #FCD34D
• Background Light:                  #F8FAFC
• Background Dark:                   #1F2937
```

## 📝 Implementation Notes

1. **Use these text diagrams as reference** when creating visual diagrams
2. **Follow the color scheme** for consistency
3. **Add proper icons** for each component
4. **Include connection arrows** showing data flow
5. **Add brief annotations** where needed
6. **Export in high resolution** for professional presentation

**Next Step**: Use these specifications to create visual diagrams in Figma or Miro! 