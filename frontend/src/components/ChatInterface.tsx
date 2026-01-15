"use client";

import { useState, useRef, useEffect, FormEvent, KeyboardEvent } from "react";
import { sendChatMessage, ChatResponse, ToolCallResult } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCallResult[];
  timestamp: Date;
}

// Generate a simple user ID for demo purposes
// In production, this would come from authentication
function getUserId(): string {
  if (typeof window === "undefined") return "user-demo";

  let userId = localStorage.getItem("todo-chatbot-user-id");
  if (!userId) {
    userId = `user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem("todo-chatbot-user-id", userId);
  }
  return userId;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const userId = getUserId();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e?: FormEvent) => {
    e?.preventDefault();

    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    // Clear input immediately
    setInput("");
    setError(null);

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmedInput,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response: ChatResponse = await sendChatMessage(
        userId,
        trimmedInput,
        conversationId
      );

      // Update conversation ID for future messages
      setConversationId(response.conversation_id);

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.response,
        toolCalls: response.tool_calls,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Something went wrong";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shadow-sm">
        <h1 className="text-lg font-semibold text-gray-800">
          Todo AI Assistant
        </h1>
        <button
          onClick={handleNewConversation}
          className="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
        >
          New Conversation
        </button>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">&#128221;</div>
              <h2 className="text-xl font-medium text-gray-700 mb-2">
                Welcome to Todo AI Assistant
              </h2>
              <p className="text-gray-500 max-w-md mx-auto">
                I can help you manage your tasks. Try saying things like:
              </p>
              <ul className="mt-4 text-sm text-gray-600 space-y-1">
                <li>&quot;Add a task to buy groceries&quot;</li>
                <li>&quot;Show me my pending tasks&quot;</li>
                <li>&quot;Mark the groceries task as done&quot;</li>
                <li>&quot;Delete the completed tasks&quot;</li>
              </ul>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white border border-gray-200 text-gray-800 shadow-sm"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  {message.toolCalls && message.toolCalls.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-100">
                      {message.toolCalls.map((tc, idx) => (
                        <div
                          key={idx}
                          className="text-xs text-gray-500 flex items-center gap-1"
                        >
                          <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded">
                            {tc.tool}
                          </span>
                          {tc.error ? (
                            <span className="text-red-500">
                              {tc.error.message}
                            </span>
                          ) : (
                            <span className="text-green-600">&#10003;</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="flex justify-center">
              <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 text-red-600 text-sm">
                {error}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Container */}
      <div className="border-t border-gray-200 bg-white px-4 py-3">
        <form
          onSubmit={handleSubmit}
          className="max-w-2xl mx-auto flex items-end gap-3"
        >
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              disabled={isLoading}
              rows={1}
              className="w-full resize-none rounded-xl border border-gray-300 px-4 py-2.5 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              style={{ minHeight: "44px", maxHeight: "120px" }}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="flex items-center justify-center w-11 h-11 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="w-5 h-5"
            >
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          </button>
        </form>
        {conversationId && (
          <div className="max-w-2xl mx-auto mt-2 text-xs text-gray-400 text-center">
            Conversation #{conversationId}
          </div>
        )}
      </div>
    </div>
  );
}
