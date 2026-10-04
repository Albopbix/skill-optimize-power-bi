from sklearn.ensemble import IsolationForest
import pandas as pd


class AnomalyDetector:

    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

    def detect(self, df):

        numeric = df.select_dtypes(include="number").copy()

        if numeric.empty:
            return None

        numeric = numeric.fillna(0)

        prediction = self.model.fit_predict(numeric)

        result = df.copy()

        result["Anomaly"] = prediction

        result["Anomaly"] = result["Anomaly"].map({

            1: "Normal",

            -1: "Anomaly"

        })

        return result