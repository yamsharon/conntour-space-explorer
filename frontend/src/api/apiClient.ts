import axios, { AxiosError, AxiosInstance } from "axios";
import { ApiError } from "./types";

export const api: AxiosInstance = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
});

export function normalizeError(error: unknown): ApiError {
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

