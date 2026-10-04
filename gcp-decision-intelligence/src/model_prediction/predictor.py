import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder


class Predictor:

    def __init__(self, model_path):

        package = joblib.load(model_path)

        self.model = package["model"]
        self.feature_names = package["feature_names"]
        self.target_column = package["target_column"]
        self.problem_type = package["problem_type"]

    # ---------------------------------------
    # Validate Dataset
    # ---------------------------------------

    def validate_features(self, dataframe):

        missing = [
            col for col in self.feature_names
            if col not in dataframe.columns
        ]

        extra = [
            col for col in dataframe.columns
            if col not in self.feature_names
        ]

        return missing, extra

    # ---------------------------------------
    # Prediction
    # ---------------------------------------

    

    def predict(self, dataframe):

    # Check missing columns
        missing = [
            col for col in self.feature_names
            if col not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                "The uploaded dataset does not match the selected model."
            )

        dataframe = dataframe[self.feature_names].copy()

        return self.model.predict(dataframe)