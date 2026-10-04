class DashboardGenerator:

    def __init__(self, dataframe):

        self.df = dataframe

    def recommend_visualizations(self):

        recommendations = []

        numeric_columns = self.df.select_dtypes(include="number").columns

        categorical_columns = self.df.select_dtypes(include="object").columns

        datetime_columns = self.df.select_dtypes(
            include=["datetime64", "datetime64[ns]"]
        ).columns

        if len(numeric_columns) >= 1:
            recommendations.append(
                "Bar Chart"
            )

            recommendations.append(
                "Histogram"
            )

        if len(numeric_columns) >= 2:
            recommendations.append(
                "Correlation Heatmap"
            )

            recommendations.append(
                "Scatter Plot"
            )

        if len(categorical_columns) >= 1:
            recommendations.append(
                "Pie Chart"
            )

            recommendations.append(
                "Category Distribution"
            )

        if len(datetime_columns) >= 1:
            recommendations.append(
                "Time Series Trend"
            )

        recommendations.append(
            "KPI Cards"
        )

        return recommendations