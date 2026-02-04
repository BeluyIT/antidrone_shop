from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """Hierarchical product category."""

    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Батьківська категорія'
    )
    description = models.TextField('Опис', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class MPTTMeta:
        order_insertion_by = ['order', 'name']

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Product in the catalog."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категорія'
    )
    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    sku = models.CharField('Артикул', max_length=50, blank=True)
    description = models.TextField('Короткий опис', blank=True)
    full_description = models.TextField('Повний опис', blank=True)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2, null=True, blank=True)
    old_price = models.DecimalField('Стара ціна', max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField('В наявності', default=True)
    is_popular = models.BooleanField('Популярний', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={
            'category_slug': self.category.slug,
            'product_slug': self.slug
        })

    def get_main_image(self):
        """Get the main product image or first available."""
        main_image = self.images.filter(is_main=True).first()
        if main_image:
            return main_image
        return self.images.first()


class ProductImage(models.Model):
    """Product image."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар'
    )
    image = models.ImageField('Зображення', upload_to='products/%Y/%m/')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_main = models.BooleanField('Головне зображення', default=False)

    class Meta:
        verbose_name = 'Зображення товару'
        verbose_name_plural = 'Зображення товарів'
        ordering = ['order', 'id']

    def __str__(self):
        return f'Зображення {self.product.name}'
