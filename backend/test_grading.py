from grading import provisional_grade
from models import GradeMetrics


def test_gem_candidate():
    result = provisional_grade(
        GradeMetrics(
            front_centering_lr=49,
            front_centering_tb=50,
            back_centering_lr=48,
            back_centering_tb=49,
            image_quality=0.95,
        )
    )
    assert result.provisional_grade >= 9.5


def test_damage_reduces_grade():
    clean = provisional_grade(GradeMetrics(front_centering_lr=50, front_centering_tb=50))
    worn = provisional_grade(
        GradeMetrics(
            front_centering_lr=50,
            front_centering_tb=50,
            corner_defects=4,
            edge_defects=8,
            surface_defects=4,
        )
    )
    assert worn.provisional_grade < clean.provisional_grade
