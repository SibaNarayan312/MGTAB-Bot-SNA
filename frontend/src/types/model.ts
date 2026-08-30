export interface ConfusionMatrixData {
  true_negative: number;  // Actual Human, Predicted Human (TN)
  false_positive: number; // Actual Human, Predicted Bot (FP)
  false_negative: number; // Actual Bot, Predicted Human (FN)
  true_positive: number;  // Actual Bot, Predicted Bot (TP)
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  pr_auc?: number;
  log_loss?: number;
}

export interface ModelMetadata {
  model_name: string;
  model_version?: string;
  architecture_type?: string;
  dataset_name: string;
  dataset_version?: string;
  training_samples?: number;
  test_samples?: number;
  validation_split?: string;
  evaluation_date?: string;
  feature_count?: number;
  graph_layers?: number;
  embedding_dimension?: number;
  epochs_trained?: number;
}

export interface ROCPoint {
  fpr: number;
  tpr: number;
  threshold?: number;
}

export interface ModelPerformanceResponse {
  metrics: ModelMetrics;
  confusion_matrix: ConfusionMatrixData;
  metadata: ModelMetadata;
  roc_curve?: ROCPoint[];
  feature_importances?: {
    feature: string;
    importance: number;
    category?: 'graph' | 'user' | 'text' | 'temporal';
  }[];
  baseline_comparisons?: {
    model_name: string;
    accuracy: number;
    f1_score: number;
    roc_auc: number;
  }[];
}
