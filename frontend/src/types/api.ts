export type PredictionLabel = 'BOT' | 'HUMAN' | 'UNKNOWN';

export type RelationshipType = 
  | 'FOLLOW' 
  | 'FRIEND' 
  | 'MENTION' 
  | 'RETWEET' 
  | 'REPLY' 
  | 'CO_ENGAGEMENT' 
  | string;

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp?: string;
}

export interface BackendStatus {
  connected: boolean;
  isMock: boolean;
  latencyMs?: number;
  baseUrl: string;
  version?: string;
}
