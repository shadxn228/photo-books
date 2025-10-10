from django.urls import path
from . import views

app_name = 'mysite'

urlpatterns = [
  path('', views.project_list, name='project_list'),
  path('<int:id>/', views.project_detail, name='project_detail'),
  path("project/create/", views.project_create, name="project_create"),
  path("project/<int:id>/edit/", views.project_update, name="project_update"),
  path("project/<int:id>/delete/", views.project_delete, name="project_delete"),
]