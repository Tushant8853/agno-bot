// API service for Agno chatbot backend
const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  // Chat APIs
  static async createSession(userId = null, metadata = {}) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId || `user-${Date.now()}`,
        metadata: { ...metadata, source: 'web-frontend' }
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    return response.json();
  }

  static async sendMessage(message, sessionId, userId = null, memoryContext = true) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        user_id: userId || `user-${Date.now()}`,
        memory_context: memoryContext,
        context: {}
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send message');
    }

    return response.json();
  }

  static async getSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get session: ${response.statusText}`);
    }

    return response.json();
  }

  static async getSessionHistory(sessionId, limit = 50) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}/history?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get session history: ${response.statusText}`);
    }

    return response.json();
  }

  static async getSessionAnalytics(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}/analytics`);
    
    if (!response.ok) {
      throw new Error(`Failed to get session analytics: ${response.statusText}`);
    }

    return response.json();
  }

  static async closeSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to close session: ${response.statusText}`);
    }

    return response.json();
  }

  // Memory APIs
  static async getMemoryContext(sessionId, userId = null, query = null) {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (query) params.append('query', query);

    const response = await fetch(`${API_BASE_URL}/api/v1/memory/context/${sessionId}?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get memory context: ${response.statusText}`);
    }

    return response.json();
  }

  static async searchMemory(query, filters = {}, limit = 10) {
    const response = await fetch(`${API_BASE_URL}/api/v1/memory/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        query_type: 'semantic',
        filters,
        limit
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to search memory: ${response.statusText}`);
    }

    return response.json();
  }

  static async createRelationship(sourceEntity, targetEntity, relationshipType, sessionId = null, confidence = 0.8) {
    const params = new URLSearchParams({
      source_entity: sourceEntity,
      target_entity: targetEntity,
      relationship_type: relationshipType,
      confidence: confidence.toString()
    });
    if (sessionId) params.append('session_id', sessionId);

    const response = await fetch(`${API_BASE_URL}/api/v1/memory/relationships?${params}`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error(`Failed to create relationship: ${response.statusText}`);
    }

    return response.json();
  }

  static async getMemoryAnalytics(userId = null, sessionId = null) {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (sessionId) params.append('session_id', sessionId);

    const response = await fetch(`${API_BASE_URL}/api/v1/memory/analytics?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get memory analytics: ${response.statusText}`);
    }

    return response.json();
  }

  static async getMemoryDebugInfo(sessionId, userId = null) {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);

    const response = await fetch(`${API_BASE_URL}/api/v1/memory/debug/${sessionId}?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get memory debug info: ${response.statusText}`);
    }

    return response.json();
  }

  static async getFacts(sessionId = null, userId = null, source = null, limit = 50) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (sessionId) params.append('session_id', sessionId);
    if (userId) params.append('user_id', userId);
    if (source) params.append('source', source);

    const response = await fetch(`${API_BASE_URL}/api/v1/memory/facts?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get facts: ${response.statusText}`);
    }

    return response.json();
  }

  static async getRelationships(sessionId = null, userId = null, source = null, limit = 50) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (sessionId) params.append('session_id', sessionId);
    if (userId) params.append('user_id', userId);
    if (source) params.append('source', source);

    const response = await fetch(`${API_BASE_URL}/api/v1/memory/relationships?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get relationships: ${response.statusText}`);
    }

    return response.json();
  }

  static async deleteFact(factId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/memory/facts/${factId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete fact: ${response.statusText}`);
    }

    return response.json();
  }

  static async deleteRelationship(relationshipId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/memory/relationships/${relationshipId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete relationship: ${response.statusText}`);
    }

    return response.json();
  }

  static async getMemoryStats(userId = null, sessionId = null) {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (sessionId) params.append('session_id', sessionId);

    const response = await fetch(`${API_BASE_URL}/api/v1/memory/stats?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get memory stats: ${response.statusText}`);
    }

    return response.json();
  }

  // Authentication APIs
  static async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }
    return response.json();
  }

  static async signup(username, email, password) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Signup failed');
    }
    return response.json();
  }

  static async logout(sessionToken) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken }
    });
    if (!response.ok) {
      throw new Error('Logout failed');
    }
    return response.json();
  }

  // Health check APIs
  static async getHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async getChatHealth() {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/health`);
    
    if (!response.ok) {
      throw new Error(`Chat health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async getMemoryHealth() {
    const response = await fetch(`${API_BASE_URL}/api/v1/memory/health`);
    
    if (!response.ok) {
      throw new Error(`Memory health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async getWebSocketHealth() {
    const response = await fetch(`${API_BASE_URL}/api/v1/ws/health`);
    
    if (!response.ok) {
      throw new Error(`WebSocket health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  // WebSocket connection
  static createWebSocketConnection(sessionId, userId = null) {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);

    const wsUrl = `ws://localhost:8000/api/v1/ws/${sessionId}?${params}`;
    return new WebSocket(wsUrl);
  }
}

export default ApiService; 