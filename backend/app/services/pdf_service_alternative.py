"""
PDF Generation Service (Alternative - using reportlab/xhtml2pdf)
Generates PDF documents from SOAP notes without WeasyPrint dependencies
"""

import logging
from io import BytesIO
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF documents from consultation data"""

    def __init__(self):
        logger.info("📄 PDFService initialized (using reportlab)")

    def generate_consultation_pdf(
        self,
        consultation_data: Dict[str, Any]
    ) -> BytesIO:
        """
        Generate PDF from consultation data using reportlab
        
        Args:
            consultation_data: Dictionary containing consultation information
            
        Returns:
            BytesIO: PDF file as bytes
        """
        try:
            # Extract data
            patient_name = consultation_data.get("patient_name", "N/A")
            language = consultation_data.get("language", "ta")
            language_display = "Tamil" if language == "ta" else "Telugu"
            created_at = consultation_data.get("created_at", "")
            completed_at = consultation_data.get("completed_at", "")
            
            # Extract transcript
            transcript = consultation_data.get("transcript", {})
            if isinstance(transcript, dict):
                transcript_text = transcript.get("full_text", transcript.get("text", "No transcript available"))
            else:
                transcript_text = str(transcript) if transcript else "No transcript available"
            
            # Extract SOAP note
            soap_note = consultation_data.get("soap_note", {})
            if isinstance(soap_note, dict):
                soap_markdown = soap_note.get("markdown", "")
                if not soap_markdown:
                    # Build from sections
                    sections = []
                    if soap_note.get("subjective"):
                        sections.append(f"## Subjective\n{soap_note['subjective']}")
                    if soap_note.get("objective"):
                        sections.append(f"## Objective\n{soap_note['objective']}")
                    if soap_note.get("assessment"):
                        sections.append(f"## Assessment\n{soap_note['assessment']}")
                    if soap_note.get("plan"):
                        sections.append(f"## Plan\n{soap_note['plan']}")
                    soap_markdown = "\n\n".join(sections)
            else:
                soap_markdown = str(soap_note) if soap_note else "No SOAP note available"
            
            # Extract entities
            entities = consultation_data.get("entities", {})
            entities_text = ""
            if entities:
                entities_text = "Extracted Entities:\n"
                if entities.get("symptoms"):
                    entities_text += f"Symptoms: {', '.join(entities['symptoms'])}\n"
                if entities.get("medications"):
                    entities_text += f"Medications: {', '.join(entities['medications'])}\n"
                if entities.get("diagnoses"):
                    entities_text += f"Diagnoses: {', '.join(entities['diagnoses'])}\n"
            
            # Extract ICD codes
            icd_codes = consultation_data.get("icd_codes", [])
            icd_text = ""
            if icd_codes:
                icd_text = f"ICD-10 Codes: {', '.join(icd_codes)}"
            
            # Create PDF using reportlab
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=12,
                spaceBefore=12,
            )
            normal_style = styles['Normal']
            
            # Title
            elements.append(Paragraph("Medical Consultation Report", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Patient Info
            info_text = f"""
            <b>Patient:</b> {patient_name}<br/>
            <b>Language:</b> {language_display}<br/>
            <b>Created:</b> {created_at}<br/>
            """
            if completed_at:
                info_text += f"<b>Completed:</b> {completed_at}<br/>"
            
            elements.append(Paragraph(info_text, normal_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Transcript
            elements.append(Paragraph("Transcript", heading_style))
            # Escape HTML and preserve line breaks
            transcript_escaped = transcript_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
            elements.append(Paragraph(transcript_escaped, normal_style))
            elements.append(Spacer(1, 0.2*inch))
            elements.append(PageBreak())
            
            # SOAP Note
            elements.append(Paragraph("SOAP Note", heading_style))
            # Parse markdown-style SOAP note
            soap_lines = soap_markdown.split('\n')
            for line in soap_lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('##'):
                    # Heading
                    heading_text = line.replace('##', '').strip()
                    elements.append(Paragraph(f"<b>{heading_text}</b>", heading_style))
                elif line.startswith('-'):
                    # List item
                    item_text = line.replace('-', '').strip()
                    elements.append(Paragraph(f"• {item_text}", normal_style))
                else:
                    elements.append(Paragraph(line, normal_style))
            
            elements.append(Spacer(1, 0.2*inch))
            
            # Entities
            if entities_text:
                elements.append(Paragraph("Extracted Entities", heading_style))
                entities_escaped = entities_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
                elements.append(Paragraph(entities_escaped, normal_style))
                elements.append(Spacer(1, 0.2*inch))
            
            # ICD Codes
            if icd_text:
                elements.append(Paragraph(icd_text, normal_style))
                elements.append(Spacer(1, 0.2*inch))
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("<i>Generated by MedScribe AI</i>", ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
            elements.append(Paragraph("<i>This document is for medical use only.</i>", ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            logger.info(f"✅ PDF generated successfully using reportlab")
            return buffer
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {str(e)}", exc_info=True)
            raise Exception(f"PDF generation failed: {str(e)}")


pdf_service = PDFService()

