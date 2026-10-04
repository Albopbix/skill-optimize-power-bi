class ModelRecommender:

    def recommend(self, model_name, score, problem_type):

        recommendations = []

        recommendations.append(
            f"🏆 Best Model Selected: {model_name}"
        )

        recommendations.append(
            f"Problem Type: {problem_type.title()}"
        )

        recommendations.append(
            f"Model Score: {round(score,2)}%"
        )

        if score >= 95:

            recommendations.append(
                "Excellent performance. Ready for deployment."
            )

        elif score >= 90:

            recommendations.append(
                "Very good performance. Minor tuning may improve results."
            )

        elif score >= 80:

            recommendations.append(
                "Good model. Consider feature engineering and hyperparameter tuning."
            )

        elif score >= 70:

            recommendations.append(
                "Model performance is acceptable. More training data is recommended."
            )

        else:

            recommendations.append(
                "Model accuracy is low. Improve data quality before deployment."
            )

        recommendations.append(
            "Perform cross-validation before production deployment."
        )

        recommendations.append(
            "Monitor model performance continuously after deployment."
        )

        recommendations.append(
            "Retrain periodically as new data becomes available."
        )

        return recommendations