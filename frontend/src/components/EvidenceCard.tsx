import React, { useState } from 'react';
import { FileText, Maximize2, X } from 'lucide-react';
import Image from 'next/image';

interface EvidenceProps {
    evidenceUrl: string;
    metadata?: {
        authority?: string;
        title?: string;
        source_title?: string;
        page_number?: number;
        source_url?: string;
    } | null;
}

export default function EvidenceCard({ evidenceUrl, metadata }: EvidenceProps) {
    const [isOpen, setIsOpen] = useState(false);

    if (!evidenceUrl) return null;

    // Construct full URL if relative
    // API is at localhost:8000, but Image might be relative.
    // In dev, we can proxy or use full path.
    // For now assuming localhost:8000 prefix.
    const fullUrl = evidenceUrl.startsWith('http')
        ? evidenceUrl
        : `http://localhost:8000${evidenceUrl}`;

    return (
        <div className="mt-4">
            <div className="bg-yellow-50/50 border border-yellow-200 rounded-lg p-3 max-w-xs">
                <div className="flex items-center gap-2 mb-2 text-yellow-800 text-sm font-medium">
                    <FileText className="w-4 h-4" />
                    <span>Visual Provenance</span>
                </div>

                <div className="relative group cursor-pointer" onClick={() => setIsOpen(true)}>
                    <div className="aspect-[4/3] relative rounded overflow-hidden border border-yellow-100">
                        {/* Use standard img for external localhost url to avoid Next.js Image config setup for now */}
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                            src={fullUrl}
                            alt="Evidence Highlight"
                            className="object-cover w-full h-full hover:scale-105 transition-transform"
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                            <Maximize2 className="text-white w-6 h-6 drop-shadow-md" />
                        </div>
                    </div>
                </div>

                <div className="mt-2 text-xs text-yellow-700">
                    <span className="font-bold text-amber-600 block sm:inline">
                        {metadata?.authority || 'BNM'}
                        {metadata?.source_title ? ` (${metadata.source_title})` : ''} - Page {metadata?.page_number || '1'}
                    </span>    <p className="opacity-75 truncate">{metadata?.title}</p>
                </div>
            </div>

            {/* Lightbox Modal */}
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/95 backdrop-blur-sm animate-fade-in" onClick={() => setIsOpen(false)}>
                    <div className="relative bg-white max-w-4xl w-full max-h-[90vh] rounded-2xl overflow-hidden flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
                        <div className="overflow-auto flex-1 bg-slate-100 flex items-center justify-center p-4 group/image">
                            <img
                                src={fullUrl}
                                alt="Full Evidence"
                                className="max-w-full h-auto shadow-sm"
                            />
                        </div>
                        <div className="bg-white border-t border-slate-200 p-4 text-center relative z-10">
                            <h4 className="font-bold text-slate-800 text-sm">
                                {metadata?.authority || 'Source Document'}
                            </h4>
                            <p className="text-xs text-slate-500 mt-1">
                                {metadata?.title} • Page {metadata?.page_number}
                            </p>
                            {metadata?.source_url && (
                                <a
                                    href={`${metadata.source_url}#page=${metadata.page_number || 1}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 mt-3 px-4 py-2 bg-slate-900 text-white text-xs font-medium rounded-lg hover:bg-slate-800 transition-colors"
                                >
                                    <FileText className="w-3 h-3" />
                                    View Source PDF
                                </a>
                            )}
                        </div>

                        {/* Close Button - Now inside the white card for better mobile/desktop alignment */}
                        <button
                            onClick={() => setIsOpen(false)}
                            className="absolute top-4 right-4 text-slate-400 hover:text-slate-700 bg-white/80 p-2 rounded-full hover:bg-white shadow-sm transition-all border border-slate-200 z-50"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            )
            }
        </div>
    );
}
