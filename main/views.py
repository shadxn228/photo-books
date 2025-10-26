from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from mysite.models import Projects, Photos, PhotosInPages, Orders, Users, Pages
from .forms import SearchForm
from .forms import ProjectForm

# Create your views here.
def home(request):
    return render(request, "main/index.html")

# Виджеты
def home(request):

    latest_projects = Projects.inprocess.filter(status='inprocess').order_by('-created')[:3]
    popular_projects = Projects.inprocess.annotate(num_pages=Count('pages')).order_by('-num_pages')[:3]

    used_photo_ids = PhotosInPages.objects.values_list('photo_id', flat=True)
    unused_photos = Photos.objects.exclude(id__in=used_photo_ids)[:3]

    context = {
        'latest_projects': latest_projects,
        'popular_projects': popular_projects,
        'unused_photos': unused_photos,
    }

    return render(request, 'main/index.html', context)

# Поиск
def project_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Projects.objects.filter(
                Q(title__icontains=query) |
                Q(template__name__icontains=query)
            )
            
    return render(request,
                 'main/search.html',
                 {'form': form,
                  'query': query,
                  'results': results})


def project_list(request):
  projects = Projects.objects.select_related('user').all()
  return render(request, 'main/project/project_list.html', {"projects": projects})

def project_detail(request, id):
  project = get_object_or_404(Projects.inprocess.prefetch_related('pages__photos_in_page__photo'), id=id, status=Projects.Status.INPROCESS)
  return render(request, 'main/project/project_detail.html', {"project": project,})

# Создание проекта
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            project.save()  

            for i in range(1, 4):
                Pages.objects.create(
                    project=project,
                    pageNumber=i,
                    title=f"Страница {i}"
                )

            return redirect("main:project_list")
    else:
        form = ProjectForm()

    return render(request, "main/project/project_form.html", {"form": form})

# Редактирование проекта 
def project_edit(request, id):
    project = get_object_or_404(Projects, id=id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()

            Pages.objects.filter(project=project).update(text="Обновлено при редактировании проекта")

            return redirect("main:project_detail", id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, "main/project/project_form.html", {"form": form})

# Удаление проекта
def project_delete(request, id):
    project = get_object_or_404(Projects, id=id)
    if request.method == "POST":
        project.delete()
        return redirect("main:project_list")
    return render(request, "main/project/project_delete.html", {"project": project})