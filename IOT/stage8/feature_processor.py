import numpy as np
import pandas as pd


class FeatureProcessor:

    def __init__(self, master_features):
        self.master_features = list(master_features)

    # --------------------------------------------------------
    # Convert input into DataFrame
    # --------------------------------------------------------

    def to_dataframe(self, data):

        if isinstance(data, pd.DataFrame):
            df = data.copy()

        elif isinstance(data, dict):
            df = pd.DataFrame([data])

        elif isinstance(data, list):
            df = pd.DataFrame(data)

        else:
            raise TypeError(
                "Input must be a pandas DataFrame, dict or list."
            )

        return df

    # --------------------------------------------------------
    # Align features
    # --------------------------------------------------------

    def prepare(self, data):

        df = self.to_dataframe(data)

        # Remove Label if accidentally supplied
        if "Label" in df.columns:
            df = df.drop(columns=["Label"])

        # Add missing master features
        for feature in self.master_features:

            if feature not in df.columns:
                df[feature] = 0

        # Keep only known features
        df = df[self.master_features]

        # Convert everything to numeric
        for column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # Replace invalid values
        df = df.replace(
            [np.inf, -np.inf],
            np.nan
        )

        df = df.fillna(0)

        return df