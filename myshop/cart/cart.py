from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart:
    def __int__(self, request):
        """Ініціалізувати кошик"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Створити пустий кошик в сеансі
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Додати товар в кошик або змінити його кількість"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """Відзначити сеанс, як змінений, щоб виконати збереження"""
        self.session.modified = True

    def remove(self, product):
        """Видалити товар із кошика"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Прокрутити товарні позиції в циклі та отримати товари із бази даних"""
        product_ids = self.cart.keys()
        # Отримати об'єкти product та додати їх до кошика
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Підрахувати всі позиції в кошику"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Підрахунок загальної вартості товарів у кошику"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Видалити кошик із сеансу"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
