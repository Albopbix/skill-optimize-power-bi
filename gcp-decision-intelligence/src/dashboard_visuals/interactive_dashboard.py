import plotly.express as px


class InteractiveDashboard:

    def bar_chart(self, df, x, y):

        return px.bar(
            df,
            x=x,
            y=y,
            title=f"{y} by {x}"
        )

    def pie_chart(self, df, names, values):

        return px.pie(
            df,
            names=names,
            values=values,
            title=f"{names} Distribution"
        )

    def histogram(self, df, column):

        return px.histogram(
            df,
            x=column,
            title=column
        )

    def scatter(self, df, x, y):

        return px.scatter(
            df,
            x=x,
            y=y,
            title=f"{x} vs {y}"
        )

    def heatmap(self, corr):

        return px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Blues"
        )