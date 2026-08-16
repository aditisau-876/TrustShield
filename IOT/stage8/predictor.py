# ============================================================
# DEVTRUST — STAGE 8 PREDICTOR
# ============================================================

from pathlib import Path
import numpy as np
import pandas as pd

from artifact_loader import (
    load_pickle,
    load_lightgbm,
    load_json,
    load_features,

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
)

from feature_adapter import (
    adapt_features,
    prepare_dataframe,
)

from hierarchy import route_family


class DevTrustPredictor:

    def __init__(self):

        print("=" * 70)
        print("DEVTRUST — INITIALIZING HIERARCHICAL PREDICTOR")
        print("=" * 70)

        # ====================================================
        # STAGE 1
        # ====================================================

        self.stage1_model = load_pickle(
            STAGE1_MODEL
        )

        self.stage1_features = load_json(
            STAGE1_FEATURES
        )

        # ====================================================
        # STAGE 2
        # ====================================================

        self.stage2_model = load_pickle(
            STAGE2_MODEL
        )

        self.stage2_encoder = load_pickle(
            STAGE2_ENCODER
        )

        # ====================================================
        # STAGE 3 — DDOS
        # ====================================================

        self.stage3_model = load_pickle(
            STAGE3_MODEL
        )

        self.stage3_encoder = load_pickle(
            STAGE3_ENCODER
        )

        # ====================================================
        # STAGE 4 — DOS
        # ====================================================

        self.stage4_model = load_pickle(
            STAGE4_MODEL
        )

        self.stage4_features = load_features(
            STAGE4_FEATURES
        )

        self.stage4_encoder = load_pickle(
            STAGE4_ENCODER
        )

        # ====================================================
        # STAGE 5 — VULNERABILITY
        # ====================================================

        self.stage5_model = load_lightgbm(
            STAGE5_MODEL
        )

        self.stage5_features = load_features(
            STAGE5_FEATURES
        )

        self.stage5_encoder = load_pickle(
            STAGE5_ENCODER
        )

        # ====================================================
        # STAGE 6 — RECON
        # ====================================================

        self.stage6_model = load_lightgbm(
            STAGE6_MODEL
        )

        self.stage6_features = load_features(
            STAGE6_FEATURES
        )

        self.stage6_encoder = load_pickle(
            STAGE6_ENCODER
        )

        # ====================================================
        # STAGE 7 — MIRAI
        # ====================================================

        self.stage7_model = load_lightgbm(
            STAGE7_MODEL
        )

        self.stage7_features = load_features(
            STAGE7_FEATURES
        )

        self.stage7_encoder = load_pickle(
            STAGE7_ENCODER
        )

        print("\n✓ All DevTrust models initialized.")

    # ========================================================
    # MODEL FEATURE DISCOVERY
    # ========================================================

    def _get_model_features(
        self,
        model,
        fallback_features=None
    ):
        """
        Determine the exact feature schema expected by a model.

        Priority:

        1. LightGBM Booster feature names
        2. sklearn feature_names_in_
        3. fallback feature artifact
        4. n_features_in_ + generated names

        This is important because some DevTrust models were trained
        with a 'label' column still present.
        """

        # ----------------------------------------------------
        # LightGBM sklearn wrapper
        # ----------------------------------------------------

        if hasattr(model, "booster_"):

            try:
                names = model.booster_.feature_name()

                if names:
                    return list(names)

            except Exception:
                pass

        # ----------------------------------------------------
        # Native LightGBM Booster
        # ----------------------------------------------------

        try:

            if hasattr(model, "feature_name"):

                names = model.feature_name()

                if names:
                    return list(names)

        except Exception:
            pass

        # ----------------------------------------------------
        # sklearn models
        # ----------------------------------------------------

        if hasattr(
            model,
            "feature_names_in_"
        ):

            names = model.feature_names_in_

            if names is not None:
                return list(names)

        # ----------------------------------------------------
        # Saved feature artifact
        # ----------------------------------------------------

        if fallback_features is not None:

            features = list(
                fallback_features
            )

            return features

        # ----------------------------------------------------
        # Last resort
        # ----------------------------------------------------

        expected = getattr(
            model,
            "n_features_in_",
            None
        )

        if expected is not None:

            return [
                f"feature_{i}"
                for i in range(
                    int(expected)
                )
            ]

        raise ValueError(
            "Unable to determine model feature schema."
        )

    # ========================================================
    # FEATURE PREPARATION
    # ========================================================

    def _prepare_for_model(
        self,
        data,
        model,
        fallback_features=None,
        stage_name="MODEL"
    ):
        """
        Prepare input using the model's ACTUAL training schema.

        Important:
        If the model was trained with a 'label' column, that column
        remains part of the input schema and will be filled with 0
        when it is not supplied by the caller.

        This prevents LightGBM / sklearn feature-count mismatches.
        """

        required_features = self._get_model_features(
            model,
            fallback_features
        )

        df = adapt_features(
            data,
            required_features,
            stage_name
        )

        # ----------------------------------------------------
        # Final sanity check
        # ----------------------------------------------------

        expected = len(
            required_features
        )

        received = df.shape[1]

        if received != expected:

            raise ValueError(
                f"{stage_name}: feature mismatch.\n"
                f"Expected: {expected}\n"
                f"Received: {received}\n"
                f"Features: {required_features}"
            )

        return df

    # ========================================================
    # GENERIC SKLEARN PREDICTION
    # ========================================================

    def _predict_sklearn(
        self,
        model,
        X
    ):

        prediction = model.predict(
            X
        )

        prediction = np.asarray(
            prediction
        )

        if prediction.ndim == 0:
            return int(prediction)

        return int(
            prediction[0]
        )

    # ========================================================
    # GENERIC SKLEARN CONFIDENCE
    # ========================================================

    def _confidence_sklearn(
        self,
        model,
        X
    ):

        if not hasattr(
            model,
            "predict_proba"
        ):
            return None

        probabilities = model.predict_proba(
            X
        )

        probabilities = np.asarray(
            probabilities
        )

        if probabilities.ndim == 1:
            return float(
                np.max(probabilities)
            )

        return float(
            np.max(
                probabilities[0]
            )
        )

    # ========================================================
    # GENERIC LIGHTGBM PREDICTION
    # ========================================================

    def _predict_lightgbm(
        self,
        model,
        X
    ):
        """
        LightGBM Booster prediction.

        Handles both:

        - multiclass output
        - binary output
        """

        probabilities = model.predict(
            X
        )

        probabilities = np.asarray(
            probabilities
        )

        # ----------------------------------------------------
        # Binary / scalar prediction
        # ----------------------------------------------------

        if probabilities.ndim == 0:

            return int(
                probabilities
            )

        # ----------------------------------------------------
        # Single value
        # ----------------------------------------------------

        if probabilities.ndim == 1:

            if len(probabilities) == 1:

                return int(
                    probabilities[0]
                )

            # Multiclass
            return int(
                np.argmax(
                    probabilities
                )
            )

        # ----------------------------------------------------
        # 2D output
        # ----------------------------------------------------

        return int(
            np.argmax(
                probabilities[0]
            )
        )

    # ========================================================
    # GENERIC LIGHTGBM CONFIDENCE
    # ========================================================

    def _confidence_lightgbm(
        self,
        model,
        X
    ):

        probabilities = model.predict(
            X
        )

        probabilities = np.asarray(
            probabilities
        )

        if probabilities.ndim == 0:

            return float(
                probabilities
            )

        if probabilities.ndim == 1:

            if len(probabilities) == 1:
                return float(
                    probabilities[0]
                )

            return float(
                np.max(
                    probabilities
                )
            )

        return float(
            np.max(
                probabilities[0]
            )
        )

    # ========================================================
    # STAGE 1 — BINARY
    # ========================================================

    def predict_stage1(
        self,
        data
    ):

        df = self._prepare_for_model(
            data,
            self.stage1_model,
            self.stage1_features,
            "STAGE 1"
        )

        pred = self._predict_sklearn(
            self.stage1_model,
            df
        )

        # ----------------------------------------------------
        # Stage 1 labels
        # ----------------------------------------------------

        if int(pred) == 0:

            label = "BENIGN"

        else:

            label = "ATTACK"

        confidence = self._confidence_sklearn(
            self.stage1_model,
            df
        )

        return {
            "stage": 1,
            "prediction": label,
            "class_id": int(pred),
            "confidence": confidence,
        }

    # ========================================================
    # STAGE 2 — ATTACK FAMILY
    # ========================================================

    def predict_stage2(
        self,
        data
    ):

        df = self._prepare_for_model(
            data,
            self.stage2_model,
            None,
            "STAGE 2"
        )

        pred = self._predict_sklearn(
            self.stage2_model,
            df
        )

        family = self.stage2_encoder.inverse_transform(
            [int(pred)]
        )[0]

        confidence = self._confidence_sklearn(
            self.stage2_model,
            df
        )

        return {
            "stage": 2,
            "prediction": str(family),
            "class_id": int(pred),
            "confidence": confidence,
        }

    # ========================================================
    # STAGE 3 — DDOS
    # ========================================================

    def predict_stage3(
        self,
        data
    ):

        df = self._prepare_for_model(
            data,
            self.stage3_model,
            None,
            "STAGE 3"
        )

        pred = self._predict_sklearn(
            self.stage3_model,
            df
        )

        label = self.stage3_encoder.inverse_transform(
            [int(pred)]
        )[0]

        confidence = self._confidence_sklearn(
            self.stage3_model,
            df
        )

        return {
            "stage": 3,
            "prediction": str(label),
            "class_id": int(pred),
            "confidence": confidence,
        }

    # ========================================================
    # STAGE 4 — DOS
    # ========================================================

    def predict_stage4(
        self,
        data
    ):

        # IMPORTANT:
        #
        # stage4_dos_specialist.pkl reports:
        #
        # 40 features
        #
        # including:
        #
        # "label"
        #
        # Therefore DO NOT remove label here.
        #
        # _prepare_for_model() obtains the actual schema directly
        # from model.booster_.feature_name().

        df = self._prepare_for_model(
            data,
            self.stage4_model,
            self.stage4_features,
            "STAGE 4"
        )

        pred = self._predict_sklearn(
            self.stage4_model,
            df
        )

        label = self.stage4_encoder.inverse_transform(
            [int(pred)]
        )[0]

        confidence = self._confidence_sklearn(
            self.stage4_model,
            df
        )

        return {
            "stage": 4,
            "prediction": str(label),
            "class_id": int(pred),
            "confidence": confidence,
        }

    # ========================================================
    # STAGE 5 — VULNERABILITY
    # ========================================================

    def predict_stage5(
        self,
        data
    ):

        df = self._prepare_for_model(
            data,
            self.stage5_model,
            self.stage5_features,
            "STAGE 5"
        )

        pred_proba = self.stage5_model.predict(
            df
        )

        pred_proba = np.asarray(
            pred_proba
        )

        # ----------------------------------------------------
        # Handle LightGBM multiclass
        # ----------------------------------------------------

        if pred_proba.ndim == 1:

            if len(pred_proba) == 1:

                pred = int(
                    pred_proba[0]
                )

                confidence = 1.0

            else:

                pred = int(
                    np.argmax(
                        pred_proba
                    )
                )

                confidence = float(
                    np.max(
                        pred_proba
                    )
                )

        else:

            pred = int(
                np.argmax(
                    pred_proba[0]
                )
            )

            confidence = float(
                np.max(
                    pred_proba[0]
                )
            )

        label = self.stage5_encoder.inverse_transform(
            [pred]
        )[0]

        return {
            "stage": 5,
            "prediction": str(label),
            "class_id": pred,
            "confidence": confidence,
        }

    # ========================================================
    # STAGE 6 — RECON
    # ========================================================

    def predict_stage6(
        self,
        data
    ):

        df = self._prepare_for_model(
            data,
            self.stage6_model,
            self.stage6_features,
            "STAGE 6"
        )

        pred_proba = self.stage6_model.predict(
            df
        )

        pred_proba = np.asarray(
            pred_proba
        )

        if pred_proba.ndim == 1:

            if len(pred_proba) == 1:

                pred = int(
                    pred_proba[0]
                )

                confidence = 1.0

            else:

                pred = int(
                    np.argmax(
                        pred_proba
                    )
                )

                confidence = float(
                    np.max(
                        pred_proba
                    )
                )

        else:

            pred = int(
                np.argmax(
                    pred_proba[0]
                )
            )

            confidence = float(
                np.max(
                    pred_proba[0]
                )
            )

        label = self.stage6_encoder.inverse_transform(
            [pred]
        )[0]

        return {
            "stage": 6,
            "prediction": str(label),
            "class_id": pred,
            "confidence": confidence,
        }

    # ========================================================
    # STAGE 7 — MIRAI
    # ========================================================

    def predict_stage7(
        self,
        data
    ):

        df = self._prepare_for_model(
            data,
            self.stage7_model,
            self.stage7_features,
            "STAGE 7"
        )

        pred_proba = self.stage7_model.predict(
            df
        )

        pred_proba = np.asarray(
            pred_proba
        )

        if pred_proba.ndim == 1:

            if len(pred_proba) == 1:

                pred = int(
                    pred_proba[0]
                )

                confidence = 1.0

            else:

                pred = int(
                    np.argmax(
                        pred_proba
                    )
                )

                confidence = float(
                    np.max(
                        pred_proba
                    )
                )

        else:

            pred = int(
                np.argmax(
                    pred_proba[0]
                )
            )

            confidence = float(
                np.max(
                    pred_proba[0]
                )
            )

        label = self.stage7_encoder.inverse_transform(
            [pred]
        )[0]

        return {
            "stage": 7,
            "prediction": str(label),
            "class_id": pred,
            "confidence": confidence,
        }

    # ========================================================
    # COMPLETE HIERARCHICAL PREDICTION
    # ========================================================

    def predict(
        self,
        data
    ):

        # ====================================================
        # STAGE 1
        # ====================================================

        stage1 = self.predict_stage1(
            data
        )

        # ----------------------------------------------------
        # BENIGN
        # ----------------------------------------------------

        if stage1["prediction"] == "BENIGN":

            return {
                "final_prediction": "BENIGN",
                "route": "STAGE1",
                "stage1": stage1,
                "stage2": None,
                "specialist": None,
            }

        # ====================================================
        # STAGE 2
        # ====================================================

        stage2 = self.predict_stage2(
            data
        )

        family = stage2["prediction"]

        # ====================================================
        # HIERARCHY ROUTING
        # ====================================================

        route = route_family(
            family
        )

        # ====================================================
        # SPECIALIST
        # ====================================================

        specialist = None

        # ----------------------------------------------------
        # DDOS
        # ----------------------------------------------------

        if route == "STAGE3_DDOS":

            specialist = self.predict_stage3(
                data
            )

        # ----------------------------------------------------
        # DOS
        # ----------------------------------------------------

        elif route == "STAGE4_DOS":

            specialist = self.predict_stage4(
                data
            )

        # ----------------------------------------------------
        # VULNERABILITY
        # ----------------------------------------------------

        elif route == "STAGE5_VULNERABILITY":

            specialist = self.predict_stage5(
                data
            )

        # ----------------------------------------------------
        # RECON
        # ----------------------------------------------------

        elif route == "STAGE6_RECON":

            specialist = self.predict_stage6(
                data
            )

        # ----------------------------------------------------
        # MIRAI
        # ----------------------------------------------------

        elif route == "STAGE7_MIRAI":

            specialist = self.predict_stage7(
                data
            )

        # ----------------------------------------------------
        # No specialist
        # ----------------------------------------------------

        else:

            specialist = {
                "stage": None,
                "prediction": family,
                "class_id": stage2["class_id"],
                "confidence": stage2["confidence"],
                "note":
                    "No fine-grained specialist exists "
                    "for this Stage-2 family."
            }

        # ====================================================
        # FINAL RESULT
        # ====================================================

        return {
            "final_prediction":
                specialist["prediction"],

            "route":
                route,

            "stage1":
                stage1,

            "stage2":
                stage2,

            "specialist":
                specialist,
        }