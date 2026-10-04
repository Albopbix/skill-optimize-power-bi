import pandas as pd


class DatasetDetector:

    def __init__(self, dataframe):
        self.df = dataframe

    def analyze_dataset(self):

        report = {
            "Rows": int(self.df.shape[0]),
            "Columns": int(self.df.shape[1]),
            "Missing Values": int(self.df.isnull().sum().sum()),
            "Duplicate Rows": int(self.df.duplicated().sum()),
            "Column Names": list(self.df.columns)
        }

        return report

    def detect_dataset_type(self):

        columns = [col.lower() for col in self.df.columns]

        ecommerce_keywords = [
            "customer",
            "order",
            "purchase",
            "payment",
            "seller",
            "product"
        ]

        score = 0

        for keyword in ecommerce_keywords:
            for column in columns:
                if keyword in column:
                    score += 1

        confidence = min(score * 20, 100)

        if score >= 3:
            return "E-Commerce Dataset", confidence
        else:
            return "Unknown Dataset", confidence

    def check_compatibility(self):

        columns = [col.lower() for col in self.df.columns]

        required_keywords = [
            "customer",
            "order"
        ]

        matched = []

        for keyword in required_keywords:
            for column in columns:
                if keyword in column:
                    matched.append(keyword)
                    break

        if len(matched) == len(required_keywords):
            return (
                "Compatible",
                "Customer and order-related information detected."
            )

        return (
            "Not Compatible",
            "Required customer/order information is missing."
        )