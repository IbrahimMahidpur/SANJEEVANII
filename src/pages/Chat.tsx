import { useState, useRef, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { PromptBox } from '../components/PromptBox';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  image?: string;
}

export default function Chat() {
  const [chats, setChats] = useState<string[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNewChat = () => {
    setMessages([]);
    console.log("New chat triggered");
  };

  const handleSend = async (message: string, image?: string | null, selectedTool?: string | null) => {
    if (!message.trim() && !image) return;

    // Add user message to chat
    const userMessage: Message = {
      role: 'user',
      content: message,
      image: image || undefined
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Add to chat history
    const newChatTitle = message.length > 30 ? message.substring(0, 30) + "..." : message || "Image Upload";
    setChats((prev) => [newChatTitle, ...prev]);

    try {
      // Prepare message history for API
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Call backend API
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          images: image ? [image.split(',')[1]] : [], // Send base64 without prefix
          history: history,
          selectedTool: selectedTool // Pass selected tool to backend
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';
      let updateScheduled = false;

      // Add empty assistant message that we'll update
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // Batch updates to reduce re-renders
      const scheduleUpdate = () => {
        if (!updateScheduled) {
          updateScheduled = true;
          requestAnimationFrame(() => {
            setMessages(prev => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1] = {
                role: 'assistant',
                content: assistantMessage
              };
              return newMessages;
            });
            updateScheduled = false;
          });
        }
      };

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                break;
              }
              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  assistantMessage += parsed.content;
                  // Schedule update instead of immediate setState
                  scheduleUpdate();
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }

        // Final update to ensure everything is rendered
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            role: 'assistant',
            content: assistantMessage
          };
          return newMessages;
        });
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend server is running and Ollama is available.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dark flex h-screen w-full bg-[#212121] text-white font-sans overflow-hidden">
      {/* Sidebar */}
      <Sidebar chats={chats} onNewChat={handleNewChat} />

      {/* Main Content */}
      <main className="flex-1 ml-[260px] flex flex-col relative">
        {/* Header */}
        <header className="flex items-center p-4">
          <button className="flex items-center gap-1 text-lg font-medium text-gray-200 hover:bg-[#2F2F2F] px-3 py-2 rounded-lg transition-colors">
            Sanjeevani
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400">
              <path d="m6 9 6 6 6-6" />
            </svg>
          </button>
          <div className="ml-auto flex items-center gap-2">
            {/* Header icons if needed */}
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 pb-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full pb-32">
              <h1 className="text-3xl font-medium mb-8 text-white">Where should we begin?</h1>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6 py-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                    ? 'bg-[#2F2F2F] text-white'
                    : 'bg-[#303030] text-gray-100'
                    }`}>
                    {msg.image && (
                      <img
                        src={msg.image}
                        alt="User upload"
                        className="max-w-full rounded-lg mb-2 max-h-64 object-contain"
                      />
                    )}
                    <div className="whitespace-pre-wrap">
                      {msg.content.split(/<think>([\s\S]*?)<\/think>/g).map((part, i) => {
                        if (i % 2 === 1) {
                          return (
                            <details key={i} className="mb-2 bg-black/20 rounded-lg overflow-hidden">
                              <summary className="px-3 py-2 text-xs font-medium text-gray-400 cursor-pointer hover:bg-white/5 select-none flex items-center gap-2">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <circle cx="12" cy="12" r="10" />
                                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                                  <line x1="12" y1="17" x2="12.01" y2="17" />
                                </svg>
                                Thinking Process
                              </summary>
                              <div className="px-3 py-2 text-sm text-gray-400 border-t border-white/5 font-mono bg-black/10">
                                {part}
                              </div>
                            </details>
                          );
                        }
                        return (
                          <div key={i} className="markdown-body">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {part}
                            </ReactMarkdown>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-[#303030] rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 pb-8">
          <div className="max-w-3xl mx-auto">
            <PromptBox onSend={handleSend} disabled={isLoading} />
          </div>
        </div>
      </main>
    </div>
  );
}
