import React from 'react';
import { motion } from 'framer-motion';

const EXAMPLES = [
  {
    label: 'Summer Wedding Kurta (No Floral)',
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
    <div className="w-full max-w-3xl mx-auto mt-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#737373]">
          Try asking naturally:
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {EXAMPLES.map((item, idx) => {
          const isActive = currentQuery === item.query;
          return (
            <motion.button
              key={idx}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              disabled={isLoading}
              onClick={() => onSelect(item.query)}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all text-left ${
                isActive
                  ? 'bg-[#171717] text-white border-[#171717]'
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
