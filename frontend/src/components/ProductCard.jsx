import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Check, Star, Sparkles, ExternalLink, ShieldCheck } from 'lucide-react';

export default function ProductCard({ item, rank }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [imgError, setImgError] = useState(false);

  const product = item.product || {};
  const score = item.score || 0;
  const scoreBreakdown = item.score_breakdown || {};
  const evidence = item.matched_requirements || [];

  // Extract clean ID & real Myntra URL
  const cleanId = product.clean_id || String(product.id || '').replace('MYN_ST_', '').replace('MYN_', '');
  const productUrl = product.product_url || `https://www.myntra.com/${cleanId}`;

  // Safe fallback image if network or CDN blocks image
  const fallbackImg = 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&q=80';
  const displayImg = !imgError && product.image_url && product.image_url !== 'unknown'
    ? product.image_url
    : fallbackImg;

  const isOriginalImage = !imgError && product.image_url && product.image_url.includes('assets.myntassets.com');

  return (
    <motion.div
      layout="position"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: rank * 0.08 }}
      className="bg-white border border-[#E5E5E5] rounded-2xl overflow-hidden shadow-xs hover:shadow-md transition-shadow duration-300 flex flex-col h-fit self-start w-full group"
    >
      {/* Product Image & Top Badges — Clickable to open on Myntra */}
      <a
        href={productUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="relative aspect-[3/4] w-full bg-[#F3F3F0] overflow-hidden block cursor-pointer"
        title={`View ${product.title} on Myntra`}
      >
        <img
          src={displayImg}
          alt={product.title}
          onError={() => setImgError(true)}
          className="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-104"
          loading="lazy"
        />

        {/* Hover overlay hint */}
        <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
          <span className="bg-white/95 backdrop-blur-xs text-[#171717] text-xs font-semibold px-3 py-1.5 rounded-full shadow-md flex items-center gap-1.5">
            <span>View on Myntra</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </span>
        </div>

        {/* Rank Badge */}
        <div className="absolute top-2.5 left-2.5 bg-[#171717]/90 backdrop-blur-xs text-white text-[11px] sm:text-xs font-bold px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-md shadow-xs flex items-center gap-1 z-10">
          <span>#{rank}</span>
          <span className="text-amber-400">★</span>
        </div>

        {/* Original Dataset Verification Badge */}
        {isOriginalImage ? (
          <div className="absolute top-2.5 right-2.5 bg-white/95 backdrop-blur-xs text-emerald-800 text-[10px] sm:text-[11px] font-semibold px-2 py-0.5 rounded-md border border-emerald-200 shadow-2xs flex items-center gap-1 z-10">
            <ShieldCheck className="w-3 h-3 text-emerald-600" />
            <span>Original Photo</span>
          </div>
        ) : (
          product.in_stock && (
            <div className="absolute top-2.5 right-2.5 bg-white/95 backdrop-blur-xs text-emerald-700 text-[10px] sm:text-[11px] font-semibold px-2 py-0.5 rounded-md border border-emerald-200 z-10">
              In Stock
            </div>
          )
        )}

        {/* Category Pill on Image Bottom */}
        <div className="absolute bottom-2.5 left-2.5 bg-white/90 backdrop-blur-xs text-[#171717] text-[10px] sm:text-[11px] font-medium px-2 py-0.5 rounded-md z-10">
          {product.category || 'Apparel'} • {product.gender || 'Unisex'}
        </div>
      </a>

      {/* Card Details */}
      <div className="p-3.5 sm:p-5 flex-1 flex flex-col justify-between">
        <div>
          {/* Brand & Rating */}
          <div className="flex items-center justify-between gap-2 mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider text-[#737373]">
              {product.brand || 'Myntra Collection'}
            </span>
            {product.rating && (
              <div className="flex items-center gap-1 text-xs text-[#171717] font-semibold">
                <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                <span>{product.rating}</span>
              </div>
            )}
          </div>

          {/* Title */}
          <h3 className="text-sm sm:text-base font-semibold text-[#171717] line-clamp-2 leading-snug mb-3">
            <a
              href={productUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-neutral-600 transition-colors"
              title={`View ${product.title} on Myntra`}
            >
              {product.title}
            </a>
          </h3>

          {/* Price */}
          <div className="flex items-baseline gap-2 mb-3.5">
            <span className="text-lg sm:text-xl font-bold text-[#171717]">
              ₹{Number(product.price).toLocaleString()}
            </span>
            <span className="text-xs text-[#737373]">Inclusive of all taxes</span>
          </div>

          {/* Key Attributes Tags */}
          <div className="flex flex-wrap gap-1.5 mb-4 text-xs text-[#737373]">
            {product.material && product.material !== 'unknown' && (
              <span className="px-2 py-0.5 rounded bg-[#F3F3F0] text-[#171717] font-medium">
                {product.material}
              </span>
            )}
            {product.pattern && product.pattern !== 'unknown' && (
              <span className="px-2 py-0.5 rounded bg-[#F3F3F0] text-[#171717] font-medium">
                {product.pattern}
              </span>
            )}
            {product.color && product.color !== 'unknown' && (
              <span className="px-2 py-0.5 rounded bg-[#F3F3F0] text-[#171717] font-medium">
                {product.color}
              </span>
            )}
          </div>

          {/* Verified Evidence Checkmarks (Section 25) */}
          <div className="space-y-1 mb-4">
            {evidence.slice(0, 3).map((ev, idx) => (
              <div key={idx} className="flex items-center gap-1.5 text-xs text-[#404040]">
                <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span className="truncate">{ev}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Match Score & Expandable Explanation */}
        <div className="pt-3 border-t border-[#E5E5E5]">
          {/* Score Bar */}
          <div className="mb-3">
            <div className="flex justify-between items-center text-xs font-semibold mb-1">
              <span className="text-[#737373] flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-500" />
                Intent Alignment
              </span>
              <span className="text-[#171717] font-bold">{score}% Match</span>
            </div>
            <div className="w-full h-2 bg-[#F3F3F0] rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(score, 100)}%` }}
                transition={{ duration: 0.6, ease: 'easeOut', delay: rank * 0.1 }}
                className={`h-full rounded-full ${
                  score >= 80 ? 'bg-emerald-600' : score >= 60 ? 'bg-amber-500' : 'bg-blue-500'
                }`}
              />
            </div>
          </div>

          {/* Toggle Why This Matches */}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full flex items-center justify-between py-2 text-xs font-semibold text-[#171717] hover:text-[#737373] transition-colors touch-manipulation cursor-pointer"
          >
            <span>{isExpanded ? 'Hide match breakdown' : 'Why this matches →'}</span>
            {isExpanded ? <ChevronUp className="w-4 h-4 shrink-0" /> : <ChevronDown className="w-4 h-4 shrink-0" />}
          </button>

          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden mt-2 pt-2 border-t border-dashed border-[#E5E5E5] text-xs space-y-2 text-[#404040]"
              >
                {/* Score Breakdown factors */}
                <div className="bg-[#FAFAF8] p-2.5 rounded-lg space-y-1">
                  <div className="text-[11px] font-bold text-[#171717] uppercase tracking-wider mb-1">
                    ML Score Breakdown
                  </div>
                  {scoreBreakdown.semantic !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-[#737373]">Semantic Relevance (50%):</span>
                      <span className="font-semibold">{Math.round(scoreBreakdown.semantic * 50)} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.preference !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-[#737373]">Soft Preferences (20%):</span>
                      <span className="font-semibold">{Math.round(scoreBreakdown.preference * 20)} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.occasion !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-[#737373]">Occasion Match (15%):</span>
                      <span className="font-semibold">{Math.round(scoreBreakdown.occasion * 15)} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.season !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-[#737373]">Season Match (10%):</span>
                      <span className="font-semibold">{Math.round(scoreBreakdown.season * 10)} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.rating !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-[#737373]">Customer Rating (5%):</span>
                      <span className="font-semibold">{Math.round(scoreBreakdown.rating * 5)} pts</span>
                    </div>
                  )}
                </div>

                {/* All matched evidence points */}
                <div className="space-y-1 pt-1">
                  <div className="text-[11px] font-bold text-[#171717] uppercase tracking-wider">
                    All Verified Evidence
                  </div>
                  {evidence.map((ev, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-[11px] text-[#525252]">
                      <span className="text-emerald-600 font-bold">•</span>
                      <span>{ev}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Buy on Myntra Action Button */}
          <a
            href={productUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full mt-3 flex items-center justify-center gap-1.5 py-2.5 px-4 rounded-xl bg-[#171717] hover:bg-[#262626] text-white text-xs font-semibold shadow-2xs transition-all duration-200 touch-manipulation group"
          >
            <span>Buy on Myntra</span>
            <ExternalLink className="w-3.5 h-3.5 text-neutral-400 group-hover:text-white transition-colors" />
          </a>
        </div>
      </div>
    </motion.div>
  );
}
