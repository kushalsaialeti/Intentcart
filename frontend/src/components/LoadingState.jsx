import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Sparkles } from 'lucide-react';

const STAGES = [
  'Understanding your request...',
  'Finding relevant products...',
  'Comparing matches & applying filters...',
  'Preparing recommendations...',
];

export default function LoadingState() {
  const [stageIdx, setStageIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIdx((prev) => (prev + 1 < STAGES.length ? prev + 1 : prev));
    }, 1200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full max-w-5xl mx-auto my-12 text-center">
      {/* Dynamic friendly message */}
      <motion.div
        key={stageIdx}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.3 }}
        className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-white border border-[#E5E5E5] shadow-xs mb-8"
      >
        <Loader2 className="w-4 h-4 text-[#171717] animate-spin" />
        <span className="text-sm font-semibold text-[#171717]">{STAGES[stageIdx]}</span>
      </motion.div>

      {/* Skeletons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-white border border-[#E5E5E5] rounded-2xl p-4 flex flex-col gap-4 animate-pulse shadow-xs"
          >
            <div className="aspect-3/4 w-full bg-[#F3F3F0] rounded-xl" />
            <div className="space-y-2">
              <div className="h-3 w-1/3 bg-[#F3F3F0] rounded" />
              <div className="h-4 w-5/6 bg-[#F3F3F0] rounded" />
              <div className="h-5 w-1/4 bg-[#F3F3F0] rounded" />
            </div>
            <div className="h-8 w-full bg-[#F3F3F0] rounded-lg mt-auto" />
          </div>
        ))}
      </div>
    </div>
  );
}
