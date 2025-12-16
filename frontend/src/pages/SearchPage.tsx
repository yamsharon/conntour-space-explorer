import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SearchResult, searchImages } from '../api/client';
import { SourceCard } from '../components/Sources';

type SearchBarProps = {
  query: string;
  onQueryChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
};

type LoadingSpinnerProps = {
  message?: string;
};

type ErrorMessageProps = {
  error: Error | null;
};

type EmptyStateProps = {
  query: string;
};

type SearchResultsProps = {
  results: SearchResult[];
};

/**
 * SearchBar component - AI-style search input with centered layout.
 * 
 * Features:
 * - Centered search input with icon
 * - Submit button that disables during loading
 * - Responsive design with max-width constraint
 * 
 * @param query - Current search query value
 * @param onQueryChange - Callback when input value changes
 * @param onSubmit - Callback when form is submitted
 * @param isLoading - Whether a search is currently in progress
 */
const SearchBar: React.FC<SearchBarProps> = ({ query, onQueryChange, onSubmit, isLoading }) => {
  return (
    <form onSubmit={onSubmit} className="flex flex-col items-center mb-8">
      <label className="mb-4 text-lg text-gray-700 font-medium" htmlFor="search-input">
        Search NASA Space Images
      </label>
      <div className="w-full max-w-2xl">
        <div className="flex items-center rounded-full shadow-lg bg-white px-4 py-3 border border-gray-200 hover:border-blue-300 transition-colors">
          <svg
            className="w-5 h-5 text-gray-400 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            id="search-input"
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder='e.g. "Astronauts in suits" or "NASA"'
            className="flex-1 bg-transparent outline-none text-gray-900 placeholder-gray-400 px-2 py-1"
          />
          <button
            type="submit"
            className="ml-2 px-6 py-2 rounded-full bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            disabled={!query.trim() || isLoading}
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>
    </form>
  );
};

/**
 * LoadingSpinner component - Displays a loading indicator.
 * 
 * Shows an animated spinner with an optional message below it.
 * Used to indicate that a search operation is in progress.
 * 
 * @param message - Optional message to display below the spinner
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message }) => {
  return (
    <div className="flex flex-col justify-center items-center py-16">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      {message && <p className="mt-4 text-gray-600">{message}</p>}
    </div>
  );
};

/**
 * ErrorMessage component - Displays error information when a search fails.
 * 
 * Shows a user-friendly error message with optional detailed error information.
 * Only displayed when a search operation has failed.
 * 
 * @param error - The error object containing error details, or null
 */
const ErrorMessage: React.FC<ErrorMessageProps> = ({ error }) => {
  return (
    <div className="text-red-500 text-center mb-4">
      Something went wrong while searching. Please try again.
      {error && (
        <div className="text-sm mt-2 text-gray-600">
          {error.message}
        </div>
      )}
    </div>
  );
};

/**
 * EmptyState component - Displays a message when no search results are found.
 * 
 * Shown when a search query has been executed but returned no results.
 * Displays the query that was searched to provide context to the user.
 * 
 * @param query - The search query that returned no results
 */
const EmptyState: React.FC<EmptyStateProps> = ({ query }) => {
  return (
    <div className="text-center text-gray-600">
      No results found for <span className="font-semibold">"{query}"</span>.
    </div>
  );
};

/**
 * SearchResults component - Displays search results in a responsive grid layout.
 * 
 * Renders search results using the same grid layout as the Browse page.
 * Each result is displayed as a SourceCard with confidence score.
 * 
 * Grid layout:
 * - 1 column on mobile
 * - 2 columns on medium screens (md)
 * - 3 columns on large screens (lg)
 * 
 * @param results - Array of search results with confidence scores
 */
const SearchResults: React.FC<SearchResultsProps> = ({ results }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {results.map((result) => (
        <SourceCard key={result.id} image={result} confidence={result.confidence} />
      ))}
    </div>
  );
};

/**
 * SearchPage component - Main page for semantic search of NASA images.
 * 
 * Features:
 * - Natural language search using semantic embeddings
 * - Real-time search with React Query caching
 * - Results displayed with confidence scores
 * - Color-coded confidence badges (green/orange/red)
 * 
 * State management:
 * - `query`: Current input value (can be edited)
 * - `submittedQuery`: The actual query used for search (set on submit)
 * 
 * The component restores the previous search query when navigating back to the page.
 * Uses React Query for data fetching with 30 second stale time for caching.
 */
const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');

  // Restore query input when returning to page with previous search
  useEffect(() => {
    if (submittedQuery && !query) {
      setQuery(submittedQuery);
    }
  }, [submittedQuery]);

  const {
    data: results,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<SearchResult[], Error>({
    queryKey: ['search', submittedQuery],
    queryFn: () => searchImages(submittedQuery),
    enabled: submittedQuery.trim().length > 0,
    staleTime: 30_000,
    retry: 2,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      return;
    }
    setSubmittedQuery(trimmed);
    refetch();
  };

  return (
    <div className="py-8">
      <SearchBar
        query={query}
        onQueryChange={setQuery}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />

      {isLoading && <LoadingSpinner />}

      {isError && submittedQuery && <ErrorMessage error={error} />}

      {submittedQuery && !isLoading && results && results.length === 0 && (
        <EmptyState query={submittedQuery} />
      )}

      {results && results.length > 0 && <SearchResults results={results} />}
    </div>
  );
};

export default SearchPage;
