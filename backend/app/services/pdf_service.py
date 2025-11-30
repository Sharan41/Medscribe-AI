"""
PDF Generation Service
Generates PDF documents from SOAP notes
"""

import logging
import os
from io import BytesIO
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Set library paths for WeasyPrint (macOS)
# These need to be set before importing weasyprint
if 'DYLD_LIBRARY_PATH' not in os.environ:
    os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/lib:/usr/local/opt/glib/lib:/usr/local/opt/pango/lib:/usr/local/opt/cairo/lib'
if 'PKG_CONFIG_PATH' not in os.environ:
    os.environ['PKG_CONFIG_PATH'] = '/usr/local/lib/pkgconfig:/usr/local/opt/glib/lib/pkgconfig:/usr/local/opt/pango/lib/pkgconfig:/usr/local/opt/cairo/lib/pkgconfig'
if 'GI_TYPELIB_PATH' not in os.environ:
    os.environ['GI_TYPELIB_PATH'] = '/usr/local/lib/girepository-1.0'

# Try WeasyPrint first, fallback to reportlab
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
    USE_REPORTLAB = False
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)
    # Fallback to reportlab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
        USE_REPORTLAB = True
        logger.info("Using reportlab as PDF generator (WeasyPrint unavailable)")
    except ImportError:
        USE_REPORTLAB = False
        logger.error("Neither WeasyPrint nor reportlab available for PDF generation")


