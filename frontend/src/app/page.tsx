import React from "react";
import { Truck, ShieldCheck, Zap, ArrowRight, PhoneCall, DollarSign } from "lucide-react";

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-1.5 text-sm font-semibold text-blue-800 shadow-sm transition-all hover:bg-blue-200 dark:bg-blue-900/40 dark:text-blue-300">
          <Zap className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          <span>AI-Powered Marketplace Live for Phase 0 Alpha</span>
        </div>

        {/* Hero Headline */}
        <h1 className="mt-8 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-6xl dark:text-white">
          Direct Trucking Marketplace <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-sky-500 bg-clip-text text-transparent">
            Zero Middleman Margins.
          </span>
        </h1>

        <p className="mt-6 text-lg leading-8 text-slate-600 sm:text-xl dark:text-slate-300">
          Eliminating 40-60% intermediary losses in India&apos;s logistics corridors. Shippers list loads with AI price floors. Carriers bid in dynamic 5-minute windows.
        </p>

        {/* CTAs */}
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a
            href="/driver/dashboard"
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-8 py-4 text-lg font-bold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-700 hover:shadow-blue-500/40 active:scale-95 sm:w-auto"
          >
            <Truck className="h-6 w-6" />
            <span>I&apos;m a Truck Driver</span>
            <ArrowRight className="h-5 w-5" />
          </a>
          <a
            href="/shipper/dashboard"
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-8 py-4 text-lg font-bold text-slate-800 shadow-sm transition-all hover:bg-slate-50 active:scale-95 sm:w-auto dark:border-slate-800 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-800"
          >
            <DollarSign className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
            <span>Post a Shipment</span>
          </a>
        </div>

        {/* Feature Grid */}
        <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400">
              <Zap className="h-6 w-6" />
            </div>
            <h3 className="mt-4 text-xl font-bold text-slate-900 dark:text-white">5-Min Dynamic Bidding</h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Fast, decisive reverse auctions within AI-protected price limits.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h3 className="mt-4 text-xl font-bold text-slate-900 dark:text-white">Photo + OTP Verification</h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Double proof of delivery and pickup protecting carriers and shippers.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
              <PhoneCall className="h-6 w-6" />
            </div>
            <h3 className="mt-4 text-xl font-bold text-slate-900 dark:text-white">Masked Exotel Calling</h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Private coordination without phone leakage or platform disintermediation.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
