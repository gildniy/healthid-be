import weasyprint

from weasyprint.fonts import FontConfiguration

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.template.loader import render_to_string

from healthid.apps.orders.models import SupplierOrderDetails
from healthid.utils.app_utils.database import get_model_object


class SupplierOrderFormPDFView(View):

    def get(self, request, *args, **kwargs):
        supplier_order_detail_id = kwargs.get('supplier_order_detail_id')
        supplier_order_detail = get_model_object(SupplierOrderDetails, 'id',
                                                 supplier_order_detail_id)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=supplier_order_form.pdf'
        html = render_to_string('orders/supplier_order_form.html',
                                {'detail': supplier_order_detail})
        font_config = FontConfiguration()
        css = weasyprint.CSS(settings.STATIC_ROOT + "/css/order-pdf.css",
                             font_config=font_config)
        weasyprint.HTML(string=html).write_pdf(
            response, stylesheets=[css])
        return response
