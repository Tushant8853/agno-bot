# Agno Chatbot Frontend

A React-based frontend application for the Agno chatbot with advanced memory management and real-time communication capabilities.

## Features

### 🚀 Core Features
- **Real-time Chat**: Send and receive messages with the AI assistant
- **WebSocket Support**: Real-time communication with typing indicators
- **Session Management**: Create, manage, and view chat sessions
- **Memory Integration**: Access and search through conversation memory
- **System Health Monitoring**: Real-time status of all backend services

### 🧠 Memory Management
- **Memory Context**: View facts, relationships, and summaries from conversations
- **Memory Search**: Search through stored memory with semantic queries
- **Memory Analytics**: Get statistics and analytics about memory usage
- **Memory Stats**: View detailed memory system statistics

### 📊 Session Features
- **Session History**: View complete conversation history
- **Session Analytics**: Get insights about conversation patterns
- **New Chat**: Start fresh conversations with new sessions

### 🔧 System Monitoring
- **Health Checks**: Monitor the status of all backend services
- **Connection Status**: Real-time WebSocket connection indicator
- **Error Handling**: Comprehensive error reporting and display

## API Integration

The frontend integrates with all backend APIs:

### Chat APIs
- `POST /api/v1/chat/sessions` - Create new chat sessions
- `POST /api/v1/chat/send` - Send messages to the chatbot
- `GET /api/v1/chat/sessions/{id}` - Get session details
- `GET /api/v1/chat/sessions/{id}/history` - Get conversation history
- `GET /api/v1/chat/sessions/{id}/analytics` - Get session analytics
- `DELETE /api/v1/chat/sessions/{id}` - Close sessions

### Memory APIs
- `GET /api/v1/memory/context/{session_id}` - Get memory context
- `POST /api/v1/memory/search` - Search memory
- `POST /api/v1/memory/relationships` - Create relationships
- `GET /api/v1/memory/analytics` - Get memory analytics
- `GET /api/v1/memory/debug/{session_id}` - Get debug information
- `GET /api/v1/memory/facts` - Get memory facts
- `GET /api/v1/memory/relationships` - Get memory relationships
- `GET /api/v1/memory/stats` - Get memory statistics

### WebSocket APIs
- `WS /api/v1/ws/ws/{session_id}` - Real-time chat connection
- `GET /api/v1/ws/health` - WebSocket health check

### Health APIs
- `GET /health` - Main application health
- `GET /api/v1/chat/health` - Chat service health
- `GET /api/v1/memory/health` - Memory service health

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Usage

### Basic Chat
1. The application automatically creates a new chat session when loaded
2. Type your message in the input field and press Enter or click Send
3. The AI will respond with context from previous conversations

### Memory Management
1. Click the "Memory" button in the header to open the memory panel
2. Use "Get Context" to retrieve current memory context
3. Use the search feature to find specific information in memory
4. View analytics and statistics about memory usage

### Session History
1. Click the "History" button to view the complete conversation history
2. The history shows all messages with timestamps and roles

### System Health
1. Click the "Health" button to check the status of all backend services
2. The connection status indicator shows WebSocket connection state

### Starting New Conversations
1. Click "New Chat" to start a fresh conversation
2. This creates a new session and clears the current chat

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── App.js          # Main application component
│   ├── App.css         # Application styles
│   ├── api.js          # API service layer
│   ├── index.js        # Application entry point
│   └── index.css       # Global styles
├── package.json
└── README.md
```

## API Service Layer

The `api.js` file contains a comprehensive service layer that handles all backend communication:

- **ChatService**: Session and message management
- **MemoryService**: Memory operations and queries
- **WebSocketService**: Real-time communication
- **HealthService**: System health monitoring

## Styling

The application uses vanilla CSS with:
- Responsive design for mobile and desktop
- Modern gradient backgrounds
- Smooth animations and transitions
- Clean, professional UI design
- No external UI libraries

## Error Handling

The application includes comprehensive error handling:
- Network error detection and display
- API error messages
- WebSocket connection status
- Graceful degradation when services are unavailable

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development

### Available Scripts

- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run eject` - Eject from Create React App

### Environment Variables

The application is configured to connect to the backend at `http://localhost:8000`. To change this, modify the `API_BASE_URL` in `src/api.js`.

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure the backend server is running on port 8000
   - Check that CORS is properly configured on the backend

2. **WebSocket Connection Issues**
   - Verify WebSocket endpoint is accessible
   - Check browser console for connection errors

3. **Memory Features Not Working**
   - Ensure memory services are properly configured on the backend
   - Check that required environment variables are set

### Debug Mode

Open browser developer tools to see:
- API request/response logs
- WebSocket connection status
- Error messages and stack traces

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Agno chatbot system.
