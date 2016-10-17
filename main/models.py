from django.db import models
from clients.models import Client


class News(models.Model):
    author = models.ForeignKey(Client, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Comment(models.Model):
    news = models.ForeignKey(News)
    author = models.ForeignKey(Client)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'
