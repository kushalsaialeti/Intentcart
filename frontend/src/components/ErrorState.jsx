import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function ErrorState({ error, onRetry }) {
  return (
    <div className="w-full max-w-xl mx-auto my-12 bg-white border border-rose-200 rounded-2xl p-8 text-center shadow-xs">
      <div className="w-12 h-12 mx-auto rounded-full bg-rose-50 flex items-center justify-center text-rose-600 mb-4">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h3 className="text-lg font-bold text-[#171717] mb-2">Something Went Wrong</h3>
      <p className="text-sm text-[#737373] mb-5">
        {error || 'Unable to complete search request. Please verify connection and try again.'}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-[#171717] text-white hover:bg-[#262626] transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Retry Search</span>
        </button>
      )}
    </div>
  );
}
