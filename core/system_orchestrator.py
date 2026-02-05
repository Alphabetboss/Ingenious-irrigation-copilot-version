from ai.hydration_scorer import compute_hydration_score
from ai.decision_engine import decide
from core.logger import setup_logger

logger = setup_logger()

def run_cycle(detections, health_metrics):
    hydration_score = compute_hydration_score(health_metrics)
    decision = decide(detections, hydration_score)

    logger.info(f"Hydration score: {hydration_score}")
    logger.info(f"Decision: {decision}")

    return decision
