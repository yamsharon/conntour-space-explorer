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

export async function searchImages(query: string, skipHistory: boolean = false): Promise<SearchResult[]> {
  try {
    const response = await api.get<SearchResult[]>("/api/search", {
      params: { q: query, skipHistory },
    });
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
}

// History API - Backend models
export interface SearchResultHistory {
  id: string;
  query: string;
  time_searched: string;
  top_three_images: SearchResult[];
}

export interface HistoryResponse {
  items: SearchResultHistory[];
  total: number;
}

export async function getHistory(
  startIndex: number = 0,
  limit: number = 10
): Promise<{ items: SearchResultHistory[]; total: number }> {
  try {
    const response = await api.get<HistoryResponse>("/api/history", {
      params: { startIndex, limit },
    });
    
    return {
      items: response.data.items,
      total: response.data.total,
    };
  } catch (error) {
    throw normalizeError(error);
  }
}

export async function deleteHistoryItem(id: string): Promise<void> {
  try {
    await api.delete(`/api/history/${id}`);
  } catch (error) {
    throw normalizeError(error);
  }
}

export { normalizeError, api as apiClient };


