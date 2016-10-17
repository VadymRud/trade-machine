from django.contrib import admin
from .models import News, Comment


class NewsAdmin(admin.ModelAdmin):
    fields = ['title', 'text']
    list_display = ('title', 'author', 'date',)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


class CommentAdmin(admin.ModelAdmin):
    fields = ['news', 'author', 'text']
    list_display = ('news', 'author')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()

admin.site.register(News, NewsAdmin)
admin.site.register(Comment, CommentAdmin)
