class VisualizationRecommender:

    def __init__(self, dataframe):

        self.df = dataframe

    def recommend(self):

        recommendations = []

        numeric = self.df.select_dtypes(include="number").columns
        categorical = self.df.select_dtypes(include="object").columns

        if len(numeric) >= 2:
            recommendations.append(
                "📊 Correlation Heatmap"
            )

            recommendations.append(
                "📈 Scatter Plot"
            )

            recommendations.append(
                "📉 Histogram"
            )

        if len(categorical) >= 1:

            recommendations.append(
                "🥧 Pie Chart"
            )

            recommendations.append(
                "📊 Category Distribution"
            )

        for col in self.df.columns:

            name = col.lower()

            if (
                "date" in name
                or "time" in name
            ):

                recommendations.append(
                    "📅 Time Series Analysis"
                )

            if (
                "city" in name
                or "country" in name
                or "state" in name
                or "region" in name
            ):

                recommendations.append(
                    "🌍 Geographic Dashboard"
                )

        recommendations.append(
            "📌 KPI Dashboard"
        )

        return list(dict.fromkeys(recommendations))