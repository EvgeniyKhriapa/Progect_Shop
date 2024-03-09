from django.db import models
from shop.models import Product


class Order(models.Model):
    """Інформація про клієнта"""
    first_name = models.CharField(max_length=50, verbose_name='Імя')
    last_name = models.CharField(max_length=50, verbose_name='Прізвище')
    email = models.EmailField(verbose_name='Електронна адреса')
    address = models.CharField(max_length=250, verbose_name='Адреса')
    postal_code = models.CharField(max_length=20, verbose_name='Поштовий індекс')
    city = models.CharField(max_length=100, verbose_name='Місто')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        """Загальна вартість товарів"""
        return sum(item.get_cost() for item in self.items.all())

    def get_stripe_url(self):
        if not self.stripe_id:
            # ніяких асоційованих платежів
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # Stripe шлях для тестових платежів
            path = '/test/'
        else:
            # Stripe шлях для справжніх платежів
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    """Зберігає інформацію за кожний оплачений товар"""
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE, verbose_name='Замовлення')
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE, verbose_name='Продукт')
    price = models.DecimalField(max_digits=10,
                                decimal_places=2, verbose_name='Ціна')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
