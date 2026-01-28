import React from 'react';
import { Check, Info, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-slate-50 font-sans">
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
                <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2 group">
                        <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                            <span className="text-emerald-700">Al-Muwathiq</span>
                        </h1>
                        <span className="text-slate-400 text-sm group-hover:text-emerald-600 transition-colors">← Back to Chat</span>
                    </Link>
                </div>
            </header>

            <main className="pt-24 pb-20 px-4">
                <div className="max-w-6xl mx-auto">
                    {/* Hero */}
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
                            Transparent Pricing for <br /> <span className="text-emerald-700">Shariah Compliance</span>
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            Choose the plan that fits your institution. All plans include automated daily updates from BNM SAC and verifiable PDF citations.
                        </p>
                    </div>

                    {/* Pricing Cards */}
                    <div className="grid md:grid-cols-3 gap-8 mb-20">
                        {/* Starter */}
                        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-xl transition-all relative overflow-hidden group">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-slate-200 group-hover:bg-slate-300 transition-colors" />
                            <h3 className="text-xl font-semibold text-slate-900 mb-2">Starter</h3>
                            <p className="text-slate-500 text-sm mb-6">For junior auditors and students.</p>
                            <div className="flex items-baseline gap-1 mb-8">
                                <span className="text-4xl font-bold text-slate-900">Free</span>
                            </div>

                            <ul className="space-y-4 mb-8">
                                <li className="flex items-start gap-3 text-sm text-slate-600">
                                    <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                                    <span>Basic Document Search</span>
                                </li>
                                <li className="flex items-start gap-3 text-sm text-slate-600">
                                    <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                                    <span>BNM Shariah Standards Access</span>
                                </li>
                                <li className="flex items-start gap-3 text-sm text-slate-600">
                                    <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                                    <span>50 Queries / Month</span>
                                </li>
                            </ul>
                            <button className="w-full py-3 rounded-xl border-2 border-slate-200 text-slate-700 font-semibold hover:border-slate-800 hover:text-slate-900 transition-colors">
                                Get Started
                            </button>

                            <div className="mt-6 pt-6 border-t border-slate-100 text-xs text-slate-400">
                                <p>Cost per query: $0.00</p>
                                <p>Infra cost covered by Grant.</p>
                            </div>
                        </div>

                        {/* Professional */}
                        <div className="bg-slate-900 rounded-3xl p-8 border border-slate-800 shadow-2xl relative overflow-hidden transform md:-translate-y-4">
                            <div className="absolute top-0 right-0 bg-emerald-500 text-white text-xs font-bold px-3 py-1 rounded-bl-xl">POPULAR</div>
                            <h3 className="text-xl font-semibold text-white mb-2">Professional</h3>
                            <p className="text-slate-400 text-sm mb-6">For banks and Shariah departments.</p>
                            <div className="flex items-baseline gap-1 mb-8">
                                <span className="text-4xl font-bold text-white">RM 450</span>
                                <span className="text-slate-400">/mo</span>
                            </div>

                            <ul className="space-y-4 mb-8">
                                <li className="flex items-start gap-3 text-sm text-slate-300">
                                    <Check className="w-5 h-5 text-emerald-400 shrink-0" />
                                    <span>Unlimited Search & Chat</span>
                                </li>
                                <li className="flex items-start gap-3 text-sm text-slate-300">
                                    <Check className="w-5 h-5 text-emerald-400 shrink-0" />
                                    <span>Automated Daily Ingestion</span>
                                </li>
                                <li className="flex items-start gap-3 text-sm text-slate-300">
                                    <Check className="w-5 h-5 text-emerald-400 shrink-0" />
                                    <span>Visual Provenance (Page-Level)</span>
                                </li>
                                <li className="flex items-start gap-3 text-sm text-slate-300">
                                    <Check className="w-5 h-5 text-emerald-400 shrink-0" />
                                    <span>Audit Trail Export</span>
                                </li>
                            </ul>
                            <button className="w-full py-3 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-500 transition-colors shadow-lg shadow-emerald-900/50">
                                Subscribe Now
                            </button>

                            <div className="mt-6 pt-6 border-t border-slate-800 text-xs text-slate-500">
                                <div className="flex justify-between mb-1">
                                    <span>Est. Cost per Query:</span>
                                    <span className="text-emerald-400">$0.02</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Margin:</span>
                                    <span className="text-emerald-400">65%</span>
                                </div>
                            </div>
                        </div>

                        {/* Enterprise */}
                        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-xl transition-all relative overflow-hidden group">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-slate-200 group-hover:bg-emerald-600 transition-colors checked:bg-emerald-600" />
                            <h3 className="text-xl font-semibold text-slate-900 mb-2">Enterprise</h3>
                            <p className="text-slate-500 text-sm mb-6">For regulatory bodies & multi-national.</p>
                            <div className="flex items-baseline gap-1 mb-8">
                                <span className="text-4xl font-bold text-slate-900">Custom</span>
                            </div>

                            <ul className="space-y-4 mb-8">
                                <li className="flex items-start gap-3 text-sm text-slate-600">
                                    <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                                    <span>Private Cloud Deployment</span>
                                </li>
                                <li className="flex items-start gap-3 text-sm text-slate-600">
                                    <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                                    <span>Custom Data Connectors</span>
                                </li>
                                <li className="flex items-start gap-3 text-sm text-slate-600">
                                    <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                                    <span>SLA & Priority Support</span>
                                </li>
                            </ul>
                            <button className="w-full py-3 rounded-xl border-2 border-slate-200 text-slate-700 font-semibold hover:border-emerald-600 hover:text-emerald-700 transition-colors">
                                Contact Sales
                            </button>

                            <div className="mt-6 pt-6 border-t border-slate-100 text-xs text-slate-400">
                                <p>Fully Scalable Architecture</p>
                            </div>
                        </div>
                    </div>

                    {/* Cost Breakdown Section */}
                    <div className="mt-20 border-t border-slate-200 pt-16">
                        <h3 className="text-2xl font-bold text-slate-900 mb-8 text-center">Infrastructure Cost Breakdown (Monthly)</h3>

                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-slate-600">
                                <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                                    <tr>
                                        <th className="px-6 py-4 font-semibold">Cost Component</th>
                                        <th className="px-6 py-4 font-semibold">100 Users</th>
                                        <th className="px-6 py-4 font-semibold">1,000 Users</th>
                                        <th className="px-6 py-4 font-semibold">10,000 Users</th>
                                        <th className="px-6 py-4 font-semibold">Notes</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    <tr className="bg-white hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-slate-900">Vector Database (Chroma/Pinecone)</td>
                                        <td className="px-6 py-4">$15</td>
                                        <td className="px-6 py-4">$70</td>
                                        <td className="px-6 py-4">$300</td>
                                        <td className="px-6 py-4">Scales with document count & query volume</td>
                                    </tr>
                                    <tr className="bg-white hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-slate-900">LLM Inference (Gemini Flash)</td>
                                        <td className="px-6 py-4">$50</td>
                                        <td className="px-6 py-4">$450</td>
                                        <td className="px-6 py-4">$4,000</td>
                                        <td className="px-6 py-4">Est. 1M tokens / user / month</td>
                                    </tr>
                                    <tr className="bg-white hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-slate-900">Hosting (Vercel/AWS)</td>
                                        <td className="px-6 py-4">$20</td>
                                        <td className="px-6 py-4">$100</td>
                                        <td className="px-6 py-4">$500</td>
                                        <td className="px-6 py-4">Bandwidth & Compute</td>
                                    </tr>
                                    <tr className="font-bold bg-slate-50 text-slate-900 border-t-2 border-slate-200">
                                        <td className="px-6 py-4">Total Monthly Cost</td>
                                        <td className="px-6 py-4">$85</td>
                                        <td className="px-6 py-4">$620</td>
                                        <td className="px-6 py-4">$4,800</td>
                                        <td className="px-6 py-4"></td>
                                    </tr>
                                    <tr className="text-emerald-700 font-bold bg-emerald-50/50">
                                        <td className="px-6 py-4">Cost Per User</td>
                                        <td className="px-6 py-4">$0.85</td>
                                        <td className="px-6 py-4">$0.62</td>
                                        <td className="px-6 py-4">$0.48</td>
                                        <td className="px-6 py-4">Economies of scale applied</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className="mt-16 bg-slate-100 rounded-2xl p-8 flex items-start gap-4">
                        <Info className="w-6 h-6 text-slate-400 shrink-0 mt-1" />
                        <div>
                            <h4 className="font-bold text-slate-800">Why Transparent Pricing?</h4>
                            <p className="text-slate-600 text-sm mt-2 leading-relaxed">
                                We believe in building trust not just through our AI's citations, but through our business practices.
                                Our margins are calculated to ensure sustainable development of the "Cyber-Fiqh" engine while keeping
                                accessibility high for Islamic Financial Institutions globally.
                            </p>
                        </div>
                    </div>

                </div>
            </main>
        </div>
    );
}
