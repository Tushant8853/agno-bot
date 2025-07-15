import React, { useState, useEffect, useRef, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import SignupPage from './SignupPage';
import LogoutButton from './LogoutButton';
import ChatInput from './ChatInput';
import ApiService from './api';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [memoryContext, setMemoryContext] = useState(null);
  const [showMemory, setShowMemory] = useState(false);
  const [memorySearchQuery, setMemorySearchQuery] = useState('');
  const [memorySearchResults, setMemorySearchResults] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [websocket, setWebsocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [systemStatus, setSystemStatus] = useState({});
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  const [auth, setAuth] = useState(() => {
    const token = localStorage.getItem('access_token');
    return token ? { tokens: { access_token: token, session_token: localStorage.getItem('session_token') } } : null;
  });

  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
      // Also scroll the container to ensure it's at the bottom
      if (messagesContainerRef.current) {
        messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
      }
    }
  }, []);

  const handleScroll = useCallback(() => {
    if (messagesContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
      const isScrolledUp = scrollTop + clientHeight < scrollHeight - 100;
      setShowScrollButton(isScrolledUp);
    }
  }, []);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Add scroll event listener to messages container
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  // Add keyboard shortcut for scrolling to bottom (Ctrl/Cmd + End)
  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'End') {
        event.preventDefault();
        scrollToBottom();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [scrollToBottom]);

  // Handle message sending from ChatInput component
  const handleSendMessage = useCallback(async (messageText) => {
    if (!messageText.trim() || !sessionId) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const data = await ApiService.sendMessage(messageText, sessionId);
      
      const assistantMessage = {
        id: data.message_id,
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update memory context if available
      if (data.memory_context) {
        setMemoryContext(data.memory_context);
      }
    } catch (err) {
      setError(err.message || 'Failed to send message');
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    // Create a new session when the app loads
    createNewSession();
    // Check system health
    checkSystemHealth();
  }, []);

  // WebSocket connection
  useEffect(() => {
    if (sessionId) {
      connectWebSocket();
    }
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [sessionId]);

  const checkSystemHealth = async () => {
    try {
      const [health, chatHealth, memoryHealth, wsHealth] = await Promise.all([
        ApiService.getHealth(),
        ApiService.getChatHealth(),
        ApiService.getMemoryHealth(),
        ApiService.getWebSocketHealth()
      ]);

      setSystemStatus({
        main: health.status,
        chat: chatHealth.status,
        memory: memoryHealth.status,
        websocket: wsHealth.status
      });
    } catch (err) {
      console.error('Health check failed:', err);
      setSystemStatus({
        main: 'error',
        chat: 'error',
        memory: 'error',
        websocket: 'error'
      });
    }
  };

  const connectWebSocket = () => {
    const ws = ApiService.createWebSocketConnection(sessionId);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    setWebsocket(ws);
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'chat_message':
        const assistantMessage = {
          id: data.message_id,
          role: 'assistant',
          content: data.message,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
        break;
      case 'typing_indicator':
        // Handle typing indicator
        break;
      case 'error':
        setError(data.message);
        setIsLoading(false);
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const createNewSession = async () => {
    try {
      const session = await ApiService.createSession();
      setSessionId(session.id);
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: 'Hello! I\'m Agno, your AI assistant. How can I help you today?',
        timestamp: new Date().toLocaleTimeString()
      }]);
      setMemoryContext(null);
      setError(null);
    } catch (err) {
      setError('Failed to create chat session');
      console.error('Error creating session:', err);
    }
  };

  

  const searchMemory = async () => {
    if (!memorySearchQuery.trim()) return;

    try {
      const data = await ApiService.searchMemory(memorySearchQuery, { session_id: sessionId });
      setMemorySearchResults(data);
    } catch (err) {
      setError(err.message || 'Failed to search memory');
      console.error('Error searching memory:', err);
    }
  };

  const getMemoryContext = async () => {
    if (!sessionId) return;

    try {
      const data = await ApiService.getMemoryContext(sessionId);
      setMemoryContext(data);
    } catch (err) {
      setError(err.message || 'Failed to get memory context');
      console.error('Error getting memory context:', err);
    }
  };

  const getSessionHistory = async () => {
    if (!sessionId) return;

    try {
      const data = await ApiService.getSessionHistory(sessionId);
      setSessionHistory(data.messages || []);
      setShowHistory(true);
    } catch (err) {
      setError(err.message || 'Failed to get session history');
      console.error('Error getting session history:', err);
    }
  };

  const getMemoryAnalytics = async () => {
    try {
      const data = await ApiService.getMemoryAnalytics(null, sessionId);
      console.log('Memory Analytics:', data);
      // You can display this data in a modal or sidebar
      alert(`Memory Analytics:\nTotal Facts: ${data.total_facts}\nTotal Relationships: ${data.total_relationships}`);
    } catch (err) {
      setError(err.message || 'Failed to get memory analytics');
      console.error('Error getting memory analytics:', err);
    }
  };

  const getMemoryStats = async () => {
    try {
      const data = await ApiService.getMemoryStats(null, sessionId);
      console.log('Memory Stats:', data);
      alert(`Memory Stats:\n${JSON.stringify(data, null, 2)}`);
    } catch (err) {
      setError(err.message || 'Failed to get memory stats');
      console.error('Error getting memory stats:', err);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setMemoryContext(null);
    setMemorySearchResults(null);
    setSessionHistory([]);
    setShowHistory(false);
    createNewSession();
  };

  const sendWebSocketMessage = (message) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({
        type: 'chat_message',
        message: message,
        session_id: sessionId,
        timestamp: new Date().toISOString()
      }));
    }
  };

  // Only show chat UI if authenticated
  function ChatUI() {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Agno Chatbot</h1>
          <div className="header-controls">
            <button onClick={clearChat} className="header-button">
              New Chat
            </button>
            <button onClick={getSessionHistory} className="header-button">
              History
            </button>
            <button onClick={() => setShowMemory(!showMemory)} className="header-button">
              Memory
            </button>
            <button onClick={checkSystemHealth} className="header-button">
              Health
            </button>
            <div className="connection-status">
              <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '1rem' }}>
              <LogoutButton setAuth={setAuth} />
            </div>
          </div>
        </header>

        <main className="chat-container">
          <div className="sidebar">
            {showMemory && (
              <div className="memory-panel">
                <h3>Memory Management</h3>

                <div className="memory-section">
                  <h4>Memory Context</h4>
                  <button onClick={getMemoryContext} className="memory-button">
                    Get Context
                  </button>
                  {memoryContext && (
                    <div className="memory-content">
                      <h5>Facts:</h5>
                      <ul>
                        {memoryContext.facts && memoryContext.facts.map((fact, index) => (
                          <li key={index}>{fact}</li>
                        ))}
                      </ul>
                      <h5>Relationships:</h5>
                      <ul>
                        {memoryContext.relationships && memoryContext.relationships.map((rel, index) => (
                          <li key={index}>{rel}</li>
                        ))}
                      </ul>
                      {memoryContext.summary && (
                        <div>
                          <h5>Summary:</h5>
                          <p>{memoryContext.summary}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="memory-section">
                  <h4>Memory Search</h4>
                  <div className="search-input">
                    <input
                      type="text"
                      value={memorySearchQuery}
                      onChange={(e) => setMemorySearchQuery(e.target.value)}
                      placeholder="Search memory..."
                      className="memory-search-input"
                    />
                    <button onClick={searchMemory} className="memory-button">
                      Search
                    </button>
                  </div>
                  {memorySearchResults && (
                    <div className="search-results">
                      <h5>Search Results:</h5>
                      <p>Total: {memorySearchResults.total_count}</p>
                      <p>Time: {memorySearchResults.search_time_ms}ms</p>
                      {memorySearchResults.results && memorySearchResults.results.map((result, index) => (
                        <div key={index} className="search-result">
                          <strong>{result.source}</strong>
                          <p>{result.content}</p>
                          <small>Score: {result.score}</small>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="memory-section">
                  <h4>Analytics & Stats</h4>
                  <button onClick={getMemoryAnalytics} className="memory-button">
                    Get Analytics
                  </button>
                  <button onClick={getMemoryStats} className="memory-button">
                    Get Stats
                  </button>
                </div>
              </div>
            )}

            {showHistory && (
              <div className="history-panel">
                <h3>Session History</h3>
                <div className="history-list">
                  {sessionHistory.map((message, index) => (
                    <div key={index} className="history-item">
                      <div className="history-role">{message.role}</div>
                      <div className="history-content">{message.content}</div>
                      <div className="history-time">{message.timestamp}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(systemStatus).length > 0 && (
              <div className="system-status-panel">
                <h3>System Status</h3>
                <div className="status-item">
                  <span>Main API:</span>
                  <span className={`status ${systemStatus.main}`}>{systemStatus.main}</span>
                </div>
                <div className="status-item">
                  <span>Chat API:</span>
                  <span className={`status ${systemStatus.chat}`}>{systemStatus.chat}</span>
                </div>
                <div className="status-item">
                  <span>Memory API:</span>
                  <span className={`status ${systemStatus.memory}`}>{systemStatus.memory}</span>
                </div>
                <div className="status-item">
                  <span>WebSocket:</span>
                  <span className={`status ${systemStatus.websocket}`}>{systemStatus.websocket}</span>
                </div>
              </div>
            )}
          </div>

          <div className="main-chat">
            <div className="messages-container" ref={messagesContainerRef}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
                >
                  <div className="message-content">
                    {message.content}
                  </div>
                  <div className="message-timestamp">
                    {message.timestamp}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message assistant-message">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {showScrollButton && (
              <button 
                className="scroll-to-bottom-button"
                onClick={scrollToBottom}
                title="Scroll to bottom"
              >
                ↓
              </button>
            )}

                        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          </div>
        </main>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage setAuth={setAuth} />} />
        <Route path="/signup" element={<SignupPage setAuth={setAuth} />} />
        <Route
          path="/*"
          element={auth ? <ChatUI /> : <Navigate to="/login" replace />}
        />
      </Routes>
    </Router>
  );
}

export default App;
