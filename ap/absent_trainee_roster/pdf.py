import cStringIO as StringIO

from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponse

import xhtml2pdf.pisa as pisa
from cgi import escape


def render_to_pdf(template_src, context_dict):
	template = get_template(template_src)
	# context = Context(context_dict)
	html = template.render(context=context_dict)
	result = StringIO.StringIO()

	pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return HttpResponse('We had some errors<pre>%s</pre>' %escape(html))
