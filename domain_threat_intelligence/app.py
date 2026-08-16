from threat_intelligence.normalize import normalize_url
from threat_intelligence.reputation import check_threat_intelligence
from fusion.risk_engine import calculate_final_risk


def analyze_url(
    url,
    ml_probability
):

    # -----------------------------------------------
    # 1. NORMALIZE
    # -----------------------------------------------

    normalized_url = normalize_url(url)

    if not normalized_url:

        return {
            "url": url,
            "decision": "WARN",
            "risk_score": 0.5,
            "reason": "Invalid URL"
        }

    # -----------------------------------------------
    # 2. THREAT INTELLIGENCE
    # -----------------------------------------------

    threat_result = check_threat_intelligence(
        normalized_url
    )

    # -----------------------------------------------
    # 3. RISK FUSION
    # -----------------------------------------------

    final_result = calculate_final_risk(

        ml_probability=ml_probability,

        threat_score=threat_result[
            "threat_score"
        ],

        threat_status=threat_result[
            "status"
        ]
    )

    # -----------------------------------------------
    # 4. FINAL RESULT
    # -----------------------------------------------

    return {

        "url": normalized_url,

        "ml_probability":
            round(float(ml_probability), 4),

        "threat_intelligence":
            threat_result,

        "risk_score":
            final_result["risk_score"],

        "decision":
            final_result["decision"],

        "reason":
            final_result["reason"]
    }


if __name__ == "__main__":

    url = input(
        "Enter URL: "
    ).strip()

    # TEMPORARY:
    # Replace this with your existing URL Shield
    # prediction later.

    ml_probability = 0.20

    result = analyze_url(
        url,
        ml_probability
    )

    print("\n" + "=" * 60)
    print("URL THREAT ANALYSIS")
    print("=" * 60)

    print(
        "URL:",
        result["url"]
    )

    print(
        "ML probability:",
        result["ml_probability"]
    )

    print(
        "Threat status:",
        result[
            "threat_intelligence"
        ]["status"]
    )

    print(
        "Threat score:",
        result[
            "threat_intelligence"
        ]["threat_score"]
    )

    print(
        "FINAL RISK:",
        result["risk_score"]
    )

    print(
        "DECISION:",
        result["decision"]
    )

    print(
        "REASON:",
        result["reason"]
    )