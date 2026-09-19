import React from 'react';
import ProductCard from './ProductCard';

export default function ResultsGrid({ results }) {
  if (!results || results.length === 0) return null;

  return (
    <section className="w-full max-w-5xl mx-auto my-8">
      <div className="flex items-center justify-between mb-6 pb-2 border-b border-[#E5E5E5]">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#737373]">
            Curated Recommendations
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-[#171717]">
            Top Matches Ranked For You
          </h2>
        </div>
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-[#F3F3F0] text-[#171717] border border-[#E5E5E5]">
          {results.length} Products Verified
        </span>
      </div>

      {/* Responsive Grid: 1 col mobile, 2 col tablet, 3 col desktop */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {results.map((item, idx) => (
          <ProductCard key={item.product?.id || idx} item={item} rank={item.rank || idx + 1} />
        ))}
      </div>
    </section>
  );
}
