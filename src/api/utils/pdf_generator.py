import json
from io import BytesIO

import markdown
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf(data):
    # Extract the original input and results from the data
    original_input = data["original_input"]
    results = data["results"]

    # Create a new PDF document
    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    # Create a list to hold the PDF elements
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    heading_style = styles["Heading1"]
    heading_style.textColor = colors.HexColor("#2C3E50")  # Dark Blue
    heading_style.fontSize = 24
    heading_style.spaceAfter = 20
    heading_style.alignment = 1  # Center alignment

    subheading_style = styles["Heading2"]
    subheading_style.textColor = colors.HexColor("#E74C3C")  # Red
    subheading_style.fontSize = 18
    subheading_style.spaceBefore = 20
    subheading_style.spaceAfter = 10

    normal_style = styles["Normal"]
    normal_style.fontSize = 12
    normal_style.spaceAfter = 10

    code_style = styles["Code"]
    code_style.fontSize = 12
    code_style.spaceAfter = 20

    # Add a title to the document
    title = Paragraph(f"{original_input} Recipes and Techniques", heading_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5 * inch))

    # Add a table of contents
    toc_data = [["Category", "Subcategory", "Page"]]
    toc_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498DB")),  # Blue
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),  # Light Gray
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("ALIGN", (0, 1), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 12),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ]
    )

    page_counter = 1
    for result in results:
        category = result["category"]
        subcategory = result["subcategory"]
        toc_data.append([category.capitalize(), subcategory.capitalize(), page_counter])
        page_counter += 1

    toc_table = Table(toc_data)
    toc_table.setStyle(toc_style)
    elements.append(toc_table)
    elements.append(PageBreak())

    # Iterate over each result and add it to the PDF
    for result in results:
        category = result["category"]
        subcategory = result["subcategory"]
        preamble = result["preamble"]
        search_query = result["search_query"]
        response = result["response"]

        # Add category and subcategory
        category_text = f"{category.capitalize()} - {subcategory.capitalize()}"
        elements.append(Paragraph(category_text, subheading_style))

        # Add preamble and search query
        elements.append(Paragraph(f"<b>Preamble:</b> {preamble}", normal_style))
        elements.append(Paragraph(f"<b>Search Query:</b> {search_query}", normal_style))

        # Add the response answer
        if isinstance(response, dict) and "Answer" in response:
            answer = response["Answer"]
            # Convert Markdown to HTML and replace newlines with <br/> tags
            html_answer = markdown.markdown(answer.replace("\n", "<br/>"))
            elements.append(Paragraph("<b>Answer:</b>", normal_style))
            elements.append(Paragraph(html_answer, normal_style))

            # Add a horizontal line separator
            line_separator = Table([[""]], colWidths=["100%"], rowHeights=[1])
            line_separator.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor("#E67E22"),
                        ),  # Orange
                        ("LINEWIDTH", (0, 0), (-1, -1), 1),
                        ("LINESTYLE", (0, 0), (-1, -1), 0),  # Solid line
                    ]
                )
            )
            elements.append(line_separator)
            elements.append(PageBreak())
        else:
            continue

    # Build the PDF document
    doc.build(elements, canvasmaker=Canvas)
    pdf_content = output.getvalue()
    output.close()
    return pdf_content
