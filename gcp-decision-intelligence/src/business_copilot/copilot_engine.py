import pandas as pd


class BusinessCopilot:

    def __init__(self, dataframe):
        self.df = dataframe

    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    def executive_summary(self):

        return {
            "Rows": len(self.df),
            "Columns": len(self.df.columns),
            "Missing": int(self.df.isnull().sum().sum()),
            "Duplicates": int(self.df.duplicated().sum())
        }

    # =====================================================
    # BUSINESS HEALTH SCORE
    # =====================================================

    def business_score(self):

        missing = int(self.df.isnull().sum().sum())

        duplicates = int(self.df.duplicated().sum())

        score = 100

        score -= min(missing * 2, 30)

        score -= min(duplicates * 2, 20)

        return max(score, 0)

    # =====================================================
    # AI RECOMMENDATIONS
    # =====================================================

    def recommendations(self):

        recommendations = []

        if self.df.isnull().sum().sum() > 0:
            recommendations.append("Clean missing values.")

        if self.df.duplicated().sum() > 0:
            recommendations.append("Remove duplicate rows.")

        recommendations.append("Train AutoML model.")
        recommendations.append("Run Explainable AI.")
        recommendations.append("Run Business Forecast.")
        recommendations.append("Run Anomaly Detection.")
        recommendations.append("Generate Executive Report.")

        return recommendations

    # =====================================================
    # NEXT ACTIONS
    # =====================================================

    def next_actions(self):

        return self.recommendations()

    # =====================================================
    # ASK AI
    # =====================================================

    def ask(self, question):

        q = question.lower()

        if "row" in q:
            return f"The dataset contains {len(self.df):,} rows."

        elif "column" in q:
            return f"The dataset contains {len(self.df.columns)} columns."

        elif "missing" in q:
            return f"There are {self.df.isnull().sum().sum()} missing values."

        elif "duplicate" in q:
            return f"There are {self.df.duplicated().sum()} duplicate rows."

        elif "shape" in q:
            return self.df.shape

        elif "head" in q:
            return self.df.head()

        elif "tail" in q:
            return self.df.tail()

        elif "summary" in q:
            return self.df.describe(include="all")

        elif "correlation" in q:

            numeric = self.df.select_dtypes(include="number")

            if numeric.empty:
                return "No numeric columns available."

            return numeric.corr()

        elif "mean" in q or "average" in q:

            numeric = self.df.select_dtypes(include="number")

            if numeric.empty:
                return "No numeric columns available."

            return numeric.mean()

        elif "highest" in q or "maximum" in q:

            numeric = self.df.select_dtypes(include="number")

            if numeric.empty:
                return "No numeric columns available."

            return numeric.max()

        elif "lowest" in q or "minimum" in q:

            numeric = self.df.select_dtypes(include="number")

            if numeric.empty:
                return "No numeric columns available."

            return numeric.min()

        elif "health" in q:
            return f"Business Health Score: {self.business_score()}/100"

        elif "recommend" in q:
            return self.recommendations()

        else:

            return (
                "I can answer questions about:\n\n"
                "• Rows\n"
                "• Columns\n"
                "• Missing values\n"
                "• Duplicate rows\n"
                "• Dataset summary\n"
                "• Correlation\n"
                "• Mean values\n"
                "• Highest values\n"
                "• Lowest values\n"
                "• Business Health\n"
                "• AI Recommendations"
            )