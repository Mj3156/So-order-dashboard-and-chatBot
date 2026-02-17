'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MessageSquare, Send, X, Bot, User, Sparkles, Maximize2, Trash2, LayoutDashboard, BarChart3, PieChart, TrendingUp } from 'lucide-react';
import { api } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

const QUICK_PROMPTS: any[] = [];

export default function ChatAssistant() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Resizing State
    const [dimensions, setDimensions] = useState({ width: 75, height: 75 });
    const isResizing = useRef(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initial Load & Persistence
    useEffect(() => {
        const savedMessages = localStorage.getItem('ai_chat_history');
        if (savedMessages) {
            setMessages(JSON.parse(savedMessages));
        } else {
            setMessages([
                {
                    role: 'assistant',
                    content: "Hello! I'm your AI Data Assistant. I can analyze 340k+ records and create beautiful visualizations with full data details. Try one of the quick prompts below!"
                }
            ]);
        }
    }, []);

    useEffect(() => {
        if (messages.length > 0) {
            localStorage.setItem('ai_chat_history', JSON.stringify(messages));
        }
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) scrollToBottom();
    }, [messages, isOpen]);

    // Resize Logic
    const startResizing = useCallback((e: React.MouseEvent) => {
        e.preventDefault();
        isResizing.current = true;
        document.addEventListener('mousemove', handleResize);
        document.addEventListener('mouseup', stopResizing);
        document.body.style.cursor = 'nwse-resize';
    }, []);

    const stopResizing = useCallback(() => {
        isResizing.current = false;
        document.removeEventListener('mousemove', handleResize);
        document.removeEventListener('mouseup', stopResizing);
        document.body.style.cursor = 'default';
    }, []);

    const handleResize = useCallback((e: MouseEvent) => {
        if (!isResizing.current) return;
        const newWidth = ((window.innerWidth - e.clientX) / window.innerWidth) * 100;
        const newHeight = ((window.innerHeight - e.clientY) / window.innerHeight) * 100;
        setDimensions({
            width: Math.max(30, Math.min(90, newWidth)),
            height: Math.max(30, Math.min(90, newHeight))
        });
    }, []);

    const handleSend = async (customQuery?: string) => {
        const queryToSend = customQuery || input;
        if (!queryToSend.trim() || isLoading) return;

        const userMessage: Message = { role: 'user', content: queryToSend };
        setMessages(prev => [...prev, userMessage]);
        if (!customQuery) setInput('');
        setIsLoading(true);

        try {
            const response = await api.chat(queryToSend, messages);
            const assistantMessage: Message = { role: 'assistant', content: response.response };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "⚠️ I couldn't reach the AI backend. Please ensure the server is active on Port 8008."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const clearHistory = () => {
        localStorage.removeItem('ai_chat_history');
        setMessages([
            {
                role: 'assistant',
                content: "History cleared. How can I help you today?"
            }
        ]);
    };

    const posRight = isOpen ? `${(100 - dimensions.width) / 2}%` : '50%';
    const posBottom = isOpen ? `${(100 - dimensions.height) / 2}%` : '-100%';

    return (
        <>
            {/* Floating Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-2xl z-[150] flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95 ${isOpen
                    ? 'bg-slate-800 text-white rotate-90 border border-slate-700'
                    : 'bg-blue-600 text-white animate-pulse-subtle'
                    }`}
            >
                {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
            </button>

            {/* Chat Window */}
            <div
                style={{
                    width: `${dimensions.width}%`,
                    height: `${dimensions.height}%`,
                    bottom: posBottom,
                    right: posRight,
                    transition: isResizing.current ? 'none' : 'all 0.5s ease-out',
                }}
                className={`fixed bg-slate-900 border border-slate-800 rounded-[2.5rem] shadow-[0_20px_100px_rgba(0,0,0,0.7)] z-[150] flex flex-col overflow-hidden transform origin-center ${isOpen ? 'scale-100 opacity-100' : 'scale-75 opacity-0 pointer-events-none'
                    }`}
            >
                {/* Resize Handle (Top-Left) */}
                <div
                    onMouseDown={startResizing}
                    className="absolute top-0 left-0 w-12 h-12 cursor-nwse-resize z-[160] flex items-center justify-center group"
                >
                    <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center border border-white/5 group-hover:bg-blue-600 transition-colors">
                        <Maximize2 className="w-3.5 h-3.5 text-slate-400 rotate-90 group-hover:text-white" />
                    </div>
                </div>

                {/* Header */}
                <div className="p-6 border-b border-white/5 bg-gradient-to-r from-blue-600/10 to-indigo-600/10 flex items-center justify-between">
                    <div className="flex items-center gap-4 ml-8">
                        <div className="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center border border-blue-500/30">
                            <Bot className="w-7 h-7 text-blue-400" />
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-white flex items-center gap-2">
                                Data Analyst AI
                                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                            </h3>
                            <div className="flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                <p className="text-[10px] text-emerald-400/80 font-bold uppercase tracking-wider">Operational</p>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={clearHistory}
                            className="text-slate-500 hover:text-red-400 transition-colors p-2 rounded-xl hover:bg-red-400/10"
                            title="Clear History"
                        >
                            <Trash2 className="w-5 h-5" />
                        </button>
                        <button onClick={() => setIsOpen(false)} className="text-slate-500 hover:text-white transition-colors p-2 rounded-xl hover:bg-slate-800">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950/40 custom-scrollbar">
                    {messages.map((m, i) => (
                        <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] p-4 rounded-3xl shadow-xl ${m.role === 'user'
                                ? 'bg-blue-600 text-white rounded-tr-sm font-medium'
                                : 'bg-slate-800 text-slate-200 border border-slate-700/50 rounded-tl-sm'
                                }`}>
                                <div className="flex items-center gap-2.5 mb-2 opacity-50">
                                    {m.role === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                                    <span className="text-[10px] font-bold uppercase tracking-widest leading-none">
                                        {m.role === 'user' ? 'Client' : 'Assistant'}
                                    </span>
                                </div>
                                <div className="prose prose-invert prose-sm max-w-none text-[14px] leading-relaxed">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            code: ({ node, ...props }) => (
                                                <code className="bg-black/40 rounded px-2 py-0.5 text-blue-300 font-mono text-[12px]" {...props} />
                                            ),
                                            pre: ({ node, ...props }) => (
                                                <pre className="bg-black/60 rounded-2xl p-4 border border-white/5 overflow-x-auto my-3 custom-scrollbar shadow-inner" {...props} />
                                            ),
                                            img: ({ node, ...props }) => (
                                                <div className="bg-white/5 rounded-2xl border border-white/10 p-3 my-4 shadow-2xl relative overflow-hidden group">
                                                    <img
                                                        className="w-full h-auto rounded-xl"
                                                        {...props}
                                                        alt="AI Analysis"
                                                    />
                                                    <div className="absolute top-5 right-5 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <Sparkles className="w-5 h-5 text-blue-400 drop-shadow-lg" />
                                                    </div>
                                                </div>
                                            ),
                                            table: ({ node, ...props }) => (
                                                <div className="overflow-x-auto my-4 rounded-xl border border-white/10 shadow-lg bg-slate-900/50">
                                                    <table className="min-w-full divide-y divide-white/10" {...props} />
                                                </div>
                                            ),
                                            thead: ({ node, ...props }) => <thead className="bg-white/5" {...props} />,
                                            th: ({ node, ...props }) => <th className="px-4 py-2.5 text-left text-[11px] font-bold uppercase tracking-wider text-blue-400" {...props} />,
                                            td: ({ node, ...props }) => <td className="px-4 py-2 border-t border-white/5 text-[12px] text-slate-300" {...props} />,
                                            h3: ({ node, ...props }) => <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-blue-500/80 mb-3 mt-6" {...props} />
                                        }}
                                    >
                                        {m.content}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="bg-slate-800 text-slate-200 border border-slate-700/50 p-5 rounded-3xl rounded-tl-sm flex gap-2">
                                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce"></div>
                                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Quick Prompts & Input Area */}
                <div className="p-6 bg-slate-900 border-t border-white/5 space-y-4">

                    <form
                        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                        className="relative flex items-center"
                    >
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask for highlights, trends, or specific orders..."
                            disabled={isLoading}
                            className="w-full bg-slate-800/50 border border-white/5 rounded-3xl pl-7 pr-16 py-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-all placeholder:text-slate-500 disabled:opacity-50 shadow-inner"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="absolute right-3 w-11 h-11 bg-blue-600 hover:bg-blue-500 rounded-2xl flex items-center justify-center text-white transition-all shadow-lg active:scale-90 disabled:opacity-30"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </form>
                    <p className="text-[10px] text-center text-slate-600 uppercase tracking-[0.2em] font-bold">
                        AI Data Engine Active • High Saturation Visuals
                    </p>
                </div>
            </div>
        </>
    );
}
