from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order


@shared_task
def payment_completed(order_id):
    """Завдання по відправленні листа на електронну адресу при успішній оплаті замовлення"""
    order = Order.objects.get(id=order_id)
    # створити рахунок на e-mail
    subject = f'Мій магазин - Рахунок за номером: {order.id}'
    message = 'Будь ласка, додайте рахунок-фактуру для вашої нещодавньої покупки.'
    email = EmailMessage(subject, message, 'admin@myshop.com', [order.email])
    # генерування PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # прикріпити PDF файл
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    # відправити e-mail
    email.send()
