import sys
from pathlib import Path

import pandas as pd

# ======================================================================
# PATH SETUP
# ======================================================================

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stage8.predictor import DevTrustPredictor


# ======================================================================
# HEADER
# ======================================================================

print("=" * 70)
print("DEVTRUST — STAGE 8 MULTI-CASE TEST")
print("=" * 70)


# ======================================================================
# INITIALIZE PREDICTOR
# ======================================================================

print("\nInitializing pipeline...\n")

try:
    predictor = DevTrustPredictor()

    print("\n✓ Pipeline initialized")

except Exception as e:
    print("\n❌ PIPELINE INITIALIZATION FAILED")
    print("Error:", repr(e))
    sys.exit(1)


# ======================================================================
# FEATURE SCHEMA
# ======================================================================

FEATURES = [
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


# ======================================================================
# BUILD ONE FLOW
# ======================================================================

def make_flow(**overrides):

    # Start with all 39 features
    row = {feature: 0.0 for feature in FEATURES}

    # Reasonable normal defaults
    row["Header_Length"] = 20.0
    row["Protocol Type"] = 6.0
    row["Time_To_Live"] = 64.0
    row["Rate"] = 10.0

    row["Tot sum"] = 100.0
    row["Min"] = 10.0
    row["Max"] = 100.0
    row["AVG"] = 50.0
    row["Std"] = 10.0
    row["Tot size"] = 100.0
    row["IAT"] = 0.05
    row["Number"] = 1.0
    row["Variance"] = 100.0

    # Accept accidental underscore spelling too
    if "Protocol_Type" in overrides:
        overrides["Protocol Type"] = overrides.pop("Protocol_Type")

    # Validate
    for key in overrides:

        if key not in FEATURES:
            raise ValueError(
                f"Unknown feature '{key}'.\n"
                f"Valid protocol feature name is 'Protocol Type'."
            )

    row.update(overrides)

    # IMPORTANT:
    # Return exactly one row with the correct feature order.
    return pd.DataFrame(
        [[row[feature] for feature in FEATURES]],
        columns=FEATURES,
    )


# ======================================================================
# TEST CASES
# ======================================================================

TEST_CASES = [

    (
        "NORMAL TCP TRAFFIC",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "Rate": 8,
                "Header_Length": 20,
                "ack_flag_number": 1,
                "ack_count": 5,
                "Number": 5,
                "Tot size": 500,
            }
        ),
    ),

    (
        "UDP HIGH-RATE TRAFFIC",
        make_flow(
            **{
                "Protocol Type": 17,
                "UDP": 1,
                "Rate": 5000,
                "Number": 1000,
                "Tot size": 60000,
                "IAT": 0.001,
            }
        ),
    ),

    (
        "SYN FLOOD PATTERN",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "Rate": 8000,
                "syn_flag_number": 1,
                "syn_count": 1000,
                "ack_flag_number": 0,
                "ack_count": 0,
                "rst_flag_number": 0,
                "Number": 1500,
                "Tot size": 90000,
                "IAT": 0.0005,
            }
        ),
    ),

    (
        "ICMP SWEEP PATTERN",
        make_flow(
            **{
                "Protocol Type": 1,
                "ICMP": 1,
                "Rate": 1500,
                "Number": 800,
                "Tot size": 48000,
                "IAT": 0.002,
            }
        ),
    ),

    (
        "HTTP WEB ATTACK PATTERN",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "HTTP": 1,
                "Rate": 2500,
                "psh_flag_number": 1,
                "ack_flag_number": 1,
                "ack_count": 100,
                "Number": 500,
                "Tot size": 50000,
            }
        ),
    ),

    (
        "HTTPS TRAFFIC",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "HTTPS": 1,
                "Rate": 100,
                "ack_flag_number": 1,
                "ack_count": 20,
                "Number": 20,
                "Tot size": 2000,
            }
        ),
    ),

    (
        "DNS TRAFFIC",
        make_flow(
            **{
                "Protocol Type": 17,
                "UDP": 1,
                "DNS": 1,
                "Rate": 200,
                "Number": 30,
                "Tot size": 3000,
            }
        ),
    ),

    (
        "SSH TRAFFIC",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "SSH": 1,
                "Rate": 80,
                "ack_flag_number": 1,
                "ack_count": 15,
                "Number": 15,
                "Tot size": 1500,
            }
        ),
    ),

    (
        "TELNET / MIRAI-LIKE PATTERN",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "Telnet": 1,
                "Rate": 4000,
                "syn_flag_number": 1,
                "syn_count": 500,
                "rst_flag_number": 1,
                "rst_count": 200,
                "Number": 700,
                "Tot size": 42000,
                "IAT": 0.001,
            }
        ),
    ),

    (
        "PORT SCAN PATTERN",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "Rate": 3000,
                "syn_flag_number": 1,
                "syn_count": 500,
                "rst_flag_number": 1,
                "rst_count": 400,
                "ack_flag_number": 0,
                "Number": 900,
                "Tot size": 54000,
                "IAT": 0.001,
            }
        ),
    ),

    (
        "RECONNAISSANCE PATTERN",
        make_flow(
            **{
                "Protocol Type": 6,
                "TCP": 1,
                "Rate": 1800,
                "syn_flag_number": 1,
                "syn_count": 300,
                "rst_flag_number": 1,
                "rst_count": 250,
                "ack_flag_number": 0,
                "Number": 600,
                "Tot size": 36000,
                "IAT": 0.002,
            }
        ),
    ),

    (
        "HIGHLY SUSPICIOUS TRAFFIC",
        make_flow(
            **{
                "Protocol Type": 17,
                "UDP": 1,
                "Rate": 10000,
                "syn_flag_number": 1,
                "syn_count": 500,
                "rst_flag_number": 1,
                "rst_count": 300,
                "psh_flag_number": 1,
                "ack_flag_number": 1,
                "ack_count": 200,
                "Number": 2000,
                "Tot size": 120000,
                "IAT": 0.0002,
                "Variance": 5000,
            }
        ),
    ),
]


