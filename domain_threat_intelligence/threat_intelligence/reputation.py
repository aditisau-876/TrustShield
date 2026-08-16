from threat_intelligence.normalize import (
    normalize_url,
    extract_domain,
    extract_registered_domain
)

from threat_intelligence.local_db import (
    lookup_url,
    lookup_domain
)

from threat_intelligence.phishtank import (
    check_phishtank
)


def check_threat_intelligence(url):

    normalized = normalize_url(url)

    domain = extract_domain(normalized)

    registered_domain = extract_registered_domain(
        normalized
    )

    result = {
        "url": normalized,
        "domain": domain,
        "registered_domain": registered_domain,

        "local_url_match": False,
        "local_domain_match": False,

        "phishtank_match": False,

        "sources": [],
        "threat_score": 0.0,
        "status": "UNKNOWN"
    }

    # --------------------------------------------------
    # LOCAL URL DATABASE
    # --------------------------------------------------

    local_url = lookup_url(normalized)

    if local_url:

        result["local_url_match"] = True

        result["sources"].append({
            "source": "local_database",
            "type": "url",
            "confidence": local_url["confidence"],
            "threat_type": local_url["threat_type"]
        })

    # --------------------------------------------------
    # LOCAL DOMAIN DATABASE
    # --------------------------------------------------

    local_domains = lookup_domain(
        registered_domain
    )

    if local_domains:

        result["local_domain_match"] = True

        result["sources"].append({
            "source": "local_database",
            "type": "domain",
            "matches": len(local_domains)
        })

    # --------------------------------------------------
    # PHISHTANK
    # --------------------------------------------------

    phishtank = check_phishtank(
        normalized
    )

    if phishtank.get("listed"):

        result["phishtank_match"] = True

        result["sources"].append(
            phishtank
        )

    # --------------------------------------------------
    # THREAT SCORE
    # --------------------------------------------------

    score = 0.0

    if result["local_url_match"]:
        score = max(score, 1.0)

    elif result["local_domain_match"]:
        score = max(score, 0.90)

    if result["phishtank_match"]:
        score = max(score, 1.0)

    result["threat_score"] = score

    if score >= 0.90:

        result["status"] = "KNOWN_MALICIOUS"

    elif score >= 0.50:

        result["status"] = "SUSPICIOUS"

    else:

        result["status"] = "UNKNOWN"

    return result