import { api, normalizeError } from "./apiClient";
import { SearchResult } from "./types";

export async function searchImages(
  query: string,
  skipHistory: boolean = false
): Promise<SearchResult[]> {
  try {
    const response = await api.get<SearchResult[]>("/api/search", {
      params: { q: query, skipHistory },
    });
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
}

