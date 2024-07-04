from django import template
from store.models import Product

register = template.Library()

@register.filter(name='get_price_in_currency')
def get_price_in_currency(product, currency):
    return product.get_price_in_currency(currency)
