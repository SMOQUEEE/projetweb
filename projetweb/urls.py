from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from myapp import views  # Import your app's views

urlpatterns = [
    # Default Django admin site
    path('admin/', admin.site.urls),

    # Redirect /administrator/ to /admin/ for Django admin (optional)
    path('administrator/', RedirectView.as_view(url='/admin/', permanent=True)),

    # Custom administrator views
    path('administrator/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('administrator/reservations/', views.admin_reservations, name='admin_reservations'),
    path('administrator/boxes/', views.admin_boxes, name='admin_boxes'),
    path('administrator/users/', views.admin_users, name='admin_users'),
    path('administrator/users/<int:user_id>/toggle-block/', views.toggle_user_block, name='toggle_user_block'),
    path('administrator/reservations/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),

    # Include app-specific URLs
    path('', include('myapp.urls')),
]
