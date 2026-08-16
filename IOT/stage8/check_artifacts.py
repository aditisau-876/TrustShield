from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(CURRENT_DIR))

from config import (
    STAGE1_MODEL,
    STAGE2_ENCODER,
    STAGE3_ENCODER,
    STAGE4_ENCODER,
    STAGE5_ENCODER,
    STAGE6_ENCODER,
    STAGE7_ENCODER,
)

from artifact_loader import load_pickle


print("=" * 70)
print("DEVTRUST — ARTIFACT INSPECTION")
print("=" * 70)


# ============================================================
# STAGE 1
# ============================================================

model = load_pickle(STAGE1_MODEL)

print("\nSTAGE 1")
print("-" * 50)

print("Model:", type(model))

print(
    "Classes:",
    getattr(model, "classes_", "No classes_ attribute")
)


# ============================================================
# STAGE 2
# ============================================================

encoder = load_pickle(STAGE2_ENCODER)

print("\nSTAGE 2 CLASSES")
print("-" * 50)

for i, label in enumerate(encoder.classes_):
    print(i, "->", label)


# ============================================================
# Stage specialists
# ============================================================

encoders = [
    ("STAGE 3 DDOS", STAGE3_ENCODER),
    ("STAGE 4 DOS", STAGE4_ENCODER),
    ("STAGE 5 VULNERABILITY", STAGE5_ENCODER),
    ("STAGE 6 RECON", STAGE6_ENCODER),
    ("STAGE 7 MIRAI", STAGE7_ENCODER),
]

for name, path in encoders:

    encoder = load_pickle(path)

    print(f"\n{name}")
    print("-" * 50)

    for i, label in enumerate(
        encoder.classes_
    ):
        print(i, "->", label)