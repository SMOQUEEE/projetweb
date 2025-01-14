from django.urls import path, include
from django.contrib import admin
from . import views 

urlpatterns = [ 
    
    path('', views.index, name='index'),
    path('utilisateurs/', views.afficher_utilisateurs, name='afficher_utilisateurs'),
    path('register/', views.register, name='register'),
    path('menu/', views.menu, name='menu'),
    path('user/', views.user, name='user'),
    path('login/', views.index, name='login'),
    path('logout/', views.logout, name='logout'),
    path('api/boxes/available', views.get_available_boxes, name='available.boxes'),
    path('api/reservations', views.create_reservation, name='create_reservations'),
    path('change-password/', views.change_password, name='change_password'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('api/reservations/cancel', views.cancel_reservation, name='cancel_reservation'),
    path('administrator/reservations/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),
    path('administrator/users/<str:numero_etudiant>/toggle/', views.toggle_user_block, name='toggle_user_block'),
    path('check-student-number/<str:numero>/', views.check_student_number, name='check_student_number'),
]   