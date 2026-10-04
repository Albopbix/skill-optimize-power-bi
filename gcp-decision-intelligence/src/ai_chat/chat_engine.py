import logging

import pandas as pd

from src.llm import gemini_client


logger = logging.getLogger(__name__)


class ChatEngine:

    def __init__(self):
        self.last_engine = None
        self.last_error = None

    def ask(self, df, question, history=None):

        self.last_error = None

        if gemini_client.is_enabled():

            try:
                answer = gemini_client.ask(question, df, history=history)
                self.last_engine = "gemini"
                return answer

            except Exception as error:
                # Sem Vertex AI disponível, cai para o motor de regras.
                logger.warning("Gemini failed, using rules: %s", error)
                self.last_error = str(error)

        self.last_engine = "rules"

        return self.ask_rules(df, question)

    def ask_rules(self, df, question):

        q = question.lower()

        def has(*words):
            return any(word in q for word in words)

        if has("missing", "ausente", "faltante", "nulo"):

            return str(df.isnull().sum())

        elif has("rows", "linhas", "registros"):

            return f"O dataset contém {len(df):,} linhas."

        elif has("columns", "colunas"):

            return f"O dataset contém {len(df.columns)} colunas."

        elif has("describe", "summar", "resum", "descrev"):

            return str(df.describe(include="all"))

        elif has("head", "primeir"):

            return str(df.head())

        elif has("tail", "últim", "ultim"):

            return str(df.tail())

        elif has("average", "mean", "média", "media"):

            return str(df.mean(numeric_only=True))

        elif has("maximum", "máxim", "maxim", "maior"):

            return str(df.max(numeric_only=True))

        elif has("minimum", "mínim", "minim", "menor"):

            return str(df.min(numeric_only=True))

        else:

            return (
                "Ainda não entendi a pergunta. Com o Gemini desligado, "
                "consigo responder sobre linhas, colunas, valores ausentes, "
                "resumo estatístico, primeiras/últimas linhas, médias, "
                "máximos e mínimos."
            )
