import React from 'react';
import { Bot, User } from 'lucide-react';
import EvidenceCard from './EvidenceCard';

interface MessageProps {
    message: {
        id: string;
        sender: 'USER' | 'AI';
        text: string;
        evidenceUrl?: string; // Optional (Legacy)
        evidenceList?: { url: string; title?: string; page?: number }[]; // New Multi-Evidence
        metadata?: any;
    };
}

export default function MessageBubble({ message }: MessageProps) {
    const isAI = message.sender === 'AI';

    return (
        <div className={`flex gap-4 ${isAI ? 'justify-start' : 'justify-end'} mb-8 group animate-fade-in`}>
            {isAI && (
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-600 to-emerald-800 flex items-center justify-center shrink-0 shadow-md ring-4 ring-emerald-50">
                    <Bot className="w-5 h-5 text-white" />
                </div>
            )}

            <div className={`max-w-[85%] sm:max-w-[75%] ${isAI ? '' : 'flex flex-col items-end'}`}>
                <div
                    className={`
                        p-5 rounded-2xl text-sm leading-relaxed shadow-sm transition-all
                        ${isAI
                            ? 'bg-white border border-slate-100 text-slate-700 rounded-tl-none hover:shadow-md'
                            : 'bg-gradient-to-br from-emerald-600 to-emerald-700 text-white rounded-tr-none hover:shadow-md hover:from-emerald-500 hover:to-emerald-600'
                        }
                    `}
                >
                    <p className="whitespace-pre-wrap font-medium">
                        {message.text || <span className="text-slate-400 italic">No text content available.</span>}
                    </p>
                </div>

                {/* Visual Provenance (Only for AI) */}
                {isAI && (
                    <div className="mt-3 flex flex-row gap-3 overflow-x-auto pb-2 snap-x">
                        {/* New Multi-Evidence Support */}
                        {message.evidenceList && message.evidenceList.length > 0 ? (
                            message.evidenceList.map((evidence, idx) => (
                                <div key={idx} className="shrink-0 snap-start">
                                    <EvidenceCard
                                        evidenceUrl={evidence.url}
                                        metadata={{
                                            source_title: evidence.title,
                                            page_number: evidence.page
                                        }}
                                    />
                                </div>
                            ))
                        ) : message.evidenceUrl ? (
                            /* Fallback to legacy single evidence */
                            <EvidenceCard
                                evidenceUrl={message.evidenceUrl}
                                metadata={message.metadata}
                            />
                        ) : null}
                    </div>
                )}
            </div>

            {!isAI && (
                <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center shrink-0 shadow-sm">
                    <User className="w-5 h-5 text-slate-500" />
                </div>
            )}
        </div>
    );
}
