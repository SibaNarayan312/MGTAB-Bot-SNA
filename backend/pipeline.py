import argparse
import logging
from backend.scripts.export_features import export_sna_artifacts
from backend.config import DATASET_PATH, RESULTS_PATH

logger = logging.getLogger("backend.pipeline")

def run_pipeline(data_dir: str = DATASET_PATH, results_dir: str = RESULTS_PATH):
    """Executes full backend SNA data processing pipeline."""
    logger.info("=== Running MGTAB SNA Backend Pipeline ===")
    export_sna_artifacts(data_dir=data_dir, results_dir=results_dir)
    logger.info("=== Pipeline Execution Finished Successfully ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SNA Backend Precomputation Pipeline")
    parser.add_argument("--data_dir", type=str, default=DATASET_PATH, help="Path to input data directory")
    parser.add_argument("--results_dir", type=str, default=RESULTS_PATH, help="Path to results directory")
    args = parser.parse_args()

    run_pipeline(data_dir=args.data_dir, results_dir=args.results_dir)
