from django.urls import path
from django.views.generic import TemplateView

from . import api, views

app_name = 'catalog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('delivery/', TemplateView.as_view(template_name='pages/delivery.html'), name='delivery'),
    path('catalog/', views.CategoryListView.as_view(), name='category_list'),
    path('catalog/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('catalog/<slug:category_slug>/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', TemplateView.as_view(template_name='catalog/cart.html'), name='cart'),
    path('api/create-order/', api.create_order, name='create_order'),
    path('api/order/<str:order_id>/', api.get_order, name='get_order'),
    path('api/order/<str:order_id>/confirm/', api.confirm_order, name='confirm_order'),
]
