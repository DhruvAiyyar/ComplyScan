from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Scan, RuleResult


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def get_dashboard(db: Session = Depends(get_db)):

    total_scans = db.query(Scan).count()

    compliant = (
        db.query(Scan)
        .filter(Scan.overall_status == "pass")
        .count()
    )

    non_compliant = (
        db.query(Scan)
        .filter(Scan.overall_status == "fail")
        .count()
    )

    failed_rules = (
        db.query(RuleResult)
        .filter(RuleResult.status == "fail")
        .all()
    )

    violation_breakdown = {}

    for result in failed_rules:
        rule_name = result.rule_name

        if rule_name not in violation_breakdown:
            violation_breakdown[rule_name] = 0

        violation_breakdown[rule_name] += 1

    return {
        "total_scans": total_scans,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "violation_breakdown": violation_breakdown
    }