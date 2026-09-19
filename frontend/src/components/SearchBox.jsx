import React, { useRef } from 'react';
import { Search, X, Sparkles, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function SearchBox({ query, setQuery, onSearch, isLoading }) {
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query);
    }
  };

  const handleClear = () => {
    setQuery('');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="relative group w-full">
        <div className="relative flex items-center bg-white rounded-2xl border border-[#E5E5E5] shadow-xs hover:border-[#171717]/30 focus-within:border-[#171717] focus-within:ring-2 focus-within:ring-[#171717]/5 transition-all duration-200">
          <div className="pl-3 sm:pl-5 text-[#737373] shrink-0">
            <Search className="w-4 h-4 sm:w-5 sm:h-5" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe what you need in natural language..."
            enterKeyHint="search"
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck="false"
            className="flex-1 min-w-0 py-3 sm:py-4 px-2 sm:px-3.5 text-base sm:text-lg text-[#171717] placeholder:text-[#A3A3A3] bg-transparent outline-none focus:outline-none"
            disabled={isLoading}
          />

          <div className="pr-1.5 sm:pr-3 flex items-center gap-1 shrink-0">
            {query && !isLoading && (
              <button
                type="button"
                onClick={handleClear}
                className="p-1 sm:p-1.5 rounded-full text-[#737373] hover:text-[#171717] hover:bg-[#F3F3F0] transition-colors touch-manipulation"
                title="Clear input"
                aria-label="Clear input"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            <motion.button
              whileTap={{ scale: 0.96 }}
              type="submit"
              disabled={!query.trim() || isLoading}
              className={`flex items-center justify-center gap-1.5 sm:gap-2 px-3 sm:px-5 py-2 sm:py-2.5 rounded-xl font-semibold text-xs sm:text-sm transition-all duration-200 min-h-[38px] sm:min-h-[44px] shrink-0 touch-manipulation ${
                query.trim() && !isLoading
                  ? 'bg-[#171717] text-white hover:bg-[#262626] shadow-xs'
                  : 'bg-[#F3F3F0] text-[#A3A3A3] cursor-not-allowed'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin shrink-0" />
                  <span className="hidden xs:inline sm:inline">Searching...</span>
                </>
              ) : (
                <>
                  <span>Find</span>
                  <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                </>
              )}
            </motion.button>
          </div>
        </div>
      </div>
    </form>
  );
}
