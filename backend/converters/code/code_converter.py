import os
import logging
from backend.converters.base import BaseConverter
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

logger = logging.getLogger("code_converter")

class CodeConverter(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        
        code_exts = [
            "py", "js", "json", "css", "html", "htm", "xml", "yaml", "yml", 
            "c", "cpp", "h", "hpp", "java", "cs", "go", "rs", "php", 
            "sh", "bat", "ps1", "sql", "kt", "swift", "rb", "pl"
        ]
        if from_ext in code_exts:
            return to_ext in ["pdf", "html"]
        return False

    def is_available(self) -> bool:
        return True

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        to_ext = os.path.splitext(output_path)[1].lower().strip('.')
        
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            code_text = f.read()

        # Determine language/lexer
        try:
            lexer = get_lexer_for_filename(input_path)
        except Exception:
            # Fall back to plain text lexer
            lexer = get_lexer_by_name("text")

        if to_ext == "html":
            return self._code_to_html(code_text, lexer, output_path)
        elif to_ext == "pdf":
            return self._code_to_pdf(code_text, lexer, output_path, os.path.basename(input_path))

        raise RuntimeError(f"Unsupported code conversion target: .{to_ext}")

    def _code_to_html(self, code_text: str, lexer, output_path: str) -> bool:
        # Generate styled HTML code output
        formatter = HtmlFormatter(full=True, style="monokai", linenos=True)
        html_content = highlight(code_text, lexer, formatter)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True

    def _code_to_pdf(self, code_text: str, lexer, output_path: str, filename: str) -> bool:
        # Uses ReportLab to generate a beautifully highlighted syntax PDF code printout
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from pygments.token import Token

        pdf = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        # Styles
        title_style = ParagraphStyle(
            'CodeTitle',
            parent=styles['Heading2'],
            fontName="Courier-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#111827'),
            backColor=colors.HexColor('#f3f4f6'),
            borderColor=colors.HexColor('#d1d5db'),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=12
        )

        line_style = ParagraphStyle(
            'CodeLine',
            fontName="Courier",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=0
        )

        story = []
        story.append(Paragraph(filename, title_style))
        
        # Color mapping from Pygments tokens to hex strings for ReportLab HTML parsing
        # Simple, high-readability VSCode/Light color scheme
        color_map = {
            Token.Comment: "#6a737d",
            Token.Comment.Multiline: "#6a737d",
            Token.Comment.Single: "#6a737d",
            Token.Keyword: "#d73a49",
            Token.Keyword.Declaration: "#d73a49",
            Token.Keyword.Namespace: "#d73a49",
            Token.Keyword.Pseudo: "#d73a49",
            Token.Keyword.Type: "#d73a49",
            Token.String: "#032f62",
            Token.String.Char: "#032f62",
            Token.String.Double: "#032f62",
            Token.String.Single: "#032f62",
            Token.Number: "#005cc5",
            Token.Name.Function: "#6f42c1",
            Token.Name.Class: "#e36209",
            Token.Name.Builtin: "#e36209",
            Token.Name.Variable: "#24292e",
            Token.Operator: "#d73a49",
            Token.Punctuation: "#24292e"
        }

        # Tokenize code line-by-line
        lines = code_text.splitlines()
        
        # Convert each line to colored HTML strings for ReportLab Paragraph
        for idx, line in enumerate(lines):
            # Pygments tokenize line
            tokens = list(lexer.get_tokens(line))
            line_html = f"<font color='#9ca3af'>{idx+1:4d} | </font>" # Line numbering
            
            for token_type, value in tokens:
                # Escape HTML special chars
                v_amp = value.replace("&", "&amp;")
                v_lt = v_amp.replace("<", "&lt;")
                v_gt = v_lt.replace(">", "&gt;")
                escaped_val = v_gt.replace(" ", "&nbsp;")
                
                # Check style
                color = "#24292e" # default
                # Find matching token type in hierarchy
                current_type = token_type
                while current_type:
                    if current_type in color_map:
                        color = color_map[current_type]
                        break
                    current_type = current_type.parent
                
                line_html += f"<font color='{color}'>{escaped_val}</font>"
            
            story.append(Paragraph(line_html, line_style))

        pdf.build(story)
        return True
