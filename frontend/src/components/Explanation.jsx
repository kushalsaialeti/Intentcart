import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

function renderFormattedMarkdown(text) {
  if (!text) return null;

  // Split into paragraphs / lines
  const lines = text.split('\n');
  const elements = [];
  let tableRows = [];
  let inTable = false;

  const flushTable = (key) => {
    if (tableRows.length === 0) return;
    const header = tableRows[0];
    const dataRows = tableRows.slice(1).filter((r) => !r.every((cell) => cell.match(/^[-:]+$/)));

    elements.push(
      <div key={`table-${key}`} className="my-4 overflow-x-auto rounded-xl border border-[#E5E5E5] shadow-2xs">
        <table className="min-w-full text-left text-xs divide-y divide-[#E5E5E5]">
          <thead className="bg-[#F3F3F0] text-[#171717] font-semibold">
            <tr>
              {header.map((cell, cIdx) => (
                <th key={cIdx} className="px-3 py-2 sm:px-4 sm:py-2.5 whitespace-nowrap">
                  {cell.trim()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E5E5E5] bg-white">
            {dataRows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-[#FAFAF8] transition-colors">
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#383838]">
                    {cell.trim()}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
    tableRows = [];
    inTable = false;
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();

    // Check for markdown table row
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      inTable = true;
      const cells = trimmed
        .slice(1, -1)
        .split('|')
        .map((c) => c.trim());
      tableRows.push(cells);
      return;
    } else if (inTable) {
      flushTable(idx);
    }

    if (!trimmed) {
      elements.push(<div key={`empty-${idx}`} className="h-2" />);
      return;
    }

    // Headings
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4 key={`h4-${idx}`} className="text-sm sm:text-base font-bold text-[#171717] mt-4 mb-2">
          {trimmed.replace(/^###\s*/, '')}
        </h4>
      );
      return;
    }
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3 key={`h3-${idx}`} className="text-base sm:text-lg font-bold text-[#171717] mt-5 mb-2">
          {trimmed.replace(/^##\s*/, '')}
        </h3>
      );
      return;
    }

    // Bullet list items
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      const content = trimmed.slice(2);
      elements.push(
        <div key={`li-${idx}`} className="flex items-start gap-2 my-1 text-xs sm:text-sm text-[#383838]">
          <span className="text-emerald-600 font-bold mt-0.5">•</span>
          <span>{renderInlineStyles(content)}</span>
        </div>
      );
      return;
    }

    // Numbered list items
    const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
    if (numberedMatch) {
      elements.push(
        <div key={`num-${idx}`} className="flex items-start gap-2 my-1.5 text-xs sm:text-sm text-[#383838]">
          <span className="font-bold text-[#171717] shrink-0">{numberedMatch[1]}.</span>
          <span>{renderInlineStyles(numberedMatch[2])}</span>
        </div>
      );
      return;
    }

    // Regular paragraphs
    elements.push(
      <p key={`p-${idx}`} className="my-1.5 text-xs sm:text-sm text-[#383838] leading-relaxed">
        {renderInlineStyles(trimmed)}
      </p>
    );
  });

  if (inTable) {
    flushTable('last');
  }

  return elements;
}

// Helper to render bold **text**
function renderInlineStyles(text) {
  if (!text.includes('**')) return text;
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-semibold text-[#171717]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

export default function Explanation({ explanation }) {
  if (!explanation) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-5xl mx-auto my-6 sm:my-10 bg-white border border-[#E5E5E5] rounded-2xl p-4 sm:p-6 md:p-8 shadow-xs overflow-hidden"
    >
      <div className="flex items-center gap-2.5 mb-4 pb-3.5 border-b border-[#E5E5E5]">
        <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center border border-amber-200 shrink-0">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <span className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-[#737373]">
            Grounded AI Commentary
          </span>
          <h3 className="text-base sm:text-lg font-bold text-[#171717] leading-tight">
            Stylist Rationale & Constraint Confirmation
          </h3>
        </div>
      </div>

      {/* Formatted responsive markdown view */}
      <div className="w-full overflow-hidden">
        {renderFormattedMarkdown(explanation)}
      </div>
    </motion.div>
  );
}
