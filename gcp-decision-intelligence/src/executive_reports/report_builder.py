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
                "Plataforma de Inteligência de Decisão com IA",
                self.title_style
            )
        )

        story.append(
            Paragraph(
                "Relatório Executivo de Negócios",
                self.heading
            )
        )

        story.append(Spacer(1, 0.3 * inch))

        # ============================================
        # EXECUTIVE SUMMARY
        # ============================================

        story.append(
            Paragraph(
                "Resumo Executivo",
                self.heading
            )
        )

        summary = f"""
        Este relatório resume a análise de IA realizada sobre o dataset enviado.

        Total de registros : {dataset_summary["Rows"]}

        Total de colunas : {dataset_summary["Columns"]}

        Valores ausentes : {dataset_summary["Missing"]}

        Linhas duplicadas : {dataset_summary["Duplicates"]}

        Score de saúde do negócio : {health_score}/100
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
                "Estatísticas do Dataset",
                self.heading
            )
        )

        table_data = [

            ["Métrica", "Valor"],

            ["Linhas", dataset_summary["Rows"]],

            ["Colunas", dataset_summary["Columns"]],

            ["Valores ausentes", dataset_summary["Missing"]],

            ["Linhas duplicadas", dataset_summary["Duplicates"]]

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
                "Score de Saúde do Negócio",
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
                "Resultados do AutoML",
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
                "Recomendações da IA",
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
                "Detecção de Anomalias com IA",
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
                "Conclusão Executiva",
                self.heading
            )
        )

        conclusion = """
        A Plataforma de Inteligência de Decisão com IA analisou o dataset com sucesso.

        O dataset é adequado para analytics de negócio e machine learning.

        Os tomadores de decisão devem usar as recomendações da IA, os modelos do AutoML,
        a detecção de anomalias, as previsões e os módulos de IA explicável
        para tomar melhores decisões de negócio.
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