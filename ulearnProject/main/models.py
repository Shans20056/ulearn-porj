from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Вызвать стандартный метод сохранения модели
        super().save(*args, **kwargs)