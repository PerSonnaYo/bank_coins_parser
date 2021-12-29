from django.contrib import admin
from .forms import ProductForm
from .forms import CommentForm
from .models import Product
from .models import Buffer
from .models import Comments
from django.utils.html import format_html

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

@admin.register(Comments)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
            'dated',
            'name',
            'show_firm_url1',
            'show_firm_url',
            'current_price',
            'status',
            'stack',
            'post1_price',
            'name_saler',
            'comment_id',
            'buy',
        )
    def show_firm_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.url_saler)

    show_firm_url.short_description = "Firm URL"

    def show_firm_url1(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.url_lot)

    show_firm_url1.short_description = "Firm1 URL"
    list_filter = ('dated', 'status',)
    form = CommentForm