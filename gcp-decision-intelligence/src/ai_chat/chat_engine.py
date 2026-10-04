import pandas as pd


class ChatEngine:

    def ask(self, df, question):

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