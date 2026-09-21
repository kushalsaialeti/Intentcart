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
      <div key={`table-${key}`} className="my-4 overflow-x-auto rounded-xl border border-[#27272a] shadow-md">
        <table className="min-w-full text-left text-xs divide-y divide-[#27272a]">
          <thead className="bg-[#1c1c24] text-white font-semibold">
            <tr>
              {header.map((cell, cIdx) => (
                <th key={cIdx} className="px-3 py-2 sm:px-4 sm:py-2.5 whitespace-nowrap">
                  {cell.trim()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#27272a] bg-[#131318]">
            {dataRows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-[#1a1a22] transition-colors">
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#d4d4d8]">
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
        <h4 key={`h4-${idx}`} className="text-sm sm:text-base font-bold text-white mt-4 mb-2">
          {trimmed.replace(/^###\s*/, '')}
        </h4>
      );
      return;
    }
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3 key={`h3-${idx}`} className="text-base sm:text-lg font-bold text-white mt-5 mb-2">
          {trimmed.replace(/^##\s*/, '')}
        </h3>
      );
      return;
    }

    // Bullet list items
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      const content = trimmed.slice(2);
      elements.push(
        <div key={`li-${idx}`} className="flex items-start gap-2 my-1 text-xs sm:text-sm text-[#d4d4d8]">
          <span className="text-emerald-400 font-bold mt-0.5">•</span>
          <span>{renderInlineStyles(content)}</span>
        </div>
      );
      return;
    }

    // Numbered list items
    const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
    if (numberedMatch) {
      elements.push(
        <div key={`num-${idx}`} className="flex items-start gap-2 my-1.5 text-xs sm:text-sm text-[#d4d4d8]">
          <span className="font-bold text-white shrink-0">{numberedMatch[1]}.</span>
          <span>{renderInlineStyles(numberedMatch[2])}</span>
        </div>
      );
      return;
    }

    // Regular paragraphs
    elements.push(
      <p key={`p-${idx}`} className="my-1.5 text-xs sm:text-sm text-[#d4d4d8] leading-relaxed">
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
        <strong key={i} className="font-semibold text-white">
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
      className="w-full max-w-5xl mx-auto my-6 sm:my-10 bg-[#131318]/90 backdrop-blur-md border border-[#27272a] rounded-2xl p-4 sm:p-6 md:p-8 shadow-xl overflow-hidden text-[#f4f4f5]"
    >
      <div className="flex items-center gap-2.5 mb-4 pb-3.5 border-b border-[#27272a]">
        <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center border border-amber-500/20 shrink-0">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <span className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-[#a1a1aa]">
            Grounded AI Commentary
          </span>
          <h3 className="text-base sm:text-lg font-bold text-white leading-tight">
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
