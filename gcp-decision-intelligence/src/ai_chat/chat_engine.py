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

        if "rows" in q:

            return f"The dataset contains {len(df)} rows."

        elif "columns" in q:

            return f"The dataset contains {len(df.columns)} columns."

        elif "missing" in q:

            return str(df.isnull().sum())

        elif "describe" in q:

            return str(df.describe(include="all"))

        elif "head" in q:

            return str(df.head())

        elif "tail" in q:

            return str(df.tail())

        elif "average" in q:

            return str(df.mean(numeric_only=True))

        elif "maximum" in q:

            return str(df.max(numeric_only=True))

        elif "minimum" in q:

            return str(df.min(numeric_only=True))

        else:

            return "I don't understand the question yet."