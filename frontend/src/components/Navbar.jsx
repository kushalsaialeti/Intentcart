import React, { useEffect, useState } from 'react';
import { Sparkles, Activity } from 'lucide-react';
import { checkHealth } from '../services/api';

export default function Navbar() {
  const [health, setHealth] = useState({ status: 'checking' });

  useEffect(() => {
    checkHealth().then(setHealth);
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-[#FAFAF8]/90 backdrop-blur-md border-b border-[#E5E5E5] transition-all safe-top">
      <div className="max-w-6xl mx-auto px-3.5 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#171717] text-white flex items-center justify-center font-bold text-sm sm:text-base shadow-xs">
            I
          </div>
          <div>
            <span className="text-base sm:text-lg font-bold tracking-tight text-[#171717]">
              INTENT<span className="font-light text-[#737373]">CART</span>
            </span>
          </div>
        </div>

        {/* Engine Status Badge */}
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full text-[11px] sm:text-xs font-medium bg-[#F3F3F0] text-[#171717] border border-[#E5E5E5]">
            <span
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                health.status === 'ok' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
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
