import React from 'react';
import { SearchX, RefreshCw } from 'lucide-react';

export default function EmptyState({ onReset }) {
  return (
    <div className="w-full max-w-xl mx-auto my-8 sm:my-12 bg-[#08080b]/95 backdrop-blur-xl border border-white/10 rounded-2xl p-5 sm:p-8 text-center shadow-2xl text-[#f4f4f5]">
      <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto rounded-full bg-[#14141a] flex items-center justify-center text-[#a1a1aa] mb-3 sm:mb-4 border border-white/10">
        <SearchX className="w-5 h-5 sm:w-6 sm:h-6" />
      </div>
      <h3 className="text-base sm:text-lg font-bold text-white mb-1.5 sm:mb-2">No Exact Matches Found</h3>
      <p className="text-xs sm:text-sm text-[#a1a1aa] mb-4 sm:mb-5 leading-relaxed">
        Every product in the retrieved pool was excluded by one or more strict constraints (such as an exact pattern exclusion or budget cap).
      </p>

      <div className="bg-black/60 border border-white/10 rounded-xl p-4 text-left text-xs text-[#d4d4d8] mb-6 space-y-2">
        <span className="font-semibold text-white block mb-1">
          Suggestions to expand results:
        </span>
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-bold">•</span>
          <span>Slightly increase your budget limit</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-bold">•</span>
          <span>Relax one of the pattern or material exclusions</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-bold">•</span>
          <span>Try broader search keywords</span>
        </div>
      </div>

      {onReset && (
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-white text-[#0a0a0e] hover:bg-neutral-200 transition-colors shadow-md cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Search</span>
        </button>
      )}
    </div>
  );
}
