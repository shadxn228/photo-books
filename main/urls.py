from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.project_search, name='search'),
    path('projects/', views.project_list, name='project_list'),
    path("project/create/", views.project_create, name="project_create"),
    path('projects/<int:id>/', views.project_detail, name='project_detail'),
    path("project/<int:id>/edit/", views.project_edit, name="project_form"),
    path("project/<int:id>/delete/", views.project_delete, name="project_delete"),

    # path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='main:home'), name='logout'),
]