# ======================================================================
# FIND CORRECT PREDICTION METHOD
# ======================================================================

def predict_with_pipeline(data):

    # Your predictor may expose one of these interfaces.
    if hasattr(predictor, "predict"):
        return predictor.predict(data)

    if hasattr(predictor, "predict_flow"):
        return predictor.predict_flow(data)

    if hasattr(predictor, "run"):
        return predictor.run(data)

    raise AttributeError(
        "Could not find a prediction method.\n"
        "Expected predict(), predict_flow(), or run()."
    )


# ======================================================================
# RUN TEST CASES
# ======================================================================

results = []

for number, (name, data) in enumerate(TEST_CASES, start=1):

    print("\n")
    print("=" * 70)
    print(f"TEST CASE {number}: {name}")
    print("=" * 70)

    try:

        result = predict_with_pipeline(data)

        print("\n✓ TEST PASSED")
        print("\nResult:")
        print("-" * 50)

        if isinstance(result, dict):

            for key, value in result.items():
                print(f"{key:<25}: {value}")

        else:
            print(result)

        results.append(
            {
                "case": number,
                "name": name,
                "status": "PASSED",
                "result": result,
            }
        )

    except Exception as e:

        print("\n❌ TEST FAILED")
        print("Error:", repr(e))

        results.append(
            {
                "case": number,
                "name": name,
                "status": "ERROR",
                "result": e,
            }
        )


# ======================================================================
# SUMMARY
# ======================================================================

print("\n\n")
print("=" * 70)
print("DEVTRUST — TEST SUMMARY")
print("=" * 70)

passed = 0
failed = 0

for item in results:

    print(f"\nCASE {item['case']}: {item['name']}")
    print(f"  STATUS : {item['status']}")

    if item["status"] == "PASSED":
        passed += 1
    else:
        failed += 1
        print(f"  ERROR  : {item['result']}")


print("\n")
print("=" * 70)
print("FINAL TEST STATUS")
print("=" * 70)

print(f"Passed : {passed}")
print(f"Failed : {failed}")
print(f"Total  : {len(results)}")

if failed == 0:
    print("\n✓ ALL TEST CASES COMPLETED SUCCESSFULLY")
else:
    print(
        f"\n⚠ {failed} case(s) produced errors."
    )

print("=" * 70)