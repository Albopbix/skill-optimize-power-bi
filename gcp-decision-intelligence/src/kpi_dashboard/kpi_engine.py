import pandas as pd


class KPIEngine:

    def generate(self, df):

        numeric = df.select_dtypes(include="number")

        if numeric.empty:

            return None

        kpis = {

            "Rows": len(df),

            "Columns": len(df.columns),

            "Numeric Columns": len(numeric.columns),

            "Missing Values": int(df.isnull().sum().sum()),

            "Average": round(
                numeric.mean().mean(),
                2
            ),

            "Maximum": round(
                numeric.max().max(),
                2
            ),

            "Minimum": round(
                numeric.min().min(),
                2
            ),

            "Total Sum": round(
                numeric.sum().sum(),
                2
            )

        }

        return kpis