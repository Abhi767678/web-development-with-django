from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────
    path('register/',         views.register_view,       name='register'),
    path('login/',            views.login_view,           name='login'),
    path('logout/',           views.logout_view,          name='logout'),

    # ── Customer ──────────────────────────────────────────────
    path('',                      views.home_view,            name='home'),
    path('product/<int:pk>/',     views.product_detail_view,  name='product_detail'),
    path('cart/',                 views.cart_view,            name='cart'),
    path('cart/add/<int:pk>/',    views.add_to_cart_view,     name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_view,     name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart_view,name='remove_from_cart'),
    path('checkout/',             views.checkout_view,        name='checkout'),
    path('my-orders/',            views.my_orders_view,       name='my_orders'),

    # ── Admin ─────────────────────────────────────────────────
    path('dashboard/',                       views.admin_dashboard_view,     name='admin_dashboard'),
    path('dashboard/products/',              views.admin_products_view,      name='admin_products'),
    path('dashboard/products/add/',          views.admin_add_product_view,   name='admin_add_product'),
    path('dashboard/products/edit/<int:pk>/',views.admin_edit_product_view,  name='admin_edit_product'),
    path('dashboard/products/delete/<int:pk>/',views.admin_delete_product_view,name='admin_delete_product'),
    path('dashboard/orders/',                views.admin_orders_view,        name='admin_orders'),
    path('dashboard/orders/<int:pk>/',       views.admin_update_order_view,  name='admin_update_order'),
    path('dashboard/users/',                 views.admin_users_view,         name='admin_users'),
    path('dashboard/users/toggle/<int:pk>/', views.admin_toggle_user_view,   name='admin_toggle_user'),
    # Categories
    path('dashboard/categories/',                    views.admin_categories_view,      name='admin_categories'),
    path('dashboard/categories/edit/<int:pk>/',      views.admin_edit_category_view,   name='admin_edit_category'),
    path('dashboard/categories/delete/<int:pk>/',    views.admin_delete_category_view, name='admin_delete_category'),

    # Brands
    path('dashboard/brands/',                        views.admin_brands_view,          name='admin_brands'),
    path('dashboard/brands/edit/<int:pk>/',          views.admin_edit_brand_view,      name='admin_edit_brand'),
    path('dashboard/brands/delete/<int:pk>/',        views.admin_delete_brand_view,    name='admin_delete_brand'),
]