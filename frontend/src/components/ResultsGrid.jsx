import React from 'react';
import ProductCard from './ProductCard';

export default function ResultsGrid({ results }) {
  if (!results || results.length === 0) return null;

  return (
    <section className="w-full max-w-5xl mx-auto my-6 sm:my-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-4 sm:mb-6 pb-3 border-b border-[#E5E5E5]">
        <div>
          <span className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-[#737373]">
            Curated Recommendations
          </span>
          <h2 className="text-lg sm:text-2xl font-bold text-[#171717] tracking-tight">
            Top Matches Ranked For You
          </h2>
        </div>
        <span className="self-start sm:self-auto text-[11px] sm:text-xs font-semibold px-2.5 sm:px-3 py-1 rounded-full bg-[#F3F3F0] text-[#171717] border border-[#E5E5E5]">
          {results.length} Products Verified
        </span>
      </div>

      {/* Fully Responsive Grid with items-start: prevents neighbor cards from stretching when one expands */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 items-start">
        {results.map((item, idx) => (
          <ProductCard key={item.product?.id || idx} item={item} rank={item.rank || idx + 1} />
        ))}
      </div>
    </section>
  );
}
