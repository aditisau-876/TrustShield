# ============================================================
# DEVTRUST — STAGE 8 FEATURE ADAPTER
# ============================================================

from typing import Iterable, Any

import numpy as np
import pandas as pd


# ============================================================
# CANONICAL 39-FEATURE SCHEMA
# ============================================================

CANONICAL_FEATURES = [
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


# ============================================================
# STAGE 4 — ACTUAL SAVED MODEL SCHEMA
# ============================================================

STAGE4_FEATURES = CANONICAL_FEATURES + ["label"]


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def normalize_columns(data: Any) -> pd.DataFrame:
    """
    Normalize common feature-name variations.

    Different DevTrust artifacts use slightly different
    naming conventions, for example:

        Protocol_Type -> Protocol Type
        Tot_sum      -> Tot sum
        Tot_size     -> Tot size

    The canonical Stage 8 representation uses the names
    stored in the feature lists wherever possible.
    """

    df = data.copy()

    replacements = {
        "Protocol_Type": "Protocol Type",
        "Tot_sum": "Tot sum",
        "Tot_size": "Tot size",
    }

    df.rename(columns=replacements, inplace=True)

    return df


# ============================================================
# INPUT -> DATAFRAME
# ============================================================

def prepare_dataframe(data: Any) -> pd.DataFrame:
    """
    Convert supported input types into a one-row DataFrame.

    Supported:
        dict
        pandas.Series
        pandas.DataFrame
    """

    if isinstance(data, pd.DataFrame):
        df = data.copy()

    elif isinstance(data, pd.Series):
        df = data.to_frame().T

    elif isinstance(data, dict):
        df = pd.DataFrame([data])

    else:
        raise TypeError(
            "Unsupported input type: "
            f"{type(data).__name__}. "
            "Expected dict, pandas.Series, or pandas.DataFrame."
        )

    return normalize_columns(df)


# ============================================================
# NUMERIC CLEANUP
# ============================================================

def clean_numeric_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert all model features to numeric values.

    Invalid values become NaN and are subsequently replaced
    with 0.0.

    Infinite values are also replaced.
    """

    df = df.copy()

    for column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    df = df.fillna(0.0)

    return df


# ============================================================
# GENERIC FEATURE ADAPTER
# ============================================================

def adapt_features(
    data: Any,
    required_features: Iterable[str],
    stage_name: str = "MODEL",
    keep_label: bool = False,
) -> pd.DataFrame:
    """
    Adapt arbitrary input data to the exact schema required
    by a specific DevTrust model.

    Behaviour:

    1. Convert input to DataFrame.
    2. Normalize column names.
    3. Add missing features with 0.0.
    4. Optionally preserve/add 'label'.
    5. Remove unrelated extra columns.
    6. Reorder columns exactly according to required_features.
    7. Convert values to numeric.
    8. Replace NaN/inf with 0.0.
    9. Validate final feature count.

    IMPORTANT:
    The saved Stage 4 model genuinely expects 'label' as
    feature number 40, so Stage 4 must use keep_label=True.
    """

    df = prepare_dataframe(data)

    required_features = list(required_features)

    # --------------------------------------------------------
    # Determine whether this model explicitly expects label
    # --------------------------------------------------------

    expects_label = "label" in required_features

    if expects_label:
        keep_label = True

    # --------------------------------------------------------
    # Add / preserve required features
    # --------------------------------------------------------

    for feature in required_features:

        if feature not in df.columns:

            # label is a training-artifact feature in Stage 4.
            # We cannot derive a real label during inference,
            # therefore the pipeline supplies 0.0.
            #
            # This preserves the 40-column shape required by
            # the saved Stage 4 model.
            df[feature] = 0.0

    # --------------------------------------------------------
    # Remove label ONLY if model does not require it
    # --------------------------------------------------------

    if not expects_label:

        if "label" in df.columns:
            df = df.drop(
                columns=["label"]
            )

        if "Label" in df.columns:
            df = df.drop(
                columns=["Label"]
            )

    else:

        # Stage 4 explicitly expects "label".
        #
        # If the caller did not provide it, it was already
        # created above as 0.0.
        if "label" not in df.columns:
            df["label"] = 0.0

    # --------------------------------------------------------
    # Keep EXACT model order
    # --------------------------------------------------------

    df = df[required_features]

    # --------------------------------------------------------
    # Numeric cleanup
    # --------------------------------------------------------

    df = clean_numeric_dataframe(df)

    # --------------------------------------------------------
    # Shape validation
    # --------------------------------------------------------

    expected_count = len(required_features)
    received_count = df.shape[1]

    if received_count != expected_count:

        raise ValueError(
            f"\n"
            f"{stage_name}: FEATURE SHAPE MISMATCH\n"
            f"Expected : {expected_count}\n"
            f"Received : {received_count}\n"
            f"Expected features:\n"
            f"{required_features}\n"
            f"Received columns:\n"
            f"{list(df.columns)}"
        )

    return df


# ============================================================
# STAGE 1 / 3 / 5 / 6 / 7
# ============================================================

def adapt_39_features(data: Any) -> pd.DataFrame:
    """
    Adapter for the standard 39-feature models.

    Used by:
        Stage 1
        Stage 3
        Stage 5
        Stage 6
        Stage 7
    """

    return adapt_features(
        data=data,
        required_features=CANONICAL_FEATURES,
        stage_name="39-feature specialist",
        keep_label=False,
    )


# ============================================================
# STAGE 2
# ============================================================

def adapt_stage2_features(
    data: Any,
    required_features: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Stage 2 expects 40 features.

    The exact Stage 2 schema should preferably be obtained
    from the loaded model rather than guessed here.

    predictor.py should pass the model's actual feature
    names into this function.

    If required_features is not supplied, we fall back to
    the canonical 39 features plus label.
    """

    if required_features is None:

        required_features = STAGE4_FEATURES

    return adapt_features(
        data=data,
        required_features=required_features,
        stage_name="STAGE 2",
        keep_label="label" in list(required_features),
    )


# ============================================================
# STAGE 4
# ============================================================

def adapt_stage4_features(
    data: Any,
    required_features: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Stage 4 adapter.

    IMPORTANT:
    The saved Stage 4 model was trained with 40 features:

        39 normal traffic features
        +
        label

    Therefore we MUST provide all 40 columns.

    If label is not present in the incoming packet data,
    it is initialized to 0.0 so the model receives exactly
    the shape it was trained on.
    """

    if required_features is None:

        required_features = STAGE4_FEATURES

    required_features = list(required_features)

    return adapt_features(
        data=data,
        required_features=required_features,
        stage_name="STAGE 4 — DOS",
        keep_label=True,
    )


# ============================================================
# STAGE 5
# ============================================================

def adapt_stage5_features(data: Any) -> pd.DataFrame:
    """
    Stage 5 vulnerability specialist.
    """

    return adapt_features(
        data=data,
        required_features=CANONICAL_FEATURES,
        stage_name="STAGE 5 — VULNERABILITY",
        keep_label=False,
    )


# ============================================================
# STAGE 6
# ============================================================

def adapt_stage6_features(data: Any) -> pd.DataFrame:
    """
    Stage 6 reconnaissance specialist.
    """

    return adapt_features(
        data=data,
        required_features=CANONICAL_FEATURES,
        stage_name="STAGE 6 — RECON",
        keep_label=False,
    )


# ============================================================
# STAGE 7
# ============================================================

def adapt_stage7_features(data: Any) -> pd.DataFrame:
    """
    Stage 7 Mirai specialist.
    """

    return adapt_features(
        data=data,
        required_features=CANONICAL_FEATURES,
        stage_name="STAGE 7 — MIRAI",
        keep_label=False,
    )


# ============================================================
# NUMPY CONVERSION
# ============================================================

def dataframe_to_numpy(
    df: pd.DataFrame,
) -> np.ndarray:
    """
    Convert prepared DataFrame to float32 NumPy array.
    """

    return df.to_numpy(
        dtype=np.float32
    )


# ============================================================
# DEBUG / VALIDATION HELPER
# ============================================================

def inspect_adapted_features(
    data: Any,
    required_features: Iterable[str],
    stage_name: str = "MODEL",
) -> None:
    """
    Print the final schema produced by the adapter.

    Useful while debugging model feature mismatches.
    """

    df = adapt_features(
        data=data,
        required_features=required_features,
        stage_name=stage_name,
        keep_label="label" in list(required_features),
    )

    print()
    print("=" * 60)
    print(f"{stage_name} — ADAPTED FEATURE SCHEMA")
    print("=" * 60)

    print(f"Shape: {df.shape}")

    for index, column in enumerate(df.columns):
        print(
            f"{index:02d}: {column} = "
            f"{df.iloc[0][column]}"
        )

    print("=" * 60)