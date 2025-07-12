import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock the API service
jest.mock('./api', () => ({
  createSession: jest.fn(() => Promise.resolve({ id: 'test-session-id' })),
  sendMessage: jest.fn(() => Promise.resolve({ 
    message_id: 'test-message-id',
    message: 'Hello! This is a test response.',
    memory_context: null
  })),
  getHealth: jest.fn(() => Promise.resolve({ status: 'healthy' })),
  getChatHealth: jest.fn(() => Promise.resolve({ status: 'healthy' })),
  getMemoryHealth: jest.fn(() => Promise.resolve({ status: 'healthy' })),
  getWebSocketHealth: jest.fn(() => Promise.resolve({ status: 'healthy' })),
  createWebSocketConnection: jest.fn(() => ({
    onopen: jest.fn(),
    onmessage: jest.fn(),
    onclose: jest.fn(),
    onerror: jest.fn(),
    close: jest.fn()
  }))
}));

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders the app title', () => {
    render(<App />);
    const titleElement = screen.getByText(/Agno Chatbot/i);
    expect(titleElement).toBeInTheDocument();
  });

  test('renders the input field', () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Type your message here/i);
    expect(inputElement).toBeInTheDocument();
  });

  test('renders the send button', () => {
    render(<App />);
    const sendButton = screen.getByText(/Send/i);
    expect(sendButton).toBeInTheDocument();
  });

  test('renders the new chat button', () => {
    render(<App />);
    const newChatButton = screen.getByText(/New Chat/i);
    expect(newChatButton).toBeInTheDocument();
  });

  test('renders the memory button', () => {
    render(<App />);
    const memoryButton = screen.getByText(/Memory/i);
    expect(memoryButton).toBeInTheDocument();
  });

  test('renders the history button', () => {
    render(<App />);
    const historyButton = screen.getByText(/History/i);
    expect(historyButton).toBeInTheDocument();
  });

  test('renders the health button', () => {
    render(<App />);
    const healthButton = screen.getByText(/Health/i);
    expect(healthButton).toBeInTheDocument();
  });

  test('shows welcome message on load', async () => {
    render(<App />);
    await waitFor(() => {
      const welcomeMessage = screen.getByText(/Hello! I'm Agno, your AI assistant/i);
      expect(welcomeMessage).toBeInTheDocument();
    });
  });

  test('allows typing in input field', () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Type your message here/i);
    fireEvent.change(inputElement, { target: { value: 'Hello, world!' } });
    expect(inputElement.value).toBe('Hello, world!');
  });

  test('shows connection status', () => {
    render(<App />);
    const connectionStatus = screen.getByText(/Disconnected/i);
    expect(connectionStatus).toBeInTheDocument();
  });

  test('toggles memory panel when memory button is clicked', () => {
    render(<App />);
    const memoryButton = screen.getByText(/Memory/i);
    
    // Initially, memory panel should not be visible
    expect(screen.queryByText(/Memory Management/i)).not.toBeInTheDocument();
    
    // Click memory button
    fireEvent.click(memoryButton);
    
    // Memory panel should now be visible
    expect(screen.getByText(/Memory Management/i)).toBeInTheDocument();
  });

  test('toggles history panel when history button is clicked', () => {
    render(<App />);
    const historyButton = screen.getByText(/History/i);
    
    // Initially, history panel should not be visible
    expect(screen.queryByText(/Session History/i)).not.toBeInTheDocument();
    
    // Click history button
    fireEvent.click(historyButton);
    
    // History panel should now be visible
    expect(screen.getByText(/Session History/i)).toBeInTheDocument();
  });

  test('send button is disabled when input is empty', () => {
    render(<App />);
    const sendButton = screen.getByText(/Send/i);
    expect(sendButton).toBeDisabled();
  });

  test('send button is enabled when input has content', () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Type your message here/i);
    const sendButton = screen.getByText(/Send/i);
    
    fireEvent.change(inputElement, { target: { value: 'Hello!' } });
    expect(sendButton).not.toBeDisabled();
  });
}); 