from django.contrib import admin
from django.http import HttpResponse
from .models import Users, Templates, Projects, Pages, Photos, PhotosInPages, Orders, OrderItem
from django.template.loader import render_to_string
from weasyprint import HTML


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    search_fields = ("name", "email")
    list_display_links = ("id", "name")
    ordering = ("name",)


@admin.register(Templates)
class TemplatesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "description")
    search_fields = ("name",)
    list_filter = ("price",)
    list_display_links = ("id", "name")


class PagesInline(admin.TabularInline):
    model = Pages
    extra = 1
    fields = ("title", "pageNumber",)
    readonly_fields = ("pageNumber",)


class PhotosInPagesInline(admin.TabularInline):
    model = PhotosInPages
    extra = 1
    raw_id_fields = ("photo",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ("project",)
    readonly_fields = ("price", "template",)
    fields = ("project", "quantity", "price",)

    @admin.display(description="Стоимость позиции")
    def get_cost(self, obj):
        if not obj.id:
            return ""
        return f"{obj.total_sum:.2f} ₽"


@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "template", "status", "created", "modified", "page_count")
    list_filter = ("status", "created", "template")
    raw_id_fields = ("user", "template")
    search_fields = ("title", "user__name", "template__name")
    date_hierarchy = "created"
    inlines = [PagesInline]
    list_display_links = ("id", "title")
    actions = ['download_pdf']

    @admin.display(description="Страниц")
    def page_count(self, obj):
        return obj.pages.count()

    @admin.action(description="Скачать PDF")
    def download_pdf(self, request, queryset):
        html_string = render_to_string('mysite/project/pdf.html', {'projects': queryset})

        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="projects_report.pdf"'
        return response


@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "title", "pageNumber")
    list_filter = ("project",)
    raw_id_fields = ("project",)
    search_fields = ("title", "text",)
    inlines = [PhotosInPagesInline]
    list_display_links = ("id", "title")


@admin.register(Photos)
class PhotosAdmin(admin.ModelAdmin):
    list_display = ("filename", "id", "user", "upload_date")
    list_filter = ("upload_date",)
    raw_id_fields = ("user",)
    search_fields = ("filename", "user__name",)
    readonly_fields = ("upload_date",)
    date_hierarchy = "upload_date"


@admin.register(PhotosInPages)
class PhotosInPagesAdmin(admin.ModelAdmin):
    list_display = ("page", "id", "photo", "project_title", "order")
    raw_id_fields = ("page", "photo")
    search_fields = ("page__project__title", "photo__filename")

    @admin.display(description="Проект")
    def project_title(self, obj):
        return obj.page.project.title


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created", "total_cost")
    list_filter = ("status", "created")
    raw_id_fields = ("user",)
    date_hierarchy = "created"
    search_fields = ("user__name", "items__project__title")
    readonly_fields = ("created", "modified")
    inlines = [OrderItemInline]

    @admin.display(description="Сумма заказов")
    def total_cost(self, obj):
        return f"{obj.total_sum:.2f} ₽"
