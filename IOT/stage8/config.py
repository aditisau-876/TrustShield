from pathlib import Path

# ============================================================
# DEVTRUST — STAGE 8 CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"


# ------------------------------------------------------------
# STAGE 1
# ------------------------------------------------------------

STAGE1_DIR = MODELS_DIR / "stage1"

STAGE1_MODEL = STAGE1_DIR / "binary_threat_detector.pkl"
STAGE1_FEATURES = STAGE1_DIR / "feature_columns.json"


# ------------------------------------------------------------
# STAGE 2
# ------------------------------------------------------------

STAGE2_DIR = MODELS_DIR / "stage2"

STAGE2_MODEL = STAGE2_DIR / "stage2_attack_family_model.pkl"
STAGE2_ENCODER = STAGE2_DIR / "stage2_label_encoder.pkl"


# ------------------------------------------------------------
# STAGE 3 — DDOS
# ------------------------------------------------------------

STAGE3_DIR = MODELS_DIR / "stage3_ddos"

STAGE3_MODEL = STAGE3_DIR / "ddos_specialist.pkl"
STAGE3_ENCODER = STAGE3_DIR / "ddos_label_encoder.pkl"


# ------------------------------------------------------------
# STAGE 4 — DOS
# ------------------------------------------------------------

STAGE4_DIR = MODELS_DIR / "stage4_dos"

STAGE4_MODEL = STAGE4_DIR / "stage4_dos_specialist.pkl"
STAGE4_FEATURES = STAGE4_DIR / "stage4_dos_features.pkl"
STAGE4_ENCODER = STAGE4_DIR / "stage4_dos_label_encoder.pkl"


# ------------------------------------------------------------
# STAGE 5 — VULNERABILITY / WEB
# ------------------------------------------------------------

STAGE5_DIR = MODELS_DIR / "stage5"

STAGE5_MODEL = STAGE5_DIR / "stage5_vulnerability_specialist.txt"
STAGE5_FEATURES = STAGE5_DIR / "stage5_features.pkl"
STAGE5_ENCODER = STAGE5_DIR / "stage5_label_encoder.pkl"


# ------------------------------------------------------------
# STAGE 6 — RECON
# ------------------------------------------------------------

STAGE6_DIR = MODELS_DIR / "stage6_recon"

STAGE6_MODEL = STAGE6_DIR / "stage6_reconnaissance_specialist.txt"
STAGE6_FEATURES = STAGE6_DIR / "stage6_reconnaissance_features.pkl"
STAGE6_ENCODER = STAGE6_DIR / "stage6_reconnaissance_label_encoder.pkl"


# ------------------------------------------------------------
# STAGE 7 — MIRAI
# ------------------------------------------------------------

STAGE7_DIR = MODELS_DIR / "stage7"

STAGE7_MODEL = STAGE7_DIR / "stage7_mirai_lightgbm.txt"
STAGE7_FEATURES = STAGE7_DIR / "stage7_mirai_features.pkl"
STAGE7_ENCODER = STAGE7_DIR / "stage7_mirai_label_encoder.pkl"


# ------------------------------------------------------------
# Common 39 features
# ------------------------------------------------------------

COMMON_FEATURES = [
    "Header_Length",
    "Protocol Type",
    "Time_To_Live",
    "Rate",
    "fin_flag_number",
    "syn_flag_number",
    "rst_flag_number",
    "psh_flag_number",
    "ack_flag_number",
    "ece_flag_number",
    "cwr_flag_number",
    "ack_count",
    "syn_count",
    "fin_count",
    "rst_count",
    "HTTP",
    "HTTPS",
    "DNS",
    "Telnet",
    "SMTP",
    "SSH",
    "IRC",
    "TCP",
    "UDP",
    "DHCP",
    "ARP",
    "ICMP",
    "IGMP",
    "IPv",
    "LLC",
    "Tot sum",
    "Min",
    "Max",
    "AVG",
    "Std",
    "Tot size",
    "IAT",
    "Number",
    "Variance",
]