from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}, base_url=None):
    """
    Rend un template HTML en PDF (avec base_url pour images statiques)
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # Création du PDF
    pdf = pisa.CreatePDF(
        src=html,
        dest=result,
        encoding='utf-8',
        link_callback=None
    )

    if not pdf.err:
        return result.getvalue()
    return None
