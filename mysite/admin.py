from django.contrib import admin
from .models import Users, Templates, Projects, Pages, Photos, PhotosInPages, Orders


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    search_fields = ("name", "email")
    list_display_links = ("id", "name")


@admin.register(Templates)
class TemplatesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


class PagesInline(admin.TabularInline):
    model = Pages
    extra = 1
    raw_id_fields = ("project",)


class PhotosInPagesInline(admin.TabularInline):
    model = PhotosInPages
    extra = 1
    raw_id_fields = ("photo",)


@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "template", "created", "modified", "page_count")
    list_filter = ("created", "modified", "template")
    raw_id_fields = ("user", "template")
    search_fields = ("title", "user__name", "template__name")
    date_hierarchy = "created"
    inlines = [PagesInline]

    @admin.display(description="Страниц")
    def page_count(self, obj):
        return obj.pages.count()


@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "title", "pageNumber", "pageCount")
    list_filter = ("project",)
    raw_id_fields = ("project",)
    search_fields = ("text",)


@admin.register(Photos)
class PhotosAdmin(admin.ModelAdmin):
    list_display = ("id", "filename", "user", "upload_date")
    list_filter = ("upload_date",)
    raw_id_fields = ("user",)
    search_fields = ("filename",)
    readonly_fields = ("upload_date",)


@admin.register(PhotosInPages)
class PhotosInPagesAdmin(admin.ModelAdmin):
    list_display = ("id", "page", "photo")
    raw_id_fields = ("page", "photo")
    search_fields = ("page__project__title", "photo__filename")


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "project", "status", "created", "modified")
    list_filter = ("status",)
    raw_id_fields = ("user",)
    search_fields = ("user__name",)
