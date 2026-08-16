# ============================================================
# DEVTRUST — STAGE 8 PIPELINE COMPILATION
# ============================================================

from pathlib import Path
import sys


STAGE8_DIR = Path(__file__).resolve().parent

if str(STAGE8_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(STAGE8_DIR)
    )


from artifact_loader import validate_all_paths
from predictor import DevTrustPredictor
from hierarchy import hierarchy_description


print("=" * 70)
print("DEVTRUST — STAGE 8 COMPILATION")
print("=" * 70)


# ============================================================
# STEP 1 — ARTIFACT CHECK
# ============================================================

print("\n[1/4] Checking artifacts...")

if not validate_all_paths():

    raise SystemExit(
        "\n✗ Compilation stopped because "
        "some artifacts are missing."
    )

print("✓ All artifacts present.")


# ============================================================
# STEP 2 — MODEL INITIALIZATION
# ============================================================

print("\n[2/4] Initializing models...")

predictor = DevTrustPredictor()

print("✓ All models initialized.")


# ============================================================
# STEP 3 — HIERARCHY CHECK
# ============================================================

print("\n[3/4] Checking hierarchy...")

routes = hierarchy_description()

for family, route in routes.items():

    print(
        f"{family:<25} → {route}"
    )

print("✓ Hierarchy loaded.")


# ============================================================
# STEP 4 — FINAL COMPILATION
# ============================================================

print("\n[4/4] Final compilation...")

required_methods = [
    "predict_stage1",
    "predict_stage2",
    "predict_stage3",
    "predict_stage4",
    "predict_stage5",
    "predict_stage6",
    "predict_stage7",
    "predict",
]

missing_methods = [
    method
    for method in required_methods
    if not hasattr(predictor, method)
]

if missing_methods:

    print(
        "\n✗ Missing methods:"
    )

    for method in missing_methods:
        print("  -", method)

    raise SystemExit(
        "\nCompilation failed."
    )


print("\n" + "=" * 70)
print("DEVTRUST STAGE 8 COMPILATION SUCCESSFUL")
print("=" * 70)

print("""
Architecture:

INPUT
  ↓
STAGE 1 — Binary Threat Detection
  ↓
STAGE 2 — Attack Family Classification
  ↓
  ├── DDOS          → STAGE 3
  ├── DOS           → STAGE 4
  ├── VULNERABILITY → STAGE 5
  ├── RECON         → STAGE 6
  ├── MIRAI         → STAGE 7
  └── OTHER         → Stage 2 family result

✓ Hierarchical routing available
✓ Specialist models available
✓ Feature adapters available
✓ Pipeline predictor available
""")