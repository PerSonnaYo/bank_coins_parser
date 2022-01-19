from django.db import models
# from django.contrib import admin
from django.utils.html import format_html

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

class Comments(models.Model):
    dated = models.DateField(
        verbose_name='Дата',
    )
    name = models.TextField(
        verbose_name='Название',
        default='Coin'
    )
    url_lot = models.URLField(
        verbose_name='Ссылка на лот',
        unique=True,
    )
    url_saler = models.URLField(
        verbose_name='Ссылка на продавца',
    )

    # @admin.display
    # def colored_name(self):
    #     return format_html(
    #         "<a href='{url}'>{url}</a>", url=self.url_saler,
    #     )
    status = models.TextField(
        verbose_name='Статус',
    )
    post1_price = models.CharField(
        max_length=50,
        verbose_name='Почтовый ценник',
    )
    current_price = models.PositiveIntegerField(
        verbose_name='Текущая цена',
        default=0,
    )

    my_current_price = models.PositiveIntegerField(
        verbose_name='Моя текущая цена',
        default=0,
    )

    stack = models.PositiveIntegerField(
        verbose_name='Ставка',
        default=0,
    )
    name_saler = models.TextField(
        verbose_name='Имя продавца',
    )
    comment_id = models.PositiveIntegerField(
        verbose_name='Последний коммент',
        default=0,
    )
    buy = models.TextField(
        verbose_name='Оплачено/Неоплачено',
        default='No',
    )
    def __str__(self):
        return f'#{self.url_lot} {self.status} {self.stack}'

    class Meta:
        verbose_name= 'Таблица торгов в ВК'