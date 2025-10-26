'use client';

import { useState, useRef, useEffect } from 'react';

interface VoiceInterfaceProps {
  onSendMessage: (message: string) => void;
  isConnected: boolean;
}

export default function VoiceInterface({ onSendMessage, isConnected }: VoiceInterfaceProps) {
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef<any>(null);
  const synthesisRef = useRef<SpeechSynthesis | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInputMessage(transcript);
          setIsListening(false);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }

      synthesisRef.current = window.speechSynthesis;
    }
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (error) {
        console.error('Error starting speech recognition:', error);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const speak = (text: string) => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      synthesisRef.current.speak(utterance);
    }
  };

  const handleSend = () => {
    if (inputMessage.trim() && isConnected) {
      onSendMessage(inputMessage);
      speak(inputMessage);
      setInputMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Voice & Text Input</h2>
      
      <div className="flex gap-4 mb-4">
        <button
          onClick={isListening ? stopListening : startListening}
          disabled={!isConnected}
          className={`flex-1 py-4 rounded-lg font-semibold transition ${
            isListening
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-purple-500 hover:bg-purple-600 text-white disabled:bg-gray-300 disabled:cursor-not-allowed'
          }`}
        >
          {isListening ? '🎤 Listening... (Click to Stop)' : '🎤 Start Voice Input'}
        </button>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message or use voice..."
          disabled={!isConnected}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={!isConnected || !inputMessage.trim()}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold transition disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>

      {isSpeaking && (
        <div className="mt-4 text-center text-gray-600">
          🔊 Speaking...
        </div>
      )}
    </div>
  );
}
