import logging

import pandas as pd

from src.llm import gemini_client


logger = logging.getLogger(__name__)


class BusinessCopilot:

    def __init__(self, dataframe):
        self.df = dataframe
        self.last_engine = None
        self.last_error = None

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
            recommendations.append("Trate os valores ausentes.")

        if self.df.duplicated().sum() > 0:
            recommendations.append("Remova as linhas duplicadas.")

        recommendations.append("Treine um modelo no AutoML.")
        recommendations.append("Execute a IA explicável.")
        recommendations.append("Execute a previsão de negócios.")
        recommendations.append("Execute a detecção de anomalias.")
        recommendations.append("Gere o relatório executivo.")

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

        self.last_error = None

        if gemini_client.is_enabled():

            try:
                answer = gemini_client.ask(question, self.df)
                self.last_engine = "gemini"
                return answer

            except Exception as error:
                # Sem Vertex AI disponível, cai para o motor de regras.
                logger.warning("Gemini failed, using rules: %s", error)
                self.last_error = str(error)

        self.last_engine = "rules"

        return self.ask_rules(question)

    def ask_rules(self, question):

        q = question.lower()

        def has(*words):
            return any(word in q for word in words)

        def numeric_or_message():
            numeric = self.df.select_dtypes(include="number")
            return numeric, "Não há colunas numéricas disponíveis."

        if has("missing", "ausente", "faltante", "nulo", "vazio"):
            return f"Total de valores ausentes: {self.df.isnull().sum().sum():,}."

        elif has("duplicate", "duplicad"):
            return f"Total de linhas duplicadas: {self.df.duplicated().sum():,}."

        elif has("row", "linha", "registro"):
            return f"O dataset contém {len(self.df):,} linhas."

        elif has("column", "coluna", "variáve", "variave"):
            return f"O dataset contém {len(self.df.columns)} colunas."

        elif has("shape", "formato", "dimens"):
            return self.df.shape

        elif has("head", "primeir", "início", "inicio"):
            return self.df.head()

        elif has("tail", "últim", "ultim", "final"):
            return self.df.tail()

        elif has("summary", "resum", "describe", "descrev"):
            return self.df.describe(include="all")

        elif has("correlation", "correla"):

            numeric, message = numeric_or_message()

            if numeric.empty:
                return message

            return numeric.corr()

        elif has("mean", "average", "média", "media"):

            numeric, message = numeric_or_message()

            if numeric.empty:
                return message

            return numeric.mean()

        elif has("highest", "maximum", "maior", "máxim", "maxim"):

            numeric, message = numeric_or_message()

            if numeric.empty:
                return message

            return numeric.max()

        elif has("lowest", "minimum", "menor", "mínim", "minim"):

            numeric, message = numeric_or_message()

            if numeric.empty:
                return message

            return numeric.min()

        elif has("health", "saúde", "saude"):
            return f"Score de Saúde do Negócio: {self.business_score()}/100"

        elif has("recommend", "recomend"):
            return self.recommendations()

        else:

            return (
                "Posso responder perguntas sobre:\n\n"
                "• Linhas\n"
                "• Colunas\n"
                "• Valores ausentes\n"
                "• Linhas duplicadas\n"
                "• Resumo do dataset\n"
                "• Correlação\n"
                "• Médias\n"
                "• Maiores valores\n"
                "• Menores valores\n"
                "• Saúde do negócio\n"
                "• Recomendações da IA"
            )
