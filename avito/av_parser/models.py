from django.db import models

class Product(models.Model):
    name = models.TextField(
        verbose_name='Название',
    )
    year = models.PositiveIntegerField(
        verbose_name='Год',
    )
    city = models.TextField(
        verbose_name='Город',
    )
    nominal = models.TextField(
        verbose_name='Номинал',
    )
    bank = models.TextField(
        verbose_name='Банк',
    )
    nb = models.TextField(
        verbose_name='Каталожный номер',
        unique=True,
    )
    metall = models.TextField(
        verbose_name='Металл',
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена',
    )

    def __str__(self):
        return f'#{self.name} {self.price} {self.bank}'

    class Meta:
        verbose_name= 'Продукт'
        verbose_name_plural = 'Продукты'

class Buffer(models.Model):
    name = models.TextField(
        verbose_name='Название',
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена',
    )
    def __str__(self):
        return f'#{self.name} {self.price}'
    class Meta:
        verbose_name= '<Буфер>'