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

const api: AxiosInstance = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
});

// Typed API functions
export async function getImages(): Promise<ImageSource[]> {
    const response = await api.get<ImageSource[]>("/api/sources");
    return response.data;
}

export { api as apiClient };


