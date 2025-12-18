from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')
    slug = models.SlugField(max_length=200, unique=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title