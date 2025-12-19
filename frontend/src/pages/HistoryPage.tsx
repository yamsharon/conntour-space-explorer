import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getHistory, deleteHistoryItem, SearchResultHistory } from '../api/client';

const ITEMS_PER_PAGE = 10;

/**
 * Props for HistoryRow component.
 */
type HistoryRowProps = {
  item: SearchResultHistory;
  onDelete: (id: string) => void;
  onClick: (query: string) => void;
};

/**
 * HistoryRow component - Displays a single search history item.
 * 
 * Shows the query text and top 3 result thumbnails.
 * Clicking the row navigates to the search page with that query.
 * 
 * @param item - The history item containing query and results
 * @param onDelete - Callback when delete button is clicked
 * @param onClick - Callback when row is clicked
 */
const HistoryRow: React.FC<HistoryRowProps> = ({ item, onDelete, onClick }) => {
  const topThree = item.top_three_images.slice(0, 3);
  const formattedDate = new Date(item.time_searched).toLocaleString();

  const handleClick = (e: React.MouseEvent) => {
    // Don't navigate if clicking the delete button
    if ((e.target as HTMLElement).closest('button')) {
      return;
    }
    onClick(item.query);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(item.id);
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-lg shadow-md p-4 mb-4 cursor-pointer hover:shadow-lg transition-shadow border border-gray-200 hover:border-blue-300"
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-800 mb-1">{item.query}</h3>
          <p className="text-sm text-gray-500">{formattedDate}</p>
        </div>
        
        {topThree.length > 0 && (
          <div className="flex gap-2 items-center">
            {topThree.map((result) => (
              <div key={result.id} className="flex-shrink-0">
                {result.image_url ? (
                  <img
                    src={result.image_url}
                    alt={result.name}
                    className="w-14 h-14 object-cover rounded-lg border border-gray-200"
                  />
                ) : (
                  <div className="w-14 h-14 bg-gray-200 rounded-lg border border-gray-200 flex items-center justify-center">
                    <span className="text-xs text-gray-500">No image</span>
                  </div>
                )}
              </div>
            ))}
            {item.top_three_images.length > 3 && (
              <div className="flex-shrink-0 w-14 h-14 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
                <span className="text-xs text-gray-600 font-medium">
                  +{item.top_three_images.length - 3}
                </span>
              </div>
            )}
          </div>
        )}
        
        <button
          onClick={handleDelete}
          className="flex-shrink-0 text-red-500 hover:text-red-700 transition-colors p-2"
          aria-label="Delete search history"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};

/**
 * Props for PaginationControls component.
 */
type PaginationControlsProps = {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
};

/**
 * PaginationControls component - Displays pagination buttons.
 * 
 * @param currentPage - The current page number (1-indexed)
 * @param totalPages - Total number of pages
 * @param onPageChange - Callback when page changes
 */
const PaginationControls: React.FC<PaginationControlsProps> = ({
  currentPage,
  totalPages,
  onPageChange,
}) => {
  if (totalPages <= 1) return null;

  return (
    <div className="flex justify-center items-center gap-2 mt-6">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-4 py-2 rounded bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Previous
      </button>
      <span className="px-4 py-2 text-gray-700">
        Page {currentPage} of {totalPages}
      </span>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-4 py-2 rounded bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Next
      </button>
    </div>
  );
};

/**
 * HistoryPage component - Displays search history with pagination.
 * 
 * Features:
 * - Shows last 10 searches per page
 * - Each history item shows query, timestamp, and top 3 images
 * - Clicking an item navigates to search page with that query
 * - Delete button for each history item
 * - Pagination controls for navigating through history
 */
const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentPage, setCurrentPage] = useState(1);

  // Fetch history using React Query with pagination
  const {
    data: historyResponse,
    isLoading,
    isError,
  } = useQuery<{ items: SearchResultHistory[], total: number }>({
    queryKey: ['history', currentPage],
    queryFn: () => {
      const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
      return getHistory(startIndex, ITEMS_PER_PAGE);
    },
  });

  const history = historyResponse?.items || [];
  const totalItems = historyResponse?.total || 0;

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteHistoryItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });

  // Calculate pagination
  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  // Reset to page 1 if current page is out of bounds
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [currentPage, totalPages]);

  const handleItemClick = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}&skipHistory=true`);
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  if (isLoading) {
    return (
      <div className="py-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-gray-600 mt-4">Loading history...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="py-8 text-center">
        <p className="text-red-500 text-lg">Failed to load search history.</p>
      </div>
    );
  }

  if (totalItems === 0 && !isLoading) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-600 text-lg">No search history yet.</p>
        <p className="text-gray-500 mt-2">
          Start searching to see your history here.
        </p>
      </div>
    );
  }

  return (
    <div className="py-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Search History</h2>
        <p className="text-gray-600">
          {totalItems} {totalItems === 1 ? 'search' : 'searches'} total
        </p>
      </div>

      <div>
        {history.map((item) => (
          <HistoryRow
            key={item.id}
            item={item}
            onDelete={handleDelete}
            onClick={handleItemClick}
          />
        ))}
      </div>

      <PaginationControls
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
};

export default HistoryPage;
