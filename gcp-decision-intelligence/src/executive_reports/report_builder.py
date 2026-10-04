from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


class ExecutiveReportBuilder:

    def __init__(self):

        self.styles = getSampleStyleSheet()

        self.title_style = self.styles["Heading1"]
        self.title_style.alignment = TA_CENTER

        self.heading = self.styles["Heading2"]

        self.normal = self.styles["BodyText"]

    def generate(
        self,
        filename,
        dataset_summary,
        health_score,
        automl_result,
        recommendations,
        anomaly_summary
    ):

        doc = SimpleDocTemplate(filename)

        story = []

        # ============================================
        # TITLE
        # ============================================

        story.append(
            Paragraph(
                "AI-Driven Decision Intelligence Platform",
                self.title_style
            )
        )

        story.append(
            Paragraph(
                "Executive Business Report",
                self.heading
            )
        )

        story.append(Spacer(1, 0.3 * inch))

        # ============================================
        # EXECUTIVE SUMMARY
        # ============================================

        story.append(
            Paragraph(
                "Executive Summary",
                self.heading
            )
        )

        summary = f"""
        This report summarizes the AI analysis performed on the uploaded dataset.

        Total Records : {dataset_summary["Rows"]}

        Total Columns : {dataset_summary["Columns"]}

        Missing Values : {dataset_summary["Missing"]}

        Duplicate Rows : {dataset_summary["Duplicates"]}

        Business Health Score : {health_score}/100
        """

        story.append(
            Paragraph(
                summary,
                self.normal
            )
        )

        story.append(Spacer(1, 0.25 * inch))

        # ============================================
        # DATASET TABLE
        # ============================================

        story.append(
            Paragraph(
                "Dataset Statistics",
                self.heading
            )
        )

        table_data = [

            ["Metric", "Value"],

            ["Rows", dataset_summary["Rows"]],

            ["Columns", dataset_summary["Columns"]],

            ["Missing Values", dataset_summary["Missing"]],

            ["Duplicate Rows", dataset_summary["Duplicates"]]

        ]

        table = Table(table_data)

        table.setStyle(

            TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                ("GRID", (0, 0), (-1, -1), 1, colors.black),

                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

                ("BOTTOMPADDING", (0, 0), (-1, 0), 10)

            ])

        )

        story.append(table)

        story.append(Spacer(1, 0.3 * inch))

        # ============================================
        # BUSINESS HEALTH
        # ============================================

        story.append(
            Paragraph(
                "Business Health Score",
                self.heading
            )
        )

        story.append(
            Paragraph(
                f"<b>{health_score}/100</b>",
                self.normal
            )
        )

        story.append(Spacer(1, 0.3 * inch))

        # ============================================
        # AUTOML
        # ============================================

        story.append(
            Paragraph(
                "AutoML Results",
                self.heading
            )
        )

        story.append(
            Paragraph(
                automl_result,
                self.normal
            )
        )

        story.append(Spacer(1, 0.3 * inch))

        # ============================================
        # AI RECOMMENDATIONS
        # ============================================

        story.append(
            Paragraph(
                "AI Recommendations",
                self.heading
            )
        )

        for rec in recommendations:

            story.append(
                Paragraph(
                    "• " + rec,
                    self.normal
                )
            )

        story.append(Spacer(1, 0.3 * inch))

        # ============================================
        # ANOMALY SUMMARY
        # ============================================

        story.append(
            Paragraph(
                "AI Anomaly Detection",
                self.heading
            )
        )

        story.append(
            Paragraph(
                anomaly_summary,
                self.normal
            )
        )

        story.append(Spacer(1, 0.3 * inch))

        # ============================================
        # CONCLUSION
        # ============================================

        story.append(
            Paragraph(
                "Executive Conclusion",
                self.heading
            )
        )

        conclusion = """
        The AI-Driven Decision Intelligence Platform successfully analyzed the dataset.

        The dataset is suitable for business analytics and machine learning.

        Decision-makers should use the AI recommendations, AutoML models,
        anomaly detection, forecasting, and explainable AI modules
        for better business decisions.
        """

        story.append(
            Paragraph(
                conclusion,
                self.normal
            )
        )

        # ============================================
        # BUILD PDF
        # ============================================

        doc.build(story)

        return filename