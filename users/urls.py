from django.urls import path
from . import views

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.show_start_page, name='start'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    path('search-products/<str:categoria>/', views.products_list, name='search_products'),
    path('detail-product/<int:producto_id>/', views.show_detail_product, name='detail_product'),

    path('shopping-cart/', views.show_shopping_cart, name='shopping_cart'),
    path('add-to-cart/<int:producto_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:producto_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:producto_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('cart-payment/', views.cart_payment, name='cart_payment_now'),
    path('cart-payment/link-card', views.link_card, name='link_card'),
    path('cart-payment/save-address', views.register_address, name='save_address'),
    path('process-payment/', views.process_payment, name='process_payment'),

    path('successful-purchase/', views.success_purchase, name='successful_purchase'),
]