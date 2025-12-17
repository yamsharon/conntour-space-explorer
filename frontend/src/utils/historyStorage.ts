/**
 * History storage utility - Re-exports from API client.
 * 
 * This module provides a convenient interface for history operations.
 * Currently uses mocked API functions that simulate backend calls.
 * When the backend is ready, these will be replaced with real API calls.
 */

export {
  getHistory,
  saveToHistory,
  deleteHistoryItem,
  clearHistory,
  type HistoryItem,
  type HistoryResponse,
} from '../api/client';

