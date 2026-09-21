import React, { useState } from 'react';
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
import { Sparkles } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchData, setSearchData] = useState(null);

  const handleSearch = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q || !q.trim() || isLoading) return;

    setQuery(q);
    setIsLoading(true);
    setError(null);

    try {
      const response = await searchProducts(q, 5);
      setSearchData(response);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'Unable to complete search request');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setQuery('');
    setSearchData(null);
    setError(null);
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

      <Navbar />

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

        {/* Error State */}
        {!isLoading && error && (
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
