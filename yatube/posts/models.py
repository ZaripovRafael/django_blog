from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    """Класс модели записи группы"""

    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="slug",
    )
    description = models.TextField(
        max_length=200,
        verbose_name='Опиисание',
    )

    class Meta:
        default_related_name = 'group'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Класс модели публикаций"""

    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        default_related_name = 'posts'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        max_length_of_text = 15
        return self.text[:max_length_of_text]
