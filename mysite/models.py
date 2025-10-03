from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class ProjectManager(models.Manager):
    def recent(self):
        return self.filter(created__gte=timezone.now() - timezone.timedelta(days=30))

class Users(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Имя"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    password = models.CharField(max_length=255, verbose_name=_("Пароль"))

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email


class Templates(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Имя"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Шаблон")
        verbose_name_plural = _("Шаблоны")

    def __str__(self):
        return self.name


class Projects(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="projects", verbose_name=_("Пользователь"))
    template = models.ForeignKey(Templates, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Шаблон"))
    title = models.CharField(max_length=255, verbose_name=_("Название проекта"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("Дата изменения"))

    objects = ProjectManager()

    class Meta:
        verbose_name = _("Проект")
        verbose_name_plural = _("Проекты")
        ordering = ["-created"]
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", args=[str(self.id)])


class Pages(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="pages", verbose_name=_("Имя проекта"))
    title = models.CharField(max_length=255, verbose_name="Название страницы", blank=True, null=True)
    pageNumber = models.PositiveIntegerField(verbose_name=_("Номер страницы"))
    pageCount = models.PositiveIntegerField(verbose_name=_("Количество страниц"))
    text = models.TextField(blank=True, null=True, verbose_name=_("Текст"))
    img = models.ImageField(blank=True, null=True, verbose_name=_("Изображение"))

    class Meta:
        verbose_name = _("Страница проекта")
        verbose_name_plural = _("Страницы проекта")
    
    def __str__(self):
        return f"Стр. {self.pageNumber}" 


class Photos(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="photos", verbose_name=_("Пользователь"))
    filename = models.CharField(max_length=255, verbose_name=_("Имя файла"))
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата загрузки"))

    class Meta:
        verbose_name = _("Фотография")
        verbose_name_plural = _("Фотографии")
    
    def __str__(self):
        return self.filename


class PhotosInPages(models.Model):
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name="photos", verbose_name=_("Страница"))
    photo = models.ForeignKey(Photos, on_delete=models.CASCADE, related_name="pages", verbose_name=_("Фотография"))

    class Meta:
        verbose_name = _("Фото на странице")
        verbose_name_plural = _("Фотографии на страницах")
    
    def __str__(self):
        return f"{self.photo.filename} - {self.page}"

class OrderStatus(models.TextChoices):
    NEW = 'new', 'Новый'
    PROCESSING = 'processing', 'В обработке'
    DONE = 'done', 'Завершён'
    CANCELED = 'canceled', 'Отменён'

class Orders(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Пользователь"))
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="orders", verbose_name="Проект")
    status = models.CharField(max_length=50, choices=OrderStatus.choices, default="new", verbose_name=_("Статус"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")
    created = models.DateTimeField(default=timezone.now, verbose_name="Дата заказа")

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
    
    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"