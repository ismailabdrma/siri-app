
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # Ensure logout redirects to home
    path('companies/', views.companies, name='companies'),
    path('companies/add/', views.add_company, name='add_company'),
    path('companies/<int:company_id>/input_siri/', views.input_siri, name='input_siri'),
    path('companies/<int:company_id>/result/', views.result, name='result'),
    path('about/', views.about, name='about'),
]