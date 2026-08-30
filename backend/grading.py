from models import GradeMetrics, GradeResult

DISCLAIMER = (
    "Provisional computer-assisted condition estimate only. "
    "It is not a PSA, CGC, BGS or other professional grading-company grade."
)


def _centering_penalty(value: float | None) -> float:
    if value is None:
        return 0.15
    delta = abs(50.0 - value)
    if delta <= 2:
        return 0
    if delta <= 5:
        return 0.15
    if delta <= 10:
        return 0.45
    if delta <= 15:
        return 0.9
    return 1.5


def provisional_grade(metrics: GradeMetrics) -> GradeResult:
    score = 10.0
    reasons: list[str] = []

    centering_penalty = sum(
        _centering_penalty(value)
        for value in [
            metrics.front_centering_lr,
            metrics.front_centering_tb,
            metrics.back_centering_lr,
            metrics.back_centering_tb,
        ]
    )
    score -= centering_penalty
    if centering_penalty:
        reasons.append(f"Centering penalty: -{centering_penalty:.2f}")

    corner_penalty = min(3.2, metrics.corner_defects * 0.45)
    edge_penalty = min(2.5, metrics.edge_defects * 0.16)
    surface_penalty = min(3.5, metrics.surface_defects * 0.22)
    score -= corner_penalty + edge_penalty + surface_penalty

    if corner_penalty:
        reasons.append(f"Corner defects: -{corner_penalty:.2f}")
    if edge_penalty:
        reasons.append(f"Edge defects: -{edge_penalty:.2f}")
    if surface_penalty:
        reasons.append(f"Surface defects: -{surface_penalty:.2f}")

    score = max(1.0, min(10.0, round(score * 2) / 2))
    if score >= 9.5:
        label = "Gem Mint estimate"
    elif score >= 9:
        label = "Mint estimate"
    elif score >= 8:
        label = "Near Mint–Mint estimate"
    elif score >= 7:
        label = "Near Mint estimate"
    elif score >= 5:
        label = "Excellent estimate"
    else:
        label = "Played / lower-condition estimate"

    completeness = 1.0 if metrics.back_centering_lr is not None and metrics.back_centering_tb is not None else 0.85
    confidence = round(max(0.1, min(0.98, metrics.image_quality * completeness)), 2)
    if not reasons:
        reasons.append("No scored defects supplied to the provisional model.")

    return GradeResult(
        provisional_grade=score,
        label=label,
        confidence=confidence,
        reasons=reasons,
        disclaimer=DISCLAIMER,
    )
