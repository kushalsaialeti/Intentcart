import React from 'react';
import { motion } from 'framer-motion';

const EXAMPLES = [
  {
    label: 'Wedding Kurta (No Floral)',
    query: "I need a comfortable minimal wedding kurta for summer, no floral patterns and under ₹3000.",
  },
  {
    label: 'Men’s Cotton Shirt (No Stripes)',
    query: "Looking for a men's casual slim-fit shirt under 2000, breathable cotton, no stripes",
  },
  {
    label: 'Women’s Stretch Blue Jeans',
    query: "I want women's blue jeans, stretchable and comfortable, under 3500",
  },
  {
    label: 'Minimal Black Wedding Kurta',
    query: "I need a minimal black kurta for a summer wedding under 3000",
  },
  {
    label: 'Breezy Summer Dress',
    query: "Need a casual summer dress for women, breathable and light",
  },
];

export default function ExampleChips({ onSelect, currentQuery, isLoading }) {
  return (
    <div className="w-full max-w-2xl mx-auto mt-4 sm:mt-5 px-2 sm:px-0">
      <div className="flex items-center justify-center sm:justify-start gap-2 mb-2.5 text-center sm:text-left">
        <span className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-[#a1a1aa]">
          Try asking naturally:
        </span>
      </div>
      {/* Symmetrically centered chips on mobile screens */}
      <div className="flex flex-wrap justify-center sm:justify-start gap-1.5 sm:gap-2 pb-1 sm:pb-0">
        {EXAMPLES.map((item, idx) => {
          const isActive = currentQuery === item.query;
          return (
            <motion.button
              key={idx}
              whileTap={{ scale: 0.97 }}
              disabled={isLoading}
              onClick={() => onSelect(item.query)}
              className={`text-[11px] sm:text-xs px-3 py-1.5 rounded-full border transition-all cursor-pointer active:opacity-80 touch-manipulation min-h-[32px] sm:min-h-[34px] flex items-center text-center ${
                isActive
                  ? 'bg-white text-[#0a0a0e] border-white shadow-sm font-semibold'
                  : 'bg-[#18181b]/70 backdrop-blur text-[#d4d4d8] border-[#27272a] hover:border-white/30 hover:bg-[#27272a] hover:text-white'
              }`}
            >
              {item.label}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
