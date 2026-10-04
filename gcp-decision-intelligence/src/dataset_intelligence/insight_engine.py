class InsightEngine:

    def __init__(
        self,
        dataset_type,
        quality_report,
        compatibility
    ):

        self.dataset_type = dataset_type
        self.quality_report = quality_report
        self.compatibility = compatibility

    def generate_insights(self):

        insights = []

        # Dataset Type
        insights.append(
            f"Dataset Type Detected: {self.dataset_type}"
        )

        # Compatibility
        if self.compatibility == "Compatible":
            insights.append(
                "Dataset is compatible with the AI Decision Intelligence Platform."
            )
        else:
            insights.append(
                "Dataset is not fully compatible. Some required business columns are missing."
            )

        # Quality Score
        score = self.quality_report["Quality Score"]

        if score >= 90:
            insights.append(
                "Excellent data quality. Dataset is ready for Machine Learning."
            )

        elif score >= 75:
            insights.append(
                "Good data quality. Minor preprocessing is recommended."
            )

        else:
            insights.append(
                "Poor data quality. Significant cleaning is required."
            )

        # Missing Values
        if self.quality_report["Missing Values"] > 0:
            insights.append(
                f'The dataset contains {self.quality_report["Missing Values"]} missing values.'
            )

        # Duplicate Rows
        if self.quality_report["Duplicate Rows"] == 0:
            insights.append(
                "No duplicate records detected."
            )
        else:
            insights.append(
                f'{self.quality_report["Duplicate Rows"]} duplicate rows detected.'
            )

        # Business Recommendations
        if self.dataset_type == "E-Commerce Dataset":

            insights.append(
                "Recommended Business Use Cases:"
            )

            insights.append(
                "• Customer Churn Prediction"
            )

            insights.append(
                "• Customer Lifetime Value Prediction"
            )

            insights.append(
                "• Customer Segmentation"
            )

            insights.append(
                "• Product Recommendation"
            )

            insights.append(
                "• Sales Forecasting"
            )

        return insights