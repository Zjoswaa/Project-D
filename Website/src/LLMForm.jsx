import { useState } from 'react';

function LLMForm() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

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

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="grid grid-cols-1">
          <h1 className="text-2xl font-bold">Hello! I am GigaChat, NDW's personal AI assistant.</h1>
          <h2 className="text-1xl font-bold">How can I help you today?</h2>
        </div>
        {chatHistory.length > 0 && (
          <button
            onClick={clearHistory}
            className="text-red-500 hover:text-red-700 text-sm"
          >
            Clear History
          </button>
        )}
      </div>
      
      {/* Chat History */}
      {chatHistory.length > 0 && (
        <div className="mb-6 max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
          <div className="p-4 bg-gray-50 border-b">
            <h2 className="font-semibold text-lg">Chat History</h2>
          </div>
          <div className="p-4 space-y-4">
            {chatHistory.map((chat) => (
              <div key={chat.id} className="border-b border-gray-100 pb-4 last:border-b-0">
                <div className="mb-2">
                  <div className="text-sm text-gray-500 mb-1">
                    {chat.timestamp.toLocaleTimeString()}
                  </div>
                  <div className="bg-orange-50 p-3 rounded-lg">
                    <div className="text-right">{chat.question}</div>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${chat.isError ? 'bg-red-50' : 'bg-pink-50'}`}>
                  <div className="mt-1 whitespace-pre-wrap">{chat.response}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Section */}
      <div className="mb-6">
        <div className="mb-4">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question here... (Press Enter to send, Shift+Enter for new line)"
            className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="4"
          />
        </div>
        
        <button
          onClick={handleSubmit}
          disabled={loading || !question.trim()}
          className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
        >
          {loading ? 'Thinking...' : 'Ask Question'}
        </button>
      </div>

      {/* Loading indicator */}
      {loading && (
        <div className="text-center">
          <div className="inline-flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
            Processing your question...
          </div>
        </div>
      )}
    </div>
  );
}

export default LLMForm;