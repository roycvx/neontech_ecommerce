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
    path('logout/', views.logout_view, name='logout'),

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

    # Lista de productos
    path('admin/inventory/', views.admin_dashboard, name='inventory'),

    # CRUD de productos
    path('clean-form/', views.clean_form, name='clean_form'),
    path('admin/inventory/form/', views.inventory_form, name='inventory_form'),
    path('inventory/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('inventory/delete/<int:product_id>/', views.delete_product, name='delete_product'),

    # Lista de clientes 
    path('admin/clients/',      views.admin_clients,    name='admin_clients'),

    # CRUD de clientes
    path('admin/clients/delete-users/', views.delete_clients, name='delete_users'), # Eliminar Usuario
    path('admin/clients/update-data-users/<int:usuario_id>/<str:usuario_telefono>', views.update_data_users, name='update_data_users'), # Actualizar datos de clientes
    path('admin/clients/create_and_update_users/', views.create_and_update_users, name='create_and_update_users'), # Guardar datos clientes actualizados
    path('admin/client/form/', views.client_form, name='client_form'),

    # Actualizar estado de órdenes
    path('admin/orders/',       views.admin_orders,     name='admin_orders'),
    path('admin/orders/<int:compra_id>/update_state/', views.update_state, name='update_state'), # Cambiar estado
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
