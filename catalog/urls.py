from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('catalog/', views.CategoryListView.as_view(), name='category_list'),
    path('catalog/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('catalog/<slug:category_slug>/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', TemplateView.as_view(template_name='catalog/cart.html'), name='cart'),
]
