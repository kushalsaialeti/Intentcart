import React from 'react';
import { SearchX, RefreshCw } from 'lucide-react';

export default function EmptyState({ onReset }) {
  return (
    <div className="w-full max-w-xl mx-auto my-8 sm:my-12 bg-white border border-[#E5E5E5] rounded-2xl p-4 sm:p-8 text-center shadow-xs">
      <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto rounded-full bg-[#F3F3F0] flex items-center justify-center text-[#737373] mb-3 sm:mb-4">
        <SearchX className="w-5 h-5 sm:w-6 sm:h-6" />
      </div>
      <h3 className="text-base sm:text-lg font-bold text-[#171717] mb-1.5 sm:mb-2">No Exact Matches Found</h3>
      <p className="text-xs sm:text-sm text-[#737373] mb-4 sm:mb-5">
        Every product in the retrieved pool was excluded by one or more strict constraints (such as an exact pattern exclusion or budget cap).
      </p>

      <div className="bg-[#FAFAF8] border border-[#E5E5E5] rounded-xl p-4 text-left text-xs text-[#525252] mb-6 space-y-1.5">
        <span className="font-semibold text-[#171717] block mb-1">
          Suggestions to expand results:
        </span>
        <div className="flex items-center gap-2">
          <span className="text-emerald-600 font-bold">•</span>
          <span>Slightly increase your budget limit</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-emerald-600 font-bold">•</span>
          <span>Relax one of the pattern or material exclusions</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-emerald-600 font-bold">•</span>
          <span>Try broader search keywords</span>
        </div>
      </div>

      {onReset && (
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-[#171717] text-white hover:bg-[#262626] transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Search</span>
        </button>
      )}
    </div>
  );
}
