import { api, normalizeError } from "./apiClient";
import {
  SearchResult,
  SearchResultHistoryResponse,
  HistoryResponse,
} from "./types";

export async function getHistory(
  startIndex: number = 0,
  limit: number = 10
): Promise<{ items: SearchResultHistoryResponse[]; total: number }> {
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

export async function getHistoryResults(
  historyId: string
): Promise<SearchResult[]> {
  try {
    const response = await api.get<SearchResult[]>(
      `/api/history/${historyId}/results`
    );
    return response.data;
  } catch (error) {
    throw normalizeError(error);
  }
}

