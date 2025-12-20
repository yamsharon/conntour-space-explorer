import { api, normalizeError } from "./apiClient";
import { ImageSource } from "./types";

export async function getImages(): Promise<ImageSource[]> {
  try {
    const response = await api.get<ImageSource[]>("/api/sources");
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
}

