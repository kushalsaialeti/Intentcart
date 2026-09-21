import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function ErrorState({ error, onRetry }) {
  return (
    <div className="w-full max-w-xl mx-auto my-8 sm:my-12 bg-[#08080b]/95 backdrop-blur-xl border border-rose-900/50 rounded-2xl p-5 sm:p-8 text-center shadow-2xl text-[#f4f4f5]">
      <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto rounded-full bg-rose-950/40 border border-rose-800/50 flex items-center justify-center text-rose-400 mb-3 sm:mb-4">
        <AlertCircle className="w-5 h-5 sm:w-6 sm:h-6" />
      </div>
      <h3 className="text-base sm:text-lg font-bold text-white mb-1.5 sm:mb-2">Something Went Wrong</h3>
      <p className="text-xs sm:text-sm text-[#a1a1aa] mb-4 sm:mb-5 leading-relaxed">
        {error || 'Unable to complete search request. Please verify connection and try again.'}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-white text-[#0a0a0e] hover:bg-neutral-200 transition-colors shadow-md cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Retry Search</span>
        </button>
      )}
    </div>
  );
}
