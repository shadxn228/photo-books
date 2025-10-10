from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Avg, Max, Sum
from django.http import Http404

from .models import Projects, Orders, Users, Pages
from .forms import ProjectForm


# Create your views here.
def project_list(request):
  projects = Projects.inprocess.all()
  return render(request, 'mysite/project/project_list.html', {"projects": projects})

def project_detail(request, id):
  project = get_object_or_404(Projects, id=id, status=Projects.Status.INPROCESS)
  return render(request, 'mysite/project/project_detail.html', {"project": project})


def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
          project = form.save(commit=False)
          project.user = request.user
          project.save()  

          for i in range(1, 4):
              Pages.objects.create(
                  project=project,
                  pageNumber=i,
                  pageCount=i-1,
                  title=f"Страница {i}"
              )

          return redirect("mysite:project_list")
    else:
        form = ProjectForm()

    return render(request, "mysite/project/project_form.html", {"form": form})


def project_update(request, id):
    project = get_object_or_404(Projects, id=id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("mysite:project_detail", id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, "mysite/project/project_form.html", {"form": form})


def project_delete(request, id):
    project = get_object_or_404(Projects, id=id)
    if request.method == "POST":
        project.delete()
        return redirect("mysite:project_list")
    return render(request, "mysite/project/project_delete.html", {"project": project})


# filter()
def projects_list(request):
  projects = Projects.objects.filter(title__icontains="свадьба")
  return render(request, "mysite/projects/project_list.html", {"projects": projects})


# exclude() 
def active_orders(request):
  orders = Orders.objects.exclude(status="canceled")
  return render(request, "mysite/project/project_list.html", {"orders": orders})


# order_by() 
def projects_by_name(request):
  projects = Projects.objects.order_by("title")
  return render(request, "mysite/projects/project_list.html", {"projects": projects})
























# # использование "__" ---
# def gmail_orders(request):
#   orders = Orders.objects.filter(user__email__icontains="@gmail.com")
#   return render(request, "orders/list.html", {"orders": orders})


# def user_projects(request, user_id):
#   user = get_object_or_404(User, id=user_id)
#   projects = users.projects.all()
#   return render(request, "projects/user_projects.html", {"user": user, "projects": projects})

















# # Агрегация и аннотация ---
# def stats(request):
#     stats_data = {
#         # 1) количество проектов у каждого пользователя
#         "users_with_projects": Users.objects.annotate(num_projects=Count("projects")),

#         # 2) средняя сумма заказов
#         "avg_order_price": Orders.objects.aggregate(avg_price=Avg("total_price"))["avg_price"],

#         # 3) последний созданный проект
#         "last_project": Projects.objects.aggregate(last_created=Max("created"))["last_created"],

#         # 4) общая сумма заказов (ещё один пример)
#         "total_orders_price": Orders.objects.aggregate(total=Sum("total_price"))["total"],
#     }
#     return render(request, "stats.html", stats_data)
