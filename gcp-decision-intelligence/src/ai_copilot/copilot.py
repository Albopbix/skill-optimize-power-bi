import pandas as pd


class AICopilot:

    def __init__(self, dataframe):

        self.df = dataframe

    def answer(self, question):

        question = question.lower()

        if "rows" in question:

            return f"The dataset contains {len(self.df)} rows."

        elif "columns" in question:

            return f"The dataset contains {len(self.df.columns)} columns."

        elif "missing" in question:

            return f"Missing values: {self.df.isnull().sum().sum()}"

        elif "duplicate" in question:

            return f"Duplicate rows: {self.df.duplicated().sum()}"

        elif "shape" in question:

            return str(self.df.shape)

        else:

            return (
                "I understand the dataset, but I cannot answer "
                "that question yet. More AI capabilities will be added."
            )