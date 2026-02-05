def compute_hydration_score(health_metrics):
    """
    0 = extremely dry
    5 = optimal
    10 = oversaturated
    """
    grass = health_metrics.get("grass", 0)
    dead = health_metrics.get("dead_grass", 0)
    water = health_metrics.get("water", 0)
    mud = health_metrics.get("mud", 0)

    score = 5
    score -= dead * 2
    score -= grass * 0.5
    score += water * 2
    score += mud * 3

    return max(0, min(10, round(score)))
