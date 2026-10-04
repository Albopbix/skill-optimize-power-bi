class VisualizationRecommender:

    def __init__(self, dataframe):

        self.df = dataframe

    def recommend(self):

        recommendations = []

        numeric = self.df.select_dtypes(include="number").columns
        categorical = self.df.select_dtypes(include="object").columns

        if len(numeric) >= 2:
            recommendations.append(
                "📊 Mapa de Calor de Correlação"
            )

            recommendations.append(
                "📈 Gráfico de Dispersão"
            )

            recommendations.append(
                "📉 Histograma"
            )

        if len(categorical) >= 1:

            recommendations.append(
                "🥧 Gráfico de Pizza"
            )

            recommendations.append(
                "📊 Distribuição por Categoria"
            )

        for col in self.df.columns:

            name = col.lower()

            if (
                "date" in name
                or "time" in name
            ):

                recommendations.append(
                    "📅 Análise de Séries Temporais"
                )

            if (
                "city" in name
                or "country" in name
                or "state" in name
                or "region" in name
            ):

                recommendations.append(
                    "🌍 Dashboard Geográfico"
                )

        recommendations.append(
            "📌 Dashboard de KPIs"
        )

        return list(dict.fromkeys(recommendations))