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
import { searchProducts } from './services/api';
import { Sparkles, ArrowRight } from 'lucide-react';

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
    <div className="min-h-screen flex flex-col bg-[#FAFAF8] text-[#171717]">
      <Navbar />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Hero & Search Section */}
        <section className="text-center max-w-3xl mx-auto mb-8 sm:mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#F3F3F0] text-xs font-semibold text-[#737373] border border-[#E5E5E5] mb-4 shadow-2xs">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Constraint-Aware Conversational Fashion Engine</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold text-[#171717] tracking-tight leading-[1.15] mb-3 sm:mb-4">
            Shop The Way You Think
          </h1>

          <p className="text-sm sm:text-base text-[#737373] max-w-xl mx-auto mb-8 leading-relaxed">
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
      <footer className="border-t border-[#E5E5E5] py-6 text-center text-xs text-[#737373]">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>IntentCart AI — Multi-Model Racing & Grounded Fashion Retrieval</span>
          <span className="text-[#A3A3A3]">1,200 Products Indexed • FAISS IndexFlatIP • Google Gemini & Groq</span>
        </div>
      </footer>
    </div>
  );
}
