class BusinessCopilot:

    def __init__(self, dataframe):

        self.df = dataframe

    def ask(self, question):

        q = question.lower()

        if "summary" in q:

            return (
                f"The dataset contains "
                f"{len(self.df)} rows and "
                f"{len(self.df.columns)} columns."
            )

        elif "missing" in q:

            return (
                f"Total missing values: "
                f"{self.df.isnull().sum().sum()}"
            )

        elif "duplicate" in q:

            return (
                f"Duplicate rows: "
                f"{self.df.duplicated().sum()}"
            )

        elif "quality" in q:

            missing = self.df.isnull().sum().sum()

            if missing == 0:

                return (
                    "Excellent dataset quality."
                )

            return (
                "Dataset contains missing values."
            )

        elif "machine learning" in q:

            return (
                "Recommended models include Random Forest, "
                "XGBoost and Gradient Boosting depending on "
                "your prediction target."
            )

        elif "business" in q:

            return (
                "The dataset can be used for dashboards, "
                "forecasting, customer segmentation, "
                "recommendation systems and predictive analytics."
            )

        else:

            return (
                "I don't understand that question yet. "
                "Try asking about summary, quality, "
                "missing values or machine learning."
            )