class PDFService:
    """Service for generating PDF documents from consultation data"""

    def __init__(self):
        if WEASYPRINT_AVAILABLE:
            logger.info("📄 PDFService initialized (using WeasyPrint)")
        elif USE_REPORTLAB:
            logger.info("📄 PDFService initialized (using reportlab)")
        else:
            logger.warning(f"⚠️ PDFService initialized but no PDF library available: {WEASYPRINT_ERROR}")

    def generate_consultation_pdf(
        self,
        consultation_data: Dict[str, Any]
    ) -> BytesIO:
        """
        Generate PDF from consultation data
        
        Args:
            consultation_data: Dictionary containing consultation information
            
        Returns:
            BytesIO: PDF file as bytes
        """
        # Use reportlab if WeasyPrint unavailable
        if not WEASYPRINT_AVAILABLE:
            if USE_REPORTLAB:
                return self._generate_with_reportlab(consultation_data)
            else:
                raise Exception(f"PDF generation unavailable: {WEASYPRINT_ERROR}. Please install reportlab: pip install reportlab")
        
        try:
            # Extract data
            patient_name = consultation_data.get("patient_name", "N/A")
            language = consultation_data.get("language", "ta")
            language_display = "Tamil" if language == "ta" else "Telugu"
            created_at = consultation_data.get("created_at", "")
            completed_at = consultation_data.get("completed_at", "")
            
            # Skip transcript - only show SOAP note in English
            transcript_text = None  # Don't include transcript in PDF
            
            # Extract SOAP note and remove Tamil text/translations
            soap_note = consultation_data.get("soap_note", {})
            logger.debug(f"SOAP note type: {type(soap_note)}, value: {str(soap_note)[:200]}...")
            
            # Handle case where SOAP note might be a flattened string
            if isinstance(soap_note, str):
                # Check if it's flattened markdown (has ## but no line breaks)
                if "##" in soap_note and "\n" not in soap_note:
                    # Reconstruct markdown with proper line breaks
                    soap_note = self._reconstruct_markdown(soap_note)
                    soap_note = {"markdown": soap_note}
            
            if isinstance(soap_note, dict):
                soap_markdown = soap_note.get("markdown", "")
                # Check if markdown is flattened (has ## but no line breaks)
                if soap_markdown and "##" in soap_markdown and "\n" not in soap_markdown:
                    logger.info("Detected flattened markdown, reconstructing...")
                    soap_markdown = self._reconstruct_markdown(soap_markdown)
                if not soap_markdown:
                    # Build from sections with proper bullet point formatting
                    sections = []
                    if soap_note.get("subjective"):
                        subjective_text = self._remove_tamil_text(soap_note['subjective'])
                        formatted_subjective = self._convert_to_bullet_points(subjective_text)
                        sections.append(f"## Subjective\n{formatted_subjective}")
                    if soap_note.get("objective"):
                        objective_text = self._remove_tamil_text(soap_note['objective'])
                        formatted_objective = self._convert_to_bullet_points(objective_text)
                        sections.append(f"## Objective\n{formatted_objective}")
                    if soap_note.get("assessment"):
                        assessment_text = self._remove_tamil_text(soap_note['assessment'])
                        formatted_assessment = self._convert_to_bullet_points(assessment_text)
                        sections.append(f"## Assessment\n{formatted_assessment}")
                    if soap_note.get("plan"):
                        plan_text = self._remove_tamil_text(soap_note['plan'])
                        formatted_plan = self._convert_to_bullet_points(plan_text)
                        sections.append(f"## Plan\n{formatted_plan}")
                    soap_markdown = "\n\n".join(sections)
                else:
                    # Remove Tamil text from markdown and ensure proper formatting
                    soap_markdown = self._remove_tamil_text(soap_markdown)
                    soap_markdown = self._ensure_bullet_points(soap_markdown)
            elif isinstance(soap_note, str):
                # If SOAP note is a string, check if it needs conversion
                soap_markdown = self._remove_tamil_text(soap_note)
                # Check if it looks like plain text with " - " separators
                if " - " in soap_markdown and not soap_markdown.strip().startswith("##"):
                    # Convert to proper markdown format
                    soap_markdown = self._ensure_bullet_points(soap_markdown)
                else:
                    soap_markdown = self._ensure_bullet_points(soap_markdown)
            else:
                soap_markdown = "No SOAP note available"
            
            # Extract entities
            entities = consultation_data.get("entities", {})
            entities_html = ""
            if entities:
                entities_html = "<h3>Extracted Entities</h3>"
                if entities.get("symptoms"):
                    entities_html += f"<p><strong>Symptoms:</strong> {', '.join(entities['symptoms'])}</p>"
                if entities.get("medications"):
                    entities_html += f"<p><strong>Medications:</strong> {', '.join(entities['medications'])}</p>"
                if entities.get("diagnoses"):
                    entities_html += f"<p><strong>Diagnoses:</strong> {', '.join(entities['diagnoses'])}</p>"
            
            # Extract ICD codes
            icd_codes = consultation_data.get("icd_codes", [])
            icd_html = ""
            if icd_codes:
                icd_html = f"<p><strong>ICD-10 Codes:</strong> {', '.join(icd_codes)}</p>"
            
            # Convert markdown to HTML (simple conversion)
            soap_html = self._markdown_to_html(soap_markdown)
            
            # Build HTML document
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Consultation Report - {patient_name}</title>
                <style>
                    body {{
                        font-family: 'DejaVu Sans', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    h1 {{
                        color: #2563eb;
                        border-bottom: 3px solid #2563eb;
                        padding-bottom: 10px;
                    }}
                    h2 {{
                        color: #1e40af;
                        margin-top: 30px;
                        border-bottom: 2px solid #e5e7eb;
                        padding-bottom: 5px;
                    }}
                    h3 {{
                        color: #3b82f6;
                        margin-top: 20px;
                    }}
                    .header {{
                        margin-bottom: 30px;
                    }}
                    .info {{
                        background-color: #f3f4f6;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .transcript {{
                        background-color: #f9fafb;
                        padding: 15px;
                        border-left: 4px solid #3b82f6;
                        margin: 20px 0;
                        white-space: pre-wrap;
                        font-family: 'DejaVu Sans', monospace;
                    }}
                    .soap-note {{
                        background-color: #f9fafb;
                        padding: 15px;
                        border-left: 4px solid #10b981;
                        margin: 20px 0;
                    }}
                    .entities {{
                        background-color: #eff6ff;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    ul {{
                        margin-left: 20px;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                    .footer {{
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                        color: #6b7280;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Medical Consultation Report</h1>
                    <div class="info">
                        <p><strong>Patient:</strong> {patient_name}</p>
                        <p><strong>Language:</strong> {language_display}</p>
                        <p><strong>Created:</strong> {created_at}</p>
                        {f'<p><strong>Completed:</strong> {completed_at}</p>' if completed_at else ''}
                    </div>
                </div>
                
                <h2>SOAP Note</h2>
                <div class="soap-note">
                    {soap_html}
                </div>
                
                {f'<div class="entities">{entities_html}</div>' if entities_html else ''}
                {f'<div class="entities">{icd_html}</div>' if icd_html else ''}
                
                <div class="footer">
                    <p>Generated by MedScribe AI</p>
                    <p>This document is for medical use only.</p>
                </div>
            </body>
            </html>
            """
            
            # Generate PDF
            font_config = FontConfiguration()
            html = HTML(string=html_content)
            pdf_bytes = BytesIO()
            html.write_pdf(pdf_bytes, font_config=font_config)
            pdf_bytes.seek(0)
            
            logger.info(f"✅ PDF generated successfully for consultation")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {str(e)}", exc_info=True)
            raise Exception(f"PDF generation failed: {str(e)}")

    def _generate_with_reportlab(self, consultation_data: Dict[str, Any]) -> BytesIO:
        """
        Generate PDF using reportlab (fallback when WeasyPrint unavailable)
        
        Args:
            consultation_data: Dictionary containing consultation information
            
        Returns:
            BytesIO: PDF file as bytes
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, ListFlowable, ListItem
            from reportlab.lib.units import inch
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.enums import TA_LEFT
            
            # Register Unicode-supporting fonts for Tamil/Telugu
            # Try to use system fonts that support Indic scripts
            tamil_font_name = None
            try:
                # Get the backend directory (go up from app/services/pdf_service.py -> app/services -> app -> backend)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                app_dir = os.path.dirname(script_dir)  # app/
                backend_dir = os.path.dirname(app_dir)  # backend/
                # Use Tamil MN (extracted from system TTC) to match web app's system font appearance
                local_tamil_font = os.path.join(backend_dir, 'fonts', 'TamilMN-Regular.ttf')
                local_telugu_font = os.path.join(backend_dir, 'fonts', 'NotoSansTelugu-Regular.ttf')
                # Fallback to Noto Sans Tamil if Tamil MN not available
                fallback_tamil_font = os.path.join(backend_dir, 'fonts', 'NotoSansTamil-Regular.ttf')
                
                # Try common system fonts that support Tamil/Telugu
                # Note: macOS has .ttc files which don't work with reportlab
                # Priority: Local downloaded fonts > System TTF fonts > Fallback
                # Determine which font to use based on language
                language = consultation_data.get("language", "ta")
                if language == "te":  # Telugu
                    font_paths = [
                        local_telugu_font,  # Local downloaded Noto Sans Telugu TTF
                        '/System/Library/Fonts/Supplemental/NotoSansTelugu-Regular.ttf',
                        '/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf',
                    ]
                else:  # Tamil (default)
                    font_paths = [
                        local_tamil_font,  # Tamil MN Regular (extracted from system TTC) - matches web app!
                        fallback_tamil_font,  # Fallback to Noto Sans Tamil if Tamil MN not available
                        '/System/Library/Fonts/Supplemental/NotoSansTamil-Regular.ttf',
                        '/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf',
                        '/Library/Fonts/NotoSansTamil-Regular.ttf',
                    ]
                # Note: Skipping .ttc files as they don't work with reportlab
                
                font_registry_name = 'IndicFont'  # Generic name for Tamil/Telugu
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            pdfmetrics.registerFont(TTFont(font_registry_name, font_path))
                            tamil_font_name = font_registry_name
                            lang_name = "Telugu" if language == "te" else "Tamil"
                            # Use print as well to ensure it shows in console
                            print(f"✅ Registered {lang_name} font: {font_path}", flush=True)
                            logger.info(f"✅ Registered {lang_name} font: {font_path}")
                            break
                        except Exception as e:
                            error_msg = str(e)
                            # Check if file is HTML (corrupted download)
                            if "version=0x0A0A0A0A" in error_msg or "not a recognized" in error_msg.lower():
                                logger.warning(f"Font file appears corrupted (HTML?): {font_path}")
                                # Try to remove corrupted file
                                try:
                                    if os.path.exists(font_path):
                                        with open(font_path, 'rb') as f:
                                            header = f.read(100)
                                            if b'<!DOCTYPE' in header or b'<html' in header:
                                                logger.warning(f"Removing corrupted HTML file: {font_path}")
                                                os.remove(font_path)
                                except:
                                    pass
                            else:
                                logger.warning(f"Could not register font {font_path}: {e}")
                            # Try next font
                            continue
                
                # If no Tamil-specific font found, try DejaVu Sans which has good Unicode support
                if not tamil_font_name:
                    try:
                        dejavu_paths = [
                            '/System/Library/Fonts/Supplemental/DejaVuSans.ttf',
                            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                        ]
                        for font_path in dejavu_paths:
                            if os.path.exists(font_path):
                                pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                                tamil_font_name = 'UnicodeFont'
                                logger.info(f"✅ Registered Unicode font: {font_path}")
                                break
                    except Exception as e:
                        logger.warning(f"Could not register DejaVu font: {e}")
                
            except Exception as e:
                logger.warning(f"Font registration failed: {e}. Tamil text may not render properly.")
            
            # Use standard Helvetica font - no Tamil text in PDF
            base_font = 'Helvetica'
            
            # Extract data - English only, no Tamil text
            patient_name = consultation_data.get("patient_name", "N/A")
            language = consultation_data.get("language", "ta")
            language_display = "Tamil" if language == "ta" else "Telugu"
            created_at = consultation_data.get("created_at", "")
            completed_at = consultation_data.get("completed_at", "")
            
            # Skip transcript - only show SOAP note in English
            transcript_text = None  # Don't include transcript in PDF
            
            # Extract SOAP note and remove Tamil text/translations
            soap_note = consultation_data.get("soap_note", {})
            logger.debug(f"SOAP note type: {type(soap_note)}, value: {str(soap_note)[:200]}...")
            
            # Handle case where SOAP note might be a flattened string
            if isinstance(soap_note, str):
                # Check if it's flattened markdown (has ## but no line breaks)
                if "##" in soap_note and "\n" not in soap_note:
                    # Reconstruct markdown with proper line breaks
                    soap_note = self._reconstruct_markdown(soap_note)
                    soap_note = {"markdown": soap_note}
            
            if isinstance(soap_note, dict):
                soap_markdown = soap_note.get("markdown", "")
                # Check if markdown is flattened (has ## but no line breaks)
                if soap_markdown and "##" in soap_markdown and "\n" not in soap_markdown:
                    logger.info("Detected flattened markdown, reconstructing...")
                    soap_markdown = self._reconstruct_markdown(soap_markdown)
                if not soap_markdown:
                    # Build from sections with proper bullet point formatting
                    sections = []
                    if soap_note.get("subjective"):
                        subjective_text = self._remove_tamil_text(soap_note['subjective'])
                        formatted_subjective = self._convert_to_bullet_points(subjective_text)
                        sections.append(f"## Subjective\n{formatted_subjective}")
                    if soap_note.get("objective"):
                        objective_text = self._remove_tamil_text(soap_note['objective'])
                        formatted_objective = self._convert_to_bullet_points(objective_text)
                        sections.append(f"## Objective\n{formatted_objective}")
                    if soap_note.get("assessment"):
                        assessment_text = self._remove_tamil_text(soap_note['assessment'])
                        formatted_assessment = self._convert_to_bullet_points(assessment_text)
                        sections.append(f"## Assessment\n{formatted_assessment}")
                    if soap_note.get("plan"):
                        plan_text = self._remove_tamil_text(soap_note['plan'])
                        formatted_plan = self._convert_to_bullet_points(plan_text)
                        sections.append(f"## Plan\n{formatted_plan}")
                    soap_markdown = "\n\n".join(sections)
                else:
                    # Remove Tamil text from markdown and ensure proper formatting
                    soap_markdown = self._remove_tamil_text(soap_markdown)
                    soap_markdown = self._ensure_bullet_points(soap_markdown)
            elif isinstance(soap_note, str):
                # If SOAP note is a string, check if it needs conversion
                soap_markdown = self._remove_tamil_text(soap_note)
                # Check if it looks like plain text with " - " separators
                if " - " in soap_markdown and not soap_markdown.strip().startswith("##"):
                    # Convert to proper markdown format
                    soap_markdown = self._ensure_bullet_points(soap_markdown)
                else:
                    soap_markdown = self._ensure_bullet_points(soap_markdown)
            else:
                soap_markdown = "No SOAP note available"
            
            # Extract entities
            entities = consultation_data.get("entities", {})
            entities_text = ""
            if entities:
                entity_parts = []
                if entities.get("symptoms"):
                    entity_parts.append(f"<b>Symptoms:</b> {', '.join(entities['symptoms'])}")
                if entities.get("medications"):
                    entity_parts.append(f"<b>Medications:</b> {', '.join(entities['medications'])}")
                if entities.get("diagnoses"):
                    entity_parts.append(f"<b>Diagnoses:</b> {', '.join(entities['diagnoses'])}")
                entities_text = "<br/>".join(entity_parts)
            
            # Extract ICD codes
            icd_codes = consultation_data.get("icd_codes", [])
            icd_text = ""
            if icd_codes:
                icd_text = f"<b>ICD-10 Codes:</b> {', '.join(icd_codes)}"
            
            # Create PDF buffer
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=72)
            
            # Container for the 'Flowable' objects
            story = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
                fontName=base_font,
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold',  # Bold for better visibility
                alignment=TA_LEFT,
            )
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                backColor=colors.HexColor('#f3f4f6'),
                leftIndent=12,
                rightIndent=12,
                spaceAfter=12,
                textColor=colors.black,
                alignment=TA_LEFT,
                fontName=base_font,
            )
            
            normal_style = ParagraphStyle(
                'NormalStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                alignment=TA_LEFT,
                fontName=base_font,
            )
            transcript_style = ParagraphStyle(
                'TranscriptStyle',
                parent=styles['Normal'],
                fontSize=10,
                leading=12,
                fontName=base_font,  # Use Unicode-supporting font
                backColor=colors.HexColor('#f9fafb'),
                leftIndent=12,
                rightIndent=12,
                spaceAfter=12,
                alignment=TA_LEFT,
                wordWrap='CJK',  # Better text wrapping for Indic scripts
            )
            soap_style = ParagraphStyle(
                'SOAPStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,  # Increased leading for better readability
                fontName=base_font,  # Use Unicode-supporting font
                backColor=colors.HexColor('#f9fafb'),
                leftIndent=0,  # No indent - handled by ListFlowable
                rightIndent=12,
                spaceAfter=6,
                spaceBefore=4,
                alignment=TA_LEFT,
                wordWrap='CJK',  # Better text wrapping for Indic scripts
            )
            
            # Title
            story.append(Paragraph("Medical Consultation Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Patient info
            info_html = f"""
            <b>Patient:</b> {patient_name}<br/>
            <b>Language:</b> {language_display}<br/>
            <b>Created:</b> {created_at}
            """
            if completed_at:
                info_html += f"<br/><b>Completed:</b> {completed_at}"
            
            story.append(Paragraph(info_html, info_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Skip transcript section - only show SOAP note
            
            # SOAP Note Section
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph("SOAP Note", heading_style))
            story.append(Spacer(1, 0.15*inch))
            
            if soap_markdown and soap_markdown.strip():
                # CRITICAL: Normalize markdown FIRST (handles flattened format completely)
                logger.info(f"SOAP markdown BEFORE normalization (first 300 chars): {soap_markdown[:300]}")
                soap_markdown = self._normalize_soap_markdown(soap_markdown)
                logger.info(f"SOAP markdown AFTER normalization (first 300 chars): {soap_markdown[:300]}")
                
                # Process SOAP note with proper formatting (bullet points and sections)
                self._add_soap_note_to_story(story, soap_markdown, soap_style, normal_style)
            else:
                story.append(Paragraph("No SOAP note available", soap_style))
            story.append(Spacer(1, 0.25*inch))
            
            # Entities
            if entities_text:
                story.append(Paragraph("Extracted Entities", heading_style))
                story.append(Paragraph(entities_text, normal_style))
                story.append(Spacer(1, 0.2*inch))
            
            # ICD Codes
            if icd_text:
                story.append(Paragraph(icd_text, normal_style))
                story.append(Spacer(1, 0.2*inch))
            
            # Footer
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("<i>Generated by MedScribe AI</i>", normal_style))
            story.append(Paragraph("<i>This document is for medical use only.</i>", normal_style))
            
            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)
            
            logger.info(f"✅ PDF generated successfully for consultation (using reportlab)")
            return pdf_buffer
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed (reportlab): {str(e)}", exc_info=True)
            raise Exception(f"PDF generation failed: {str(e)}")

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML (simple implementation)"""
        html = markdown
        
        # Headers
        html = html.replace("## ", "<h3>").replace("\n", "</h3>\n", 1)
        html = html.replace("## ", "<h3>")
        html = html.replace("### ", "<h4>")
        
        # Lists
        lines = html.split("\n")
        result = []
        in_list = False
        
        for line in lines:
            if line.strip().startswith("- "):
                if not in_list:
                    result.append("<ul>")
                    in_list = True
                result.append(f"<li>{line.strip()[2:]}</li>")
            else:
                if in_list:
                    result.append("</ul>")
                    in_list = False
                if line.strip():
                    result.append(f"<p>{line}</p>")
        
        if in_list:
            result.append("</ul>")
        
        return "\n".join(result)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#x27;")
        )
    
    def _convert_to_bullet_points(self, text: str) -> str:
        """
        Convert plain text to markdown bullet points.
        Handles text with " - " separators and converts to bullet list format.
        """
        if not text or not text.strip():
            return ""
        
        logger.debug(f"Converting to bullet points: {text[:100]}...")
        
        # Split by " - " or " -" or "- " to handle various formats
        import re
        # Split by common separators (dash with spaces, periods followed by dash, etc.)
        items = re.split(r'\s*-\s+|\s*\.\s*-\s*', text)
        
        # Clean up items and filter empty ones
        bullet_items = []
        for item in items:
            item = item.strip()
            if item:
                # Remove trailing periods if they're separators
                item = item.rstrip('.')
                if item:
                    bullet_items.append(f"- {item}")
        
        # If no bullets were created, check if it's already a single item
        if not bullet_items:
            # Check if text already has bullet points
            if text.strip().startswith("-"):
                return text.strip()
            # Otherwise, treat as single bullet point
            return f"- {text.strip()}"
        
        return "\n".join(bullet_items)
    
    def _ensure_bullet_points(self, markdown: str) -> str:
        """
        Ensure markdown has proper bullet point formatting.
        Converts plain text lines to bullet points where appropriate.
        """
        if not markdown:
            return ""
        
        lines = markdown.split("\n")
        result = []
        in_section = False
        current_section_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Keep headers as-is
            if stripped.startswith("##"):
                # Process any accumulated section lines before header
                if current_section_lines:
                    result.extend(self._process_section_lines(current_section_lines))
                    current_section_lines = []
                
                in_section = True
                result.append(line)
                continue
            
            # Skip empty lines (but preserve them)
            if not stripped:
                if current_section_lines:
                    # Process accumulated lines before empty line
                    result.extend(self._process_section_lines(current_section_lines))
                    current_section_lines = []
                result.append("")
                continue
            
            # Accumulate section content
            if in_section:
                current_section_lines.append(stripped)
            else:
                result.append(line)
        
        # Process any remaining section lines
        if current_section_lines:
            result.extend(self._process_section_lines(current_section_lines))
        
        return "\n".join(result)
    
    def _process_section_lines(self, lines: list) -> list:
        """Process lines within a section and convert to bullet points."""
        result = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # If already a bullet point (starts with "- "), keep as-is
            if stripped.startswith("- "):
                result.append(stripped)  # Already formatted correctly
            # If contains " - " separator, split into bullets
            elif " - " in stripped:
                items = stripped.split(" - ")
                for item in items:
                    item = item.strip()
                    if item:
                        # Remove trailing periods that are separators
                        item = item.rstrip('.')
                        if item:
                            result.append(f"- {item}")
            # Single item, convert to bullet
            else:
                result.append(f"- {stripped}")
        
        return result
    
    def _reconstruct_markdown(self, flattened_text: str) -> str:
        """
        Reconstruct markdown from flattened text.
        Handles cases where markdown headers (##) appear inline without line breaks.
        Example: "Subjective - text ## Objective - text" -> "## Subjective\ntext\n\n## Objective\ntext"
        """
        if not flattened_text:
            return ""
        
        import re
        
        # Split by ## headers, keeping the headers
        parts = re.split(r'(##\s+\w+)', flattened_text)
        
        sections = []
        current_header = None
        current_content = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if this is a header (starts with ##)
            if part.startswith("##"):
                # Save previous section
                if current_header or current_content:
                    if current_header:
                        sections.append(f"{current_header}\n" + "\n".join(current_content))
                    elif current_content:
                        # First section without header - add "## Subjective" if it looks like subjective
                        first_line = current_content[0] if current_content else ""
                        if "Subjective" in first_line or not current_header:
                            sections.append(f"## Subjective\n" + "\n".join(current_content))
                        else:
                            sections.append("\n".join(current_content))
                
                # Start new section
                current_header = part
                current_content = []
            else:
                # This is content
                content = part.strip()
                
                # Handle first section: "Subjective - Abdominal pain"
                # Remove "Subjective" prefix if present and no header set
                if not current_header and content.startswith("Subjective"):
                    # Remove "Subjective" and the following " - "
                    content = re.sub(r'^Subjective\s*-\s*', '', content)
                
                # Remove leading dash if it's a separator
                if content.startswith("- "):
                    content = content[2:].strip()
                elif content.startswith("-"):
                    content = content[1:].strip()
                
                if content:
                    current_content.append(content)
        
        # Add last section
        if current_header or current_content:
            if current_header:
                sections.append(f"{current_header}\n" + "\n".join(current_content))
            else:
                # Handle first section without header
                if sections:
                    # Prepend to first section
                    first_section = sections[0]
                    if not first_section.startswith("##"):
                        sections[0] = f"## Subjective\n{first_section}"
                else:
                    sections.append("## Subjective\n" + "\n".join(current_content))
        
        return "\n\n".join(sections)
    
    def _remove_tamil_text(self, text: str) -> str:
        """
        Remove Tamil text and translations from SOAP note.
        Removes text in brackets that contains Tamil characters.
        """
        if not text:
            return text
        
        import re
        # Remove Tamil text in brackets like [இருமல்], [தொண்டை வலி]
        # Pattern matches [ followed by Tamil characters and ]
        tamil_pattern = r'\[[^\]]*[\u0B80-\u0BFF][^\]]*\]'
        text = re.sub(tamil_pattern, '', text)
        
        # Remove standalone Tamil text (Tamil Unicode range: 0B80-0BFF)
        # Keep only ASCII and common punctuation
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove lines that are mostly Tamil
            tamil_chars = sum(1 for c in line if '\u0B80' <= c <= '\u0BFF')
            if tamil_chars < len(line) * 0.5:  # Keep line if less than 50% Tamil
                # Remove Tamil characters but keep the line structure
                cleaned_line = ''.join(c for c in line if not ('\u0B80' <= c <= '\u0BFF'))
                cleaned_lines.append(cleaned_line)
        
        result = '\n'.join(cleaned_lines)
        # Clean up extra spaces and brackets
        result = re.sub(r'\s+', ' ', result)  # Multiple spaces to single
        result = re.sub(r'\s*\[\s*\]\s*', '', result)  # Empty brackets
        result = re.sub(r'\s+', ' ', result)  # Clean up again
        return result.strip()
    
    def _escape_html_for_reportlab(self, text: str) -> str:
        """Escape HTML special characters for reportlab (handles newlines)"""
        if not text:
            return ""
        # First escape HTML special characters
        escaped = (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
        )
        # Convert newlines to <br/> for reportlab
        # Also handle multiple consecutive newlines
        escaped = escaped.replace("\n\n\n", "<br/><br/>")
        escaped = escaped.replace("\n\n", "<br/><br/>")
        escaped = escaped.replace("\n", "<br/>")
        return escaped
    
    def _add_soap_note_to_story(self, story, markdown: str, soap_style, normal_style):
        """
        Completely rewritten SOAP note rendering with proper formatting.
        Handles flattened format and ensures bullet points render correctly.
        """
        from reportlab.platypus import ListFlowable, ListItem, Spacer
        from reportlab.lib.units import inch
        from reportlab.lib.styles import ParagraphStyle
        import re
        
        if not markdown:
            return
        
        # First, normalize the markdown - handle flattened format
        normalized_markdown = self._normalize_soap_markdown(markdown)
        logger.info(f"Normalized SOAP markdown (first 200 chars): {normalized_markdown[:200]}")
        
        # Create styles
        header_style = ParagraphStyle(
            'SOAPHeader',
            parent=normal_style,
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor='#1e40af',  # Blue to match PDF
            spaceAfter=6,
            spaceBefore=12,
            leftIndent=0,
        )
        
        bullet_style = ParagraphStyle(
            'SOAPBullet',
            parent=soap_style,
            fontSize=11,
            leading=16,
            leftIndent=0,
            rightIndent=0,
            spaceAfter=3,
        )
        
        # Parse markdown into sections
        lines = normalized_markdown.split("\n")
        current_section = None
        current_bullets = []
        
        for line in lines:
            stripped = line.strip()
            
            # Empty line - close current section if needed
            if not stripped:
                if current_bullets:
                    self._add_bullet_list(story, current_bullets, bullet_style)
                    current_bullets = []
                continue
            
            # Header line (## Subjective, etc.)
            if stripped.startswith("##"):
                # Close previous section
                if current_bullets:
                    self._add_bullet_list(story, current_bullets, bullet_style)
                    current_bullets = []
                
                # Add spacing before new section (except first)
                if current_section is not None:
                    story.append(Spacer(1, 0.2*inch))
                
                # Extract header text
                header_text = re.sub(r'^##\s*', '', stripped).strip()
                header_para = Paragraph(f"<b>{header_text}</b>", header_style)
                story.append(header_para)
                story.append(Spacer(1, 0.12*inch))
                
                current_section = header_text
                continue
            
            # Bullet point line
            if stripped.startswith("- "):
                bullet_text = stripped[2:].strip()
                if bullet_text:
                    current_bullets.append(bullet_text)
                continue
            
            # Regular text line - convert to bullet if needed
            if stripped:
                # If it contains " - ", split into bullets
                if " - " in stripped:
                    items = stripped.split(" - ")
                    for item in items:
                        item = item.strip()
                        if item:
                            item = item.rstrip('.')
                            if item:
                                current_bullets.append(item)
                else:
                    # Single item as bullet
                    current_bullets.append(stripped)
        
        # Close last section
        if current_bullets:
            self._add_bullet_list(story, current_bullets, bullet_style)
    
    def _add_bullet_list(self, story, bullet_items, bullet_style):
        """Helper to add a bullet list to the story with proper bullet rendering"""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        
        if not bullet_items:
            return
        
        # Create a style with left indent for bullet points
        bullet_para_style = ParagraphStyle(
            'BulletPoint',
            parent=bullet_style,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6,
        )
        
        for item in bullet_items:
            item_text = item.strip()
            if item_text:
                # Remove any "bullet" text that might have been added incorrectly
                item_text = item_text.replace("bullet", "").strip()
                if item_text:
                    # Use Unicode bullet character (•) for reliable rendering
                    bullet_text = f"• {item_text}"
                    para = Paragraph(bullet_text, bullet_para_style)
                    story.append(para)
        
        # Add spacing after the list
        story.append(Spacer(1, 0.08*inch))
    
    def _normalize_soap_markdown(self, markdown: str) -> str:
        """
        Normalize SOAP markdown - handles flattened format and ensures proper structure.
        This is the key function that fixes the flattened format issue.
        """
        if not markdown:
            return ""
        
        import re
        
        # Check if markdown is flattened (has ## but no line breaks)
        is_flattened = "##" in markdown and "\n" not in markdown
        
        if not is_flattened:
            # Already has line breaks, just ensure bullet points
            return self._ensure_bullet_points(markdown)
        
        # Handle flattened format: "Subjective - text ## Objective - text"
        logger.info("Detected flattened markdown format, reconstructing...")
        
        # Split by ## headers
        parts = re.split(r'\s*##\s+', markdown)
        
        sections = []
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            
            # First section might start with "Subjective" without ##
            if i == 0:
                if part.startswith("Subjective"):
                    # Remove "Subjective" prefix
                    content = re.sub(r'^Subjective\s*-\s*', '', part)
                    header = "## Subjective"
                else:
                    # Assume it's Subjective section
                    header = "## Subjective"
                    content = part
            else:
                # Split header name and content
                # Format: "Objective - content" or just "Objective"
                if " - " in part:
                    header_name, content = part.split(" - ", 1)
                    header = f"## {header_name.strip()}"
                    content = content.strip()
                else:
                    # No content separator, treat whole thing as header
                    header = f"## {part.strip()}"
                    content = ""
            
            # Convert content to bullet points
            if content:
                # Split by " - " to get individual items
                items = content.split(" - ")
                bullets = []
                for item in items:
                    item = item.strip()
                    if item:
                        # Remove trailing periods that are separators
                        item = item.rstrip('.')
                        if item:
                            bullets.append(f"- {item}")
                
                if bullets:
                    sections.append(f"{header}\n" + "\n".join(bullets))
                else:
                    sections.append(f"{header}\n- {content}")
            else:
                sections.append(header)
        
        result = "\n\n".join(sections)
        logger.info(f"Reconstructed markdown (first 300 chars): {result[:300]}")
        return result
    
    def _markdown_to_reportlab_html(self, markdown: str) -> str:
        """Convert markdown to reportlab-compatible HTML (for simple cases)"""
        if not markdown:
            return ""
        
        lines = markdown.split("\n")
        result = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Headers
            if stripped.startswith("## "):
                result.append(f"<b>{stripped[3:].strip()}</b>")
            elif stripped.startswith("### "):
                result.append(f"<b>{stripped[4:].strip()}</b>")
            # Bullet points
            elif stripped.startswith("- "):
                result.append(f"• {stripped[2:].strip()}")
            else:
                result.append(stripped)
        
        return "<br/>".join(result)


pdf_service = PDFService()

