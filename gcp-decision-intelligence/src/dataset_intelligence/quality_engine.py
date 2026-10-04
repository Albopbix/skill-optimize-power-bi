import pandas as pd


class QualityEngine:

    def __init__(self, dataframe):

        self.df = dataframe

    def generate_quality_report(self):

        total_rows = len(self.df)

        total_columns = len(self.df.columns)

        missing_values = int(self.df.isnull().sum().sum())

        duplicate_rows = int(self.df.duplicated().sum())

        total_cells = total_rows * total_columns

        missing_percentage = round(
            (missing_values / total_cells) * 100,
            2
        )

        duplicate_percentage = round(
            (duplicate_rows / total_rows) * 100,
            2
        )

        quality_score = 100

        quality_score -= min(missing_percentage * 2, 40)

        quality_score -= min(duplicate_percentage * 2, 30)

        quality_score = max(round(quality_score), 0)

        if quality_score >= 90:
            grade = "A"

        elif quality_score >= 75:
            grade = "B"

        elif quality_score >= 60:
            grade = "C"

        else:
            grade = "D"

        return {

            "Quality Score": quality_score,

            "Grade": grade,

            "Rows": total_rows,

            "Columns": total_columns,

            "Missing Values": missing_values,

            "Duplicate Rows": duplicate_rows,

            "Missing %": missing_percentage,

            "Duplicate %": duplicate_percentage
        }