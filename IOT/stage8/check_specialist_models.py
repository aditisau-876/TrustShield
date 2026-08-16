# ============================================================
# DEVTRUST — STAGE 8 SPECIALIST MODEL CHECK
# ============================================================

from pathlib import Path
import joblib
import lightgbm as lgb


BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"


def load_model(path):

    print(f"\nLoading: {path}")

    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")

    # --------------------------------------------------------
    # Joblib / Pickle model
    # --------------------------------------------------------

    if path.suffix.lower() in [".pkl", ".pickle", ".joblib"]:

        model = joblib.load(path)

        print("  Type:", type(model))

        return model

    # --------------------------------------------------------
    # LightGBM text model
    # --------------------------------------------------------

    if path.suffix.lower() == ".txt":

        model = lgb.Booster(
            model_file=str(path)
        )

        print("  Type:", type(model))

        return model

    raise ValueError(
        f"Unsupported model format: {path}"
    )


def inspect_model(name, path):

    print("\n" + "-" * 70)
    print(name)
    print("-" * 70)

    try:

        model = load_model(path)

        # ----------------------------------------------------
        # LightGBM sklearn model
        # ----------------------------------------------------

        if hasattr(model, "classes_"):

            print(
                "  Classes:",
                model.classes_
            )

        # ----------------------------------------------------
        # LightGBM Booster
        # ----------------------------------------------------

        if isinstance(model, lgb.Booster):

            print(
                "  Number of trees:",
                model.num_trees()
            )

            print(
                "  Number of features:",
                model.num_feature()
            )

        # ----------------------------------------------------
        # Generic sklearn/lightgbm model
        # ----------------------------------------------------

        if hasattr(model, "n_features_in_"):

            print(
                "  Expected features:",
                model.n_features_in_
            )

        print("  ✓ LOAD SUCCESS")

        return model

    except Exception as e:

        print("  ✗ LOAD FAILED")
        print(
            "  Error:",
            type(e).__name__,
            str(e)
        )

        return None


def main():

    print("=" * 70)
    print("DEVTRUST — SPECIALIST MODEL INSPECTION")
    print("=" * 70)

    models = {

        "STAGE 1 — BINARY":
            MODELS_DIR /
            "stage1" /
            "binary_threat_detector.pkl",

        "STAGE 2 — ATTACK FAMILY":
            MODELS_DIR /
            "stage2" /
            "stage2_attack_family_model.pkl",

        "STAGE 3 — DDOS":
            MODELS_DIR /
            "stage3_ddos" /
            "ddos_specialist.pkl",

        "STAGE 4 — DOS":
            MODELS_DIR /
            "stage4_dos" /
            "stage4_dos_specialist.pkl",

        "STAGE 5 — VULNERABILITY":
            MODELS_DIR /
            "stage5" /
            "stage5_vulnerability_specialist.txt",

        "STAGE 6 — RECON":
            MODELS_DIR /
            "stage6_recon" /
            "stage6_reconnaissance_specialist.txt",

        "STAGE 7 — MIRAI":
            MODELS_DIR /
            "stage7" /
            "stage7_mirai_lightgbm.txt",
    }

    loaded = {}

    for name, path in models.items():

        loaded[name] = inspect_model(
            name,
            path
        )

    print("\n" + "=" * 70)
    print("FINAL MODEL STATUS")
    print("=" * 70)

    success = 0
    failed = 0

    for name, model in loaded.items():

        if model is not None:

            print(f"✓ {name}")
            success += 1

        else:

            print(f"✗ {name}")
            failed += 1

    print("\nSuccessful:", success)
    print("Failed    :", failed)

    if failed == 0:

        print(
            "\n✓ ALL SPECIALIST MODELS LOADED SUCCESSFULLY"
        )

    else:

        print(
            "\n⚠ Some models failed to load."
        )


if __name__ == "__main__":
    main()