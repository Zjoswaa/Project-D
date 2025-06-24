import { useState } from 'react';

function LLMForm() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleSubmit = async () => {
    if (!question.trim()) return;

    const currentQuestion = question.trim();
    setLoading(true);
    setQuestion(''); // Clear input immediately
    
    try {
      // Send directly to your backend on port 8080
      const res = await fetch(`http://localhost:8080`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          Prompt: currentQuestion
        })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      const response = data.response || 'No response received';
      
      // Add the Q&A pair to chat history
      setChatHistory(prev => [...prev, {
        id: Date.now(),
        question: currentQuestion,
        response: response,
        timestamp: new Date()
      }]);
      
    } catch (error) {
      const errorResponse = `Error: ${error.message}`;
      
      // Add error to chat history as well
      setChatHistory(prev => [...prev, {
        id: Date.now(),
        question: currentQuestion,
        response: errorResponse,
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setChatHistory([]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className={`min-h-screen transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-orange-900' 
        : 'bg-gradient-to-br from-orange-50 via-white to-orange-100'
    }`}>
      {/* Header */}
      <div className={`backdrop-blur-sm border-b shadow-sm sticky top-0 z-10 transition-all duration-300 ${
        isDarkMode 
          ? 'bg-gray-800/90 border-orange-700' 
          : 'bg-white/90 border-orange-200'
      }`}>
        <div className="max-w-4xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-orange-800 bg-clip-text text-transparent">
                  Hello! I am ChadBot, NDW's personal AI assistant.
                </h1>
                <h2 className={`text-lg font-medium mt-1 transition-colors duration-300 ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-600'
                }`}>
                  How can I help you today?
                </h2>
                <h3 className="text-sm font-medium text-gray-500 mt-1">
                  ChadBot is made and maintained by Team GigaChat
                </h3>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {/* Dark Mode Toggle */}
              <button
                onClick={toggleDarkMode}
                className={`p-3 rounded-xl transition-all duration-200 hover:scale-105 ${
                  isDarkMode 
                    ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                    : 'bg-orange-100 hover:bg-orange-200 text-orange-600'
                }`}
                title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                {isDarkMode ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
              
              <button
                onClick={clearHistory}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-200 border hover:shadow-md ${
                  isDarkMode 
                    ? 'bg-red-900/50 hover:bg-red-800/50 text-red-300 hover:text-red-200 border-red-700' 
                    : 'bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-700 border-red-200'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span className="font-medium">Clear History</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Chat History */}
        {chatHistory.length > 0 && (
          <div className={`backdrop-blur-sm rounded-2xl border shadow-lg overflow-hidden transition-all duration-300 ${
            isDarkMode 
              ? 'bg-gray-800/70 border-orange-700' 
              : 'bg-white/70 border-orange-200'
          }`}>
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4">
              <h2 className="font-bold text-xl text-white flex items-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span>Chat History</span>
              </h2>
            </div>
            <div className="max-h-96 overflow-y-auto p-6 space-y-6">
              {chatHistory.map((chat) => (
                <div key={chat.id} className="space-y-3">
                  {/* Timestamp */}
                  <div className="text-center">
                    <span className={`text-xs px-3 py-1 rounded-full transition-colors duration-300 ${
                      isDarkMode 
                        ? 'text-gray-400 bg-gray-700' 
                        : 'text-gray-500 bg-gray-100'
                    }`}>
                      {chat.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  
                  {/* Question */}
                  <div className="flex justify-end">
                    <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-4 rounded-2xl rounded-tr-md shadow-lg max-w-[80%] relative">
                      <div className="flex items-start space-x-2">
                        <svg className="w-4 h-4 mt-1 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                        </svg>
                        <div className="leading-relaxed">{chat.question}</div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Response */}
                  <div className="flex justify-start">
                    <div className={`p-4 rounded-2xl rounded-tl-md shadow-lg max-w-[80%] relative transition-all duration-300 ${
                      chat.isError 
                        ? isDarkMode
                          ? 'bg-red-900/50 border border-red-700' 
                          : 'bg-red-50 border border-red-200'
                        : isDarkMode
                          ? 'bg-gray-700 border border-gray-600' 
                          : 'bg-white border border-orange-200'
                    }`}>
                      <div className="flex items-start space-x-2">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                          chat.isError ? 'bg-red-500' : 'bg-gradient-to-br from-orange-500 to-orange-600'
                        }`}>
                          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                          </svg>
                        </div>
                        <div className={`leading-relaxed whitespace-pre-wrap transition-colors duration-300 ${
                          chat.isError 
                            ? isDarkMode ? 'text-red-300' : 'text-red-700'
                            : isDarkMode ? 'text-gray-200' : 'text-gray-800'
                        }`}>
                          {chat.response}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input Section */}
        <div className={`backdrop-blur-sm rounded-2xl border shadow-lg p-6 space-y-4 transition-all duration-300 ${
          isDarkMode 
            ? 'bg-gray-800/70 border-orange-700' 
            : 'bg-white/70 border-orange-200'
        }`}>
          <div>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your question here..."
              className={`w-full p-4 border rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent shadow-sm transition-all duration-200 ${
                isDarkMode 
                  ? 'bg-gray-700/80 border-gray-600 text-gray-200 placeholder-gray-400' 
                  : 'bg-white/80 border-orange-200 text-gray-800 placeholder-gray-500'
              }`}
              rows="4"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className={`text-sm transition-colors duration-300 ${
              isDarkMode ? 'text-gray-400' : 'text-gray-500'
            }`}>
              Press Enter to send, Shift+Enter for new line
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={loading || !question.trim()}
              className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 disabled:from-gray-300 disabled:to-gray-400 text-white px-8 py-3 rounded-xl font-semibold shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105 disabled:hover:scale-100 disabled:hover:shadow-lg flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>Thinking...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                  <span>Ask Question</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LLMForm;