from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('write/<str:username>/', views.slam_page, name='write_slam'),
    path('submit-slam/<str:username>/', views.submit_slam, name='submit_slam'),
    path('logout/', views.logout_user, name='logout'),
]