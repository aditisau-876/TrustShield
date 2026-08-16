def calculate_final_risk(
    ml_probability,
    threat_score,
    threat_status
):

    # --------------------------------------------------
    # KNOWN MALICIOUS OVERRIDE
    # --------------------------------------------------

    if threat_status == "KNOWN_MALICIOUS":

        return {
            "risk_score": 1.0,
            "decision": "BLOCK",
            "reason": "Known malicious threat intelligence match"
        }

    # --------------------------------------------------
    # UNKNOWN / NO INTELLIGENCE MATCH
    # --------------------------------------------------

    if threat_status == "UNKNOWN":

        final_score = (
            0.75 * ml_probability
            + 0.25 * threat_score
        )

    else:

        final_score = (
            0.60 * ml_probability
            + 0.40 * threat_score
        )

    # --------------------------------------------------
    # DECISION
    # --------------------------------------------------

    if final_score >= 0.80:

        decision = "BLOCK"

    elif final_score >= 0.45:

        decision = "WARN"

    else:

        decision = "SAFE"

    return {
        "risk_score": round(
            float(final_score),
            4
        ),
        "decision": decision,
        "reason": "Combined ML + threat intelligence"
    }