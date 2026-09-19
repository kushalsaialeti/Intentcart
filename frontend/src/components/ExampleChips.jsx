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
    <div className="w-full max-w-3xl mx-auto mt-3 sm:mt-4">
      <div className="flex items-center gap-2 mb-2 text-left">
        <span className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-[#737373]">
          Try asking naturally:
        </span>
      </div>
      {/* Scrollable on small devices, wrapped on tablets/desktops */}
      <div className="flex overflow-x-auto no-scrollbar sm:flex-wrap gap-1.5 sm:gap-2 pb-1 sm:pb-0 -mx-1 px-1 touch-pan-x">
        {EXAMPLES.map((item, idx) => {
          const isActive = currentQuery === item.query;
          return (
            <motion.button
              key={idx}
              whileTap={{ scale: 0.97 }}
              disabled={isLoading}
              onClick={() => onSelect(item.query)}
              className={`text-[11px] sm:text-xs px-2.5 sm:px-3 py-1.5 rounded-full border transition-all text-left whitespace-nowrap sm:whitespace-normal cursor-pointer active:opacity-80 touch-manipulation shrink-0 sm:shrink min-h-[32px] sm:min-h-[34px] flex items-center ${
                isActive
                  ? 'bg-[#171717] text-white border-[#171717] shadow-2xs font-semibold'
                  : 'bg-white text-[#171717] border-[#E5E5E5] hover:border-[#171717]/40 hover:bg-[#F3F3F0]'
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
