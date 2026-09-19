import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Sliders, Zap, CheckCircle2, Ban } from 'lucide-react';

export default function IntentPanel({ intent, metadata, reformulatedQuery }) {
  if (!intent) return null;

  const hard = intent.hard_constraints || {};
  const soft = intent.soft_preferences || {};
  const negatives = intent.negative_preferences || [];
  const telemetry = metadata?.telemetry || {};

  // Build readable hard constraint tags
  const hardTags = [];
  if (hard.gender) hardTags.push({ label: `Gender: ${hard.gender}`, type: 'mandatory' });
  if (hard.category) hardTags.push({ label: `Category: ${hard.category}`, type: 'mandatory' });
  if (hard.max_price) hardTags.push({ label: `Max: ₹${hard.max_price.toLocaleString()}`, type: 'mandatory' });
  if (hard.in_stock_only !== false) hardTags.push({ label: 'In-Stock Only', type: 'mandatory' });

  // Negative tags
  negatives.forEach((neg) => {
    hardTags.push({ label: neg, type: 'excluded' });
  });

  // Build soft preference tags
  const softTags = [];
  if (soft.occasion) softTags.push(`Occasion: ${soft.occasion}`);
  if (soft.season) softTags.push(`Season: ${soft.season}`);
  if (Array.isArray(soft.preferences)) {
    soft.preferences.forEach((p) => softTags.push(p));
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-5xl mx-auto my-5 sm:my-8 bg-white border border-[#E5E5E5] rounded-2xl p-3.5 sm:p-6 shadow-xs"
    >
      {/* Header & Racing Telemetry */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3.5 sm:pb-4 border-b border-[#E5E5E5]">
        <div>
          <span className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-[#737373]">
            Engine Understanding
          </span>
          <h2 className="text-base sm:text-xl font-bold text-[#171717] leading-tight">
            We Interpreted Your Request
          </h2>
        </div>

        {/* Telemetry pill */}
        {telemetry.intent_winner && (
          <div className="self-start sm:self-auto inline-flex flex-wrap items-center gap-1.5 bg-[#F3F3F0] px-2.5 sm:px-3 py-1 rounded-full border border-[#E5E5E5] text-[10px] sm:text-xs font-medium text-[#171717]">
            <Zap className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            <span>Fastest: <strong className="font-semibold">{telemetry.intent_winner}</strong></span>
            <span className="text-[#A3A3A3]">•</span>
            <span className="text-[#737373]">{telemetry.intent_latency_ms} ms</span>
          </div>
        )}
      </div>

      {/* Constraints Grid: stacks on mobile (< 768px), 2 columns on tablet/desktop (>= 768px) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mt-3.5 sm:mt-4">
        {/* Mandatory Hard Constraints */}
        <div>
          <div className="flex items-center gap-1.5 text-[10px] sm:text-xs font-bold text-[#171717] uppercase tracking-wider mb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>Strict Requirements (Deterministic Filters)</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {hardTags.length > 0 ? (
              hardTags.map((tag, idx) => (
                <span
                  key={idx}
                  className={`inline-flex items-center gap-1 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-md text-[10px] sm:text-xs font-medium ${
                    tag.type === 'excluded'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                  }`}
                >
                  {tag.type === 'excluded' ? <Ban className="w-3 h-3 shrink-0" /> : <CheckCircle2 className="w-3 h-3 shrink-0" />}
                  <span>{tag.label}</span>
                </span>
              ))
            ) : (
              <span className="text-xs text-[#737373]">No strict exclusions specified</span>
            )}
          </div>
        </div>

        {/* Soft Preferences */}
        <div>
          <div className="flex items-center gap-1.5 text-[10px] sm:text-xs font-bold text-[#171717] uppercase tracking-wider mb-2">
            <Sliders className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <span>Soft Preferences (Hybrid Weights)</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {softTags.length > 0 ? (
              softTags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-md text-[10px] sm:text-xs font-medium bg-[#F3F3F0] text-[#171717] border border-[#E5E5E5] capitalize"
                >
                  {tag}
                </span>
              ))
            ) : (
              <span className="text-xs text-[#737373]">General catalog relevance</span>
            )}
          </div>
        </div>
      </div>

      {/* Reformulated vector query & filtering stats */}
      <div className="mt-4 pt-3 border-t border-[#E5E5E5] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] sm:text-xs text-[#737373]">
        {reformulatedQuery && (
          <div className="break-words min-w-0">
            <span className="font-semibold text-[#171717]">Dense Vector Query: </span>
            <span className="italic">"{reformulatedQuery}"</span>
          </div>
        )}
        {metadata && (
          <div className="shrink-0 flex flex-wrap items-center gap-1.5">
            <span className="text-[#737373]">Filter Pipeline:</span>
            <span className="px-1.5 py-0.5 rounded bg-[#F3F3F0] text-[#171717] font-semibold border border-[#E5E5E5]">
              {metadata.retrieved_count} retrieved
            </span>
            <span>→</span>
            <span className="px-1.5 py-0.5 rounded bg-rose-50 text-rose-700 font-semibold border border-rose-200">
              {metadata.rejected_count} excluded
            </span>
            <span>→</span>
            <span className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 font-semibold border border-emerald-200">
              {metadata.final_count} ranked
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
