# ============================================================
# DEVTRUST — STAGE 8 HIERARCHY
# ============================================================

# Stage 2 family names
FAMILY_DDOS = "DDOS"
FAMILY_DOS = "DOS"
FAMILY_RECON = "RECON"
FAMILY_MIRAI = "MIRAI"
FAMILY_VULNERABILITY = "VULNERABILITY_SCAN"


# Families without a dedicated specialist
GENERAL_ATTACK_FAMILIES = {
    "BROWSER_HIJACKING",
    "BRUTE_FORCE",
    "INJECTION",
    "MALWARE",
    "MITM",
    "SPOOFING",
    "UPLOADING_ATTACK",
}


def route_family(family):
    """
    Decide which specialist should process a Stage-2 family.
    """

    family = str(family).upper().strip()

    if family == FAMILY_DDOS:
        return "STAGE3_DDOS"

    if family == FAMILY_DOS:
        return "STAGE4_DOS"

    if family == FAMILY_VULNERABILITY:
        return "STAGE5_VULNERABILITY"

    if family == FAMILY_RECON:
        return "STAGE6_RECON"

    if family == FAMILY_MIRAI:
        return "STAGE7_MIRAI"

    if family in GENERAL_ATTACK_FAMILIES:
        return "GENERAL_ATTACK"

    return "UNKNOWN"


def hierarchy_description():
    return {
        "BENIGN": "Final benign classification",

        "DDOS": "Stage 3 DDoS specialist",

        "DOS": "Stage 4 DoS specialist",

        "VULNERABILITY_SCAN":
            "Stage 5 vulnerability/web specialist",

        "RECON":
            "Stage 6 reconnaissance specialist",

        "MIRAI":
            "Stage 7 Mirai specialist",

        "GENERAL_ATTACK":
            "Attack family returned by Stage 2",

        "UNKNOWN":
            "Unable to determine route",
    }