from django.contrib import admin
from .forms import ProductForm
from .models import Product
from .models import Buffer


# Register your models here.
PRICE_FILTER_STEPS = 10
class PriceFilter(admin.SimpleListFilter):
    title = 'Цена'
    parameter_name = 'price'
    def lookups(self, request, model_admin):
        #полный спиоск цен
        prices = [c.price for c in model_admin.model.objects.all()]
        prices = filter(None, prices)
        # TODO: найти интервалы цена
        #по 10 интервалов
        max_price = max(prices)
        chunk = int(max_price / PRICE_FILTER_STEPS)
        # print(f'max_price = {max_price}, chunk = {chunk}')

        intervals = [
            (f'{chunk * i}, {chunk * (i + 1)}', f'{chunk * i} - {chunk * (i + 1)}')
            for i in range(PRICE_FILTER_STEPS)
        ]
        return intervals
    def queryset(self, request, queryset):
        choice = self.value() or ''
        if not choice:
            return queryset
        choice = choice.split(',')
        if not len(choice) == 2:
            return queryset
        price_from, price_to = choice
        return queryset.distinct().filter(price__gte=price_from, price__lt=price_to)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'city', 'nominal', 'bank', 'nb', 'metall', 'price')
    list_filter = ('price',
                   PriceFilter,)
    form = ProductForm

@admin.register(Buffer)
class BufferAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'price',
                    )

