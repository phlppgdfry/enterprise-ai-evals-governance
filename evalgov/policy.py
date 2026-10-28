from .models import PolicyRequest


def decide(request: PolicyRequest) -> dict:
    blockers, controls = [], ["named_owner", "evaluation_gate", "incident_runbook"]
    if not request.approved_data_source:
        blockers.append("data_source_not_approved")
    if request.special_category_data:
        blockers.append("special_category_requires_privacy_review")
    if request.retention_days > 90:
        blockers.append("retention_exceeds_demo_policy")
    if request.personal_data:
        controls += ["privacy_review", "data_minimisation", "retention_schedule"]
    needs_approval = request.externally_visible_action or request.financial_posting or request.personal_data
    if needs_approval:
        controls += ["human_approval_before_action", "separation_of_duties"]
    return {"policy_version": "demo-1", "decision": "blocked" if blockers else "conditional",
            "blockers": blockers, "required_controls": controls,
            "human_approval_required": needs_approval,
            "authorization_to_execute": False,
            "note": "Advisory policy only. This response never grants execution or establishes legal compliance."}
