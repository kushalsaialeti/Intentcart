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
      className="w-full max-w-5xl mx-auto my-5 sm:my-8 bg-[#131318]/90 backdrop-blur-md border border-[#27272a] rounded-2xl p-4 sm:p-6 shadow-xl"
    >
      {/* Header & Racing Telemetry */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3.5 sm:pb-4 border-b border-[#27272a]">
        <div>
          <span className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-[#a1a1aa]">
            Engine Understanding
          </span>
          <h2 className="text-base sm:text-xl font-bold text-white leading-tight">
            We Interpreted Your Request
          </h2>
        </div>

        {/* Telemetry pill */}
        {telemetry.intent_winner && (
          <div className="self-start sm:self-auto inline-flex flex-wrap items-center gap-1.5 bg-[#1c1c24] px-2.5 sm:px-3 py-1 rounded-full border border-[#2e2e38] text-[10px] sm:text-xs font-medium text-white shadow-xs">
            <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Fastest: <strong className="font-semibold text-emerald-400">{telemetry.intent_winner}</strong></span>
            <span className="text-[#52525b]">•</span>
            <span className="text-[#a1a1aa]">{telemetry.intent_latency_ms} ms</span>
          </div>
        )}
      </div>

      {/* Constraints Grid: stacks on mobile (< 768px), 2 columns on tablet/desktop (>= 768px) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mt-3.5 sm:mt-4">
        {/* Mandatory Hard Constraints */}
        <div>
          <div className="flex items-center gap-1.5 text-[10px] sm:text-xs font-bold text-white uppercase tracking-wider mb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Strict Requirements (Deterministic Filters)</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {hardTags.length > 0 ? (
              hardTags.map((tag, idx) => (
                <span
                  key={idx}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] sm:text-xs font-medium ${
                    tag.type === 'excluded'
                      ? 'bg-rose-950/50 text-rose-300 border border-rose-800/60'
                      : 'bg-emerald-950/50 text-emerald-300 border border-emerald-800/60'
                  }`}
                >
                  {tag.type === 'excluded' ? <Ban className="w-3 h-3 shrink-0" /> : <CheckCircle2 className="w-3 h-3 shrink-0" />}
                  <span>{tag.label}</span>
                </span>
              ))
            ) : (
              <span className="text-xs text-[#a1a1aa]">No strict exclusions specified</span>
            )}
          </div>
        </div>

        {/* Soft Preferences */}
        <div>
          <div className="flex items-center gap-1.5 text-[10px] sm:text-xs font-bold text-white uppercase tracking-wider mb-2">
            <Sliders className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span>Soft Preferences (Hybrid Weights)</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {softTags.length > 0 ? (
              softTags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-md text-[10px] sm:text-xs font-medium bg-[#1f1f24] text-[#e4e4e7] border border-[#2e2e38] capitalize"
                >
                  {tag}
                </span>
              ))
            ) : (
              <span className="text-xs text-[#a1a1aa]">General catalog relevance</span>
            )}
          </div>
        </div>
      </div>

      {/* Reformulated vector query & filtering stats */}
      <div className="mt-4 pt-3 border-t border-[#27272a] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] sm:text-xs text-[#a1a1aa]">
        {reformulatedQuery && (
          <div className="break-words min-w-0">
            <span className="font-semibold text-white">Dense Vector Query: </span>
            <span className="italic text-[#d4d4d8]">"{reformulatedQuery}"</span>
          </div>
        )}
        {metadata && (
          <div className="shrink-0 flex flex-wrap items-center gap-1.5">
            <span className="text-[#a1a1aa]">Filter Pipeline:</span>
            <span className="px-1.5 py-0.5 rounded bg-[#1f1f24] text-white font-semibold border border-[#2e2e38]">
              {metadata.retrieved_count} retrieved
            </span>
            <span className="text-[#52525b]">→</span>
            <span className="px-1.5 py-0.5 rounded bg-rose-950/50 text-rose-300 font-semibold border border-rose-800/50">
              {metadata.rejected_count} excluded
            </span>
            <span className="text-[#52525b]">→</span>
            <span className="px-1.5 py-0.5 rounded bg-emerald-950/50 text-emerald-300 font-semibold border border-emerald-800/50">
              {metadata.final_count} ranked
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
