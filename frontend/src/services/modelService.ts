
import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { ModelPerformanceResponse } from '../types/model';

export const modelService = {
  async getModelPerformance(): Promise<ModelPerformanceResponse> {
    if (FORCE_MOCK) {
      return mockAdapter.getModelPerformance();
    }

    try {
      const response = await apiClient.get('/model-performance');
      const raw = response.data as any;

      const split = raw.metadata?.split ?? {};
      const architecture = raw.metadata?.architecture ?? {};
      const training = raw.metadata?.training ?? {};
      const dataset = raw.metadata?.dataset ?? {};

      return {
        ...raw,
        metadata: {
          model_name: raw.metadata?.model_name ?? raw.all_models?.[0]?.model_name ?? 'RGCN',
          model_version: raw.metadata?.model_version ?? 'v1.0.0',
          architecture_type:
            raw.metadata?.architecture_type ??
            architecture.type ??
            'Relational Graph Convolutional Network',
          dataset_name: raw.metadata?.dataset_name ?? dataset.name ?? 'MGTAB',
          training_samples: split.train_count ?? training.train_count,
          test_samples: split.test_count ?? training.test_count,
          validation_split: split.method
            ? `${Math.round((split.train_ratio ?? 0) * 100)}/${Math.round((split.val_ratio ?? 0) * 100)}/${Math.round((split.test_ratio ?? 0) * 100)}`
            : undefined,
          evaluation_date: raw.metadata?.evaluation_date,
          feature_count: architecture.input_dim,
          graph_layers: architecture.layers
            ? `${architecture.layers} Layers (${architecture.hidden_dim}-dim)`
            : undefined,
          embedding_dimension: architecture.hidden_dim,
          epochs_trained: training.best_epoch,
        },
      } as ModelPerformanceResponse;
    } catch {
      console.warn(
        '[modelService] FastAPI /model-performance unavailable, falling back to mock adapter.'
      );
      return mockAdapter.getModelPerformance();
    }
  },
};
