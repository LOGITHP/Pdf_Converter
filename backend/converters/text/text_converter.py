import os
import logging
from backend.converters.base import BaseConverter

logger = logging.getLogger("text_converter")

class TextConverter(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        
        txt_exts = ["txt", "log", "md", "rtf", "html", "xml", "json", "yaml", "yml"]
        if from_ext in txt_exts:
            return to_ext in ["pdf", "html", "txt"]
        return False

    def is_available(self) -> bool:
        return True

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        from_ext = os.path.splitext(input_path)[1].lower().strip('.')
        to_ext = os.path.splitext(output_path)[1].lower().strip('.')

        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if to_ext == "txt":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        if to_ext == "html":
            return self._text_to_html(content, from_ext, output_path)

        if to_ext == "pdf":
            if from_ext == "md":
                return self._markdown_to_pdf(content, output_path)
            else:
                return self._plain_text_to_pdf(content, output_path, os.path.basename(input_path))

        raise RuntimeError(f"Unsupported text conversion target: .{to_ext}")

    def _text_to_html(self, content: str, from_ext: str, output_path: str) -> bool:
        title = "Converted File"
        body_html = ""
        
        if from_ext == "md":
            # Optional markdown package
            try:
                import markdown
                body_html = markdown.markdown(content)
            except ImportError:
                # Custom basic markdown parser fallback
                body_html = self._basic_md_to_html(content)
        elif from_ext == "html":
            body_html = content
        else:
            # Escape text
            escaped = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
            body_html = f"<pre>{escaped}</pre>"

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; }}
        code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }}
        blockquote {{ border-left: 4px solid #047857; margin: 0; padding-left: 20px; font-style: italic; color: #555; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
    </style>
</head>
<body>
    {body_html}
</body>
</html>"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        return True

    def _basic_md_to_html(self, md_text: str) -> str:
        # A simple fallback markdown parser
        lines = md_text.splitlines()
        html_lines = []
        in_list = False
        in_code = False
        
        for line in lines:
            stripped = line.strip()
            
            # Code block
            if stripped.startswith("```"):
                in_code = not in_code
                if in_code:
                    html_lines.append("<pre><code>")
                else:
                    html_lines.append("</code></pre>")
                continue
                
            if in_code:
                html_lines.append(stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + "\n")
                continue

            # Headers
            if stripped.startswith("### "):
                html_lines.append(f"<h3>{stripped[4:]}</h3>")
            elif stripped.startswith("## "):
                html_lines.append(f"<h2>{stripped[3:]}</h2>")
            elif stripped.startswith("# "):
                html_lines.append(f"<h1>{stripped[2:]}</h1>")
            # Lists
            elif stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list:
                    in_list = True
                    html_lines.append("<ul>")
                html_lines.append(f"<li>{stripped[2:]}</li>")
            else:
                if in_list:
                    in_list = False
                    html_lines.append("</ul>")
                if stripped == "":
                    html_lines.append("<br/>")
                else:
                    html_lines.append(f"<p>{stripped}</p>")

        if in_list:
            html_lines.append("</ul>")

        return "".join(html_lines)

    def _plain_text_to_pdf(self, content: str, output_path: str, filename: str) -> bool:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        pdf = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TxtTitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=15
        )

        body_style = ParagraphStyle(
            'TxtBody',
            fontName="Courier",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=0
        )

        story = []
        story.append(Paragraph(filename, title_style))
        story.append(Spacer(1, 10))

        for line in content.splitlines():
            # Escape HTML characters for ReportLab Paragraph rendering
            escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
            if not escaped.strip():
                story.append(Spacer(1, 10))
            else:
                story.append(Paragraph(escaped, body_style))

        pdf.build(story)
        return True

    def _markdown_to_pdf(self, md_text: str, output_path: str) -> bool:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        pdf = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()

        h1_style = ParagraphStyle('MDH1', parent=styles['Heading1'], fontSize=20, leading=24, spaceBefore=12, spaceAfter=8, textColor=colors.HexColor('#047857'))
        h2_style = ParagraphStyle('MDH2', parent=styles['Heading2'], fontSize=16, leading=20, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor('#0f766e'))
        h3_style = ParagraphStyle('MDH3', parent=styles['Heading3'], fontSize=12, leading=16, spaceBefore=8, spaceAfter=4)
        body_style = ParagraphStyle('MDBody', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8)
        list_style = ParagraphStyle('MDList', parent=styles['Normal'], fontSize=10, leading=14, leftIndent=20, spaceAfter=4)
        code_style = ParagraphStyle('MDCode', fontName="Courier", fontSize=8, leading=10, backColor=colors.HexColor('#f3f4f6'), borderPadding=4, spaceAfter=8)

        story = []
        lines = md_text.splitlines()
        in_code = False
        code_buffer = []

        for line in lines:
            stripped = line.strip()
            
            # Code block toggle
            if stripped.startswith("```"):
                in_code = not in_code
                if not in_code and code_buffer:
                    code_text = "<br/>".join(code_buffer)
                    story.append(Paragraph(code_text, code_style))
                    code_buffer = []
                continue

            if in_code:
                escaped = stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                code_buffer.append(escaped)
                continue

            if stripped.startswith("### "):
                story.append(Paragraph(stripped[4:], h3_style))
            elif stripped.startswith("## "):
                story.append(Paragraph(stripped[3:], h2_style))
            elif stripped.startswith("# "):
                story.append(Paragraph(stripped[2:], h1_style))
            elif stripped.startswith("- ") or stripped.startswith("* "):
                story.append(Paragraph(f"• {stripped[2:]}", list_style))
            elif stripped == "":
                story.append(Spacer(1, 8))
            else:
                story.append(Paragraph(stripped, body_style))

        pdf.build(story)
        return True
