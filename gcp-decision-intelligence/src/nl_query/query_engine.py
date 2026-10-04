import pandas as pd


class QueryEngine:

    def __init__(self, dataframe):

        self.df = dataframe

    def execute(self, query):

        query = query.lower()

        if "top 10" in query:

            return self.df.head(10)

        elif "columns" in query:

            return pd.DataFrame({
                "Columns": self.df.columns
            })

        elif "missing values" in query:

            return pd.DataFrame(
                self.df.isnull().sum(),
                columns=["Missing Values"]
            )

        elif "describe" in query:

            return self.df.describe()

        elif "shape" in query:

            return pd.DataFrame({
                "Rows":[self.df.shape[0]],
                "Columns":[self.df.shape[1]]
            })

        else:

            return "Query not understood yet."