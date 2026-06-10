from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard_gestor, name='dashboard'),
    path('sair/', auth_views.LogoutView.as_view(next_page='/'), name='logout_direto'),
]