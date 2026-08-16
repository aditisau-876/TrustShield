# ============================================================
# DEVTRUST — STAGE 8 PIPELINE
# ============================================================

from predictor import DevTrustPredictor


_predictor = None


def get_predictor():

    global _predictor

    if _predictor is None:
        _predictor = DevTrustPredictor()

    return _predictor


def predict(data):

    predictor = get_predictor()

    return predictor.predict(
        data
    )