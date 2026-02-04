from django.contrib import admin
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'slug', 'is_active', 'order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order', 'is_main']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'sku', 'price', 'is_available', 'is_popular', 'is_new']
    list_filter = ['category', 'is_available', 'is_popular', 'is_new']
    search_fields = ['name', 'slug', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['category']
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'slug', 'sku')
        }),
        ('Опис', {
            'fields': ('description', 'full_description')
        }),
        ('Ціна', {
            'fields': ('price', 'old_price')
        }),
        ('Статус', {
            'fields': ('is_available', 'is_popular', 'is_new')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'is_main']
    list_filter = ['is_main']
    raw_id_fields = ['product']
