from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView

from .models import Category, Product


class IndexView(TemplateView):
    """Home page view."""
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, level=0)
        context['popular_products'] = Product.objects.filter(is_popular=True, is_available=True)[:8]
        context['new_products'] = Product.objects.filter(is_new=True, is_available=True)[:8]
        return context


class CategoryListView(ListView):
    """List of root categories."""
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(is_active=True, level=0)


class CategoryDetailView(DetailView):
    """Category detail with products."""
    model = Category
    template_name = 'catalog/category_detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        # Get all descendant categories including current
        descendants = category.get_descendants(include_self=True)
        products_qs = Product.objects.filter(
            category__in=descendants,
            is_available=True
        ).select_related('category').prefetch_related('images')
        page_size = getattr(settings, 'CATALOG_PAGE_SIZE', 24)
        paginator = Paginator(products_qs, page_size)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['products'] = page_obj
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['is_paginated'] = page_obj.has_other_pages()
        context['products_count'] = paginator.count
        context['subcategories'] = category.get_children().filter(is_active=True)
        context['ancestors'] = category.get_ancestors()
        return context


class ProductDetailView(DetailView):
    """Product detail page."""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True
        ).select_related('category').prefetch_related('images')

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        return get_object_or_404(
            queryset,
            slug=self.kwargs['product_slug'],
            category__slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['category'] = product.category
        context['ancestors'] = product.category.get_ancestors()
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(pk=product.pk)[:4]
        return context
