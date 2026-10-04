import plotly.express as px


class PredictionVisualizer:

    def histogram(

        self,

        dataframe,

        column

    ):

        return px.histogram(

            dataframe,

            x=column,

            title="Prediction Distribution"

        )

    def pie(

        self,

        dataframe,

        column

    ):

        counts = dataframe[column].value_counts()

        return px.pie(

            names=counts.index,

            values=counts.values,

            title="Prediction Distribution"

        )

    def bar(

        self,

        dataframe,

        column

    ):

        counts = dataframe[column].value_counts()

        return px.bar(

            x=counts.index,

            y=counts.values,

            title="Prediction Counts"

        )