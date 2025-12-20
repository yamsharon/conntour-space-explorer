// Shared types used across API clients

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

// History API - Backend models
export interface SearchResultHistoryResponse {
  id: string;
  query: string;
  time_searched: string;
  top_three_images: SearchResult[];
}

export interface HistoryResponse {
  items: SearchResultHistoryResponse[];
  total: number;
}

