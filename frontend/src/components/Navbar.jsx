import React, { useEffect, useState } from 'react';
import { Sparkles, Activity } from 'lucide-react';
import { checkHealth } from '../services/api';

export default function Navbar() {
  const [health, setHealth] = useState({ status: 'checking' });

  useEffect(() => {
    checkHealth().then(setHealth);
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-[#0a0a0e]/85 backdrop-blur-md border-b border-[#27272a] transition-all safe-top">
      <div className="max-w-6xl mx-auto px-3.5 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-white/10 text-white flex items-center justify-center font-bold text-sm sm:text-base border border-white/10 shadow-xs">
            <img src="/favicon.png" alt="Icon" className="w-5 h-5" />
          </div>
          <div>
            <span className="text-base sm:text-lg font-bold tracking-tight text-white">
              INTENT<span className="font-light text-[#a1a1aa]">CART</span>
            </span>
          </div>
        </div>

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
