def is_model_acceptable(metrics):
    return metrics["mAP50"] > 0.6
