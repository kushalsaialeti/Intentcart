import React, { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';

export default function Navbar({ onReset }) {
  const [health, setHealth] = useState({ status: 'checking' });

  useEffect(() => {
    checkHealth().then(setHealth);
  }, []);

  const handleLogoClick = () => {
    onReset?.();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header className="sticky top-0 z-50 bg-[#0a0a0e]/85 backdrop-blur-md border-b border-[#27272a] transition-all safe-top">
      <div className="max-w-6xl mx-auto px-3.5 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        {/* Logo and Brand Name - Clickable to Reset View */}
        <button
          type="button"
          onClick={handleLogoClick}
          className="flex items-center gap-2 sm:gap-2.5 cursor-pointer select-none group text-left outline-none bg-transparent border-0 p-0"
          title="Reset to clean home view"
          aria-label="Reset to clean home view"
        >
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-white/10 text-white flex items-center justify-center font-bold text-sm sm:text-base border border-white/10 shadow-xs group-hover:scale-105 group-hover:bg-white/15 group-hover:border-white/20 transition-all">
            <img src="/favicon.png" alt="Icon" className="w-5 h-5" />
          </div>
          <div>
            <span className="text-base sm:text-lg font-bold tracking-tight text-white group-hover:text-neutral-200 transition-colors">
              INTENT<span className="font-light text-[#a1a1aa] group-hover:text-white/80 transition-colors">CART</span>
            </span>
          </div>
        </button>

        {/* Engine Status Badge */}
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-medium bg-[#18181b]/90 text-[#f4f4f5] border border-[#27272a]">
            <span
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                health.status === 'ok' ? 'bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.6)]' : 'bg-amber-400'
              }`}
            />
            <span>
              {health.status === 'ok' ? (
                <>
                  <span className="inline sm:hidden">Ready</span>
                  <span className="hidden sm:inline">AI Engine Ready</span>
                </>
              ) : (
                'Connecting...'
              )}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
