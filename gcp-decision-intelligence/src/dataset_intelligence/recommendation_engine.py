class RecommendationEngine:

    def __init__(self, dataset_type):

        self.dataset_type = dataset_type

    def recommend(self):

        recommendations = {

            "Dataset de E-commerce": [
                "Predição de churn de clientes",
                "Segmentação de clientes",
                "Sistema de recomendação de produtos",
                "Previsão de vendas",
                "Predição de Lifetime Value (LTV) dos clientes"
            ],

            "Dataset de Saúde": [
                "Predição de doenças",
                "Predição de readmissão de pacientes",
                "Otimização de recursos hospitalares",
                "Análise de risco médico"
            ],

            "Dataset de Trânsito": [
                "Predição de congestionamentos",
                "Detecção de pontos críticos de acidentes",
                "Otimização de rotas"
            ],

            "Dataset Desconhecido": [
                "O dataset precisa de mais análise antes que recomendações de IA possam ser geradas."
            ]
        }

        return recommendations.get(
            self.dataset_type,
            recommendations["Dataset Desconhecido"]
        )

