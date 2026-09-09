import { apiClient, FORCE_MOCK, FORCE_MOCK_PREDICTION } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import {
  UserProfile,
  PredictRequest,
  PredictResponse,
} from '../types/user';
import { NetworkGraphData } from '../types/network';

export const userService = {
  async getUser(userId: string): Promise<UserProfile> {
    if (FORCE_MOCK) {
      return mockAdapter.getUser(userId);
    }

    try {
      const response = await apiClient.get<UserProfile>(`/user/${userId}`);
      return response.data;
    } catch (error) {
      console.warn(
        `[userService] FastAPI /user/${userId} unavailable.`
      );

      return mockAdapter.getUser(userId);
    }
  },

  async getUserNetwork(userId: string): Promise<NetworkGraphData> {
    if (FORCE_MOCK) {
      return mockAdapter.getUserNetwork(userId);
    }

    try {
      const response = await apiClient.get<NetworkGraphData>(
        `/user/${userId}/network`
      );

      return response.data;
    } catch (error) {
      console.warn(
        `[userService] FastAPI /user/${userId}/network unavailable.`
      );

      return mockAdapter.getUserNetwork(userId);
    }
  },

  async predictUser(req: PredictRequest): Promise<PredictResponse> {

    const response = await apiClient.post<PredictResponse>(
      '/predict',
      req
    );

    const data = response.data;


    let normalizedPrediction: 'BOT' | 'HUMAN' | 'UNKNOWN';

    if (data.prediction_label) {
      const label = data.prediction_label.toUpperCase();

      if (label === 'BOT') {
        normalizedPrediction = 'BOT';
      } else if (label === 'HUMAN') {
        normalizedPrediction = 'HUMAN';
      } else {
        normalizedPrediction = 'UNKNOWN';
      }
    } else if (data.prediction === 1) {
      normalizedPrediction = 'BOT';
    } else if (data.prediction === 0) {
      normalizedPrediction = 'HUMAN';
    } else {
      normalizedPrediction = 'UNKNOWN';
    }

    return {
      ...data,
      prediction: data.prediction,
      prediction_label: normalizedPrediction,
      probability: data.probability,
    };
  },
};