from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Цена"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Описание"))
    
    class Meta:
        verbose_name = _("Шаблон")
        verbose_name_plural = _("Шаблоны")

    def __str__(self):
        return self.name

class ProcessManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Projects.Status.INPROCESS)

class Projects(models.Model):

    class Status(models.TextChoices):
        INPROCESS = 'inprocess', 'В процессе'
        ORDERED = 'ordered', 'Заказано'
        ARCHIVE = 'archive', 'Архив'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects", verbose_name=_("Пользователь"))
    template = models.ForeignKey(Templates, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Шаблон"))
    title = models.CharField(max_length=255, verbose_name=_("Название проекта"))
    status = models.CharField(max_length=50, choices=Status.choices, default="inprocess", verbose_name=_("Статус"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("Дата изменения"))

    inprocess = ProcessManager()

    class Meta:
        verbose_name = _("Проект")
        verbose_name_plural = _("Проекты")
        ordering = ["-created"]
        indexes = [
            models.Index(fields=['-created']),
        ]

    def is_expired(self):
        return timezone.now() > self.created + timedelta(days=90)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("mysite:project_detail", args=[str(self.id)])


class Pages(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="pages", verbose_name=_("Имя проекта"))
    title = models.CharField(max_length=255, verbose_name="Название страницы", blank=True, null=True)
    photos = models.ManyToManyField("Photos", through="PhotosInPages", through_fields=("page", "photo"), related_name="pages", verbose_name="Фотографии")
    pageNumber = models.PositiveIntegerField(verbose_name=_("Номер страницы"), blank=True, null=True)
    text = models.TextField(blank=True, null=True, verbose_name=_("Текст"))

    class Meta:
        verbose_name = _("Страница проекта")
        verbose_name_plural = _("Страницы проекта")
    
    def __str__(self):
        return f"Стр. {self.pageNumber}" 


class Photos(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="photos", verbose_name=_("Пользователь"))
    filename = models.CharField(max_length=255, verbose_name=_("Имя файла"), blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата загрузки"))
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, verbose_name=_("Изображение"))

    class Meta:
        verbose_name = _("Фотография")
        verbose_name_plural = _("Фотографии")

    def is_old(self):
        return self.upload_date < timezone.now() - timedelta(days=30)
    
    def __str__(self):
        return self.filename


class PhotosInPages(models.Model):
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name="photos_in_page", verbose_name=_("Страница"))
    photo = models.ForeignKey(Photos, on_delete=models.CASCADE, related_name="photos_in_pages", verbose_name=_("Фотография"))
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))

    class Meta:
        verbose_name = _("Фото на странице")
        verbose_name_plural = _("Фотографии на страницах")
        ordering = ['order', 'added_at']
    
    def __str__(self):
        return f"{self.photo.filename} - {self.page}"


class Orders(models.Model):

    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        PROCESSING = 'processing', 'В обработке'
        DONE = 'done', 'Завершён'
        CANCELED = 'canceled', 'Отменён'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Пользователь"))
    status = models.CharField(max_length=50, choices=Status.choices, default="new", verbose_name=_("Статус"))
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    modified = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    projects = models.ManyToManyField("Projects", through='OrderItem', related_name="orders")

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
    
    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"

    def is_new(self):
        return (timezone.now() - self.created).days < 1

    @property
    def total_sum(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    project = models.ForeignKey(Projects, on_delete=models.PROTECT, verbose_name="Проект", null=True, blank=True,)
    template = models.ForeignKey(Templates, on_delete=models.PROTECT, verbose_name="Шаблон", editable=False, null=True, blank=True,)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", null=True, blank=True,)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.project.title} × {self.quantity}"

    def save(self, *args, **kwargs):
        if self.project:
            self.template = self.project.template
            if self.template and not self.price:
                self.price = self.template.price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.price * self.quantity
