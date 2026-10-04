class ModelRecommender:

    def recommend(self, model_name, score, problem_type):

        recommendations = []

        recommendations.append(
            f"🏆 Melhor modelo selecionado: {model_name}"
        )

        recommendations.append(
            f"Tipo de problema: {problem_type.title()}"
        )

        recommendations.append(
            f"Score do modelo: {round(score,2)}%"
        )

        if score >= 95:

            recommendations.append(
                "Desempenho excelente. Pronto para produção."
            )

        elif score >= 90:

            recommendations.append(
                "Desempenho muito bom. Ajustes finos podem melhorar os resultados."
            )

        elif score >= 80:

            recommendations.append(
                "Bom modelo. Considere engenharia de variáveis e ajuste de hiperparâmetros."
            )

        elif score >= 70:

            recommendations.append(
                "Desempenho aceitável. Recomenda-se mais dados de treino."
            )

        else:

            recommendations.append(
                "Acurácia baixa. Melhore a qualidade dos dados antes de colocar em produção."
            )

        recommendations.append(
            "Faça validação cruzada antes de colocar em produção."
        )

        recommendations.append(
            "Monitore o desempenho do modelo continuamente após a implantação."
        )

        recommendations.append(
            "Retreine periodicamente conforme novos dados forem chegando."
        )

        return recommendations