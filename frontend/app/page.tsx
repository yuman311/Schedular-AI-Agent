'use client';

import { useState, useEffect, useRef } from 'react';
import VoiceInterface from './components/VoiceInterface';
import ConversationDisplay from './components/ConversationDisplay';
import AvailableSlots from './components/AvailableSlots';
import AuthStatus from './components/AuthStatus';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [availableSlots, setAvailableSlots] = useState<Array<any>>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const clientId = useRef(`client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    checkAuthStatus();
    
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'success') {
      setIsAuthenticated(true);
      window.history.replaceState({}, '', '/');
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/status');
      const data = await response.json();
      setIsAuthenticated(data.authenticated);
    } catch (error) {
      console.error('Error checking auth status:', error);
    }
  };

  const connectWebSocket = () => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId.current}`);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received:', data);
      
      if (data.type === 'response') {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.content
        }]);
        
        if (data.available_slots && data.available_slots.length > 0) {
          setAvailableSlots(data.available_slots);
        }
      }
    };
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    setWs(websocket);
  };

  const disconnectWebSocket = () => {
    if (ws) {
      ws.close();
      setWs(null);
    }
  };

  const sendMessage = (message: string) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, {
        role: 'user',
        content: message
      }]);
      
      ws.send(JSON.stringify({
        type: 'message',
        content: message
      }));
    }
  };

  const resetConversation = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'reset'
      }));
    }
    setMessages([]);
    setAvailableSlots([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Smart Scheduler AI Agent
          </h1>
          <p className="text-gray-600">
            Your AI-powered meeting scheduling assistant
          </p>
        </header>

        <div className="max-w-6xl mx-auto">
          <AuthStatus 
            isAuthenticated={isAuthenticated}
            onAuthChange={checkAuthStatus}
          />

          {isAuthenticated && (
            <>
              <div className="mb-6 flex gap-4 justify-center">
                {!isConnected ? (
                  <button
                    onClick={connectWebSocket}
                    className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-semibold transition"
                  >
                    Connect to Agent
                  </button>
                ) : (
                  <>
                    <button
                      onClick={disconnectWebSocket}
                      className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                      Disconnect
                    </button>
                    <button
                      onClick={resetConversation}
                      className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                      Reset Conversation
                    </button>
                  </>
                )}
              </div>

              {isConnected && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 space-y-6">
                    <ConversationDisplay messages={messages} />
                    <VoiceInterface 
                      onSendMessage={sendMessage}
                      isConnected={isConnected}
                    />
                  </div>
                  
                  <div className="lg:col-span-1">
                    <AvailableSlots 
                      slots={availableSlots}
                      onSelectSlot={(slot) => {
                        sendMessage(`I'd like to book the ${slot.formatted_start} slot`);
                      }}
                    />
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
