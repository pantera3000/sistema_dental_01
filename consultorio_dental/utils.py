from django.template.loader import get_template
from django.http import HttpResponse
import io
import logging

logger = logging.getLogger(__name__)

def render_to_pdf(template_src, context_dict={}):
    """
    Renderiza un template de Django a PDF usando xhtml2pdf.
    La importación es lazy para evitar errores al iniciar el servidor.
    """
    try:
        from xhtml2pdf import pisa
    except ImportError as e:
        logger.error(f"xhtml2pdf no está disponible: {e}")
        return HttpResponse(
            "Error: xhtml2pdf no está instalado. Por favor ejecuta: pip install xhtml2pdf",
            status=500
        )
    
    try:
        template = get_template(template_src)
        html = template.render(context_dict)
        result = io.BytesIO()
        
        # Generar PDF
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            pdf_content = result.getvalue()
            logger.info(f"PDF generado exitosamente: {len(pdf_content)} bytes")
            return HttpResponse(pdf_content, content_type='application/pdf')
        else:
            logger.error(f"Error en pisa.pisaDocument: {pdf.err}")
            return HttpResponse(f"Error generando PDF: {pdf.err}", status=500)
    except Exception as e:
        logger.exception("Error inesperado generando PDF")
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)
