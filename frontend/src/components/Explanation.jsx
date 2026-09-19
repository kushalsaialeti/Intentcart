import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, MessageSquare } from 'lucide-react';

export default function Explanation({ explanation }) {
  if (!explanation) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-5xl mx-auto my-8 bg-white border border-[#E5E5E5] rounded-2xl p-6 sm:p-8 shadow-xs"
    >
      <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-[#E5E5E5]">
        <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center border border-amber-200">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#737373]">
            Grounded AI Commentary
          </span>
          <h3 className="text-lg font-bold text-[#171717]">
            Stylist Rationale & Constraint Confirmation
          </h3>
        </div>
      </div>

      <div className="prose prose-sm max-w-none text-[#383838] leading-relaxed whitespace-pre-line font-normal">
        {explanation}
      </div>
    </motion.div>
  );
}
