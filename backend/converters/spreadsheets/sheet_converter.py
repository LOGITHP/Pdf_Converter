import os
import subprocess
import logging
import pandas as pd
from backend.converters.base import BaseConverter
from backend.utils.sys_info import get_libreoffice_path

logger = logging.getLogger("sheet_converter")

class SheetConverter(BaseConverter):
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        from_ext = from_ext.lower().strip('.')
        to_ext = to_ext.lower().strip('.')
        
        if from_ext in ["xlsx", "xls", "csv", "ods"]:
            return to_ext in ["pdf", "csv", "xlsx"]
        return False

    def is_available(self) -> bool:
        return True

    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        from_ext = os.path.splitext(input_path)[1].lower().strip('.')
        to_ext = os.path.splitext(output_path)[1].lower().strip('.')

        # If converting XLSX/XLS/ODS/CSV to CSV (or vice versa) without PDF, we can do it natively in Python
        if to_ext == "csv" and from_ext in ["xlsx", "xls", "ods", "csv"]:
            return self._sheet_to_csv(input_path, output_path)
        if to_ext == "xlsx" and from_ext == "csv":
            return self._csv_to_xlsx(input_path, output_path)

        # Check for LibreOffice (best quality for PDF)
        lo_path = get_libreoffice_path()
        if lo_path and to_ext == "pdf":
            return self._convert_with_libreoffice(lo_path, input_path, output_path)

        # Fallback PDF conversion if LibreOffice is missing
        if to_ext == "pdf":
            logger.warning("LibreOffice not detected. Using ReportLab + Pandas Excel PDF fallback.")
            return self._sheet_to_pdf_fallback(input_path, output_path)

        raise RuntimeError(f"Unsupported spreadsheet conversion: .{from_ext} -> .{to_ext}")

    def _convert_with_libreoffice(self, lo_path: str, input_path: str, output_path: str) -> bool:
        logger.info(f"Converting sheet to PDF using LibreOffice: {input_path}")
        out_dir = os.path.dirname(output_path)
        
        cmd = [
            lo_path,
            "--headless",
            "--convert-to",
            "pdf:calc_pdf_Export",
            "--outdir",
            out_dir,
            input_path
        ]
        
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            if result.returncode != 0:
                logger.error(f"LibreOffice failed: {result.stderr}")
                raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")

            in_basename = os.path.basename(input_path)
            in_name_no_ext = os.path.splitext(in_basename)[0]
            lo_output_path = os.path.join(out_dir, f"{in_name_no_ext}.pdf")

            if os.path.exists(lo_output_path) and os.path.abspath(lo_output_path) != os.path.abspath(output_path):
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(lo_output_path, output_path)
                return True
            elif os.path.exists(output_path):
                return True
            else:
                raise FileNotFoundError(f"LibreOffice output not found at {lo_output_path}")
        except subprocess.TimeoutExpired:
            logger.error("LibreOffice calculation conversion timed out.")
            raise RuntimeError("LibreOffice calculation conversion timed out.")

    def _sheet_to_csv(self, input_path: str, output_path: str) -> bool:
        from_ext = os.path.splitext(input_path)[1].lower().strip('.')
        if from_ext == "csv":
            # Just copy the file
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        # Read Excel/ODS sheet
        engine = "openpyxl" if from_ext == "xlsx" else ("odf" if from_ext == "ods" else None)
        df = pd.read_excel(input_path, engine=engine)
        df.to_csv(output_path, index=False)
        return True

    def _csv_to_xlsx(self, input_path: str, output_path: str) -> bool:
        df = pd.read_csv(input_path)
        df.to_excel(output_path, index=False, engine="openpyxl")
        return True

    def _sheet_to_pdf_fallback(self, input_path: str, output_path: str) -> bool:
        from_ext = os.path.splitext(input_path)[1].lower().strip('.')
        
        # Read using pandas
        if from_ext == "csv":
            df = pd.read_csv(input_path)
        else:
            engine = "openpyxl" if from_ext == "xlsx" else ("odf" if from_ext == "ods" else None)
            df = pd.read_excel(input_path, engine=engine)

        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        # Setup standard document in landscape for sheet layouts
        pdf = SimpleDocTemplate(output_path, pagesize=landscape(letter), leftMargin=15, rightMargin=15, topMargin=15, bottomMargin=15)
        styles = getSampleStyleSheet()
        
        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontSize=8,
            leading=10
        )
        
        header_style = ParagraphStyle(
            'HeaderCellText',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.white
        )

        data = []
        
        # Header Row
        headers = [Paragraph(str(col), header_style) for col in df.columns]
        data.append(headers)

        # Max 200 rows for fallback to prevent huge PDFs
        max_rows = min(len(df), 200)
        for i in range(max_rows):
            row_data = []
            for val in df.iloc[i]:
                row_data.append(Paragraph(str(val) if pd.notna(val) else "", cell_style))
            data.append(row_data)

        story = []
        story.append(Paragraph(f"Spreadsheet Export: {os.path.basename(input_path)}", styles['Heading2']))
        story.append(Spacer(1, 10))

        if data:
            # Table automatically divides horizontal space
            num_cols = len(data[0])
            col_width = (pdf.width) / num_cols
            t = Table(data, colWidths=[col_width] * num_cols)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#047857')), # Green header
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t)
            if len(df) > 200:
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"... truncated {len(df) - 200} rows for layout formatting ...", styles['Normal']))

        pdf.build(story)
        return True
