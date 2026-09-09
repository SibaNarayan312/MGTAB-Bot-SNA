import { PredictionLabel } from './api';

export interface UserNetworkMetrics {
  degree?: number;
  in_degree?: number;
  out_degree?: number;
  pagerank?: number;
  betweenness?: number;
  clustering?: number;
  eigenvector?: number;
  coreness?: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  description?: string;
  direction?: 'positive' | 'negative' | 'neutral';
}

export interface UserAccountFeatures {
  followers_count?: number;
  following_count?: number;
  statuses_count?: number;
  favourites_count?: number;
  listed_count?: number;
  created_at?: string;
  verified?: boolean;
  default_profile?: boolean;
  default_profile_image?: boolean;
  geo_enabled?: boolean;
  description_length?: number;
  account_age_days?: number;
  tweet_frequency_per_day?: number;

  [key: string]: unknown;
}

export interface UserProfile {
  user_id: string;
  screen_name?: string;
  name?: string;

  /*
   * Prediction displayed by the frontend.
   * This is normalized from the backend's prediction_label.
   */
  prediction?: PredictionLabel;

  /*
   * Probability returned by the real ML model.
   * Example: 0.99986 = 99.986%
   */
  probability?: number;

  confidence_score?: number;

  community_id?: string | number;

  features?: UserAccountFeatures;

  network?: UserNetworkMetrics;

  explanation?: FeatureImportance[];

  recent_activity?: {
    total_tweets_sampled?: number;
    hashtags?: string[];
    mentioned_users?: string[];
    urls_shared?: string[];
  };
}

/*
 * Request sent to FastAPI /predict
 */
export interface PredictRequest {
  user_id: string;
  features?: Record<string, unknown>;
}

/*
 * Response returned by FastAPI /predict
 *
 * Backend currently returns:
 *
 * {
 *   status: "success",
 *   message: "...",
 *   user_id: 100,
 *   prediction: 0,
 *   prediction_label: "Human",
 *   probability: 0.99986
 * }
 */
export interface PredictResponse {
  status: string;
  message: string;
  user_id: number;
  prediction: number;
  prediction_label: 'BOT' | 'HUMAN' | 'UNKNOWN' | string;
  probability: number;
  confidence?: number;
  explanation?: FeatureImportance[];
}