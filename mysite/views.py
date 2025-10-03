from django.shortcuts import render, get_object_or_404
from django.utils import timezone


# Create your views here.
def index(request):
  return render(request, 'mysite/index.html')

from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Max, Sum
from django.utils import timezone

from .models import Projects, Orders, Users


# --- 1. filter() ---
def projects_list(request):
  projects = Projects.objects.filter(title__icontains="свадьба")
  return render(request, "projects/list.html", {"projects": projects})


# --- 2. exclude() ---
def active_orders(request):
  orders = Orders.objects.exclude(status="canceled")
  return render(request, "orders/list.html", {"orders": orders})


# --- 3. order_by() ---
def projects_by_name(request):
  projects = Projects.objects.order_by("title")
  return render(request, "projects/list.html", {"projects": projects})


# --- 4. использование "__" ---
def gmail_orders(request):
  orders = Orders.objects.filter(user__email__icontains="@gmail.com")
  return render(request, "orders/list.html", {"orders": orders})


def user_projects(request, user_id):
  user = get_object_or_404(User, id=user_id)
  projects = users.projects.all()
  return render(request, "projects/user_projects.html", {"user": user, "projects": projects})


# --- 6. get_absolute_url (redirect/ссылки) ---
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/detail.html", {"project": project})
    # в шаблоне можно написать <a href="{{ project.get_absolute_url }}">


# --- 7. Агрегация и аннотация ---
def stats(request):
    stats_data = {
        # 1) количество проектов у каждого пользователя
        "users_with_projects": Users.objects.annotate(num_projects=Count("projects")),

        # 2) средняя сумма заказов
        "avg_order_price": Orders.objects.aggregate(avg_price=Avg("total_price"))["avg_price"],

        # 3) последний созданный проект
        "last_project": Projects.objects.aggregate(last_created=Max("created"))["last_created"],

        # 4) общая сумма заказов (ещё один пример)
        "total_orders_price": Orders.objects.aggregate(total=Sum("total_price"))["total"],
    }
    return render(request, "stats.html", stats_data)
