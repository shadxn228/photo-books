from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Avg, Max, Sum
from django.http import Http404
from django.contrib import messages

from .models import Projects, Orders, Users, Pages
from .forms import ProjectForm


# Create your views here.
def project_list(request):
  projects = Projects.inprocess.select_related('user').all()
  return render(request, 'mysite/project/project_list.html', {"projects": projects})

def project_detail(request, id):
  project = get_object_or_404(Projects.inprocess.prefetch_related('pages__photos_in_page__photo'), id=id, status=Projects.Status.INPROCESS)
  return render(request, 'mysite/project/project_detail.html', {"project": project})

# Создание проекта
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user

            existing_count = Projects.inprocess.filter(user=request.user).count()
            if existing_count >= 7:
                messages.warning(request, "Вы достигли лимита проектов.")
                return redirect("mysite:project_list")

            project.save()  

            for i in range(1, 4):
                Pages.objects.create(
                    project=project,
                    pageNumber=i,
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

            Pages.modified.filter(project=project).update(text="Обновлено при редактировании проекта")

            return redirect("mysite:project_detail", id=pкеш-фреймворкаroject.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, "mysite/project/project_form.html", {"form": form})


def project_delete(request, id):
    project = get_object_or_404(Projects, id=id)
    if request.method == "POST":
        project.delete()
        return redirect("mysite:project_list")
    return render(request, "mysite/project/project_delete.html", {"project": project})

# Добавление фото
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('photo_list')
    else:
        form = PhotoForm()

    photo_names = Photos.objects.values_list('filename', flat=True)

    return render(request, 'mysite/photo/upload.html', {'form': form})
