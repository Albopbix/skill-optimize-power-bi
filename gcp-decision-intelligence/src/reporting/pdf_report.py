from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


class PDFReportGenerator:

    def generate(self, report_text, filename):

        doc = SimpleDocTemplate(filename)

        styles = getSampleStyleSheet()

        story = []

        for line in report_text.split("\n"):

            story.append(
                Paragraph(line, styles["BodyText"])
            )

        doc.build(story)