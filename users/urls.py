from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # """URLS Auth"""
    path('', views.show_start_page, name='start'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='start'), name='logout'),

    # """URLS del Client"""
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),

    # Búsqueda y detalles de productos
    path('search-products/<str:categoria>/', views.products_list, name='search_products'),
    path('detail-product/<int:producto_id>/', views.show_detail_product, name='detail_product'),

    # Carrito de compras
    path('shopping-cart/', views.show_shopping_cart, name='shopping_cart'),
    path('add-to-cart/<int:producto_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:producto_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:producto_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Pagos
    path('cart-payment/', views.cart_payment, name='cart_payment_now'),
    path('cart-payment/link-card', views.link_card, name='link_card'),
    path('cart-payment/save-address', views.register_address, name='save_address'),
    path('process-payment/', views.process_payment, name='process_payment'),

    # Confirmación de compra exitosa
    path('successful-purchase/', views.success_purchase, name='successful_purchase'),

    # """URLS del Admin"""
    path('admin/inventory/', views.admin_dashboard, name='inventory'),
    path('admin/inventory/form/', views.inventory_form, name='inventory_form'),
    path('inventory/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('inventory/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin/clients/',      views.admin_clients,    name='admin_clients'),
    path('admin/client/form/', views.client_form, name='client_form'),
    path('admin/orders/',       views.admin_orders,     name='admin_orders'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)