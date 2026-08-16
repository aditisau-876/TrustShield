# ============================================================
# DEVTRUST — DEEP ARTIFACT / FEATURE SCHEMA INSPECTION
# ============================================================

from pathlib import Path
import pickle
import joblib
import json
import lightgbm as lgb


BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"


def separator(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def inspect_model(name, path):
    separator(name)

    print("File:")
    print(path)

    if not path.exists():
        print("❌ FILE NOT FOUND")
        return None

    print(f"\nSize: {path.stat().st_size / 1024:.2f} KB")

    try:
        if path.suffix == ".txt":
            model = lgb.Booster(model_file=str(path))
        else:
            model = joblib.load(path)

        print("\nModel type:")
        print(type(model))

        print("\nModel representation:")
        print(model)

        # ----------------------------------------------------
        # LightGBM sklearn model
        # ----------------------------------------------------
        if hasattr(model, "n_features_in_"):
            print("\nExpected features:")
            print(model.n_features_in_)

        # ----------------------------------------------------
        # LightGBM Booster
        # ----------------------------------------------------
        if hasattr(model, "num_feature"):
            print("\nBooster feature count:")
            print(model.num_feature())

        if hasattr(model, "feature_name"):
            try:
                names = model.feature_name()

                print("\nBooster feature names:")
                print(f"Count: {len(names)}")

                for i, feature in enumerate(names):
                    print(f"{i}: {feature}")

            except Exception as e:
                print("Could not read booster feature names:", e)

        return model

    except Exception as e:
        print("\n❌ LOAD FAILED")
        print(type(e).__name__, e)
        return None


def inspect_pickle_file(name, path):
    separator(name)

    print("File:")
    print(path)

    if not path.exists():
        print("❌ FILE NOT FOUND")
        return

    try:
        obj = joblib.load(path)

        print("\nType:")
        print(type(obj))

        if isinstance(obj, list):
            print("Length:", len(obj))

            for i, item in enumerate(obj):
                print(f"{i}: {item}")

        elif isinstance(obj, dict):
            print("Dictionary keys:")

            for key in obj.keys():
                print(repr(key))

        else:
            print(obj)

    except Exception as e:
        print("\n❌ ERROR")
        print(type(e).__name__, e)


# ============================================================
# STAGE 1
# ============================================================

stage1_model = inspect_model(
    "STAGE 1 — BINARY MODEL",
    MODELS_DIR / "stage1" / "binary_threat_detector.pkl"
)


# ============================================================
# STAGE 1 FEATURE JSON
# ============================================================

stage1_features = MODELS_DIR / "stage1" / "feature_columns.json"

separator("STAGE 1 — FEATURE JSON")

print("File:")
print(stage1_features)

try:
    with open(stage1_features, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\nJSON type:")
    print(type(data))

    print("\nJSON content:")
    print(data)

except Exception as e:
    print("\n❌ JSON ERROR")
    print(type(e).__name__, e)


# ============================================================
# STAGE 2
# ============================================================

stage2_model = inspect_model(
    "STAGE 2 — ATTACK FAMILY MODEL",
    MODELS_DIR / "stage2" / "stage2_attack_family_model.pkl"
)


# ============================================================
# STAGE 3
# ============================================================

stage3_model = inspect_model(
    "STAGE 3 — DDOS MODEL",
    MODELS_DIR / "stage3_ddos" / "ddos_specialist.pkl"
)


# ============================================================
# STAGE 3 LABEL ENCODER
# ============================================================

inspect_pickle_file(
    "STAGE 3 — LABEL ENCODER",
    MODELS_DIR / "stage3_ddos" / "ddos_label_encoder.pkl"
)


# ============================================================
# STAGE 4
# ============================================================

stage4_model = inspect_model(
    "STAGE 4 — DOS MODEL",
    MODELS_DIR / "stage4_dos" / "stage4_dos_specialist.pkl"
)


# ============================================================
# STAGE 4 FEATURES
# ============================================================

inspect_pickle_file(
    "STAGE 4 — FEATURE LIST",
    MODELS_DIR / "stage4_dos" / "stage4_dos_features.pkl"
)


# ============================================================
# STAGE 5
# ============================================================

stage5_model = inspect_model(
    "STAGE 5 — VULNERABILITY MODEL",
    MODELS_DIR / "stage5" / "stage5_vulnerability_specialist.txt"
)


inspect_pickle_file(
    "STAGE 5 — FEATURE LIST",
    MODELS_DIR / "stage5" / "stage5_features.pkl"
)


# ============================================================
# STAGE 6
# ============================================================

stage6_model = inspect_model(
    "STAGE 6 — RECONNAISSANCE MODEL",
    MODELS_DIR / "stage6_recon" /
    "stage6_reconnaissance_specialist.txt"
)


inspect_pickle_file(
    "STAGE 6 — FEATURE LIST",
    MODELS_DIR / "stage6_recon" /
    "stage6_reconnaissance_features.pkl"
)


# ============================================================
# STAGE 7
# ============================================================

stage7_model = inspect_model(
    "STAGE 7 — MIRAI MODEL",
    MODELS_DIR / "stage7" /
    "stage7_mirai_lightgbm.txt"
)


inspect_pickle_file(
    "STAGE 7 — FEATURE LIST",
    MODELS_DIR / "stage7" /
    "stage7_mirai_features.pkl"
)


# ============================================================
# SUMMARY
# ============================================================

separator("FINAL ARCHITECTURE SUMMARY")

print("""
STAGE 1  → Binary threat detection
STAGE 2  → Attack family classification
STAGE 3  → DDOS specialist
STAGE 4  → DOS specialist
STAGE 5  → Vulnerability/Web specialist
STAGE 6  → Reconnaissance specialist
STAGE 7  → MIRAI specialist
STAGE 8  → Final hierarchical pipeline
""")

print("Inspection complete.")