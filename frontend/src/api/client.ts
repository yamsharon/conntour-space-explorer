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

export { normalizeError, api as apiClient };


