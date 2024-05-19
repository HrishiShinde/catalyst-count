# upload/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_page, name='upload_page'),
    path('query-builder/', views.query_builder, name='query_builder'),
    path('users/', views.users, name='users'),
    path('add/', views.add_user, name='add_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
