import os
import json
import logging
from backend.converters.base import BaseConverter

logger = logging.getLogger("notebook_converter")

class NotebookConverter(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        
        if from_ext == "ipynb":
            return to_ext in ["pdf", "html", "md", "py"]
        return False

    def is_available(self) -> bool:
        try:
            import nbconvert
            import nbformat
            return True
        except ImportError:
            return False

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        to_ext = os.path.splitext(output_path)[1].lower().strip('.')
        
        # Load the notebook
        import nbformat
        with open(input_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        if to_ext == "py":
            return self._nb_to_python(nb, output_path)
        elif to_ext == "md":
            return self._nb_to_markdown(nb, output_path)
        elif to_ext == "html":
            return self._nb_to_html(nb, output_path)
        elif to_ext == "pdf":
            return self._nb_to_pdf(nb, output_path)

        raise RuntimeError(f"Unsupported notebook conversion: .ipynb -> .{to_ext}")

    def _nb_to_python(self, nb, output_path: str) -> bool:
        from nbconvert import PythonExporter
        exporter = PythonExporter()
        body, _ = exporter.from_notebook_node(nb)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(body)
        return True

    def _nb_to_markdown(self, nb, output_path: str) -> bool:
        from nbconvert import MarkdownExporter
        exporter = MarkdownExporter()
        body, _ = exporter.from_notebook_node(nb)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(body)
        return True

    def _nb_to_html(self, nb, output_path: str) -> bool:
        from nbconvert import HTMLExporter
        exporter = HTMLExporter()
        body, _ = exporter.from_notebook_node(nb)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(body)
        return True

    def _nb_to_pdf(self, nb, output_path: str) -> bool:
        from nbconvert import PDFExporter
        exporter = PDFExporter()
        try:
            # First try the standard nbconvert PDF exporter (requires pdflatex)
            body, _ = exporter.from_notebook_node(nb)
            with open(output_path, "wb") as f:
                f.write(body)
            return True
        except Exception as e:
            logger.warning(f"Standard LaTeX-based nbconvert PDF exporter failed: {e}. Falling back to ReportLab manual builder.")
            return self._nb_to_pdf_fallback(nb, output_path)

    def _nb_to_pdf_fallback(self, nb, output_path: str) -> bool:
        # Generates a styled, readable PDF of the Jupyter Notebook without LaTeX
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter

        pdf = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        # Styles
        title_style = ParagraphStyle(
            'NotebookTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#047857'),
            spaceAfter=15
        )

        md_style = ParagraphStyle(
            'NotebookMD',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=8
        )

        code_style = ParagraphStyle(
            'NotebookCode',
            parent=styles['Code'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1f2937'),
            backColor=colors.HexColor('#f3f4f6'),
            borderColor=colors.HexColor('#e5e7eb'),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=6
        )

        output_style = ParagraphStyle(
            'NotebookOutput',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#374151'),
            backColor=colors.HexColor('#f9fafb'),
            borderColor=colors.HexColor('#e5e7eb'),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=12
        )

        story = []
        story.append(Paragraph("Jupyter Notebook Export", title_style))
        story.append(Spacer(1, 10))

        cells = nb.get('cells', [])
        for cell in cells:
            cell_type = cell.get('cell_type')
            source = "".join(cell.get('source', []))
            if not source.strip():
                continue

            if cell_type == 'markdown':
                # Quick strip of raw markdown characters for basic readability in PDF
                clean_md = source.replace('#', '').strip()
                story.append(Paragraph(clean_md, md_style))
                story.append(Spacer(1, 5))
            
            elif cell_type == 'code':
                exec_count = cell.get('execution_count') or ' '
                story.append(Paragraph(f"In [{exec_count}]:", ParagraphStyle('InPrompt', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
                
                # Format code
                story.append(Paragraph(source.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

                # Outputs
                outputs = cell.get('outputs', [])
                for out in outputs:
                    out_type = out.get('output_type')
                    if out_type == 'stream':
                        text = "".join(out.get('text', []))
                        story.append(Paragraph(text.replace('\n', '<br/>').replace(' ', '&nbsp;'), output_style))
                    elif out_type in ['execute_result', 'display_data']:
                        data = out.get('data', {})
                        if 'text/plain' in data:
                            text = "".join(data['text/plain'])
                            story.append(Paragraph(text.replace('\n', '<br/>').replace(' ', '&nbsp;'), output_style))
                        if 'image/png' in data:
                            # Handle base64 image decoding and saving for rendering in PDF
                            import base64
                            from reportlab.platypus import Image as RLImage
                            from io import BytesIO
                            
                            img_data = base64.b64decode(data['image/png'])
                            img_buf = BytesIO(img_data)
                            
                            # Keep size reasonable (fit to letter width)
                            try:
                                rli = RLImage(img_buf, width=400, height=280)
                                rli.hAlign = 'CENTER'
                                story.append(rli)
                                story.append(Spacer(1, 10))
                            except Exception as img_err:
                                logger.error(f"Failed to embed notebook image in PDF: {img_err}")
                    elif out_type == 'error':
                        tb = "\n".join(out.get('traceback', []))
                        # Strip ANSI color codes
                        import re
                        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-9;]*[a-zA-Z])')
                        clean_tb = ansi_escape.sub('', tb)
                        error_style = ParagraphStyle(
                            'ErrorStyle',
                            parent=output_style,
                            textColor=colors.HexColor('#b91c1c'),
                            backColor=colors.HexColor('#fef2f2'),
                            borderColor=colors.HexColor('#fca5a5')
                        )
                        story.append(Paragraph(clean_tb.replace('\n', '<br/>').replace(' ', '&nbsp;'), error_style))

        pdf.build(story)
        return True
