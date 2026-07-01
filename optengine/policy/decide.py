from optengine.context import Context


def decide(context: Context) -> None:
    context.log("Policy decision started.")

    confidence = context.metrics.get("confidence", 0.0)
    improvement = context.metrics.get("expected_improvement", 0.0)

    if confidence >= 0.70 and improvement >= 0.05:
        action = "scale"
        reason = "Additional low-cost search is justified."
    elif confidence < 0.70:
        action = "switch"
        reason = "Escalate to a stronger solver or verifier."
    else:
        action = "stop"
        reason = "Marginal utility is too low."

    context.decision = {
        "action": action,
        "reason": reason,
    }

    context.log(f"Policy decision completed: {action}.")
