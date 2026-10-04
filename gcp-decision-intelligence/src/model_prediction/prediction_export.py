import pandas as pd


class PredictionExporter:

    def export_csv(

        self,

        dataframe,

        filename="Predictions.csv"

    ):

        dataframe.to_csv(

            filename,

            index=False

        )

        return filename