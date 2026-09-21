import React, { useState, useRef } from 'react';
import Navbar from './components/Navbar';
import SearchBox from './components/SearchBox';
import ExampleChips from './components/ExampleChips';
import IntentPanel from './components/IntentPanel';
import ResultsGrid from './components/ResultsGrid';
import Explanation from './components/Explanation';
import LoadingState from './components/LoadingState';
import EmptyState from './components/EmptyState';
import ErrorState from './components/ErrorState';
import ShapeGrid from './components/ShapeGrid';
import { searchProducts } from './services/api';
import { Sparkles, AlertCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchData, setSearchData] = useState(null);
  const [isStopped, setIsStopped] = useState(false);
  const abortControllerRef = useRef(null);

  const handleSearch = async (searchQuery) => {
    const q = searchQuery !== undefined ? searchQuery : query;
    if (!q || !q.trim()) return;

    // Abort any existing pending search
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setQuery(q);
    setIsLoading(true);
    setError(null);
    setIsStopped(false);

    try {
      const response = await searchProducts(q, 5, controller.signal);
      setSearchData(response);
    } catch (err) {
      if (err.name === 'AbortError') {
        // Handled cleanly by handleStop
        return;
      }
      console.error('Search error:', err);
      setError(err.message || 'Unable to complete search request');
    } finally {
      if (abortControllerRef.current === controller) {
        setIsLoading(false);
        abortControllerRef.current = null;
      }
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
    setIsStopped(true);
  };

  const handleReset = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setQuery('');
    setSearchData(null);
    setError(null);
    setIsStopped(false);
    setIsLoading(false);
  };

  return (
    <div className="relative min-h-screen flex flex-col bg-[#0a0a0e] text-[#f4f4f5] selection:bg-purple-500/30 selection:text-white">
      {/* Ambient Animated ShapeGrid Background with very slow, unnoticeable motion */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden" aria-hidden="true">
        <ShapeGrid
          direction="diagonal"
          speed={0.06}
          borderColor="rgba(255, 255, 255, 0.04)"
          squareSize={46}
          hoverFillColor="rgba(255, 255, 255, 0.07)"
          shape="square"
          hoverTrailAmount={2}
        />
      </div>

      <Navbar onReset={handleReset} />

      <main className="relative z-10 flex-1 max-w-6xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-5 sm:py-10">
        {/* Hero & Search Section */}
        <section className="text-center max-w-3xl mx-auto mb-6 sm:mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#18181b]/80 backdrop-blur text-[10px] sm:text-xs font-semibold text-[#a1a1aa] border border-[#27272a] mb-3 sm:mb-4 shadow-sm max-w-full">
            {/* <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" /> */}
            <span className="truncate sm:whitespace-normal">Constraint-Aware Conversational Fashion Engine</span>
          </div>

          <h1 className="text-2xl sm:text-4xl md:text-5xl font-extrabold text-white tracking-tight leading-[1.18] sm:leading-[1.15] mb-2 sm:mb-3">
            Shop The Way You Think
          </h1>

          <p className="text-xs sm:text-base text-[#a1a1aa] max-w-xl mx-auto mb-5 sm:mb-8 leading-relaxed px-1 sm:px-0">
            Describe what you need in natural language. We strictly enforce your constraints
            and rank products by true styling intent.
          </p>

          {/* Search Box */}
          <SearchBox
            query={query}
            setQuery={setQuery}
            onSearch={handleSearch}
            onStop={handleStop}
            isLoading={isLoading}
          />

          {/* Example Queries */}
          <ExampleChips
            onSelect={(selectedQuery) => {
              setQuery(selectedQuery);
              handleSearch(selectedQuery);
            }}
            currentQuery={query}
            isLoading={isLoading}
          />
        </section>

        {/* Loading State */}
        {isLoading && <LoadingState />}

        {/* Stopped / Interrupted State: "Oops" Red Card */}
        {!isLoading && isStopped && (
          <div className="w-full max-w-lg mx-auto my-6 p-6 sm:p-7 rounded-3xl bg-gradient-to-b from-[#240e13]/95 to-[#140608]/98 border border-rose-500/40 shadow-[0_0_50px_rgba(244,63,94,0.18)] backdrop-blur-xl text-center flex flex-col items-center animate-in fade-in zoom-in-95 duration-300">
            <div className="w-13 h-13 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-400 flex items-center justify-center mb-3.5 shadow-[0_0_20px_rgba(244,63,94,0.3)]">
              <AlertCircle className="w-7 h-7 text-rose-400" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-white mb-2 tracking-tight">
              Oops! Search Stopped
            </h3>
            <p className="text-xs sm:text-sm text-rose-200/70 max-w-md mx-auto mb-5 leading-relaxed">
              Your search was interrupted. Your query and constraints are kept safe  above so you can tweak any detail!
            </p>
            <button
              type="button"
              onClick={() => {
                setIsStopped(false);
                const input = document.querySelector('.prompt-bar__input');
                input?.focus();
              }}
              className="px-6 py-2.5 sm:py-3 rounded-2xl font-bold text-xs sm:text-sm bg-gradient-to-r from-rose-500 via-rose-600 to-red-600 hover:from-rose-400 hover:to-red-500 text-white shadow-lg shadow-rose-950/70 hover:shadow-rose-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all cursor-pointer select-none"
            >
              lets try something new for youu!!!
            </button>
          </div>
        )}

        {/* Error State */}
        {!isLoading && !isStopped && error && (
          <ErrorState error={error} onRetry={() => handleSearch(query)} />
        )}

        {/* Results Flow */}
        {!isLoading && !error && searchData && (
          <>
            {searchData.results?.length === 0 ? (
              <EmptyState onReset={handleReset} />
            ) : (
              <>
                {/* 1. Interpreted Requirements & Telemetry */}
                <IntentPanel
                  intent={searchData.intent}
                  metadata={searchData.metadata}
                  reformulatedQuery={searchData.reformulated_query}
                />

                {/* 2. Ranked Product Matches */}
                <ResultsGrid results={searchData.results} />

                {/* 3. Grounded Stylist Explanation */}
                <Explanation explanation={searchData.stylist_explanation} />
              </>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[#27272a] bg-[#0a0a0e]/80 backdrop-blur-md py-4 sm:py-6 text-center text-[10px] sm:text-xs text-[#a1a1aa] safe-bottom">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-1.5 sm:gap-2">
          <span>IntentCart AI — Multi-Model Racing & Grounded Fashion Retrieval</span>
          <span className="text-[#71717a]">1,200 Products • FAISS Dense Index • Google Gemini & Groq</span>
        </div>
      </footer>
    </div>
  );
}
