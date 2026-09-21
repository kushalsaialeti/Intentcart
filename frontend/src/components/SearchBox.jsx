import React from 'react';
import PromptBar from './PromptBar';

export default function SearchBox({ query, setQuery, onSearch, onStop, isLoading }) {
  const handleSend = (text, meta) => {
    if (text && !isLoading) {
      onSearch(text);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col items-center justify-center px-2 sm:px-0">
      <PromptBar
        value={query}
        onChange={setQuery}
        onSend={handleSend}
        onStop={onStop}
        busy={isLoading}
        placeholder="Describe what you need in natural language..."
        width={680}
        className="w-full"
      />
    </div>
  );
}
