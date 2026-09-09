/// <reference types="vite/client" />
import axios, { AxiosInstance, AxiosError } from 'axios';
import { BackendStatus } from '../types/api';

const DEFAULT_API_URL = 'http://localhost:8000';

export const API_BASE_URL: string = 
  import.meta.env.VITE_API_BASE_URL || DEFAULT_API_URL;

export const FORCE_MOCK: boolean = 
  import.meta.env.VITE_USE_MOCK === 'true' || import.meta.env.VITE_USE_MOCK === '1';

export const FORCE_MOCK_PREDICTION: boolean =
  import.meta.env.VITE_USE_MOCK_PREDICTION === 'true' ||
  import.meta.env.VITE_USE_MOCK_PREDICTION === '1';

// Create Axios Instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Helper to check backend connectivity
export async function checkBackendHealth(): Promise<BackendStatus> {
  if (FORCE_MOCK) {
    return {
      connected: true,
      isMock: true,
      baseUrl: API_BASE_URL,
      version: 'Mock Adapter (MGTAB Offline Mode)',
    };
  }

  const startTime = Date.now();
  try {
    const res = await apiClient.get('/health', { timeout: 3000 });
    const latency = Date.now() - startTime;
    return {
      connected: true,
      isMock: false,
      latencyMs: latency,
      baseUrl: API_BASE_URL,
      version: res.data?.version || 'FastAPI v0.1.0',
    };
  } catch {
    // If backend is not running, fallback to Mock gracefully
    return {
      connected: false,
      isMock: true,
      baseUrl: API_BASE_URL,
      version: 'FastAPI Offline — Fallback to MGTAB Mock',
    };
  }
}

export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<{ message?: string; detail?: string }>;
    if (axiosErr.response?.data?.detail) {
      return String(axiosErr.response.data.detail);
    }
    if (axiosErr.response?.data?.message) {
      return String(axiosErr.response.data.message);
    }
    if (axiosErr.message) {
      return axiosErr.message;
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected network or API error occurred.';
}
