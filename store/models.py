from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Pork', 'Carne de Cerdo'),
        ('Dairy', 'Derivados de Leche'),
        ('Horse', 'Caballos de Raza'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'
