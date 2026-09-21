import React from 'react';
import PromptBar from './PromptBar';

export default function SearchBox({ query, setQuery, onSearch, isLoading }) {
  const handleSend = (text, meta) => {
    if (text && !isLoading) {
      onSearch(text);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <PromptBar
        value={query}
        onChange={setQuery}
        onSend={handleSend}
        busy={isLoading}
        placeholder="Describe what you need in natural language..."
        width={680}
      />
    </div>
  );
}
