# ============================================================
# DEVTRUST — STAGE 8 ARTIFACT LOADER
# ============================================================
#
# Supports:
#   1. Joblib / pickle models
#   2. LightGBM .txt Booster models
#   3. JSON files
#   4. Pickled feature lists
#   5. Pickled LabelEncoders
#
# ============================================================

from pathlib import Path
import json
import joblib
import lightgbm as lgb


# ============================================================
# BASE PATHS
# ============================================================

STAGE8_DIR = Path(__file__).resolve().parent
IOT_DIR = STAGE8_DIR.parent
MODELS_DIR = IOT_DIR / "models"


# ============================================================
# GENERIC PATH CHECK
# ============================================================

def check_file(path):
    """
    Check whether an artifact exists.

    Parameters
    ----------
    path : str or Path

    Returns
    -------
    Path
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"\nArtifact not found:\n{path}"
        )

    if not path.is_file():
        raise FileNotFoundError(
            f"\nExpected a file but found something else:\n{path}"
        )

    return path


# ============================================================
# JOBLIB / PICKLE LOADER
# ============================================================

def load_pickle(path):
    """
    Load .pkl / joblib artifacts.

    Your models were saved using joblib, so joblib.load()
    should be preferred over raw pickle.load().
    """

    path = check_file(path)

    print(f"[joblib] Loading: {path.name}")

    try:
        obj = joblib.load(path)

    except Exception as e:
        raise RuntimeError(
            f"\nFailed to load Joblib/Pickle artifact:\n"
            f"{path}\n\n"
            f"Error:\n{e}"
        ) from e

    return obj


# ============================================================
# LIGHTGBM BOOSTER LOADER
# ============================================================

def load_lightgbm(path):
    """
    Load a native LightGBM Booster saved as .txt.

    Used by:
        Stage 5 vulnerability specialist
        Stage 6 reconnaissance specialist
        Stage 7 MIRAI specialist
    """

    path = check_file(path)

    print(f"[LightGBM] Loading: {path.name}")

    try:
        model = lgb.Booster(
            model_file=str(path)
        )

    except Exception as e:
        raise RuntimeError(
            f"\nFailed to load LightGBM model:\n"
            f"{path}\n\n"
            f"Error:\n{e}"
        ) from e

    return model


# ============================================================
# JSON LOADER
# ============================================================

def load_json(path):
    """
    Load JSON artifact.
    """

    path = check_file(path)

    print(f"[JSON] Loading: {path.name}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        raise RuntimeError(
            f"\nFailed to load JSON artifact:\n"
            f"{path}\n\n"
            f"Error:\n{e}"
        ) from e


# ============================================================
# AUTOMATIC ARTIFACT LOADER
# ============================================================

def load_artifact(path):
    """
    Automatically determine how to load an artifact
    based on its file extension.
    """

    path = check_file(path)

    suffix = path.suffix.lower()

    if suffix in [".pkl", ".pickle", ".joblib"]:
        return load_pickle(path)

    elif suffix == ".txt":
        return load_lightgbm(path)

    elif suffix == ".json":
        return load_json(path)

    else:
        raise ValueError(
            f"\nUnsupported artifact type:\n"
            f"{path}\n\n"
            f"Supported extensions:\n"
            f"  .pkl\n"
            f"  .pickle\n"
            f"  .joblib\n"
            f"  .txt\n"
            f"  .json"
        )


# ============================================================
# FEATURE LIST LOADER
# ============================================================

def load_features(path):
    """
    Load a feature list stored as a pickle/joblib file.

    Returns
    -------
    list
    """

    features = load_pickle(path)

    if not isinstance(features, (list, tuple)):
        raise TypeError(
            f"\nExpected feature list but received:\n"
            f"{type(features)}\n"
            f"File: {path}"
        )

    features = list(features)

    print(
        f"[features] Loaded {len(features)} features "
        f"from {Path(path).name}"
    )

    return features


# ============================================================
# LABEL ENCODER LOADER
# ============================================================

def load_label_encoder(path):
    """
    Load a sklearn LabelEncoder saved as pickle/joblib.
    """

    encoder = load_pickle(path)

    if not hasattr(encoder, "classes_"):
        raise TypeError(
            f"\nArtifact does not appear to be a LabelEncoder:\n"
            f"{path}\n\n"
            f"Loaded type: {type(encoder)}"
        )

    print(
        f"[encoder] Loaded {len(encoder.classes_)} classes "
        f"from {Path(path).name}"
    )

    return encoder


# ============================================================
# MODEL INFORMATION
# ============================================================

def describe_model(model, stage_name="MODEL"):
    """
    Print useful information about a loaded model.
    """

    print("\n" + "-" * 70)
    print(stage_name)
    print("-" * 70)

    print("Type:", type(model))

    # --------------------------------------------------------
    # sklearn / LightGBM sklearn wrapper
    # --------------------------------------------------------

    if hasattr(model, "n_features_in_"):
        print(
            "Expected features:",
            model.n_features_in_
        )

    if hasattr(model, "classes_"):
        print(
            "Classes:",
            model.classes_
        )

    # --------------------------------------------------------
    # Native LightGBM Booster
    # --------------------------------------------------------

    if isinstance(model, lgb.Booster):

        print(
            "Number of features:",
            model.num_feature()
        )

        print(
            "Number of trees:",
            model.num_trees()
        )

        try:
            feature_names = model.feature_name()

            if feature_names:
                print(
                    "Feature names:",
                    len(feature_names)
                )

        except Exception:
            pass

    print("-" * 70)


# ============================================================
# LABEL ENCODER INFORMATION
# ============================================================

def describe_encoder(encoder, stage_name="LABEL ENCODER"):
    """
    Print LabelEncoder mapping.
    """

    print("\n" + "-" * 70)
    print(stage_name)
    print("-" * 70)

    if not hasattr(encoder, "classes_"):
        print("Not a valid LabelEncoder.")
        return

    for i, label in enumerate(encoder.classes_):
        print(f"{i} -> {label}")

    print("-" * 70)


# ============================================================
# FEATURE VALIDATION
# ============================================================

def validate_features(
    features,
    expected_count=None,
    stage_name="FEATURES"
):
    """
    Validate a feature list.

    Parameters
    ----------
    features : list
    expected_count : int, optional
    stage_name : str
    """

    print("\n" + "-" * 70)
    print(stage_name)
    print("-" * 70)

    if not isinstance(features, list):
        raise TypeError(
            f"{stage_name}: feature schema must be a list."
        )

    print("Feature count:", len(features))

    if expected_count is not None:

        if len(features) != expected_count:

            raise ValueError(
                f"\n{stage_name}: feature count mismatch!\n"
                f"Expected: {expected_count}\n"
                f"Found   : {len(features)}"
            )

        print(
            f"✓ Feature count matches expected "
            f"{expected_count}"
        )

    print("-" * 70)


# ============================================================
# STAGE ARTIFACT PATHS
# ============================================================

# ------------------------------------------------------------
# STAGE 1
# ------------------------------------------------------------

STAGE1_MODEL = (
    MODELS_DIR
    / "stage1"
    / "binary_threat_detector.pkl"
)

STAGE1_FEATURES = (
    MODELS_DIR
    / "stage1"
    / "feature_columns.json"
)


# ------------------------------------------------------------
# STAGE 2
# ------------------------------------------------------------

STAGE2_MODEL = (
    MODELS_DIR
    / "stage2"
    / "stage2_attack_family_model.pkl"
)

STAGE2_ENCODER = (
    MODELS_DIR
    / "stage2"
    / "stage2_label_encoder.pkl"
)


# ------------------------------------------------------------
# STAGE 3 — DDOS
# ------------------------------------------------------------

STAGE3_MODEL = (
    MODELS_DIR
    / "stage3_ddos"
    / "ddos_specialist.pkl"
)

STAGE3_ENCODER = (
    MODELS_DIR
    / "stage3_ddos"
    / "ddos_label_encoder.pkl"
)


# ------------------------------------------------------------
# STAGE 4 — DOS
# ------------------------------------------------------------

STAGE4_MODEL = (
    MODELS_DIR
    / "stage4_dos"
    / "stage4_dos_specialist.pkl"
)

STAGE4_FEATURES = (
    MODELS_DIR
    / "stage4_dos"
    / "stage4_dos_features.pkl"
)

STAGE4_ENCODER = (
    MODELS_DIR
    / "stage4_dos"
    / "stage4_dos_label_encoder.pkl"
)


# ------------------------------------------------------------
# STAGE 5 — VULNERABILITY
# ------------------------------------------------------------

STAGE5_MODEL = (
    MODELS_DIR
    / "stage5"
    / "stage5_vulnerability_specialist.txt"
)

STAGE5_FEATURES = (
    MODELS_DIR
    / "stage5"
    / "stage5_features.pkl"
)

STAGE5_ENCODER = (
    MODELS_DIR
    / "stage5"
    / "stage5_label_encoder.pkl"
)


# ------------------------------------------------------------
# STAGE 6 — RECONNAISSANCE
# ------------------------------------------------------------

STAGE6_MODEL = (
    MODELS_DIR
    / "stage6_recon"
    / "stage6_reconnaissance_specialist.txt"
)

STAGE6_FEATURES = (
    MODELS_DIR
    / "stage6_recon"
    / "stage6_reconnaissance_features.pkl"
)

STAGE6_ENCODER = (
    MODELS_DIR
    / "stage6_recon"
    / "stage6_reconnaissance_label_encoder.pkl"
)


# ------------------------------------------------------------
# STAGE 7 — MIRAI
# ------------------------------------------------------------

STAGE7_MODEL = (
    MODELS_DIR
    / "stage7"
    / "stage7_mirai_lightgbm.txt"
)

STAGE7_FEATURES = (
    MODELS_DIR
    / "stage7"
    / "stage7_mirai_features.pkl"
)

STAGE7_ENCODER = (
    MODELS_DIR
    / "stage7"
    / "stage7_mirai_label_encoder.pkl"
)


# ============================================================
# ARTIFACT PATH SUMMARY
# ============================================================

def print_artifact_paths():

    print("\n" + "=" * 70)
    print("DEVTRUST — ARTIFACT PATHS")
    print("=" * 70)

    artifacts = {
        "STAGE 1 MODEL": STAGE1_MODEL,
        "STAGE 1 FEATURES": STAGE1_FEATURES,

        "STAGE 2 MODEL": STAGE2_MODEL,
        "STAGE 2 ENCODER": STAGE2_ENCODER,

        "STAGE 3 MODEL": STAGE3_MODEL,
        "STAGE 3 ENCODER": STAGE3_ENCODER,

        "STAGE 4 MODEL": STAGE4_MODEL,
        "STAGE 4 FEATURES": STAGE4_FEATURES,
        "STAGE 4 ENCODER": STAGE4_ENCODER,

        "STAGE 5 MODEL": STAGE5_MODEL,
        "STAGE 5 FEATURES": STAGE5_FEATURES,
        "STAGE 5 ENCODER": STAGE5_ENCODER,

        "STAGE 6 MODEL": STAGE6_MODEL,
        "STAGE 6 FEATURES": STAGE6_FEATURES,
        "STAGE 6 ENCODER": STAGE6_ENCODER,

        "STAGE 7 MODEL": STAGE7_MODEL,
        "STAGE 7 FEATURES": STAGE7_FEATURES,
        "STAGE 7 ENCODER": STAGE7_ENCODER,
    }

    for name, path in artifacts.items():

        status = "✓" if path.exists() else "✗"

        print(
            f"{status} {name:<25} "
            f"{path}"
        )

    print("=" * 70)


# ============================================================
# QUICK VALIDATION
# ============================================================

def validate_all_paths():

    artifacts = [
        STAGE1_MODEL,
        STAGE1_FEATURES,

        STAGE2_MODEL,
        STAGE2_ENCODER,

        STAGE3_MODEL,
        STAGE3_ENCODER,

        STAGE4_MODEL,
        STAGE4_FEATURES,
        STAGE4_ENCODER,

        STAGE5_MODEL,
        STAGE5_FEATURES,
        STAGE5_ENCODER,

        STAGE6_MODEL,
        STAGE6_FEATURES,
        STAGE6_ENCODER,

        STAGE7_MODEL,
        STAGE7_FEATURES,
        STAGE7_ENCODER,
    ]

    missing = [
        path for path in artifacts
        if not path.exists()
    ]

    if missing:

        print("\nMissing artifacts:")

        for path in missing:
            print("  ✗", path)

        return False

    print(
        "\n✓ ALL EXPECTED ARTIFACT PATHS EXIST"
    )

    return True


# ============================================================
# END
# ============================================================

if __name__ == "__main__":

    print_artifact_paths()

    validate_all_paths()