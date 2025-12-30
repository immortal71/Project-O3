"""
PDF Generator for Research Papers
Generates downloadable PDFs from paper metadata
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def generate_paper_pdf(paper: dict) -> BytesIO:
    """
    Generate a PDF from paper metadata
    
    Args:
        paper: Dictionary containing paper data (title, abstract, authors, etc.)
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(paper.get('title', 'Untitled'), title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata table
    metadata = [
        ['Authors:', paper.get('author_string', 'Unknown')],
        ['Journal:', f"{paper.get('journal', 'Unknown')} ({paper.get('year', 'N/A')})"],
        ['PMID:', str(paper.get('pmid', 'N/A'))],
        ['DOI:', paper.get('doi', 'N/A')],
    ]
    
    if paper.get('cancer_types'):
        metadata.append(['Cancer Types:', ', '.join(paper['cancer_types'])])
    
    if paper.get('study_type'):
        metadata.append(['Study Type:', paper['study_type']])
    
    table = Table(metadata, colWidths=[1.5*inch, 5*inch])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#9ca3af')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Abstract
    abstract_heading = Paragraph('Abstract', heading_style)
    story.append(abstract_heading)
    
    abstract_text = paper.get('abstract', 'No abstract available.')
    abstract = Paragraph(abstract_text, styles['BodyText'])
    story.append(abstract)
    story.append(Spacer(1, 0.2*inch))
    
    # Keywords
    if paper.get('keywords'):
        keywords_heading = Paragraph('Keywords', heading_style)
        story.append(keywords_heading)
        
        keywords_text = ', '.join(paper['keywords'][:10])
        keywords = Paragraph(keywords_text, styles['BodyText'])
        story.append(keywords)
        story.append(Spacer(1, 0.2*inch))
    
    # PubMed Link
    link_heading = Paragraph('Access Full Paper', heading_style)
    story.append(link_heading)
    
    pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{paper.get('pmid', '')}/"
    link_text = f'<link href="{pubmed_url}" color="blue">{pubmed_url}</link>'
    link_para = Paragraph(link_text, styles['BodyText'])
    story.append(link_para)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_analysis_report_pdf(report: dict) -> BytesIO:
    """
    Generate a PDF for an analysis report
    
    Args:
        report: Dictionary containing analysis data
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=16
    )
    
    # Title
    title_text = f"Repurposing Analysis: {report.get('drug_name', 'Unknown Drug')}"
    title = Paragraph(title_text, title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Report data
    report_data = [
        ['Drug Name:', report.get('drug_name', 'Unknown')],
        ['Cancer Type:', report.get('cancer_type', 'Unknown')],
        ['Confidence Score:', f"{report.get('confidence_score', 0) * 100:.1f}%"],
        ['Clinical Phase:', report.get('clinical_phase', 'N/A')],
        ['Market Potential:', report.get('market_potential', 'N/A')],
        ['Timeline:', report.get('timeline', 'N/A')],
    ]
    
    table = Table(report_data, colWidths=[2*inch, 4.5*inch])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#9ca3af')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Mechanism
    if report.get('mechanism'):
        mechanism_heading = Paragraph('Mechanism of Action', styles['Heading2'])
        story.append(mechanism_heading)
        mechanism = Paragraph(report['mechanism'], styles['BodyText'])
        story.append(mechanism)
        story.append(Spacer(1, 0.2*inch))
    
    # Evidence
    if report.get('evidence'):
        evidence_heading = Paragraph('Supporting Evidence', styles['Heading2'])
        story.append(evidence_heading)
        
        evidence_items = report['evidence'][:5]  # Top 5 pieces of evidence
        for item in evidence_items:
            evidence_para = Paragraph(f"• {item}", styles['BodyText'])
            story.append(evidence_para)
        story.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_market_report_pdf(report_data: dict) -> BytesIO:
    """Generate PDF from AI-generated market report data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=20,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title Page
    title = Paragraph("MARKET ANALYSIS REPORT", title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Report Details
    details = f"""
    <para align=center fontSize=14 textColor=#475569>
    <b>Drug Repurposing Opportunity Analysis</b><br/>
    {report_data['drug_name']} → {report_data['cancer_type']}<br/>
    <br/>
    Confidence Score: {report_data['confidence_score'] * 100:.1f}%<br/>
    Generated: {report_data['generated_date']}<br/>
    </para>
    """
    story.append(Paragraph(details, styles['BodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Key Metrics Box
    metrics = f"""
    <para fontSize=11 textColor=#1e293b leftIndent=20 rightIndent=20>
    <b>Clinical Phase:</b> {report_data['clinical_phase']}<br/>
    <b>Market Potential:</b> {report_data['market_potential']}<br/>
    <b>Timeline to Market:</b> {report_data['timeline']}<br/>
    <b>Mechanism:</b> {report_data['mechanism']}<br/>
    </para>
    """
    story.append(Paragraph(metrics, styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Report Content
    content_heading = Paragraph("DETAILED ANALYSIS", heading_style)
    story.append(content_heading)
    
    # Split report content into paragraphs
    content_lines = report_data['report_content'].split('\n')
    for line in content_lines:
        if line.strip():
            # Check if it's a section header (all caps, short)
            if line.strip().isupper() and len(line.strip()) < 60:
                story.append(Spacer(1, 0.2*inch))
                header_para = Paragraph(f"<b>{line.strip()}</b>", heading_style)
                story.append(header_para)
            else:
                # Regular paragraph
                para = Paragraph(line.strip(), styles['BodyText'])
                story.append(para)
                story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer = f"""
    <para align=center fontSize=9 textColor=#94a3af>
    <i>This report was generated using AI-powered analysis combined with data from<br/>
    the Broad Institute Drug Repurposing Hub and ReDO_DB.<br/>
    For internal research purposes only. Clinical validation required.</i><br/>
    <br/>
    OncoPurpose © 2025 | Market Analysis Report
    </para>
    """
    story.append(Paragraph(footer, styles['BodyText']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
