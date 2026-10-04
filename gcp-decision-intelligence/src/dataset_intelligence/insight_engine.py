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
            f"Tipo de dataset detectado: {self.dataset_type}"
        )

        # Compatibility
        if self.compatibility == "Compatible":
            insights.append(
                "O dataset é compatível com a Plataforma de Inteligência de Decisão com IA."
            )
        else:
            insights.append(
                "O dataset não é totalmente compatível. Faltam algumas colunas de negócio obrigatórias."
            )

        # Quality Score
        score = self.quality_report["Quality Score"]

        if score >= 90:
            insights.append(
                "Qualidade dos dados excelente. O dataset está pronto para Machine Learning."
            )

        elif score >= 75:
            insights.append(
                "Boa qualidade dos dados. Recomenda-se um pré-processamento leve."
            )

        else:
            insights.append(
                "Qualidade dos dados baixa. É necessária uma limpeza significativa."
            )

        # Missing Values
        if self.quality_report["Missing Values"] > 0:
            insights.append(
                f'O dataset contém {self.quality_report["Missing Values"]} valores ausentes.'
            )

        # Duplicate Rows
        if self.quality_report["Duplicate Rows"] == 0:
            insights.append(
                "Nenhum registro duplicado detectado."
            )
        else:
            insights.append(
                f'{self.quality_report["Duplicate Rows"]} linhas duplicadas detectadas.'
            )

        # Business Recommendations
        if self.dataset_type == "Dataset de E-commerce":

            insights.append(
                "Casos de uso de negócio recomendados:"
            )

            insights.append(
                "• Predição de churn de clientes"
            )

            insights.append(
                "• Predição de Lifetime Value (LTV) dos clientes"
            )

            insights.append(
                "• Segmentação de clientes"
            )

            insights.append(
                "• Recomendação de produtos"
            )

            insights.append(
                "• Previsão de vendas"
            )

        return insights