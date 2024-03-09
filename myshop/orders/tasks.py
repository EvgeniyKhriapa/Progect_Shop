from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_created(order_id):
    """
    Завдання по відправлення повідомлення за електронною адресою при успішному створенні замовлення
    """
    order = Order.objects.get(id=order_id)
    subject = f'Замовлення nr. {order.id}'
    message = f'Дорогий {order.first_name},\n\n' \
              f'Ви успішно створили замовлення.' \
              f'Ваш номер замовлення {order.id}.'
    mail_sent = send_mail(subject,
                          message,
                          'admin@myshop.com',
                          [order.email])
    return mail_sent
