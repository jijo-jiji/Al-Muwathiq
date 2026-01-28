"use client"
import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Info } from 'lucide-react';
import Link from 'next/link';
import MessageBubble from './MessageBubble';

interface Message {
    id: string;
    sender: 'USER' | 'AI';
    text: string;
    evidenceUrl?: string;
    evidenceList?: { url: string; title?: string; page?: number }[];
    metadata?: any;
}

export default function ChatInterface() {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initialize Session
    useEffect(() => {
        const initSession = async () => {
            try {
                const res = await fetch('/api/chat/session/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                });
                const data = await res.json();
                if (data.session_id) {
                    setSessionId(data.session_id);
                    console.log("Session Created:", data.session_id);
                }
            } catch (err) {
                console.error("Failed to init session:", err);
            }
        };
        initSession();
    }, []);

    // Scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || !sessionId || loading) return;

        const userText = input.trim();
        setInput('');
        setLoading(true);

        // Optimistic Update
        const tempId = Date.now().toString();
        setMessages(prev => [...prev, { id: tempId, sender: 'USER', text: userText }]);

        try {
            const res = await fetch(`/api/chat/${sessionId}/message/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: userText })
            });
            const data = await res.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Add AI Reponse
            setMessages(prev => [...prev, {
                id: Date.now().toString() + 'ai',
                sender: 'AI',
                text: data.response,
                evidenceUrl: data.evidence_url,
                evidenceList: data.evidence_list, // Capture the list
                metadata: data.metadata
            }]);

        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, {
                id: Date.now().toString() + 'err',
                sender: 'AI',
                text: "Sorry, I encountered an error connecting to the knowledge base (Check API Quota)."
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-slate-50 font-sans">
            {/* Glass Header */}
            <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
                <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
                    <div>
                        <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2 tracking-tight">
                            <span className="text-emerald-700">Al-Muwathiq</span>
                            <span className="text-[10px] uppercase tracking-wide bg-amber-500/10 text-amber-700 px-2 py-0.5 rounded-full font-semibold border border-amber-500/20">Beta</span>
                        </h1>
                        <p className="text-xs text-slate-500 font-medium ml-0.5">Shariah Compliance Assistant</p>
                    </div>

                    <Link href="/pricing" className="text-sm font-medium text-slate-600 hover:text-emerald-700 transition-colors flex items-center gap-1">
                        Pricing <span className="hidden sm:inline">& Model</span>
                    </Link>
                </div>
            </header>

            {/* Chat Area */}
            <main className="flex-1 overflow-y-auto px-4 pt-24 pb-32 scroll-smooth">
                <div className="max-w-3xl mx-auto space-y-6">
                    {messages.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 text-center text-slate-400 space-y-6 opacity-60 animate-fade-in">
                            <div className="w-20 h-20 bg-emerald-50 rounded-2xl flex items-center justify-center border border-emerald-100 shadow-sm">
                                <span className="text-4xl">🕌</span>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-slate-700">Welcome to Al-Muwathiq</h3>
                                <p className="text-sm mt-1">Ask about Shariah rulings with direct PDF evidence.</p>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm max-w-lg w-full">
                                <button onClick={() => setInput("What is the definition of Tawarruq?")} className="p-3 bg-white border border-slate-200 rounded-lg hover:border-emerald-300 hover:text-emerald-700 hover:bg-emerald-50 transition-all text-left">
                                    "What is Tawarruq?"
                                </button>
                                <button onClick={() => setInput("Who are the contracting parties?")} className="p-3 bg-white border border-slate-200 rounded-lg hover:border-emerald-300 hover:text-emerald-700 hover:bg-emerald-50 transition-all text-left">
                                    "Contracting Parties?"
                                </button>
                            </div>
                        </div>
                    )}

                    {messages.map(msg => (
                        <MessageBubble key={msg.id} message={msg} />
                    ))}

                    {loading && (
                        <div className="flex justify-start animate-fade-in">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-600 to-emerald-800 flex items-center justify-center shrink-0 mr-4 shadow-md">
                                <Loader2 className="w-5 h-5 text-white animate-spin" />
                            </div>
                            <div className="bg-white p-4 rounded-2xl rounded-tl-none border border-slate-100 shadow-sm text-slate-500 text-sm flex items-center gap-2">
                                <span className="flex gap-1">
                                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </span>
                                <span className="text-slate-400 text-xs ml-2">Consulting Scholar AI...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </main>

            {/* Input Area */}
            <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-white via-white to-white/0 pt-10 pb-6 px-4">
                <div className="max-w-3xl mx-auto">
                    <form onSubmit={handleSend} className="relative group">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask a question about Shariah standards..."
                            className="w-full p-4 pl-6 pr-14 rounded-2xl border border-slate-200 bg-white/90 backdrop-blur-sm shadow-lg shadow-slate-200/50 
                                     focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all placeholder:text-slate-400 text-slate-700"
                            disabled={loading || !sessionId}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || loading || !sessionId}
                            className="absolute right-2 top-2 bottom-2 aspect-square bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:hover:bg-emerald-600 
                                     text-white rounded-xl flex items-center justify-center transition-all shadow-md hover:shadow-lg hover:scale-105 active:scale-95"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </form>
                    <div className="text-center mt-3 flex items-center justify-center gap-1.5 text-[10px] text-slate-400 font-medium">
                        <Info className="w-3 h-3" />
                        <span>AI generated content can be inaccurate. Verify with qualified scholars.</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
