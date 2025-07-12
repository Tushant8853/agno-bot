import React, { useState, useRef, useCallback } from 'react';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [inputMessage, setInputMessage] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    onSendMessage(inputMessage);
    setInputMessage('');
  }, [inputMessage, isLoading, onSendMessage]);

  const handleChange = useCallback((e) => {
    setInputMessage(e.target.value);
  }, []);

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <input
        ref={inputRef}
        type="text"
        value={inputMessage}
        onChange={handleChange}
        placeholder="Type your message here..."
        disabled={isLoading}
        className="message-input"
      />
      <button 
        type="submit" 
        disabled={isLoading || !inputMessage.trim()}
        className="send-button"
      >
        Send
      </button>
    </form>
  );
};

export default React.memo(ChatInput); 