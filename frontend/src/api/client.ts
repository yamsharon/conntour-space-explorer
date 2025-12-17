import axios, { AxiosError, AxiosInstance } from "axios";

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

// Domain models used by the frontend
export interface ImageSource {
  id: number;
  name: string;
  description: string;
  launch_date: string;
  image_url: string;
  type: string;
  status: string;
}

export interface SearchResult extends ImageSource {
  confidence: number;
}

const api: AxiosInstance = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
});

function normalizeError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    return {
      message:
        axiosError.response?.data?.message ??
        axiosError.message ??
        "Unexpected API error",
      status: axiosError.response?.status,
      details: axiosError.response?.data,
    };
  }

  if (error instanceof Error) {
    return { message: error.message };
  }

  return { message: "Unexpected error" };
}

// Typed API functions
export async function getImages(): Promise<ImageSource[]> {
  try {
    const response = await api.get<ImageSource[]>("/api/sources");
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
}

export async function searchImages(query: string): Promise<SearchResult[]> {
  try {
    const response = await api.get<SearchResult[]>("/api/search", {
      params: { q: query },
    });
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
}

// History API (mocked for now - will be replaced with real backend calls)
export interface HistoryItem {
  id: string;
  query: string;
  results: SearchResult[];
  timestamp: number;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
}

// Mock implementation using localStorage - simulates async backend calls
const HISTORY_KEY = 'nasa_search_history';
const MAX_HISTORY_ITEMS = 100;

async function delay(ms: number = 100): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function getHistory(
  startIndex: number = 0,
  limit: number = 10
): Promise<HistoryResponse> {
  // Simulate network delay
  await delay(50);
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    if (!stored) {
      return { items: [], total: 0 };
    }
    const allHistory: HistoryItem[] = JSON.parse(stored);
    const total = allHistory.length;
    
    // Apply pagination
    const paginatedItems = allHistory.slice(startIndex, startIndex + limit);
    
    return {
      items: paginatedItems,
      total,
    };
  } catch (error) {
    throw normalizeError(error);
  }
}

export async function saveToHistory(query: string, results: SearchResult[]): Promise<void> {
  // Simulate network delay
  await delay(100);
  try {
    const historyResponse = await getHistory(0, MAX_HISTORY_ITEMS);
    const history = historyResponse.items;
    
    const newItem: HistoryItem = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      query: query.trim(),
      results: results.slice(0, 10),
      timestamp: Date.now(),
    };
    
    history.unshift(newItem);
    const trimmedHistory = history.slice(0, MAX_HISTORY_ITEMS);
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmedHistory));
  } catch (error) {
    throw normalizeError(error);
  }
}

export async function deleteHistoryItem(id: string): Promise<void> {
  // Simulate network delay
  await delay(100);
  try {
    const historyResponse = await getHistory(0, MAX_HISTORY_ITEMS);
    const history = historyResponse.items;
    const filtered = history.filter(item => item.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
  } catch (error) {
    throw normalizeError(error);
  }
}

export async function clearHistory(): Promise<void> {
  // Simulate network delay
  await delay(100);
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch (error) {
    throw normalizeError(error);
  }
}

export { normalizeError, api as apiClient };


